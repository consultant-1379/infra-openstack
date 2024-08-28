#!/bin/bash
cloud_dir=$(dirname $(readlink -f $0))
rhsm_user=kevin.fennelly@ericsson.com
# '$@' means arguments passed to start_deploy.sh will be passed to ansible-playbook command
# For example, run ./start_deploy.sh --skip-tags deploy_director to skip the director deployment (for example if director is already deployed).
read -s -p "Enter  password for Red Hat Subscritpion Manager(RHSM) user $rhsm_user: " password_rhsm  ;
[ "$password_rhsm" = "" ] && { echo "Please enter your RHSM password to proceed "  exit 1 ; } || echo
#echo " ansible-playbook -i cloud6b_inventory.yml ../../cloud_automation/buildcloud.yml -e cloud_dir=${cloud_dir} -e @cloud6b.yml -e @passwords.yml -e rhsm_user=${rhsm_user} -e rhsm_password=${password_rhsm} --ask-vault-pass --skip-tags 3par,ceph,flexos $@ "
#read -p "hit Enter to deploy cloud" rtn ;
ansible-playbook -i cloud6b_inventory.yml ../../cloud_automation/buildcloud.yml -e cloud_dir=${cloud_dir} -e @cloud6b.yml -e @passwords.yml -e rhsm_user=${rhsm_user} -e rhsm_password="${password_rhsm}" --ask-vault-pass --skip-tags 3par,ceph,flexos $@
