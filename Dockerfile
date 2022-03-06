FROM python:3.10-slim as base
RUN apt-get update && \
    apt-get install -y pbzip2 && \
    apt-get clean
# copy requirements first to avoid reloading each time a file changes
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

# install app
COPY . /app/
RUN pip3 install /app/ && rm -rf /app/
VOLUME [ "/data", "/config" ]
ENV AWS_SHARED_CREDENTIALS_FILE=/config/aws-creds
ENTRYPOINT [ "volumeBackup" ]