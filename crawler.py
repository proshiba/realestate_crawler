import os
import sys
import re
import logging
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import pytesseract
import pandas as pd
import boto3

# 画像のURL
URL = "https://www.pbn.jp/yachin/"
# このスクリプトが保存されているディレクトリを取得
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, "data")

def get_image_url_list():
    res = requests.get(URL)
    parser = BeautifulSoup(res.text, "html.parser")
    images = parser.find_all("div", {"class":"alignC mt20 sbimg"})
    image_url_list = []
    for each_div in images:
        if each_div.img:
            img_el = each_div.img
            image_url = img_el.get("src")
            image_url_list.append(image_url)
    return image_url_list

def get_newest_image_url(image_url_list):
    return image_url_list[0]

def get_newest_month(image_url):
    # 以下のようなURLから年月を取得。取得時のフォーマットは"YYYYMM"
    # URL format: https://www.pbn.jp/cms/wp-content/uploads/2024/11/202411-1.jpg
    redata = re.search(r"/uploads/(\d{4})/(\d{2})", image_url)
    this_month = f"{redata.group(1)}{redata.group(2)}"
    return this_month

def get_image_data(image_url):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    return image

# OCRでテキストを抽出
def get_extracted_text(image):
    return pytesseract.image_to_string(image, lang="jpn")

def has_prefecture_suffix(text):
    return "県" in text or "都" in text or "府" in text or "道" in text

def extract_rent_data(extracted_text):
    # 抽出されたテキストを行ごとに分割
    lines = extracted_text.split("\n")
    data = []
    for line in lines:
        parts = [ each.strip() for each in line.split('|') ]
        if len(parts) > 1 and has_prefecture_suffix(parts[0]):
            each_pref_data = []
            for each in parts:
                if "\\" in each and not each.startswith("\\"):
                    each_field = each.split("\\")
                    each_pref_data.append(each_field[0])
                    for s in each_field[1:]:
                        each_pref_data.append("\\"+s)
                else:
                    each_value = each.strip()
                    each_pref_data.append(each_value)
            tmp = [ each_pref_data[0].strip() ]
            for each in each_pref_data[1:]:
                for each_field in each.split(" "):
                    if each_field.startswith("\\"):
                        tmp.append(each_field.strip())
            data.append([tmp[0], tmp[1]])
    return data

def save_extracted_data(data, filename):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    columns = ["prefecture", "1room(yen)"]
    df = pd.DataFrame(data, columns=columns)
    csv_file_path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    df.to_csv(csv_file_path, index=False)
    logger.info(f"rent data is extracted and saved to {csv_file_path}.")
    return csv_file_path

def upload_to_s3(file_path):
    s3 = boto3.resource("s3")
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    if bucket_name:
        logger.info(f"upload to s3: {file_path}")
        bucket = s3.Bucket(bucket_name)
        bucket.upload_file(file_path, os.path.basename(file_path))
        logger.info(f"upload to s3: {file_path}")
    else:
        logger.warning("S3_BUCKET_NAME is not set. Skip uploading to S3.")

def main():
    image_url_list = get_image_url_list()
    logger.info(f"URL found Num:{len(image_url_list)}")
    newest_image_url = get_newest_image_url(image_url_list)
    newest_month = get_newest_month(newest_image_url)
    image = get_image_data(newest_image_url)
    extracted_text = get_extracted_text(image)
    data = extract_rent_data(extracted_text)
    file_path = save_extracted_data(data, newest_month)
    upload_to_s3(file_path)

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

if __name__ == "__main__":
    logger = setup_logger()
    logger.info("start crawling...")
    main()
    logger.info("finish crawling.")