FROM python:3.9-alpine3.12

ARG PIP_TAG=21.0.1

WORKDIR /opt/chained-ci-mqtt-trigger-master

COPY . .

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apk add --no-cache --virtual .build-deps gcc \
                                             musl-dev \
                                             libffi-dev \
                                             openssl-dev && \
    pip install --no-cache-dir --upgrade pip==$PIP_TAG && \
    pip install --no-cache-dir . && \
    apk del .build-deps
