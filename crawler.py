# This tool is crawling japanese real estate data
# And this script execute other scripts due to arguments
# current functions are:
# 1. crawl rent data: script: collect_rent_data.py

import argparse
import logging
import collect_rent_data

def parse_args():
    parser = argparse.ArgumentParser(description='Crawl real estate data')
    parser.add_argument('-function', type=str, help='execute function',
                        choices=['rent_data'])
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    if args.function == 'rent_data':
        collect_rent_data.main()
    else:
        raise ValueError('Invalid function')

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