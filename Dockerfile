FROM alpine:3.9

ARG PIP_TAG=19.1.1

WORKDIR /opt/chained-ci-mqtt-trigger-master

COPY . .

RUN apk add --no-cache libressl\
                       py3-pip \
                       python3 &&\
    apk add --no-cache --virtual .build-deps build-base \
                                             git \
                                             libffi-dev \
                                             libressl-dev \
                                             python3-dev &&\
    pip3 install --no-cache-dir --upgrade pip==$PIP_TAG && \
    pip3 install --no-cache-dir . &&\
    apk del .build-deps


