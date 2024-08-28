#!/bin/bash

sudo yum install -y bash-completion

openstack complete | grep -v '^'$(date +%F)' '| sudo tee /etc/bash_completion.d/openstackcli

echo "Done. Log out from all your session in order to use the bash-completion"

exit 0
