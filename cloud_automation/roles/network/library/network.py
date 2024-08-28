import re
import sys
import yaml
import paramiko
import logging
from ansible.module_utils.switch import InvalidResults, StorageSwitch, EdgeSwitch, \
     DistributionSwitch
from ansible.module_utils.filter import Filter
from ansible.module_utils.validator import Validator
from ansible.module_utils.save_settings import SaveSettings
from os import getcwd
from paramiko.ssh_exception import AuthenticationException, \
    BadAuthenticationType, BadHostKeyException, SSHException
from ansible.module_utils.basic import AnsibleModule


logging.basicConfig(filename='networking_conf.log', filemode='a', level=logging.ERROR)


def ssh_connection(host, user, passw, retry=3):
    try:
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection.connect(host, port=22, username=user, password=passw,
                           timeout=240, auth_timeout=500)
        return connection
    except (BadHostKeyException, AuthenticationException,
            BadAuthenticationType, SSHException, IOError) as con:
        if retry > 0:
            return ssh_connection(host, user, passw, retry - 1)
        logging.error("Connection error  %s %s", host, con)
        sys.exit(1)


def send_commands(con, cmd):
    try:
        stdin, stdout, stderr = con.exec_command(cmd)
        return stdout.read().decode('ascii').strip("\n")
    except SSHException as ssh:
        logging.error("SSH error (send_commands) %s", ssh)


def get_results_from_switch(connection, host, path_to_output_file):
    tag_ports = {}
    untag_ports = {}
    tag_id = []
    inactive_ports = {}
    fab_routing_IPv4 = []
    fab_routing_IPv6 = []
    lacp_inactive_ports = []

    for all_vlan in host.get_vlan():
        for vlan in all_vlan:
            vlan_results = send_commands(connection, "sh vlan " + vlan)
            tag, untag, t_id, inactive = Filter.filter_data(host, vlan,
                                                            vlan_results)
            tag_ports.update(tag)
            untag_ports.update(untag)
            tag_id.append(t_id)
            inactive_ports.update(inactive)

    jumbo_frames = 'all' in send_commands(connection, "show config | i jumbo")

    if isinstance(host, DistributionSwitch) and host.get_fabric_routing():
        fab_routing_IPv6, fab_routing_IPv4 = fabric_routing(connection, host)

    if isinstance(host, EdgeSwitch) and host.get_lacp_ports():
        lacp_results = send_commands(connection, "sh sharing")
        lacp_inactive_ports = Filter.filter_lacp(lacp_results)

    tag_id, tag_ports, untag_ports, lacp_ports = \
        Validator.validate_results(host, tag_id, tag_ports, untag_ports,
                                   lacp_inactive_ports)
    results_to_save = InvalidResults(host, tag_id, tag_ports, untag_ports,
                                     fab_routing_IPv4, fab_routing_IPv6,
                                     inactive_ports, lacp_ports, jumbo_frames,
                                     path_to_output_file)

    SaveSettings.save_results(results_to_save)
    return results_to_save


def fabric_routing(connection, host):
    fabric_results = send_commands(connection, "show config | i fabric")
    ipv6, ipv4 = Filter.filter_fabric_routing(host, fabric_results)
    return (ipv6, ipv4)


def load_yaml_file(input):
    try:
        y = getcwd() + input

        with open(y) as yaml_file:
            parsed_yaml_file = yaml.safe_load(yaml_file)
        return parsed_yaml_file
    except IOError as io:
        logging.error("Input file not found %s", io)
        sys.exit(1)


def gather_stack_info(host_name, user, passw):
    connection = ssh_connection(host_name, user, passw)
    data = send_commands(connection, "sh stacking")
    try:
        if 'Active' in data:
            data = send_commands(connection, 'sh vrrp')
            data = re.split('\n|\r|:', data)
            return int(data[-1]) > 0

        return True
    except ValueError as verr:
        logging.error(verr)


def filter_input_file(input_file, user, passw):
    distribution_hosts = input_file['switches']['distribution']['host']
    storage_vlans = input_file['vars']['st_sd_vlans']
    edge_vlans = input_file['vars']['es_vlans']
    storage_hosts = input_file['switches']['storage']['host']
    edge_hosts = input_file['switches']['edge']['host']
    sd_objects = []
    vnx_objects = []
    edge_objects = []

    add_distribution_switch(sd_objects, distribution_hosts, storage_vlans,
                            edge_vlans, user, passw)

    for name in storage_hosts:
        for host in name['name']:
            vnx_objects.append(StorageSwitch(host, storage_vlans,
                               name['untag_ports'], name['tag_ports']))
    for name in edge_hosts:
        for host in name['name']:
            edge_objects.append(EdgeSwitch(host, edge_vlans,
                                name['untag_ports'], name['tag_ports'],
                                name['director_ports'], name['lacp_ports']))

    return (sd_objects, vnx_objects, edge_objects)


def add_distribution_switch(sd_objects, host_names, sd_vlans, es_vlans, user,
                            passw):
    for host in host_names[0]['name']:
        is_fabric_routing = gather_stack_info(host, user, passw)
        if is_fabric_routing:
            extra_sw = host[:-1] + str(int(host[-1])+1)
            if 'ds' in host:
                sd_objects.append(DistributionSwitch(extra_sw, es_vlans))
                sd_objects.append(DistributionSwitch(host, es_vlans))
            elif 'sd' in host:
                sd_objects.append(DistributionSwitch(extra_sw, sd_vlans))
                sd_objects.append(DistributionSwitch(host, sd_vlans))
        else:
            if 'ds' in host:
                sw_no_fab_routing = DistributionSwitch(host, es_vlans, False)
                sd_objects.append(sw_no_fab_routing)
            elif 'sd' in host:
                sw_no_fab_routing = DistributionSwitch(host, sd_vlans, False)
                sd_objects.append(sw_no_fab_routing)


def main():
    mod_args = dict(
        user=dict(type='str', required=True),
        passw=dict(type='str', required=True),
        input=dict(type='str', required=True),
        output=dict(type='str', required=True),
    )
    module = AnsibleModule(
        argument_spec=mod_args,
        supports_check_mode=True
    )

    yaml_file = load_yaml_file(module.params['input'])
    networking_results = []
    distribution_objects, storage_objects, edge_objects = \
        filter_input_file(yaml_file, module.params['user'],
                          module.params['passw'])

    for host in storage_objects + distribution_objects + edge_objects:
        connection = ssh_connection(host.get_name(), module.params['user'],
                                    module.params['passw'])
        results = get_results_from_switch(connection, host,
                                          module.params['output'])
        networking_results.append(results.get_all_results())

    module.exit_json(results=networking_results, rc=0)


if __name__ == '__main__':
    main()
