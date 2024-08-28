#!/usr/bin/env python3
import logging
import sys
import time
import openstack
from keystoneauth1.exceptions.http import HttpError as OpenStackHttpError

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logging.getLogger('').setLevel(logging.INFO)

class CheckDetachingVolumes:
    _REATTACH_JSON = {"os-reset_status": {"status": "in-use","attach_status": "attached"}}
    _DETACH_JSON = {"os-reset_status": {"status": "available","attach_status": "detached"}}

    def __init__(self):
        self.log = logging.getLogger('CheckDetachingVolumes')
        self._get_connection()

    def _get_connection(self):
        try:
            self.connection =  openstack.connect(cloud="devstack")
            self.cloud = self.connection.config.get_auth_args()["auth_url"] \
                                        .replace("https://","").split(".")[0]
            self.log.info(f"Connected to {self.cloud}")
        except OpenStackHttpError as os_err:
            self.log.error(os_err)
            sys.exit(1)

    def _reset_volume(self,volume_id,detach=True):
        action = self._DETACH_JSON if detach else self._REATTACH_JSON
        action_msg = "detached" if detach else "attached"
        response=self.connection.block_storage.post(f'/volumes/{volume_id}/action',json=action)
        if response.status_code == 202:
            self.log.info(f"Successfully {action_msg} volume {volume_id}")
        else:
            self.log.warn(f"Failed resetting volume with JSON {action}. "
                          f"Response code {response.status_code}"
                          f" Response: {response.text}")


    def _print_volumes(self,volumes=[]):
        if volumes:
            self.log.info("{:60} {:45} {:30}".format("Volume Name","Volume ID","Project"))
            for vol in volumes:
                project = self.connection.get_project(vol.location.project.id)
                self.log.info(f"{vol.name:60} {vol.id:45} {vol.location.project.id:45}")
        else:
            self.log.info("There are no volumes to print.")

    def reset_detaching_volumes(self):

        self.log.info("Checking for volumes in detaching state")

        detaching_vols = list(self.connection.block_storage.volumes(details=True,
                                        all_projects=True,status="detaching"))
        if not detaching_vols:
            self.log.info("There are no volumes in detaching state.")
            return
        self.log.info(f"There are {len(detaching_vols)} volumes in detaching state.")
        self._print_volumes(detaching_vols)
        self.log.info("Sleeping for 5 minutes")
        time.sleep(300)
        self.log.info("Getting list of detaching volumes (again)")
        check_detach_vols = list(self.connection.block_storage.volumes(details=True,
                                        all_projects=True,status="detaching"))
        self.log.info(f"There are {len(check_detach_vols)} volumes in detaching state.")
        self._print_volumes(check_detach_vols)

        # Only select volumes which were in detaching state in first call
        # and are still detaching after the 5 minute sleep
        vols = [v for v in check_detach_vols if v in detaching_vols]
        self.log.info(f"There are {len(vols)} volumes to be checked.")
        self._print_volumes(vols)
        for v in vols:
            project = self.connection.get_project(v.location.project.id)
            # Get a connection object scoped to a single project so call
            # to get_server is faster
            project_connection = self.connection.connect_as_project(project)
            self.log.info(f"Checking volume {v.name} ID {v.id} in {project.name}")
            if v.attachments:
                for a in v.attachments:
                    vm = project_connection.get_server(a["server_id"],detailed=True)
                    # Case #1 - volume in detaching, server has been deleted
                    if not vm:
                        self._reset_volume(v.id)
                        continue

                    self.log.info(f"{vm.name} is running on {a['host_name']}")
                    vm_vols_attached = []
                    # "os-extended-volumes:volumes_attached" is from the older version of openstacksdk
                    # used in old awx - remove after old awx is decommissioned
                    if "os-extended-volumes:volumes_attached" in vm:
                        vm_vols_attached = [ vol.id for vol in vm["os-extended-volumes:volumes_attached"]]
                    else:
                        vm_vols_attached = [ vol.id for vol in vm.attached_volumes]
                    vm_attachment_count = vm_vols_attached.count(v.id)
                    self.log.info(f"vm_attachment_count is {vm_attachment_count}")
                    # Case #2 - volume in detaching, Nova shows volume attached multiple times
                    if vm_attachment_count >1:
                        self.log.warn(f"Volume {v.id} {v.name} is attached to {vm.name}"
                                       f"{vm_attachment_count} times. This requires manual intervention.")
                    elif vm_attachment_count == 1:
                        # Case #3 - volume in detaching, VM still exists - set the volume's
                        # attach status to attached and set its state to in-use
                        self._reset_volume(v.id,detach=False)
                    else:
                        self.log.info(f"Volume {v.id} {v.name} is not attached to {vm.name} (according to Nova)")
            else:
                self.log.info(f"volume {v.name} ID {v.id} in {project.name} is not attached to any VM.")
        self.log.info("End of Script")

if __name__ == '__main__':
    check_detach = CheckDetachingVolumes()
    check_detach.reset_detaching_volumes()
