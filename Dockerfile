FROM public.ecr.aws/debian/debian:stable-slim as debian_base
RUN apt-get update -y
RUN apt-get install build-essential cmake libbluetooth-dev libsdl2-dev \
  libcurl4-openssl-dev libenet-dev libfreetype6-dev libharfbuzz-dev \
  libjpeg-dev libogg-dev libopenal-dev libpng-dev \
  libssl-dev libvorbis-dev libmbedtls-dev pkg-config zlib1g-dev git sqlite3 subversion -y
RUN apt install -y python3-pip
RUN pip install pyenet
RUN apt install -y curl vim unzip jq
COPY udp-flood.py /udp-flood.py
RUN chmod +x /udp-flood.py
