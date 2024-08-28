#!/usr/bin/bash
source ~/overcloudrc
echo "This script will create one VM on each compute node and attach/detach a unique thin volume to each VM and then delete all related volumes/Vms"
compnodecount=$( openstack hypervisor list  -f value -c 'Hypervisor Hostname'|wc -l)

cloud=$( openstack hypervisor list --matching compute-std-0 -f value -c 'Hypervisor Hostname'|cut -f1 -d- )
echo "There are $compnodecount Compute Nodes on Cloud $cloud"

# Reduce $nodes by 1 to allow count to start from 0
nodes=$(($compnodecount-1))
source ~/overcloudrc

# create flavor if not already present
echo "Checking if infra_flavor is present... if not ... will create"
infra_flavor_id=$(openstack flavor list -f value |grep -i   infra_flavor|cut -f1 -d" ")
if [ "$infra_flavor_id" = "" ] ; then
openstack flavor create --ram 4096 --vcpus 2 infra_flavor
echo "infra_flavor has been created"
infra_flavor_id=$(openstack flavor list -f value |grep -i   infra_flavor|cut -f1 -d" ")
else
echo "Flavor already existed"
fi
infra_flavor_name=$(openstack flavor list -f value |grep -i   infra_flavor|cut -f1,2 -d" ")

# create security group if not already present
echo "Checking if infra_sec_group is present... if not ... will create"
infra_secgroup_id=$(openstack security group list -f value |grep -i   infra_secgroup |cut -f1 -d" ")
if [ "$infra_secgroup_id" = "" ] ; then
openstack security group create infra_secgroup
openstack security group rule create --protocol icmp --ingress --remote-ip 0.0.0.0/0 --dst-port 1:65535 --ethertype IPv4 infra_secgroup
openstack security group rule create --protocol udp --ingress --remote-ip 0.0.0.0/0 --dst-port 1:65535 --ethertype IPv4 infra_secgroup
openstack security group rule create --protocol tcp --ingress --remote-ip 0.0.0.0/0 --dst-port 1:65535 --ethertype IPv4 infra_secgroup
openstack security group rule create --protocol icmp --egress --remote-ip 0.0.0.0/0 --dst-port 1:65535 --ethertype IPv4 infra_secgroup
openstack security group rule create --protocol udp --egress --remote-ip 0.0.0.0/0 --dst-port 1:65535 --ethertype IPv4 infra_secgroup
openstack security group rule create --protocol tcp --egress --remote-ip 0.0.0.0/0 --dst-port 1:65535 --ethertype IPv4 infra_secgroup
echo "infra_secgroup has been created and rules added"
infra_secgroup_id=$(openstack security group list -f value |grep -i   infra_secgroup |cut -f1 -d" ")
else
echo "Security group already exists"
fi
infra_secgroup_name=$(openstack security group list -f value |grep -i   infra_secgroup |cut -f1,2 -d" ")

# create cirros image if not already present

echo "Checking if cirros image is present... if not ... will create"
infra_cirros_id=$(openstack image list -f value -c ID --name infra_cirros --limit 1)
if [ "$infra_cirros_id" = "" ] ; then
cd /home/stack/
wget http://10.44.77.158/openstack/iso/cirros-0.5.2-x86_64-disk.img
sleep 30
openstack image create --disk-format qcow2 --file cirros-0.5.2-x86_64-disk.img infra_cirros
#time while true ; do [ $(openstack image list -f value -c Name infra_cirros --status active) ] && break ; done
time while true ; do [ $(openstack image list -f value |grep -i   infra_cirros |cut -f3 -d" ")=="active" ] && break ; done
echo "Cirros image created"
infra_cirros_id=$(openstack image list -f value -c ID --name infra_cirros --limit 1)
else
echo "Cirros image already exists"
fi

infra_cirros_name=$(openstack image list -f value |grep -i   infra_cirros|cut -f1,2 -d" ")

# checking no instances or volumes created in admin project
scount=$(openstack server list -f value|wc -l)
vcount=$(openstack volume list -f value|wc -l)
echo "Number of Instances in Admin Project= $scount"
echo "Number of Volumes in Admin Project  = $vcount"
read -p  "Please ensure all volumes/servers  are deleted from admin project. Hit Enter to continue" ans ;

