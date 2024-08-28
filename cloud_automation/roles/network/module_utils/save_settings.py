from .switch import DistributionSwitch


class SaveSettings(object):

    @staticmethod
    def save_results(results):
        if results.is_invalid_results():
            with open(results.get_path() + 'wrong_settings.txt', 'a+') as file:
                file.write("****" + results.get_host().get_name() + "****")
                if results.get_tag_id():
                    SaveSettings._save_tag_id(
                        file, results.get_tag_id())
                if results.get_untag_ports():
                    file.write("\nMissing untag ports: ")
                    SaveSettings._save_ports(
                        file, results.get_untag_ports())
                if results.get_tag_ports():
                    file.write("\nMissing tag ports: ")
                    SaveSettings._save_ports(
                        file, results.get_tag_ports())
                if isinstance(results.get_host(), DistributionSwitch)\
                        and results.get_fab_IPv4():
                    file.write("\nFabric routing disabled (IPv4): " +
                               ', '.join(results.get_fab_IPv4()))
                if isinstance(results.get_host(), DistributionSwitch)\
                        and results.get_fab_IPv6():
                    file.write("\nFabric routing disabled (IPv6): " +
                               ', '.join(results.get_fab_IPv6()))
                if results.get_inactive_ports():
                    file.write("\nInactive ports: ")
                    SaveSettings._save_ports(
                        file, results.get_inactive_ports())
                if results.get_lacp_ports():
                    file.write("\nInactive LACP ports: " +
                               ', '.join(results.get_lacp_ports()))
                if not results.get_jumbo_frames():
                    file.write("\nJumbo frames disabled")
                file.write("\n")

    @staticmethod
    def _save_ports(file, data):
        for k, v in data.items():
            file.write(k + ": " + ', '.join(v) + ", ")

    @staticmethod
    def _save_tag_id(file, tag_id):
        file.write("\nWrong tag id: ")
        for k, v in tag_id.items():
            file.write(k + " : " + v + " ")
