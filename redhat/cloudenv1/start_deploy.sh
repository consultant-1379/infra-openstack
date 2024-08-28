#!/bin/bash
cloud_dir=$(dirname $(readlink -f $0))
ansible-playbook -i cloudenv1_inventory.yml ../../cloud_automation/buildcloud.yml -e cloud_dir=${cloud_dir} -e @cloudenv1.yml -e @passwords.yml --ask-vault-pass --skip-tags ceph,3par $@
