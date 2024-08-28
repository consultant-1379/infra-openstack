#!/bin/sh
if [ $# -ne 1 ]
then
  echo "Usage: $0 cinder_volume_id"
  exit
fi
echo $1 | tr -d "-" | /usr/bin/xxd -r -p | base64

