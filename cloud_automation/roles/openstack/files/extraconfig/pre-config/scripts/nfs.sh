#!/bin/bash

# Check if first NFS share is already mounted and if it's not then proceed with the configuration
mount -l | grep nfs | grep "${NfsMount}" | grep -q "${NfsFirstServer}"
if [[ "$?" != "0" ]]; then
  echo "NFS configuration on $(hostname)"
  echo "NFS first server: ${NfsFirstServer}"
  NfsEnableTrunking=$(echo $NfsEnableTrunking | tr '[:upper:]' '[:lower:]')
  if ${NfsEnableTrunking}; then
    echo "NFS second server: ${NfsSecondServer}"
  fi
  echo "NFS mount path: ${NfsMount}"
  echo "NFS mount options: ${NfsOptions}"
  
  # Create directory for the mount point
  mkdir -p ${NfsMount}
  # Fix the owership
  glance_uid=42415
  echo ${NfsMount} | grep -q -i "glance" || chown -R ${glance_uid} ${NfsMount}
  echo ${NfsMount} | grep -q -i "nova" || chown -R nova ${NfsMount}
  echo ${NfsMount} | grep -q -i "cinder" || chown -R cinder ${NfsMount}
  # Make sure in the compute node to enable the proper Selinux boolean
  # https://github.com/openstack/puppet-tripleo/blob/stable/queens/manifests/profile/base/nova/compute.pp#L86-L90
  echo ${NfsMount} | grep -q -i "nova" || setsebool -P virt_use_nfs on
  
  # Check FSTAB content
  grep -q "${NfsFirstServer}" /etc/fstab || echo "${NfsFirstServer} ${NfsMount} nfs defaults,${NfsOptions} 0 0" >> /etc/fstab
  if ${NfsEnableTrunking}; then
    grep -q "${NfsSecondServer}" /etc/fstab || echo "${NfsSecondServer} ${NfsMount} nfs defaults,${NfsOptions} 0 0" >> /etc/fstab
  fi
  
  # Mount anything new in FSTAB
  mount -a
fi
exit 0
