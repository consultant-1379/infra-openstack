#!/usr/bin/env python3
# Create an SSH session with python
import os
import shlex
import sys
import yaml

SERVER_TYPE_MAPPINGS = {"compute": "Compute", "computehp": "ComputeHP",
                        "control": "Controller"}
DEFAULT_INVENTORY = "/home/stack/ansible/inventory.yaml"


def create_ssh(host, user, command):
    # """Create a SSH session"""
    ssh = f"/usr/bin/ssh -t {user}@{host} {command}"
    pid = os.fork()
    if pid == 0:  # a child process
        print(f"Executing: {ssh}")
        cmd = shlex.split(ssh)
        os.execv(cmd[0], cmd)

    os.wait()
    print("SSH session is finished. :)")


def get_servers(inventory, server_type):
    return inventory[server_type]["hosts"] if "hosts" in \
            inventory[server_type] else \
            inventory[f"overcloud_{server_type}"]["hosts"]


def get_inventory(inventory_file=DEFAULT_INVENTORY):
    try:
        with open(inventory_file) as file:
            return yaml.load(file)
    except IOError as io_err:
        print(f"Error reading {inventory_file}: {io_err}\n"
              "Exiting...")
        sys.exit(1)
    except yaml.YAMLError as yaml_err:
        print(f"Error parsing yaml from {inventory_file}: {yaml_err}.\n"
              "Exiting...")
        sys.exit(1)


def get_server_ip(server_type, node_index):
    servers = get_servers(get_inventory(), server_type)
    first = list(servers.keys())[0]
    overcloud = "-".join(first.split("-")[:-1])
    host = "{0}-{1}".format(overcloud, node_index)
    try:
        return servers[host]["ansible_host"]
    except KeyError as key_err:
        print(f"Error: {key_err} does not exist in the inventory.\n"
              "Invalid Node number entered - Exiting")
        sys.exit(1)


def main():
    num_args = len(sys.argv)
    if num_args <= 1:
        print("No arguments provided to indicate node number .. Exiting")
        sys.exit()
    command = ""
    node_index = sys.argv[1]
    if num_args > 2:
        command = sys.argv[2]
    path = sys.argv[0]
    server_type = os.path.basename(path)

    if server_type not in SERVER_TYPE_MAPPINGS.keys():
        print("Invalid file name - must one of these values:"
              f"{''.join(SERVER_TYPE_MAPPINGS.keys())}")
        sys.exit()

    create_ssh(get_server_ip(SERVER_TYPE_MAPPINGS[server_type], node_index),
               "heat-admin",
               command)


if __name__ == "__main__":
    main()
