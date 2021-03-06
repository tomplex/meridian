FROM python:3.8-buster

RUN apt-get update && \
    apt-get install -y \
    libgeos-dev

RUN wget -qO- http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz | tar xz -C /tmp && \
        cd /tmp/spatialindex-src-1.8.5 && \
        ./configure && \
        make && \
        make install && \
        ldconfig && \
        cd /tmp && \
        rm -rf spatialindex-src-1.8.5

RUN pip3 install meridian