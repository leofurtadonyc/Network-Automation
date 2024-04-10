# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
import os
import argparse
import time
import yaml
import ipaddress
from jinja2 import Environment, FileSystemLoader

def load_yaml(yaml_path):
    """Load data from a YAML file."""
    with open(yaml_path, 'r') as file:
        return yaml.safe_load(file)

def render_template(template_name, context):
    """Render configuration from Jinja2 templates."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template(template_name)
    return template.render(context)

def write_to_file(directory, filename, data):
    """Write data to a file and ensure the directory exists."""
    base_path = os.path.abspath(directory)
    filepath = os.path.join(base_path, filename)

    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, 'w') as file:
        file.write(data)

    print(f"Configuration written to {filepath}")

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
    return (customer_name, access_device, access_interface, circuit_id, qos_input, qos_output, vlan_id, vlan_id_outer, pw_id, irb_ipaddr, irb_ipv6addr, ipv4_lan, ipv4_nexthop, ipv6_nexthop, ipv6_lan, pe_device, service_type)

def valid_ip_network(network):
    """Validate an IP network prefix."""
    try:
        network_obj = ipaddress.ip_network(network, strict=False)
        return str(network_obj)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP network: {network}")

def valid_ip_address(address):
    """Validate an IP address."""
    try:
        ip_obj = ipaddress.ip_address(address)
        return str(ip_obj)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {address}")

def main():
    parser = argparse.ArgumentParser(description="Generate service provisioning configurations for network devices.")
    parser.add_argument("--customer-name", type=str, help="Customer name for the service.")
    parser.add_argument("--access-device", type=str, help="Hostname of the access device.")
    parser.add_argument("--access-interface", type=str, help="Interface name on the access device.")
    parser.add_argument("--circuit-id", type=int, help="Circuit ID for the service.")
    parser.add_argument("--qos-input", type=int, help="Input QoS policer in bits.")
    parser.add_argument("--qos-output", type=int, help="Output QoS policer in bits.")
    parser.add_argument("--vlan-id", type=int, help="VLAN ID (1-4095).")
    parser.add_argument("--vlan-id-outer", type=int, help="VLAN ID (1-4095).")
    parser.add_argument("--pw-id", type=int, help="Pseudowire ID.")
    parser.add_argument("--irb-ipaddr", type=valid_ip_network, help="IP address for the BVI or IRB PE interface.")
    parser.add_argument("--irb-ipv6addr", type=valid_ip_network, help="IPv6 address for the BVI or IRB PE interface.")
    parser.add_argument("--ipv4-lan", type=valid_ip_network, help="Customer IPv4 LAN network. Format prefix/mask.")
    parser.add_argument("--ipv4-nexthop", type=valid_ip_address, help="IPv4 next-hop address to customer's LAN")
    parser.add_argument("--ipv6-lan", type=valid_ip_network, help="Customer IPv6 LAN network. Format prefix/mask.")
    parser.add_argument("--ipv6-nexthop", type=valid_ip_address, help="IPv6 next-hop address to customer's LAN")
    parser.add_argument("--pe-device", type=str, help="Hostname of the Provider Edge device.")
    parser.add_argument("--service-type", choices=['p2p', 'p2mp'], help="Service type: point-to-point or point-to-multipoint.")
    parser.add_argument("--interactive", action='store_true', help="Run the script in interactive mode to gather input from the operator.")

    args = parser.parse_args()

    if args.interactive:
        args.customer_name, args.access_device, args.access_interface, args.circuit_id, args.qos_input, args.qos_output, args.vlan_id, args.vlan_id_outer, args.pw_id, args.irb_ipaddr, args.irb_ipv6addr, args.ipv4_lan, args.ipv6_lan, args.pe_device, args.service_type = collect_inputs()

    start_time = time.time()

    devices_config = load_yaml('devices/network_devices.yaml')
    access_device_info = next((device for device in devices_config['devices'] if device['hostname'] == args.access_device), None)
    pe_device_info = next((device for device in devices_config['devices'] if device['hostname'] == args.pe_device), None)

    if not access_device_info or not pe_device_info:
        print("Error: Device information is missing or incorrect in the YAML file.")
        return
    
    if access_device_info['device_type'] == 'cisco_xe' and args.service_type == 'p2p':
        access_template_name = "p2p_cisco_xe_to_generic.j2"
    elif access_device_info['device_type'] == 'cisco_xe' and args.service_type == 'p2mp':
        access_template_name = "p2mp_cisco_xe_to_generic.j2"
    else:
        print(f"Unsupported Access device type: {access_device_info['device_type']}")
        return
    
    if not pe_device_info:
        print("Error: Provider Edge device information is missing or incorrect.")
        return

    if pe_device_info['device_type'] == 'cisco_xr' and args.service_type == 'p2p':
        pe_template_name = "p2p_cisco_xr_to_generic.j2"
    elif pe_device_info['device_type'] == 'juniper_junos' and args.service_type == 'p2p':
        pe_template_name = "p2p_juniper_junos_to_generic.j2"
    elif pe_device_info['device_type'] == 'cisco_xr' and args.service_type == 'p2mp':
        pe_template_name = "p2mp_cisco_xr_to_generic.j2"
    elif pe_device_info['device_type'] == 'juniper_junos' and args.service_type == 'p2mp':
        pe_template_name = "p2mp_juniper_junos_to_generic.j2"
    else:
        print(f"Unsupported PE device type: {pe_device_info['device_type']}")
        return

    print(f"Using template: {access_template_name} for Access device configuration")
    print(f"Using template: {pe_template_name} for PE device configuration")

    context = {
        'customer_name': args.customer_name,
        'interface_name': args.access_interface,
        'service_instance_id': args.circuit_id,
        'qos_input': args.qos_input,
        'qos_output': args.qos_output,
        'vlan_id': args.vlan_id,
        'vlan_id_outer': args.vlan_id_outer,
        'pw_id': args.pw_id,
        'irb_ipaddr': args.irb_ipaddr,
        'irb_ipv6addr': args.irb_ipv6addr,
        'ipv4_lan': args.ipv4_lan,
        'ipv4_nexthop': args.ipv4_nexthop,
        'ipv6_lan': args.ipv6_lan,
        'ipv6_nexthop': args.ipv6_nexthop,
        'access_address': access_device_info['ip_address'],
        'pe_address': pe_device_info['ip_address'],
        'device_type': pe_device_info['device_type']
    }

    access_rendered_config = render_template(access_template_name, context) + '\n'
    access_output_file = f"{args.customer_name}_access_config.txt"
    write_to_file('generated_configs', access_output_file, access_rendered_config)

    pe_rendered_config = render_template(pe_template_name, context) + '\n'
    pe_output_file = f"{args.customer_name}_pe_config.txt"
    write_to_file('generated_configs', pe_output_file, pe_rendered_config)

    elapsed_time = time.time() - start_time
    print(f"Configuration generation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
