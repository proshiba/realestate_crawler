# based on ubuntu:22.04
FROM ubuntu:22.04

# working directory is /opt/crawler
WORKDIR /opt/crawler

# copy all files from the current directory to /opt/crawler
COPY . .

# install with script named install.sh
RUN chmod +x install.sh && ./install.sh
