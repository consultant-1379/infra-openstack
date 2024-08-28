source $HOME/infra-openstack/redhat/cloud6b/overcloud-networks/overcloudrc
# Create and Test  Networks
ansible-playbook deploy_networks.yml -e @cloud6b_networks.yml

