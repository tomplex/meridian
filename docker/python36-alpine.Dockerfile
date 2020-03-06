FROM python:3.6-alpine

RUN apk update && \
    apk add wget build-base && \
    apk add --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted geos

RUN wget -qO- http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz | tar xz -C /tmp && \
        cd /tmp/spatialindex-src-1.8.5 && \
        ./configure && \
        make && \
        make install && \
        cd /tmp && \
        rm -rf spatialindex-src-1.8.5

RUN pip3 install meridian
