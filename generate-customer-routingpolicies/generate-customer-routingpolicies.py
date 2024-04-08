import os
import argparse
from jinja2 import Environment, FileSystemLoader

def load_data_from_file(filename):
    """Load data from a specified file."""
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except FileNotFoundError as e:
        print(f"Failed to find necessary data file: {e}")
        return None

def write_to_file_with_check(filepath, data):
    """Write data to a file and check that it is not empty."""
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    with open(filepath, 'w') as file:
        file.write(data)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print("Configuration generated successfully.")
    else:
        os.remove(filepath)
        raise Exception("Error: The configuration file was created but is empty.")

def generate_policies_juniper_junos(asn, customer_name):
    """Generate routing policies for Juniper devices."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template('juniper_junos_customer_routing_policy.j2')
    
    as_path_group_name = f"AS{asn}:{customer_name}_ASPATH"
    route_filter_list_ipv4_name = f"AS{asn}:{customer_name}_IMPORT_IPV4"
    route_filter_list_ipv6_name = f"AS{asn}:{customer_name}_IMPORT_IPV6"

    rendered_config = template.render(
        policy_name_ipv4=f"AS{asn}:{customer_name}-IMPORT-IPV4",
        policy_name_ipv6=f"AS{asn}:{customer_name}-IMPORT-IPV6",
        as_path_group_name=as_path_group_name,
        route_filter_list_ipv4_name=route_filter_list_ipv4_name,
        route_filter_list_ipv6_name=route_filter_list_ipv6_name
    )

    output_file = f"generated_policies/AS{asn}-{customer_name}_policies_juniper_junos.txt"
    try:
        write_to_file_with_check(output_file, rendered_config)
    except Exception as e:
        print(e)

def generate_policies_cisco_xe(asn, customer_name):
    """Generate routing policies for Cisco IOS XE devices."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template('cisco_xe_customer_routing_policy.j2')
    
    # as_path_acl = f"AS{asn}:{customer_name}_ASPATH"
    prefix_list_ipv4_name = f"AS{asn}:{customer_name}_IMPORT_IPV4"
    prefix_list_ipv6_name = f"AS{asn}:{customer_name}_IMPORT_IPV6"

    rendered_config = template.render(
        policy_name_ipv4=f"AS{asn}:{customer_name}-IMPORT-IPV4",
        policy_name_ipv6=f"AS{asn}:{customer_name}-IMPORT-IPV6",
        #as_path_acl=as_path_acl,
        prefix_list_ipv4_name=prefix_list_ipv4_name,
        prefix_list_ipv6_name=prefix_list_ipv6_name
    )

    output_file = f"generated_policies/AS{asn}-{customer_name}_policies_cisco_xe.txt"
    try:
        write_to_file_with_check(output_file, rendered_config)
    except Exception as e:
        print(e)

def generate_policies_cisco_xr(asn, customer_name):
    """Generate routing policies for Cisco IOS XR devices."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template('cisco_xr_customer_routing_policy.j2')
    
    as_path_set_name = f"AS{asn}:{customer_name}_ASPATH"
    prefix_set_ipv4_name = f"AS{asn}:{customer_name}_IMPORT_IPV4"
    prefix_set_ipv6_name = f"AS{asn}:{customer_name}_IMPORT_IPV6"

    rendered_config = template.render(
        policy_name_ipv4=f"AS{asn}:{customer_name}-IMPORT-IPV4",
        policy_name_ipv6=f"AS{asn}:{customer_name}-IMPORT-IPV6",
        as_path_set_name=as_path_set_name,
        prefix_set_ipv4_name=prefix_set_ipv4_name,
        prefix_set_ipv6_name=prefix_set_ipv6_name
    )

    output_file = f"generated_policies/AS{asn}-{customer_name}_policies_cisco_xr.txt"
    try:
        write_to_file_with_check(output_file, rendered_config)
    except Exception as e:
        print(e)

def generate_policies_huawei_vrp(asn, customer_name):
    """Generate routing policies for Huawei VRP devices."""
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template('huawei_vrp_customer_routing_policy.j2')
    
    as_path_filter_name = f"AS{asn}:{customer_name}_ASPATH"
    ip_prefix_name = f"AS{asn}:{customer_name}_IMPORT_IPV4"
    ipv6_prefix_name = f"AS{asn}:{customer_name}_IMPORT_IPV6"

    rendered_config = template.render(
        policy_name_ipv4=f"AS{asn}:{customer_name}-IMPORT-IPV4",
        policy_name_ipv6=f"AS{asn}:{customer_name}-IMPORT-IPV6",
        as_path_filter_name=as_path_filter_name,
        ip_prefix_name=ip_prefix_name,
        ipv6_prefix_name=ipv6_prefix_name
    )

    output_file = f"generated_policies/AS{asn}-{customer_name}_policies_huawei_vrp.txt"
    try:
        write_to_file_with_check(output_file, rendered_config)
    except Exception as e:
        print(e)

def main():
    parser = argparse.ArgumentParser(description="Generate routing policies based on ASN, AS-SET, and CUSTOMER NAME.")
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    parser.add_argument("as_set", type=str, help="AS-SET for IP prefix expansion.")
    parser.add_argument("customer_name", type=str, help="Customer name for configuration naming.")
    args = parser.parse_args()

    # List of vendors to generate policies for
    vendors = ['juniper_junos', 'cisco_xe', 'cisco_xr', 'huawei_vrp']
    #for vendor in vendors:
    generate_policies_juniper_junos(args.asn, args.customer_name)
    generate_policies_cisco_xe(args.asn, args.customer_name)
    generate_policies_cisco_xr(args.asn, args.customer_name)
    generate_policies_huawei_vrp(args.asn, args.customer_name)

if __name__ == "__main__":
    main()
