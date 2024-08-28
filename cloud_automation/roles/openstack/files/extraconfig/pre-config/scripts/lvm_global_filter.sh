#!/bin/bash
lvm_conf=/etc/lvm/lvm.conf
# This script configures LVM to ignore logical volumes from VM guests
# Details of why this is required are here: https://access.redhat.com/solutions/3213311

echo "Updating ${lvm_conf} to hide LVM guest devices from the host."
sed -E 's/(^\s+)#?\s*global_filter\s+=.*/\1global_filter  = [ \"r|.*|\" ]/g' -i ${lvm_conf}

# Check if global_filter is set correctly
awk '/global_filter\s+=\s+/{
   gsub(/\s+/,"",$0);
   if($0!="global_filter=[\"r|.*|\"]"){
      print("awk global_filter regex did not match");
   }
}' ${lvm_conf}
updated_lvm_conf=$?

if [ ${updated_lvm_conf} -ne 0 ];then
    echo "Failed to update ${lvm_conf}."
    echo "Exit code is ${updated_lvm_conf}"
    exit ${updated_lvm_conf}
else
    echo "Successfully updated ${lvm_conf}"
fi
echo "Rescanning LVM physical volumes (pvscan --cache)"
pvscan --cache
[ $? -ne 0 ] && echo "pvscan --cache exited with code $?"
echo "List logical volumes"
lvs
[ $? -ne 0 ] && echo "lvs exited with code $?"
exit 0
