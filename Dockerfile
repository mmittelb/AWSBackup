FROM python:3.10-slim as base
COPY . /app/
RUN pip3 install /app/
RUN rm -rf /app/
VOLUME [ "/data", "/config" ]
ENTRYPOINT [ "volumeBackup" ]