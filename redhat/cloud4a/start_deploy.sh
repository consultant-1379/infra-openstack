#!/bin/bash
cloud_dir=$(dirname $(readlink -f $0))
ansible-playbook -i cloud4_inventory ../../cloud_automation/buildcloud.yml -e @cloud4a.yml -e @passwords.yml -e cloud_dir=${cloud_dir} --ask-vault-pass

