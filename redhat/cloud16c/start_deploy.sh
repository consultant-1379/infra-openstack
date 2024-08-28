#!/bin/bash
cloud_dir=$(dirname $(readlink -f $0))

# '$@' means arguments passed to start_deploy.sh will be passed to ansible-playbook command
# For example, run ./start_deploy.sh --skip-tags deploy_director to skip the director deployment (for example if director is already deployed).


#the script when run asks for both username and password information

read -s -p "Enter  username for Red Hat Subscritpion Manager(RHSM): " rhsm_user  ;
[ "$rhsm_user" = "" ] && { echo "Please enter your RHSM username to proceed "  exit 1 ; } || echo

read -s -p "Enter  password for Red Hat Subscritpion Manager(RHSM) user $rhsm_user: " password_rhsm  ;
[ "$password_rhsm" = "" ] && { echo "Please enter your RHSM password to proceed "  exit 1 ; } || echo
ansible-playbook -i cloud16c_inventory.yml ../../cloud_automation/buildcloud.yml -e cloud_dir=${cloud_dir} -e @cloud16c.yml -e @passwords.yml -e rhsm_user=$rhsm_user -e rhsm_password=$password_rhsm --ask-vault-pass --skip-tags vnx,unity,3par,ceph $@



