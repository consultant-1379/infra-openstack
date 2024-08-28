import argparse
from collections import namedtuple
import logging
import os
import sys

from storops import VNXSystem
from storops.connection.exceptions import HttpError
from storops.exception import VNXLunNotFoundError,VNXCredentialError

vnx_lun_info = namedtuple("VNXLunInfo",['name','description','host_access','lun'])

logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s',stream=sys.stdout)
log = logging.getLogger('__file__')
log.setLevel(logging.INFO)

def get_volumes_to_delete(storage_array,volumes_not_in_openstack):
    volumes_to_delete = []
    alu_hlu_map_list = [list(sg.alu_hlu_map.keys()) for sg in storage_array.get_sg() if sg.alu_hlu_map ]
    lun_ids_in_storage_group = set([ id for alu_list in alu_hlu_map_list for id in alu_list ])

    log.info("Checking if LUNs are in storage groups")
    for lun in volumes_not_in_openstack:
        connected_to_host = lun.lun_id in lun_ids_in_storage_group
        if not lun.existed:
            log.warning("LUN %s returned from %s. It seems to have already been deleted/empty" % (lun,storage_array.name))
        else:
            volumes_to_delete.append(vnx_lun_info(lun.name,'No description on VNX.',connected_to_host,lun))

    return volumes_to_delete

def get_volumes_not_in_openstack(storage_array,openstack_volume_ids):
    luns = get_luns(storage_array)
    visible_lun_ids = [ lun.name.replace("volume-","") for lun in luns if not lun.name.startswith("hidden") ]
    hidden_luns = [ lun for lun in luns if lun.name.startswith("hidden") ]
    log.info("Comparing LUNs on %s to volumes in OpenStack", storage_array.name)

    volids_not_in_openstack = set(visible_lun_ids) - set(openstack_volume_ids)
    volumes_not_in_openstack = [ lun for lun in luns if lun.name.replace("volume-","") in volids_not_in_openstack ]

    log.info("There are %d volumes on the storage array which are not in openstack",len(volumes_not_in_openstack))

    total_number_of_luns = len(openstack_volume_ids) + len(volumes_not_in_openstack) + len(hidden_luns)
    log.info("%d (openstack volumes) + %d (left over volumes) + %d (hidden volumes) = %d",
             len(openstack_volume_ids),len(volumes_not_in_openstack),len(hidden_luns),total_number_of_luns)

    # add in hidden LUNs as some of these can be cleaned up if they are not in use as a thin clone base
    volumes_not_in_openstack.extend(hidden_luns)
    return volumes_not_in_openstack

def get_openstack_volume_ids():
    log.info("Getting list of volumes from OpenStack")
    volume_ids = list()
    with open('/tmp/openstack_vol_ids') as f:
        volume_ids = f.read().split(" ")
    log.info("There are %d volumes in openstack",len(volume_ids))
    return volume_ids

def print_volumes_to_delete(volumes_to_delete):
    log.info("There are %d LUNs which can be deleted.",len(volumes_to_delete))
    print("{:55}{:70}{:20}\n\n{:#^145}\n".format("Name","Description","Connected to host",""))
    for lun in volumes_to_delete:
        connected_to_host = "Yes" if lun.host_access else "No"
        print("{:55}{:70}{:80}".format(lun.name,lun.description,connected_to_host))

def get_luns(storage_array):
    log.info("Getting list of LUNs")
    luns = storage_array.get_lun()
    log.info("There are %d LUNs on %s",len(luns),storage_array.name)
    return luns

def delete_luns(volumes_to_delete):
    log.info("Starting to delete LUNs.")
    for vol in volumes_to_delete:
        log.info("Deleting %s",vol.name)
        try:
            vol.lun.delete(delete_snapshots=True,force=True)
        except VNXLunNotFoundError:
            log.warning("Error deleting %s. This LUN may have already been deleted",vol.name)

def compare_cinder_with_storage_array(storage_array,delete=False):
    volumes_not_in_openstack = get_volumes_not_in_openstack(storage_array,get_openstack_volume_ids())
    num_vols_not_in_openstack = len(volumes_not_in_openstack)

    if num_vols_not_in_openstack == 0:
        log.info("There are no LUNs on %s which are not in OpenStack", storage_array.name)
        return 0

    log.info("There are %d LUNs which are not directly in use by OpenStack. Some of these can be deleted. "
            "Others cannot,such as those in use as a Thin Clone Base.",num_vols_not_in_openstack)
    volumes_to_delete = get_volumes_to_delete(storage_array,volumes_not_in_openstack)
    if len(volumes_to_delete) == 0:
        log.info("There are no LUNs to be deleted")
        return 0

    print_volumes_to_delete(volumes_to_delete)
    if delete:
        delete_luns(volumes_to_delete)
    return len(volumes_to_delete)

def get_inputs():
    parser = argparse.ArgumentParser(description="script to compare the number of LUNS on the VNX vs the number of volumes in cinder")
    parser.add_argument("--ip",dest="ip",required=True,metavar="<IP address>",help="The management IP address of the storage array")
    parser.add_argument("--user",dest="user",required=True,help="Username for the storage array")
    parser.add_argument("--delete",dest="delete",required=False,help="Deletes (without confirmation) any LUNs on VNX which are not in openstack.",action='store_true')
    args = parser.parse_args()
    return (args.ip,args.user,args.delete)

def main():
    try:
        mgmt_ip,user,delete = get_inputs()
        password = os.environ.get('vnx_password',None)
        storage_array = VNXSystem(mgmt_ip,user,password)
        log.info("Retrieving information from %s",storage_array.name)
        compare_cinder_with_storage_array(storage_array,delete)
    except (HttpError,VNXCredentialError) as e:
        log.error("There was an error communicating with the storage array. Please check the IP address,username and password provided are correct.")
        log.error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        log.error("Ctrl+C pressed. Exiting...")
        sys.exit(1)

if __name__ == '__main__':
    main()
