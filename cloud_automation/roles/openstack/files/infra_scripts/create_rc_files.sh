#!/usr/bin/bash
RC_LOC=/home/stack/rc_files
source ~/overcloudrc
mkdir -p  $RC_LOC/backup 2>/dev/null
rm -rf $RC_LOC/backup/* 2 >/dev/null
for file in $RC_LOC/*
do
if [ -f "$file" ] ; then
mv  $RC_LOC/* $RC_LOC/backup 2>/dev/null
fi
done
cp ~/overcloudrc  $RC_LOC/
if [ -f ~/overcloudrc.v3 ] ; then
cp ~/overcloudrc.v3  $RC_LOC/
fi
function rc_v2 {
if ! grep -q "unset" ~/overcloudrc ; then
echo "for key in \$( set | awk '{FS=\"=\"}  /^OS_/ {print \$1}' ); do unset \$key ; done" 
fi
egrep -v "OS_TENANT_NAME|OS_PROJECT_NAME|OS_PROJECT_ID" ~/overcloudrc 
echo "export OS_PROJECT_NAME=$project" 
echo "export OS_TENANT_NAME=$project" 
echo "export OS_TENANT_ID=$ID" 
echo "export OS_PROJECT_ID=$ID" 
if [ $rel -le 10 ] ; then
extra="# Add OS_CLOUDNAME to PS1
if [ -z \"\${CLOUDPROMPT_ENABLED:-}\" ] ; then
    export PS1=\${PS1:-\"\"}
    export PS1=\${OS_CLOUDNAME:+\"(\$OS_CLOUDNAME)\"}\ \$PS1
    export CLOUDPROMPT_ENABLED=1
fi "
echo $extra
fi
}
function rc_v3 {
echo "for key in \$( set | awk '{FS=\"=\"}  /^OS_/ {print \$1}' ); do unset \$key ; done" 
egrep -v "OS_TENANT_NAME|OS_PROJECT_NAME" ~/overcloudrc.v3 
echo "export OS_PROJECT_NAME=$i"
echo "export OS_TENANT_NAME=$i"
echo "#export OS_TENANT_ID=$ID"
}
domain=" --domain default "
declare -i rel
rel=$(cat /etc/rhosp-release|awk '{print $6}'|cut -f1 -d.)
echo $rel
[ $rel -le 10 ] && unset domain     
openstack project list  -f value ${domain} |egrep -v " admin| service| monitoring"|while read line
do
project=$(echo $line|cut -f2 -d" ")
#echo $project
ID=$(echo $line|cut -f1 -d" ")
#echo $ID
echo creating rc file for project $project
rc_v2 >  "${RC_LOC}/${project}"
[ -f ~/overcloudrc.v3 ] && { rc_v3 >  ${RC_LOC}/$project.v3 ; }
done
ls -l ${RC_LOC}/*
