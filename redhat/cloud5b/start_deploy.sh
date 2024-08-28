#!/bin/bash
cloud_dir=$(dirname $(readlink -f $0))
# '$@' means arguments passed to start_deploy.sh will be passed to ansible-playbook command
# For example, run ./start_deploy.sh --skip-tags deploy_director to skip the director deployment (for example if director is already deployed).
ansible-playbook -i cloud5b_inventory.yml ../../cloud_automation/buildcloud.yml -e cloud_dir=${cloud_dir} -e @cloud5b.yml -e @passwords.yml --ask-vault-pass $@
