from ansible.module_utils.basic import AnsibleModule
import itertools
max_volumes = 9
max_memory_used = 0.95
number_of_vm_to_move = 5


def run_module():
    module_args = dict(
        servers=dict(type='list', required=False),
        volumes=dict(type='list', required=False),
        server_group=dict(type='list', required=False),
        all_hosts=dict(type='list', required=False),
        anti_affinity_hosts=dict(type='list', required=False),
        active_host=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        anti_affinity=[],
        servers=[],
        hosts_for_all_vms=[],
        hosts_for_single_vm=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.params['volumes'] is not None:
        validate_volumes(module)
        validate_affinity_and_anti_affinity(result, module)
    elif module.params['all_hosts'] is not None:
        find_valid_hosts(result, module)
        result['servers'] = module.params['servers']

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)


def find_valid_hosts(result, module):
    total = 0
    invalid_host_names = flatten_list(module)
    valid_hosts = []
    for server in module.params['servers']:
        if 'affinity_vms' in server:
            total = total + calculate_total_memory(server['affinity_vms'])
        else:
            total = total + calculate_total_memory(server['anti_affinity_vms'])

    for host in module.params['all_hosts']:
        if host['host_name'] not in invalid_host_names and \
           host['host_name'] != module.params['active_host']:
            mem_in_percent = (float(host['used_memory']) + total) / \
                             float(host['total_memory'])

            if mem_in_percent < max_memory_used:
                valid_hosts.append(host['host_name']+'.localdomain')

    result['hosts_for_all_vms'] = valid_hosts
    single_vm_hosts(result, module)


def flatten_list(module):
    invalid_hosts = set()

    for entry in module.params['anti_affinity_hosts']:
        for host in entry['hosts']:
            end = host.find('.')
            invalid_hosts.add(host[:end])

    return list(invalid_hosts)


def is_valid(server_uuid, host_name, module):
    for entry in module.params['anti_affinity_hosts']:
        if server_uuid in entry['vm_uuid']:
            for host in entry['hosts']:
                end = host.find('.')
                if host[:end] == host_name:
                    return False
    return True


def calculate_total_memory(all_servers):
    total = 0
    for server in all_servers:
        end = server[0].find('G')
        total = total + (int(server[0][:end]) * 1024)

    return total


def add_valid_hosts(valid_hosts, host_name, all_servers):
    if 'vms' in valid_hosts:
        valid_hosts['valid_hosts'].append(host_name + '.localdomain')
    else:
        valid_hosts['vms'] = all_servers
        valid_hosts['valid_hosts'] = [host_name + '.localdomain']


def get_valid_host(module, valid_hosts, all_servers, anti_affinity=False):
    total = calculate_total_memory(all_servers)

    for host in module.params['all_hosts']:
        if module.params['active_host'] != host['host_name']:
            if (not anti_affinity and valid_host(host, total)) or \
                    anti_affinity_and_valid_host(host, total, all_servers,
                                                 module):

                add_valid_hosts(valid_hosts, host['host_name'], all_servers)
    if not valid_hosts:
        valid_hosts['N/A'] = all_servers


def valid_host(host, total):
    mem_in_percent = (float(host['used_memory']) + total) / \
                                float(host['total_memory'])
    return mem_in_percent < max_memory_used


def anti_affinity_and_valid_host(host, total, all_servers, module):
    return valid_host(host, total) and is_valid(all_servers[0][1],
                                                host['host_name'], module)


def single_vm_hosts(result, module):
    for all_servers in module.params['servers']:
        valid_hosts = {}
        if 'affinity_vms' in all_servers:
            get_valid_host(module, valid_hosts, all_servers['affinity_vms'])
        else:
            get_valid_host(module, valid_hosts,
                           all_servers['anti_affinity_vms'], True)
        result['hosts_for_single_vm'].append(valid_hosts)


def validate_volumes(module):
    for i, volume in enumerate(module.params['volumes']):
        if module.params['servers'][i] and len(volume) > max_volumes:
            module.params['servers'][i] = []


def validate_affinity_and_anti_affinity(result, module):
    module.params['servers'] = [server for server in
                                module.params['servers'] if server]

    for server in module.params['servers']:
        if result['servers'] and \
           len(result['servers']) >= number_of_vm_to_move:

            break
        for member in module.params['server_group']:
            if server[1] in member['Members'] and\
               member['Policies'] == 'affinity':

                validate_affinity_members(member['Members'].split(', '),
                                          module.params['servers'], result)
            elif server[1] in member['Members']:
                result['anti_affinity'].append({server[1]:
                                                member['Members'].split(', ')})
                result['servers'].append({'anti_affinity_vms': [server]})
        result['servers'] = remove_duplicates(result['servers'])


def remove_duplicates(list_to_sort):
    list_to_sort.sort()
    return list(list_to_sort for list_to_sort, _ in
                itertools.groupby(list_to_sort))


def validate_affinity_members(member_list, valid_vms_list, result):
    temp = {}
    for uuid in member_list:
        vms = filter(lambda vm: uuid in vm, valid_vms_list)
        if not vms:
            return
        elif temp:
            temp['affinity_vms'].append(vms[0])
        else:
            temp['affinity_vms'] = vms

    result['servers'].append(temp)


def main():
    run_module()


if __name__ == '__main__':
    main()
