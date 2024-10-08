from base64 import b64decode
from binascii import b2a_hex, Error

def powerflex_to_openstack(powerflex_vols):
    """
    Update a list of Dell Powerflex volumes with a new 'openstack_id'
    attribute containing the corresponding openstack volume id.

    Args:
      powerflex_vols:
         A list of Powerflex volumes
    Returns:
      An updated list of powerflex volumes
    """
    # based on infra_scripts/openstack-to-flex.sh
    for vol in iter(powerflex_vols):
        try:
            # PowerFlex volumes names are generated by the PowerFlex Cinder driver by
            # removing the dashes from the OpenStack volume id, converting that string to binary and
            # then base64 encoding the result.
            # The lines below reverse that process to recover the OpenStack volume id.
            v = b2a_hex(b64decode(vol["name"])).decode('utf-8')
            vol["openstack_id"] = f"{v[0:8]}-{v[8:12]}-{v[12:16]}-{v[16:20]}-{v[20:32]}"
        except Error:
            # Ignore any non OpenStack cinder volumes
            # i.e. when the vol["name"] isn't a base64 string
            vol["openstack_id"] = "non_openstack_vol"

    return powerflex_vols

class FilterModule(object):
    dict_filters = {
        'powerflex_to_openstack': powerflex_to_openstack
    }

    def filters(self):
        return self.dict_filters
