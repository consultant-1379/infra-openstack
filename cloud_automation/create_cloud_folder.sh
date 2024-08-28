#!/bin/bash
script_dir="$(dirname $(readlink -f $0))"
infra_top_dir=$(readlink -f ${script_dir}/..)
ansible-playbook init_cloud.yml -e topdir=${infra_top_dir}
