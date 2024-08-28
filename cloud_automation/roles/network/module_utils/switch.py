class Switch(object):
    def __init__(self, host_name, vlan, tag_ports=[], untag_ports=[]):
        self._host_name = host_name
        self._vlan = vlan
        self._tag_ports = tag_ports
        self._untag_ports = untag_ports

    def get_name(self):
        return self._host_name

    def get_vlan(self):
        return self._vlan

    def get_untag_ports(self):
        self._untag_ports = [str(port) for port in self._untag_ports]
        return self._untag_ports

    def get_tag_ports(self):
        self._tag_ports = [str(port) for port in self._tag_ports]
        return self._tag_ports

    def get_all_ports(self):
        return self.get_tag_ports() + self.get_untag_ports()


class EdgeSwitch(Switch):
    def __init__(self, host_name, vlan, untag_ports, tag_ports,
                 director_port, lacp_ports):
        Switch.__init__(self, host_name, vlan, tag_ports, untag_ports)
        self._director_port = director_port
        self._lacp_ports = lacp_ports

    def get_lacp_ports(self):
        self._lacp_ports = [str(port) for port in self._lacp_ports]
        return self._lacp_ports

    def get_director_port(self):
        self._director_port = [str(port) for port in self._director_port]
        return self._director_port

    def get_all_ports(self):
        return self.get_tag_ports() + self.get_untag_ports()\
             + self.get_director_port()

    def ecn_ports(self):
        return self.get_untag_ports() + self.get_director_port()

    def provisioning_ports(self):
        return list(set(self.get_tag_ports()) - set(self.get_untag_ports()))\
             + self.get_director_port()

    def internal_api_ports(self):
        return self.get_tag_ports() + self.get_director_port()


class DistributionSwitch(Switch):
    def __init__(self, host_name, vlan, fabric_routing=True):
        Switch.__init__(self, host_name, vlan)
        self._is_IPv6 = {}
        self._check_fabric_routing = fabric_routing

    def get_fabric_routing(self):
        return self._check_fabric_routing

    def get_IPv6(self):
        return self._is_IPv6

    def set_IPv6(self, value):
        self._is_IPv6.update(value)


class StorageSwitch(Switch):
    def __init__(self, host_name, vlan, untag_ports, tag_ports):
        Switch.__init__(self, host_name, vlan, tag_ports, untag_ports)


class InvalidResults(object):
    def __init__(self, host, tag_id, tag_ports, untag_ports,
                 fabric_routing_IPv4, fabric_routing_IPv6,
                 inactive_ports, lacp_inactive_ports, jumbo_frames,
                 path_to_output_file):
        self._host = host
        self._tag_id = tag_id
        self._tag_ports = tag_ports
        self._untag_ports = untag_ports
        self._fabric_routing_IPv4 = fabric_routing_IPv4
        self._fabric_routing_IPv6 = fabric_routing_IPv6
        self._inactive_ports = inactive_ports
        self._lacp_inactive_ports = lacp_inactive_ports
        self._jumbo_frames = jumbo_frames
        self._path = path_to_output_file

    def get_host(self):
        return self._host

    def get_tag_id(self):
        return self._tag_id

    def get_tag_ports(self):
        return self._tag_ports

    def get_untag_ports(self):
        return self._untag_ports

    def get_fab_IPv4(self):
        return self._fabric_routing_IPv4

    def get_fab_IPv6(self):
        return self._fabric_routing_IPv6

    def get_inactive_ports(self):
        return self._inactive_ports

    def get_lacp_ports(self):
        return self._lacp_inactive_ports

    def get_jumbo_frames(self):
        return self._jumbo_frames

    def get_path(self):
        return self._path

    def is_invalid_results(self):
        return any([self._tag_id, self._tag_ports, self._untag_ports,
                    self._fabric_routing_IPv4, self._fabric_routing_IPv6,
                    self._inactive_ports, not self._jumbo_frames,
                    self._lacp_inactive_ports])

    def get_all_results(self):
        results = {
            'host': self.get_host().get_name(),
            'tag_id': self.get_tag_id(),
            'tag_ports': self.get_tag_ports(),
            'untag_ports': self.get_untag_ports(),
            'fab_ipv4': self.get_fab_IPv4(),
            'fab_ipv6': self.get_fab_IPv6(),
            'inactive_ports': self.get_inactive_ports(),
            'lacp_ports': self.get_lacp_ports(),
            'jumbo_frames': 'enabled' if self.get_jumbo_frames()
                            else 'disabled'
        }

        return results
