import argparse
import datetime
import json

def main():
    script_description = """
        This script sets the RX and TX buffer size for the traffic and
        storage NICs in Red Hat OpenStack.

        """
    parser = argparse.ArgumentParser(
    description="", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('config_file',metavar="CONFIG_FILE",
                    help="Path to the os-net-config configuration file")
    parser.add_argument('nic_buffers',metavar="NIC_BUFFERS",
                    help="Path to the JSON file containing ring buffer sizes for each nic.")
    args = parser.parse_args()

    try:
        with open(args.nic_buffers) as nb_file:
            nic_buffers = json.load(nb_file)
        with open(args.config_file) as config_file:
            config = json.load(config_file)

        # backup config file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
        with open(f"{args.config_file}.{timestamp}",'w') as backup_file:
            json.dump(config,backup_file,indent=2)

        # get list of nics = traffic nics + storage nics
        nics = config["network_config"][0]["members"][0]["members"] + config["network_config"][1]["members"]
        for nic in nics:
            rx_buffer = nic_buffers[nic["name"]]["rx"]
            tx_buffer = nic_buffers[nic["name"]]["tx"]
            nic["ethtool_opts"] = f"-G ${{DEVICE}} rx {rx_buffer} tx {tx_buffer}"

        with open(args.config_file,'w') as updated_config_file:
            json.dump(config,updated_config_file,indent=2)
    except IOError as io:
        raise SystemExit(io)

if __name__ == '__main__':
    main()
