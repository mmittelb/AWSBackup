#! /bin/bash
function genCert {
    if [ -s ~/.dockerVolumeBackup/cert.pem -o -s ~/.dockerVolumeBackup/key.pem ]; then
        echo "Skipping certificate generation."
    else
        docker run \
            --rm -it \
            -v "$HOME/.dockerVolumeBackup:/config:rw" \
            mmittelb/aws-backup:latest gencert
    fi
}

function createAWScreds {
    if [ -s ~/.dockerVolumeBackup/aws-creds ]; then
        echo "Skipping AWS credential file generation."
    else
        echo "Enter AWS access key id:"
        read aws_access_key_id
        echo "Enter AWS secret access key:"
        read aws_secret_access_key
        cat <<EOF > ~/.dockerVolumeBackup/aws-creds
AWS_ACCESS_KEY_ID=$aws_access_key_id
AWS_SECRET_ACCESS_KEY=$aws_secret_access_key
EOF
    fi
}

function installScript {
    curl -o /usr/local/sbin/aws-backup https://raw.githubusercontent.com/mmittelb/AWSBackup/main/bin/aws-backup.sh
    chmod 755 /usr/local/sbin/aws-backup
}

if [ $(id -u) -ne 0 ]; then
    echo "Please run as root."
fi
if [ $(which docker) ]; then
    if [ ! -d ~/.dockerVolumeBackup ]; then
        mkdir ~/.dockerVolumeBackup
    fi
    genCert
    createAWScreds
    installScript
else
    echo "Please install docker."
fi