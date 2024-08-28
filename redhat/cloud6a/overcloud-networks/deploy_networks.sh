source $HOME/infra-openstack/redhat/cloud6a/overcloud-networks/overcloudrc
# Create and Test  Networks
ansible-playbook deploy_networks.yml -e @cloud6a_networks.yml

