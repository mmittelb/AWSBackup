#! /bin/bash
function help {
    echo "Usage: $0 <backup|restore> <bucket> <volume>"
    exit 1
}

if [ -z $1 -o -z $2 -o -z $3 ]; then 
    echo "Missing positional argument."
    help
fi
if [ "$1" = "backup" ]; then
    mode="$1"
    bucket="$2"
    volume="$3:/data:ro"
    filename="backup/$3"
elif [ "$1" = "restore" ]; then
    mode="$1"
    bucket="$2"
    volume="$3:/data:rw"
    filename="backup/$3"
else
    echo "Choose backup or restore."
    help
fi

docker run \
    --rm -it \
    -v "$volume" \
    -v "$HOME/.dockerVolumeBackup:/config:ro" \
    --env-file "$HOME/.dockerVolumeBackup/aws-creds" \
    mmittelb/aws-backup:latest "$mode" "$bucket" "$filename"