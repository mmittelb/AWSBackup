#! /bin/bash
openssl req -newkey rsa:4096 \
            -x509 \
            -sha256 \
            -days 36500 \
            -out cert.pem \
            -keyout key.pem \
            -subj "/CN=backup"