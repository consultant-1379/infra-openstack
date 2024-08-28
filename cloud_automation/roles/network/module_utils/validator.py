from .switch import DistributionSwitch
from .switch import EdgeSwitch
import itertools


class Validator(object):

    @staticmethod
    def validate_results(host, tag_id, tag_ports, untag_ports, lacp_ports):
        invalid_tag_ports = {}
        invalid_untag_ports = {}
        invalid_lacp_ports = []
        invalid_tag_id = Validator._validate_tag_id(host, tag_id)

        if not isinstance(host, DistributionSwitch):
            invalid_tag_ports = Validator._validate_tag_ports(host, tag_ports)
            invalid_untag_ports = \
                Validator._validate_untag_ports(host, untag_ports)
        if isinstance(host, EdgeSwitch):
            invalid_lacp_ports = \
                Validator._validate_lacp_ports(host, lacp_ports)
        return (invalid_tag_id, invalid_tag_ports,
                invalid_untag_ports, invalid_lacp_ports)

    @staticmethod
    def _validate_lacp_ports(host, lacp_ports):
        if lacp_ports:
            lacp_ports = [port for port in host.get_lacp_ports()
                          if port in lacp_ports]
        return lacp_ports

    @staticmethod
    def _validate_untag_ports(host, untag_ports):
        results = {}
        if isinstance(host, EdgeSwitch) and untag_ports:
            Validator._validate_edge_untag_ports(host.get_untag_ports(),
                                                 untag_ports, results)
        elif untag_ports:
            flatten_results =\
                list(itertools.chain.from_iterable(untag_ports.values()))
            ports = list(set(host.get_untag_ports()) - set(flatten_results))
            if ports:
                results['storage_vlan'] = ports
        elif host.get_untag_ports():
            results['storage_vlan'] = host.get_untag_ports()

        return results

    @staticmethod
    def _validate_edge_untag_ports(host_ports, untag_ports, results):
        prov_untag = list(map(untag_ports.get, filter(lambda x: 'Prov' in x,
                                                      untag_ports)))
        if not prov_untag and host_ports:
            results['storage_vlan'] = host_ports
        elif prov_untag:
            ports = list(set(host_ports) - set(prov_untag[0]))
            if ports:
                results['storage_vlan'] = ports

    @staticmethod
    def _validate_tag_ports(host, tag_ports):
        results = {}
        if isinstance(host, EdgeSwitch):
            Validator._validate_tag_ports_edge(host, tag_ports, results)
        else:
            for vlan, ports in tag_ports.items():
                missing_ports = list(set(host.get_tag_ports()) - set(ports))
                if missing_ports:
                    results[vlan] = missing_ports
        results = {k: v for k, v in results.items() if v}

        return results

    @staticmethod
    def _validate_tag_ports_edge(host, tag_ports, results):
        for key, value in tag_ports.items():
            if 'ECN' in key:
                results[key] = list(set(host.ecn_ports()) - set(value))
            elif 'Prov' in key:
                results[key] =\
                    list(set(host.provisioning_ports()) - set(value))
            elif 'API' in key:
                results[key] =\
                    list(set(host.internal_api_ports()) - set(value))
            else:
                results[key] = list(set(host.get_tag_ports()) - set(value))

    @staticmethod
    def _validate_tag_id(host, tag_id):
        results = {}
        for vlan in tag_id:
            if vlan not in host.get_vlan():
                results.update(vlan)
        return results
