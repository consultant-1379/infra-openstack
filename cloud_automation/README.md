DE OpenStack Clouds
==============================================================================

Deployment
------------------------------------------------------------------------------

This repo contains ansible playbooks to automate the deployment of OpenStack
on SuSE OpenStack Cloud (SOC) and Red Hat Openstack Platform (RHOSP).

### Steps

1. Create a new directory under the redhat or suse directory called cloudX where X is the
number of the cloud e.g. cloud15.
2. Copy the variables file cloud_automation/cloudX.yml to the directory you've just created. Rename it to match the cloud name e.g. cloud15.yml.
3. Fill in the deployment specific information in the variables file cloudX/cloudX.yml.
4. Create a passwords.yml in the cloudX directory

```bash
     # iLO/iDRAC password
     ipmi_password: <iLO/iDRAC password>
     # Dell OME password (omit if HPE deployment)
     ome_password: <OME password here>
     unity_password: <Unity password here>
````
5. Encrypt the passwords.yml file using ansible and enter a password when prompted:
```bash
     ansible-vault encrypt passwords.yml
     New Vault password:
     Confirm New Vault password:
     Encryption successful
```

## Red Hat Openstack
The playbooks for RHOSP create the directory structure and scripts on the director.
In future the deployment itself could be automated
```bash
ansible-playbook -i inventory buildcloud.yml -e @cloudX/cloudX.yml -e @cloudX/passwords.yml --ask-vault-pass
```

**Example Inventory for RHOSP**
```
director ansible_host=10.10.10.120 ansible_user=stack
```


## Ansible Roles

There are 2 main roles
 - common
 - openstack

### _common_

 The common role pulls information needed for the introspection (RHOSP)/ cobbler-deploy (SOC) stage, from the OA (for HPE servers) or OME (for Dell servers). This information includes the iLO/iDRAC IP address, the server name and the MAC address of the first NIC port.

### _openstack_
This role creates the environment files, instackenv.json and scripts to be used to deploy Red Hat OpenStack.


## Custom network interface templates

The OpenStack TripleO heat templates provide several example network interface templates. Our clouds are deployed using
custom network interface templates. These templates assume a certain NIC layout on each server. If your NIC layout differs from the
default controller.yaml and compute.yaml in cloud_automation/roles/openstack/files/nic-configs/, an alternative controller.yaml must be created and used.

This new custom network interface template file must be placed in the _cloud_automation/roles/openstack/files/nic-configs/_ directory.
The cloudX.yml variables file for your cloud must specify the relative path in a custom_controller_nicconfig and custom_compute_nicconfig variable.

**Example**

```yaml
custom_controller_nicconfig: ../nic-configs/controller_15a.yml
custom_compute_nicconfig: ../nic-configs/compute_15a.yml
```
## Deploying provider networks

Login to the director as the _stack_ user and source the _overcloudrc_ file.
```bash
$ source overcloudrc
```
Run the deploy_networks.yml playbook
```bash
$ ansible-playbook ~/cloudX/playbooks/deploy_networks.yml -e @networks_cloudX.yml
```
### Generating the network details file for deploy_networks.yml
Login to the director as the _stack_ user and source the _overcloudrc_ file.
```bash
$ source overcloudrc
```
Run the get_networks.yml playbook **before** tearing down the cloud.
```bash
$ ansible-playbook ~/cloudX/playbooks/get_networks.yml -e cloudname=cloudX
```
