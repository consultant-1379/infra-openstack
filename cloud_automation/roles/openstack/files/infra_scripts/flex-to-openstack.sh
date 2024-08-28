#!/bin/sh
if [ $# -ne 1 ]
then
  echo "Usage: $0 cinder_volume_id"
  exit
fi
CID=`echo $1 | base64 -d | /usr/bin/xxd -p`
C1=`echo -n $CID | cut -c1-8`
C2=`echo -n $CID | cut -c9-12`
C3=`echo -n $CID | cut -c13-16`
C4=`echo -n $CID | cut -c17-20`
C5=`echo -n $CID | cut -c21-32`
echo $C1"-"$C2"-"$C3"-"$C4"-"$C5

