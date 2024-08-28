from .switch import DistributionSwitch
import re


class Filter(object):

    @staticmethod
    def filter_data(host, vlan, data):
        tag_ports, untag_ports, tag_id = Filter._sep_ports_and_id(host, vlan,
                                                                  data)
        inactive_ports = {}

        if tag_ports and not isinstance(host, DistributionSwitch):
            inactive_ports.update(
                Filter._filter_inactive_ports(host, tag_ports))
            tag_ports = Filter._filter_ports(tag_ports)
        if untag_ports and not isinstance(host, DistributionSwitch):
            results = Filter._filter_inactive_ports(host, untag_ports)

            if ''.join(results.keys()) in inactive_ports:
                ports_to_add = results[''.join(results.keys())]
                inactive_ports[''.join(results.keys())].append(
                                ''.join(ports_to_add))
            else:
                inactive_ports.update(results)
            untag_ports = Filter._filter_ports(untag_ports)

        return (tag_ports, untag_ports, tag_id, inactive_ports)

    @staticmethod
    def _filter_ports(ports):
        for key in ports:
            for i, port in enumerate(ports[key]):
                if port.startswith('*') or port.startswith('!'):
                    ports[key][i] = Filter._remove_unvanted_chars(port[1:])

        return ports

    @staticmethod
    def _remove_unvanted_chars(port):
        result = ''
        for char in port:
            if char.isdigit():
                result = result + char
            else:
                break
        if port[-1] == 'g':
            result = result + 'g'

        return result

    @staticmethod
    def _sep_ports_and_id(host, vlan, data):
        if data is None or 'Unrecognized' in data:
            return ({}, {}, {vlan: 'does not exist/check spelling'})
        else:
            tag_ports = {}
            tag_id = {}
            untag_ports = {}
            results = data.replace(" ", '')
            results = re.split('\n|\r', results)
            results = [str(r) for r in results if r]
            for index, line in enumerate(results):
                if line.startswith('AdminState'):
                    tag_id[vlan] = line.split(':')[-1].split('Tag')[-1]
                elif line.startswith('Tag'):
                    temp = line.split(':')[-1]
                    temp += Filter._filter_all_ports(results[index+1:])
                    tag_ports[vlan] = temp.split(',')
                elif line.startswith('Untag'):
                    temp = line.split(':')[-1]
                    temp += Filter._filter_all_ports(results[index+1:])
                    untag_ports[vlan] = temp.split(',')
                elif line.startswith('IPv6:') and 'None' not in line:
                    host.set_IPv6({vlan: True})

            return (tag_ports, untag_ports, tag_id)

    @staticmethod
    def filter_lacp(lacp_results):
        lacp_ports = []
        results = lacp_results.replace(" ", '')
        results = re.split('\n|\r', results)
        results = [str(r) for r in results if r]

        for i, line in enumerate(results):
            if line.startswith('='):
                lacp_ports = Filter._get_all_lacp_ports(results[i+1:])
                break
        return lacp_ports

    @staticmethod
    def _get_all_lacp_ports(results):
        output = []
        i = 0
        while i < len(results) and not results[i].startswith('='):
            stop = results[i].find('-')
            if stop > -1:
                start = results[i].rfind('L')+2
                if results[i][start:].startswith('A'):
                    output.append(results[i][start+1:stop])
                else:
                    output.append(results[i][start:stop])
            i = i+1
        return output

    @staticmethod
    def _filter_all_ports(data):
        output = ''
        i = 0
        while data[i].startswith('*') or data[i][0].isdigit() \
                or data[i].startswith('!'):
            output += data[i]
            i += 1
        return output

    @staticmethod
    def _filter_inactive_ports(host, ports):
        inactive_ports = {}
        for key in ports:
            for port in ports[key]:
                port = Filter._remove_unvanted_chars(port[1:]) \
                        if port.startswith('!') \
                        else Filter._remove_unvanted_chars(port)
                if port in host.get_all_ports() and key in inactive_ports:
                    inactive_ports[key].append(port)
                elif port in host.get_all_ports():
                    inactive_ports[key] = [port]

        return inactive_ports

    @staticmethod
    def filter_fabric_routing(host, data):
        results = re.split('\n', data)
        ipv4 = set()
        ipv6 = set()
        all_vlans = list(set().union(*(d.keys() for d in host.get_vlan())))
        all_vlans = [vlan.strip(' ') for vlan in all_vlans]
        ipv6_vlans = [vlan.strip(' ') for vlan, is_IPv6 in
                      host.get_IPv6().items() if is_IPv6]
        ipv6, ipv4 = Filter._fabric_routing(all_vlans, ipv6_vlans, ipv4, ipv6,
                                            results)

        return (ipv6, ipv4)

    @staticmethod
    def _fabric_routing(all_vlans, ipv6_vlans, ipv4, ipv6, results):
        for line in results:
            line_list = str(line).split(' ')
            for value in line_list:
                if value in all_vlans and 'vrid 1' in str(line):
                    ipv4.add(value)
                    if value not in ipv6_vlans:
                        break
                if value in all_vlans and 'vrid 6' in str(line):
                    ipv6.add(value)

        ipv4 = list(set(all_vlans) - ipv4)
        ipv6 = list(set(ipv6_vlans) - ipv6)

        return(ipv6, ipv4)
