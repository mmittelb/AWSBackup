#! /bin/bash
function help {
    echo "Usage: $0 <backup|restore> <bucket> <volume|path>"
    exit 1
}

function expandPath {
    echo "$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
}

if [ -z "$1" -o -z "$2" -o -z "$3" ]; then 
    echo "Missing positional argument."
    help
fi
mode="$1"
bucket="$2"
if [ "$mode" = "backup" ]; then
    mount_permission="ro"
elif [ "$mode" = "restore" ]; then
    mount_permission="rw"
else
    echo "Choose backup or restore."
    help
fi
if [ -d $3 ]; then
    absolute_path="$(expandPath "$3")"
    # replace slash with _
    filename="fs-backup/${absolute_path//\//_}"
    mount="$absolute_path:/data:$mount_permission"
    echo "local directory $absolute_path <-> s3 $bucket/$filename"
else
    filename="volume-backup/$3"
    mount="$3:/data:$mount_permission"
    echo "local volume $absolute_path <-> s3 $bucket/$filename"
fi

docker run \
    --rm -it \
    -v "$mount" \
    -v "$HOME/.aws-backup:/config:ro" \
    mmittelb/aws-backup:latest "$mode" "$bucket" "$filename"