FROM debian:stable

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    iproute2 \
    net-tools \
    iputils-ping \
    curl \
    vim \
    procps \
    dnsutils \
    netcat-openbsd \
    tcpdump \
    && apt clean

WORKDIR /workspace
