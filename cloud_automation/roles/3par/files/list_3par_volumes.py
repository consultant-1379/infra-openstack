#!/usr/bin/env python
import uuid
import base64
import sys
import openstack
from keystoneauth1.exceptions.http import HttpError as OpenStackHttpError
import os

def list_volumes():
    cloud = os.environ["OS_AUTH_URL"].replace("https://","").split(".")[0]
    print("Connecting to %s" % cloud)
    try:
        connection = openstack.connect(load_envvars=True)
        volumes = connection.block_storage.volumes(all_tenants=True)
    except OpenStackHttpError as os_err:
        print(err)
        sys.exit(1)

def print_volumes(volumes):
    if volumes:
        print("{0:<36} | {1:<26} | {2:40}".format("OpenStack Volume ID", "3PAR VV ID", "OpenStack Name"))
        for volume in volumes:
            print("{0:<36} | {1:<26} | {2:40}".format(volume.id, encode_name(volume.id), volume.name))
    else:
        print("No volumes found")


def encode_name(volume_id):
    uuid_str = volume_id.replace("-", "")
    vol_uuid = uuid.UUID('urn:uuid:%s' % uuid_str)
    vol_encoded = base64.b64encode(vol_uuid.bytes)

    # 3par doesn't allow +, nor /
    vol_encoded = vol_encoded.replace('+', '.')
    vol_encoded = vol_encoded.replace('/', '-')
    # strip off the == as 3par doesn't like those.
    vol_encoded = vol_encoded.replace('=', '')
    return "osv-" + vol_encoded


if __name__ == '__main__':
    USAGE_MSG = "Source the overcloudrc file and run the script to list openstack volumes.\n\n./list_3par_volumes.py"
    if len(sys.argv) > 1:
        print(USAGE_MSG)
        sys.exit(1)

    print_volumes(list_volumes())
