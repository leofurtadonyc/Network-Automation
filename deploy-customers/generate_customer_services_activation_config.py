# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import os
import argparse
import time
import yaml
import json
import ipaddress
import re
from jinja2 import Environment, FileSystemLoader

def load_yaml(yaml_path):
    """Load device data from a YAML file."""
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)
        return data['devices']

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


def render_template(template_name, context):
    """Render customer configuration from Jinja2 templates."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template(template_name)
    return template.render(context)

def write_to_file(directory, filename, data):
    """Write data to a file and ensure the directory exists."""
    base_path = os.path.abspath(directory)
    filepath = os.path.join(base_path, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
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
    return (customer_name, access_device, access_interface, circuit_id, qos_input, qos_output, vlan_id, vlan_id_outer, pw_id, irb_ipaddr, irb_ipv6addr, ipv4_lan, ipv4_nexthop, ipv6_lan, ipv6_nexthop, pe_device, service_type)

def valid_ip_irb(network):
    """Validate an IP network prefix and return the first usable IP address with the prefix."""
    try:
        network_obj = ipaddress.ip_network(network, strict=False)
        first_usable_ip = next(network_obj.hosts())
        return f"{first_usable_ip}/{network_obj.prefixlen}"
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid IP network: {network}. Error: {e}")

def valid_ip_nexthop(address):
    """Validate an IP address."""
    try:
        ip_obj = ipaddress.ip_address(address)
        return str(ip_obj)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {address}")
    
def valid_ip_lan(network):
    """Validate an IP network prefix."""
    try:
        network_obj = ipaddress.ip_network(network, strict=False)
        return str(network_obj)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP network: {network}")

def interface_allowed(device_info, interface_name):
    """Check if the specified interface is allowed based on forbidden ranges in the device configuration."""
    forbidden_patterns = device_info.get('forbidden_interfaces', [])
    for pattern in forbidden_patterns:
        if re.match(pattern, interface_name):
            return False
    return True

def log_error(directory, customer_name, message, error_code):
    """Log an error message with an error code to a structured JSON file for future reference. The deploy script should not move forward if an error is logged."""
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    error_info = {
        "error_message": message,
        "error_code": error_code,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(error_path, 'w') as file:
        json.dump(error_info, file, indent=4)
    print(f"Error logged to {error_path}")

def delete_error_log(directory, customer_name):
    """Delete a previous error log file for the customer if it exists. This is to unblock the deployment if the error condition is resolved."""
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    if os.path.exists(error_path):
        os.remove(error_path)
        print(f"Deleted any old error log to unblock deployment: {error_path}")

def main():
    """Main function to parse arguments, load device data, and render configurations."""
    parser = argparse.ArgumentParser(description="Generate service provisioning configurations for network devices.")
    parser.add_argument("--customer-name", type=str, help="Customer name for the service.")
    parser.add_argument("--access-device", type=str, help="Hostname of the access device.")
    parser.add_argument("--access-interface", type=str, help="Interface name on the access device.")
    parser.add_argument("--circuit-id", type=int, help="Circuit ID for the service.")
    parser.add_argument("--qos-input", type=int, help="Input QoS policer in bits.")
    parser.add_argument("--qos-output", type=int, help="Output QoS policer in bits.")
    parser.add_argument("--vlan-id", type=int, help="VLAN ID (1-4095).")
    parser.add_argument("--vlan-id-outer", type=int, help="Outer VLAN ID (1-4095).")
    parser.add_argument("--pw-id", type=int, help="Pseudowire ID.")
    parser.add_argument("--irb-ipaddr", type=valid_ip_irb, help="IP address for the BVI or IRB PE interface.")
    parser.add_argument("--irb-ipv6addr", type=valid_ip_irb, help="IPv6 address for the BVI or IRB PE interface.")
    parser.add_argument("--ipv4-lan", type=valid_ip_lan, help="Customer IPv4 LAN network. Format prefix/mask.")
    parser.add_argument("--ipv4-nexthop", type=valid_ip_nexthop, help="IPv4 next-hop address to customer's LAN")
    parser.add_argument("--ipv6-lan", type=valid_ip_lan, help="Customer IPv6 LAN network. Format prefix/mask.")
    parser.add_argument("--ipv6-nexthop", type=valid_ip_nexthop, help="IPv6 next-hop address to customer's LAN")
    parser.add_argument("--pe-device", type=str, help="Hostname of the Provider Edge device.")
    parser.add_argument("--service-type", choices=['p2p', 'p2mp'], help="Service type: point-to-point or point-to-multipoint.")
    parser.add_argument("--interactive", action='store_true', help="Run the script in interactive mode to gather input from the operator.")
    parser.add_argument("--recipe", type=str, help="Path to a YAML or JSON file containing the recipe for customer service activation.")

    args = parser.parse_args()
    
    """If a YAML or JSON recipe file is provided, load the data from that file."""
    if args.recipe:
        recipe_data = load_recipe(args.recipe)
        args.customer_name = recipe_data['customer']['name']
        args.access_device = recipe_data['customer']['devices']['access']['name']
        args.access_interface = recipe_data['customer']['devices']['access']['interface']
        args.circuit_id = recipe_data['customer']['configuration']['circuit_id']
        args.qos_input = recipe_data['customer']['configuration']['qos']['input']
        args.qos_output = recipe_data['customer']['configuration']['qos']['output']
        args.vlan_id = recipe_data['customer']['configuration']['vlan']['id']
        args.vlan_id_outer = recipe_data['customer']['configuration']['vlan']['outer_id']
        args.pw_id = recipe_data['customer']['configuration']['pseudowire_id']
        args.irb_ipaddr = recipe_data['customer']['configuration']['irb']['ipv4_address']
        args.irb_ipv6addr = recipe_data['customer']['configuration']['irb']['ipv6_address']
        args.ipv4_lan = recipe_data['customer']['configuration']['lan']['ipv4']['network']
        args.ipv4_nexthop = recipe_data['customer']['configuration']['lan']['ipv4']['next_hop']
        args.ipv6_lan = recipe_data['customer']['configuration']['lan']['ipv6']['network']
        args.ipv6_nexthop = recipe_data['customer']['configuration']['lan']['ipv6']['next_hop']
        args.pe_device = recipe_data['customer']['devices']['pe']['name']
        args.service_type = recipe_data['customer']['service_type']

    elif args.interactive:
        args.customer_name, args.access_device, args.access_interface, args.circuit_id, args.qos_input, args.qos_output, args.vlan_id, args.vlan_id_outer, args.pw_id, args.irb_ipaddr, args.irb_ipv6addr, args.ipv4_lan, args.ipv6_lan, args.pe_device, args.service_type = collect_inputs()

    start_time = time.time()

    devices_config = load_yaml('devices/network_devices.yaml')
    access_device_info = devices_config.get(args.access_device)
    pe_device_info = devices_config.get(args.pe_device)

    """If neither Access or PE device is found in the network_devices YAML file, print an error message and exit."""
    if not access_device_info or not pe_device_info:
        print("Error: Device information is missing or incorrect in the YAML file.")
        print("Please check the devices names.")
        log_error('generated_configs', args.customer_name, 
                  "Device information is missing or incorrect in the YAML file. Please check the device names.",
                  400)
        return
    
    """Preventing configuration generation if the specified access interface is not allowed for customer configurations (i.e., management or uplink interface)."""
    if not interface_allowed(access_device_info, args.access_interface):
        print(f"Error: The specified interface {args.access_interface} on the Access device {args.access_device} is not allowed for customer configurations.")
        log_error('generated_configs', args.customer_name, 
                  f"The specified interface {args.access_interface} on the Access device {args.access_device} is not allowed for customer configurations.",
                  400)
        return

    """Preventing configuration if device roles don't match the expected roles for the specified devices."""
    if access_device_info.get('device_role') != 'access' and pe_device_info.get('device_role') != 'pe':
        print(f"Error: Incorrect device roles specified. The device '{args.access_device}' is assigned the role '{access_device_info.get('device_role')}', but expected 'access'.")
        print(f"Similarly, the device '{args.pe_device}' is assigned the role '{pe_device_info.get('device_role')}', but expected 'pe'.")
        print("Please check the device roles in the configuration.")
        log_error('generated_configs', args.customer_name, 
                  f"Incorrect device roles specified. The device '{args.access_device}' is assigned the role '{access_device_info.get('device_role')}', but expected 'access'. The device '{args.pe_device}' is assigned the role '{pe_device_info.get('device_role')}', but expected 'pe'.",
                  400)
        return

    if access_device_info.get('device_role') != 'access':
        print(f"Error: The specified Access device {args.access_device} has a role of {access_device_info.get('device_role')}, not 'access'.")
        log_error('generated_configs', args.customer_name, 
                  f"The specified Access device {args.access_device} has a role of {access_device_info.get('device_role')}, not 'access'.",
                  400)
        return

    if pe_device_info.get('device_role') != 'pe':
        print(f"Error: The specified PE device {args.pe_device} has a role of {pe_device_info.get('device_role')}, not 'pe'.")
        log_error('generated_configs', args.customer_name,
                    f"The specified PE device {args.pe_device} has a role of {pe_device_info.get('device_role')}, not 'pe'.",
                    400)
        return
    
    """Preventing configuration generation if customer provisioning is disabled for the specified devices."""
    if not access_device_info.get('customer_provisioning', False) and not pe_device_info.get('customer_provisioning', False):
        print(f"Error: Customer provisioning is disabled for both specified devices, Access device {args.access_device} and PE device {args.pe_device}.")
        print("Cannot proceed with configuration.")
        log_error('generated_configs', args.customer_name,
                  f"Customer provisioning is disabled for both specified devices, Access device {args.access_device} and PE device {args.pe_device}. Cannot proceed with configuration.",
                  400)
        return

    if not access_device_info.get('customer_provisioning', False):
        print(f"Error: Customer provisioning is disabled for this specified Access device {args.access_device}.")
        print("Cannot proceed with configuration.")
        log_error('generated_configs', args.customer_name,
                  "Customer provisioning is disabled for the specified Access device. Cannot proceed with configuration.",
                  400)
        return

    if not pe_device_info.get('customer_provisioning', False):
        print(f"Error: Customer provisioning is disabled for this specified PE device {args.pe_device}.")
        print("Cannot proceed with configuration.")
        log_error('generated_configs', args.customer_name,
                    "Customer provisioning is disabled for the specified PE device. Cannot proceed with configuration.",
                    400)
        return
    
    """Rendering configurations based on device types and service types."""
    if access_device_info['device_type'] == 'cisco_xe' and args.service_type == 'p2p':
        access_template_name = "p2p_cisco_xe_to_generic.j2"
        access_template_name_remove = "p2p_cisco_xe_to_generic_remove.j2"
    elif access_device_info['device_type'] == 'cisco_xe' and args.service_type == 'p2mp':
        access_template_name = "p2mp_cisco_xe_to_generic.j2"
        access_template_name_remove = "p2mp_cisco_xe_to_generic_remove.j2"
    elif access_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2p':
        access_template_name = "p2p_huawei_vrp_to_generic.j2"
        access_template_name_remove = "p2p_huawei_vrp_to_generic_remove.j2"
    elif access_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2mp':
        access_template_name = "p2mp_huawei_vrp_to_generic.j2"
        access_template_name_remove = "p2mp_huawei_vrp_to_generic_remove.j2"
    elif access_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2p':
        access_template_name = "p2p_huawei_vrp_xpl_to_generic.j2"
        access_template_name_remove = "p2p_huawei_vrp_xpl_to_generic_remove.j2"
    elif access_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2mp':
        access_template_name = "p2mp_huawei_vrp_xpl_to_generic.j2"
        access_template_name_remove = "p2mp_huawei_vrp_xpl_to_generic_remove.j2"
    else:
        print(f"Unsupported Access device type: {access_device_info['device_type']}")
        return

    if pe_device_info['device_type'] == 'cisco_xr' and args.service_type == 'p2p':
        pe_template_name = "p2p_cisco_xr_to_generic.j2"
        pe_template_name_remove = "p2p_cisco_xr_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'cisco_xr' and args.service_type == 'p2mp':
        pe_template_name = "p2mp_cisco_xr_to_generic.j2"
        pe_template_name_remove = "p2mp_cisco_xr_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'juniper_junos' and args.service_type == 'p2p':
        pe_template_name = "p2p_juniper_junos_to_generic.j2"
        pe_template_name_remove = "p2p_juniper_junos_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'juniper_junos' and args.service_type == 'p2mp':
        pe_template_name = "p2mp_juniper_junos_to_generic.j2"
        pe_template_name_remove = "p2mp_juniper_junos_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2p':
        pe_template_name = "p2p_huawei_vrp_to_generic.j2"
        pe_template_name_remove = "p2p_huawei_vrp_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2mp':
        pe_template_name = "p2mp_huawei_vrp_to_generic.j2"
        pe_template_name_remove = "p2mp_huawei_vrp_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2p':
        pe_template_name = "p2p_huawei_vrp_xpl_to_generic.j2"
        pe_template_name_remove = "p2p_huawei_vrp_xpl_to_generic_remove.j2"
    elif pe_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2mp':
        pe_template_name = "p2mp_huawei_vrp_xpl_to_generic.j2"
        pe_template_name_remove = "p2mp_huawei_vrp_xpl_to_generic_remove.j2"
    else:
        print(f"Unsupported PE device type: {pe_device_info['device_type']}")
        return

    print(f"Using template: {access_template_name_remove} to remove any previous configuration for this customer from the Access device")
    print(f"Using template: {pe_template_name_remove} to remove any previous configuration for this customer from the PE device")
    print(f"Using template: {access_template_name} for Access device new configuration")
    print(f"Using template: {pe_template_name} for PE device new configuration")

    """Context dictionary to pass to the Jinja2 templates."""
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
        'access_loopback': access_device_info['loopback'],
        'pe_loopback': pe_device_info['loopback'],
        'device_type': pe_device_info['device_type']
    }

    try:
        access_rendered_config_remove = render_template(access_template_name_remove, context) + '\n'
        pe_rendered_config_remove = render_template(pe_template_name_remove, context) + '\n'
        access_rendered_config = render_template(access_template_name, context) + '\n'
        pe_rendered_config = render_template(pe_template_name, context) + '\n'
        access_remove_output_file = f"{args.customer_name}_{args.access_device}_access_config_remove.txt"
        pe_remove_output_file = f"{args.customer_name}_{args.pe_device}_pe_config_remove.txt"
        access_output_file = f"{args.customer_name}_{args.access_device}_access_config.txt"
        pe_output_file = f"{args.customer_name}_{args.pe_device}_pe_config.txt"
        write_to_file('generated_configs', access_remove_output_file, access_rendered_config_remove)
        write_to_file('generated_configs', pe_remove_output_file, pe_rendered_config_remove)
        write_to_file('generated_configs', access_output_file, access_rendered_config)
        write_to_file('generated_configs', pe_output_file, pe_rendered_config)
        delete_error_log('generated_configs', args.customer_name)
        print("Configuration generation completed successfully.")
    except Exception as e:
        log_error('generated_configs', args.customer_name,
                  f"Failed to generate configurations due to: {str(e)}",
                  500)
        return

    elapsed_time = time.time() - start_time
    print(f"Configuration generation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
