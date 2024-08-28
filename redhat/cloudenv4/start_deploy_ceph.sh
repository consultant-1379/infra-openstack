#!/bin/bash
cloud_dir=$(dirname $(readlink -f $0))
# '$@' means arguments passed to start_deploy.sh will be passed to ansible-playbook command
# For example, run ./start_deploy.sh --skip-tags deploy_director to skip the director deployment (for example if director is already deployed).
ansible-playbook -i cloudenv4_inventory.yml ../../cloud_automation/buildcloud.yml -e cloud_dir=${cloud_dir} -e @cloudenv4-ceph.yml -e @passwords-ceph.yml --ask-vault-pass --skip-tags vnx,unity,3par,flexos $@
