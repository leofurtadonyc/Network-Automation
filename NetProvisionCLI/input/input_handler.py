import yaml
import json
import os

def load_recipe(file_path):
    """Load intended customer's configuration data from a YAML or JSON recipe file."""
    _, file_extension = os.path.splitext(file_path)
    if file_extension in ['.yaml', '.yml']:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
    elif file_extension == '.json':
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        raise ValueError("Unsupported file type. Please provide a YAML or JSON file.")
    return data

def collect_inputs():
    """Collect inputs interactively from the user."""
    print("Enter the configuration details:")
    customer_name = input("Customer Name: ")
    access_device = input("Access Device Hostname: ")
    access_interface = input("Access Interface: ")
    circuit_id = input("Circuit ID (1-4000): ")
    qos_input = input("Input QoS Policier (in bits): ")
    qos_output = input("Output QoS Policier (in bits): ")
    vlan_id = input("VLAN ID (1-4095): ")
    vlan_id_outer = input("Outer VLAN ID (1-4095): ")
    pw_id = input("Pseudowire ID: ")
    irb_ipaddr = input("IP Address for the BVI or IRB PE interface: ")
    irb_ipv6addr = input("IPv6 address for the BVI or IRB PE interface: ")
    ipv4_lan = input("Customers IPv4 LAN network for the static routes on PE device. Format prefix/mask: ")
    ipv4_nexthop = input("IPv4 next-hop address to customer's LAN: ")
    ipv6_lan = input("Customers IPv6 LAN network for the static routes on PE device. Format prefix/mask: ")
    ipv6_nexthop = input("IPv6 next-hop address to customer's LAN: ")
    pe_device = input("Provider Edge Device Hostname: ")
    service_type = input("Service Type (p2p or p2mp): ")
    return (customer_name, access_device, access_interface, circuit_id, qos_input, qos_output, vlan_id, vlan_id_outer, pw_id, irb_ipaddr, irb_ipv6addr, ipv4_lan, ipv4_nexthop, ipv6_lan, ipv6_nexthop, pe_device, service_type)
