FROM python:3.10-slim as base
RUN apt-get update && \
    apt-get install -y xz-utils && \
    apt-get clean
COPY . /app/
RUN pip3 install /app/
RUN rm -rf /app/
VOLUME [ "/data", "/config" ]
ENTRYPOINT [ "volumeBackup" ]