# checking networks available
echo "The following are the list of shared networks on cloud $cloud"
openstack network list -f value -c Name --share
read -p  "Please enter network name or hit enter to choose Floating Network " netname ;
echo $netname
if [ "$netname" = "" ] ; then
networkid=$(openstack network list -f value |grep -i   Floating|cut -f1 -d" ")
[ "$networkid" = "" ] && { echo "The Floating Network does not exist" ; exit 1 ; }
network_name=$(openstack network show $networkid |awk  '/name    / {print $4}' )
else
networkid=$(openstack network list --name $netname -f value -c ID  --limit 1)
[ "$networkid" = "" ] && { echo "The Network $netname does not exist" ; exit 1 ; }
network_name=$netname
fi

# check vol type
#voltype=
unset $voltype
#setvoltype="--type ${voltype}"

# setting vm name
vmfilter=prov1-vm-

# displaying cloud details
echo Network Name:   $network_name
echo Network ID:    $networkid
echo Cloud Name:    $cloud
echo Cirrros Image: $infra_cirros_name
echo infra_flavor: $infra_flavor_name
echo infra_secgroup: $infra_secgroup_name
#echo Volume Type: $voltype
echo "Press enter to continue"
read
for net in   ${networkid}
do
echo Net=$net
#starting timer for overall test
SECONDS=0

# create volumes
time for i in $( seq 0 $nodes ); do openstack volume create --size 5 --image $infra_cirros_id --availability-zone nova cinder_testvol_5G_$i; done

# time openstack volume list
echo Volumes created - Waiting for volumes to reach status available
time while true ; do [ $(openstack volume list -f value -c ID --status available|wc -l) -eq  $compnodecount ] && break ; done
echo volumes created
time openstack volume list

# creating instances
time for i in $( seq 0 $nodes ); do nova boot --image $infra_cirros_id --flavor infra_flavor --availability-zone nova:${cloud}-compute-std-$i.localdomain --nic net-id=${net} --config-drive yes --security-groups $infra_secgroup_id prov1-vm-$i; done

# time openstack server list --name '.*prov*.'
echo Servers created - Waiting for servers to reach status ACTIVE
time while true ; do [ $(openstack server list -f value -c ID --status ACTIVE|wc -l) -eq  $compnodecount ] && break ; done
echo servers created
time openstack server list --name '.*prov*.'


#Determine which IPV4 address
ip1=$(openstack server list --name prov1-vm-0 -f value -c Networks|cut -f2 -d=|cut -f1 -d,)
ip2=$(openstack server list --name prov1-vm-0 -f value -c Networks|cut -f2 -d=|cut -f2 -d,)
grep ":" <<< $ip1  && ipv4=2 || ipv4=1

for i in $(openstack server list -f value -c Networks|cut -f2 -d=|cut -f${ipv4} -d, )
do
echo " --------------------------------------------------------- "
ping $i -c 3
echo " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
done

echo attaching volumes
time for i in $( seq 0 $nodes ); do openstack server add volume prov1-vm-$i cinder_testvol_5G_$i; done


time while true ; do [ $(openstack volume list -f value -c ID --status in-use|wc -l) -eq  $compnodecount ] && break ; done
echo volumes attached
time openstack volume list

echo detaching volumes
time for i in $( seq 0 $nodes ); do openstack server remove volume prov1-vm-$i cinder_testvol_5G_$i; done
time while true ; do [ $(openstack volume list -f value -c ID --status available|wc -l) -eq  $compnodecount ] && break ; done
echo volumes detached
time openstack volume list
echo Deleting Volumes
time for i in $( seq 0 $nodes ); do openstack volume delete cinder_testvol_5G_$i; done

time while true ; do [ $(openstack volume list -f value -c ID --status deleting|wc -l) -eq  0 ] && break ; done
echo volumes deleted

openstack volume list

echo Deleting Servers
time for i in $(openstack server list --name '.*prov*.' -f value -c ID); do openstack server delete $i; done


time while true ; do [ $(openstack server list -f value -c ID --name .prov. |wc -l) -eq  0 ] && break ; done
echo servers  deleted
openstack server list
done

#this is overall time taken
duration=$SECONDS
echo "Time taken to"
echo "create volumes, instances, attach detach , ping"
echo "delete instances and volumes"
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
