ARG VER="3.8"
FROM python:${VER}-slim

RUN apt-get update && apt-get install -y tzdata \
&& apt-get install -y libopencv-dev \
&& apt-get install -y git \
&& apt-get install -y wget \
&& apt-get install -y unzip \
&& apt-get install -y sqlite3

WORKDIR /tmp/work
COPY requirements.txt ${PWD}
RUN pip install -r requirements.txt

EXPOSE 8881

ENV TZ=Asia/Tokyo

