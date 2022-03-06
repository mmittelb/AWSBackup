#! /bin/bash
function genCert {
    if [ -s ~/.aws-backup/cert.pem -o -s ~/.aws-backup/key.pem ]; then
        echo "Skipping certificate generation."
    else
        docker run \
            --rm -it \
            -v "$HOME/.aws-backup:/config:rw" \
            mmittelb/aws-backup:latest gencert
    fi
}

function createAWScreds {
    if [ -s ~/.aws-backup/aws-creds ]; then
        echo "Skipping AWS credential file generation."
    else
        echo "Enter AWS access key id:"
        read aws_access_key_id
        echo "Enter AWS secret access key:"
        read aws_secret_access_key
        cat <<EOF > ~/.aws-backup/aws-creds
[default]
aws_access_key_id=$aws_access_key_id
aws_secret_access_key=$aws_secret_access_key
EOF
    fi
}

function installScript {
    if [ -f /usr/local/sbin/aws-backup ]; then
        echo "Backing up old script."
        mv /usr/local/sbin/aws-backup /usr/local/sbin/aws-backup.old
    fi
    curl -o /usr/local/sbin/aws-backup https://raw.githubusercontent.com/mmittelb/AWSBackup/main/bin/aws-backup.sh
    chmod 755 /usr/local/sbin/aws-backup
}

if [ $(id -u) -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi
if [ $(which docker) ]; then
    if [ ! -d ~/.aws-backup ]; then
        mkdir ~/.aws-backup
    fi
    docker pull mmittelb/aws-backup:latest
    genCert
    createAWScreds
    installScript
    echo "Finished installation."
    echo "It is recommended to move /root/.aws-backup/key.pem somewhere safe."
    echo "For restore operation recreate it. "
else
    echo "Please install docker."
fi