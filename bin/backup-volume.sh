#! /bin/bash
function help {
    echo "Usage: $0 <bucket> <volume>"
    exit 1
}
if [ -z $1 ]; then 
    echo "First argument ist missing."
    help
fi
if [ -z $2 ]; then 
    echo "Second argument ist missing."
    help
fi

docker run --rm -v "$2:/data:ro" --env-file "$HOME/aws-creds" docker-volume-backup:latest backup "$1" "backup/$2"