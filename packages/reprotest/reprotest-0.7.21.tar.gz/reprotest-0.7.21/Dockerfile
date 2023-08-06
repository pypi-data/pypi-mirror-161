FROM debian:stretch
RUN apt-get update -q && DEBIAN_FRONTEND=noninteractive apt-get install -qy --no-install-recommends \
    python3 python3-setuptools ca-certificates \
    diffoscope disorderfs faketime locales-all sudo \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /reprotest
COPY . .
RUN python3 setup.py install
ENTRYPOINT ["reprotest"]
