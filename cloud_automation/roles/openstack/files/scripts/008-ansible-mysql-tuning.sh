#!/bin/bash

# Change directory to where this script is located
# Given the above assumption, all path are local ones
cd $(dirname $(readlink -f $0))

export ANSIBLE_HOST_KEY_CHECKING=False
ansible-playbook -i ~/ansible/inventory.yaml ../playbooks/postinstall/mysql_tuning.yml

exit 0
