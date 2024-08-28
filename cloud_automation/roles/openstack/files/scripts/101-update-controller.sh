#!/bin/bash

# Change directory to where this script is located
# Given the above assumption, all path are local ones
cd $(dirname $(readlink -f $0))

source ~/stackrc

# Move to home folder to output the generared files during the deployment there
cd ~/

# Not possile to use "--environment-directory" due to https://bugzilla.redhat.com/show_bug.cgi?id=1593077

openstack overcloud update run --nodes Controller

exit 0
