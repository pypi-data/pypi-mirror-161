FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    build-essential \
    software-properties-common \
    python3 python3-distutils \
    git wget rsync nano htop zip unzip graphviz

RUN mkdir /opt/get-pip && \
    cd /opt/get-pip && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    chmod +x get-pip.py && \
    python3 ./get-pip.py && \
    pip install tox wheel pbr pytest

RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
    python3.7 python3.8 python3.9 python3.10 python3.11 \
    python3.7-distutils python3.8-distutils python3.9-distutils python3.10-distutils python3.11-distutils
