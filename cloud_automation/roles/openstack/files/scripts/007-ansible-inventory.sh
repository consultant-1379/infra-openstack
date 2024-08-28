#!/bin/bash

source ~/stackrc

mkdir ~/ansible 2>/dev/null

export ANSIBLE_HOST_KEY_CHECKING=False
tripleo-ansible-inventory --static-yaml-inventory ~/ansible/inventory.yaml
ansible --inventory ~/ansible/inventory.yaml -m ping all

exit 0
