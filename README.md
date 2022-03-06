# AWS Backup
This software can be used to backup docker volumes or part of the file system to a AWS S3 bucket. The data is AES encrypted.
Disclaimer: Backups and restore operations are dangerous. Though I tried my best to decrease the risc of dataloss and leakage be careful. I am not responsible for lost data.
## Installation
- Install docker client.
- Setup AWS S3:
    - Create a policy. Don't forget to replace `<BUCKET_NAME>` with the name of your backup bucket.
    ```
    ...
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::<BUCKET_NAME>/*",
                "arn:aws:s3:::<BUCKET_NAME>"
            ]
        }
    ]
    ...
    ```
    - Create a service user, attach the new policy and generate an access key. 
- Download and run install script as root.
```
wget https://raw.githubusercontent.com/mmittelb/AWSBackup/main/bin/install.sh && chmod +x install.sh && sudo ./install.sh
```
## Usage
### Backup
`aws-backup backup <BUCKET_NAME> <VOLUME_NAME or PATH>`
### Restore
Remember to put key into `/root/.aws-backup/key.pem`.
`aws-backup restore <BUCKET_NAME> <VOLUME_NAME or PATH>`

## Implementation details
### Encryption
The data is AES encrypted using the Fernet implementation from the cryptography python library. Each backup generates its own encryption key. This key encrypted with the RSA public key created during installation and is part of the encrypted file uploaded to the cloud. To avoid huge memory usage the data is encrypted in 1MB blocks.