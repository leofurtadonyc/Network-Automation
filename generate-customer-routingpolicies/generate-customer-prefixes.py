import argparse
import subprocess
import os
import re

def valid_customer_name(name):
    """Validate the customer name format."""
    if re.match(r"^[A-Za-z0-9]{1,12}$", name):
        return name
    raise argparse.ArgumentTypeError("Customer name must be 1-12 characters long, alphanumeric, no spaces.")

def expand_ipv4_as_set(as_set):
    """Use bgpq3 to expand the AS-SET for IPv4 route objects."""
    command = ['bgpq3', '-j', as_set]
    return run_bgpq3(command)

def expand_ipv6_as_set(as_set):
    """Use bgpq3 to expand the AS-SET for IPv6 route objects."""
    command = ['bgpq3', '-j', '-6', as_set]
    return run_bgpq3(command)

def run_bgpq3(command):
    """Executes the bgpq3 command and handles output."""
    try:
        output = subprocess.run(command, capture_output=True, text=True)
        if output.stderr:
            print("Error output from bgpq3:", output.stderr)
        if not output.stdout:
            print("No output returned from bgpq3")
            return None
        return output.stdout
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command {command}: {e}")
        return None

def parse_prefixes(text_data):
    """Parse the custom format data to extract IP prefixes."""
    prefixes = []
    try:
        lines = text_data.split('\n')
        for line in lines:
            if '/' in line:  # Check if the line contains an IP prefix
                start = line.find('"prefix": "') + 11
                end = line.find('",', start)
                if start > 10 and end != -1:
                    prefix = line[start:end].replace('\/', '/')
                    prefixes.append(prefix)
        return prefixes
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

def write_to_file(folder, filename, data):
    """Write the given data to a file within the specified folder."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w') as file:
        for line in data:
            file.write(line + '\n')

def generate_commands(vendor, as_number, customer_name, prefixes, is_ipv6=False):
    prefix_list_name = f"AS{as_number}:{customer_name}_IMPORT_IPV{'6' if is_ipv6 else '4'}"
    commands = []

    if vendor == 'cisco_xe':
        prefix_type = "ipv6 prefix-list" if is_ipv6 else "ip prefix-list"
        commands.append(f"{prefix_type} {prefix_list_name} description Generated for AS{as_number} - {customer_name}")
        for prefix in prefixes:
            commands.append(f"{prefix_type} {prefix_list_name} permit {prefix}")

    elif vendor == 'juniper_junos':
        filter_list_name = f"AS{as_number}:{customer_name}_IMPORT_IPV{'6' if is_ipv6 else '4'}"
        commands.append(f'set policy-options route-filter-list {filter_list_name}')
        for prefix in prefixes:
            commands.append(f'set policy-options route-filter-list {filter_list_name} {prefix} exact')

    elif vendor == 'cisco_xr':
        commands.append(f"prefix-set {prefix_list_name}")
        last_index = len(prefixes) - 1
        for index, prefix in enumerate(prefixes):
            if index == last_index:
                commands.append(f"  {prefix}")  # No comma for the last entry
            else:
                commands.append(f"  {prefix},")  # Comma for all but last
        commands.append("end-set")

    elif vendor == 'huawei_vrp':
        prefix_type = "ip ipv6-prefix" if is_ipv6 else "ip prefix-list"
        commands.append(f"{prefix_type} {prefix_list_name} description Generated for AS{as_number} - {customer_name}")
        for prefix in prefixes:
            commands.append(f'  rule permit {prefix}')  # Huawei syntax may vary

    elif vendor == 'huawei_vrp_xpl':
        commands.append(f'xpl ip-prefix-list {prefix_list_name}')
        last_index = len(prefixes) - 1
        for index, prefix in enumerate(prefixes):
            ip, mask = prefix.split('/')
            if index == last_index:
                commands.append(f'  {ip} {mask} eq {mask}')  # No comma for the last entry
            else:
                commands.append(f'  {ip} {mask} eq {mask},')  # Comma for all but last
        commands.append('end-list')

    elif vendor == 'nokia_sros':
        commands.append(f'prefix-list "{prefix_list_name}"')
        for prefix in prefixes:
            commands.append(f'  prefix {prefix} exact')
        commands.append('exit')

    return commands

def run_bgpq3_aspath(asn, as_set, customer_name):
    """Generates AS-path filters using bgpq3 based on ASN and AS-SET."""
    commands = {}
    base_label = f"AS{asn}:{customer_name}_ASPATH"
    bgpq3_commands = {
        'cisco_xe': ["bgpq3", "-l", base_label, "-3f", str(asn), as_set],
        'cisco_xr': ["bgpq3", "-l", base_label, "-X3f", str(asn), as_set],
        'juniper_junos': ["bgpq3", "-l", base_label, "-J3f", str(asn), as_set],
        'huawei_vrp': ["bgpq3", "-l", base_label, "-U3f", str(asn), as_set],
        'nokia_sros': ["bgpq3", "-l", base_label, "-N3f", str(asn), as_set]
    }

    for vendor, cmd in bgpq3_commands.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stderr:
                print(f"Error output from bgpq3 for {vendor}: {result.stderr}")
            if result.stdout:
                # Assume the output is directly usable for your purposes
                commands[vendor] = result.stdout.strip().split('\n')
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute bgpq3 for {vendor}: {e}")
    
    return commands

def write_vendor_commands(folder, asn, customer_name, commands_dict):
    """Writes each vendor's commands to separate files."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    for vendor, commands in commands_dict.items():
        filename = f"{folder}/AS{asn}-{customer_name}_{vendor}_aspath.txt"
        with open(filename, 'w') as file:
            for command in commands:
                file.write(command + "\n")
        print(f"{vendor} AS-path commands written to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate network configurations from AS-SET and ASN details. This script is designed to help "
                    "network engineers quickly and easily generate IPv4 and IPv6 prefix-lists, prefix-sets, route-filter-sets, and " 
                    "IP AS-Path access-lists in multivendor environments. "
                    "It supports the syntax of Cisco IOS, Cisco IOS XE, Cisco IOS XR, Huawei (including XPL), and Nokia SR "
                    "but it can be easily extended to support other syntaxes as well. "
                    "It requires bgpq3 in order to produce both the IPv4/6 prefix lists and AS-Path access-lists.",
        epilog="Example usage: python generate-routingpolicy-prefixes.py 16509 AS16509:AS-AMAZON AMAZON",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    parser.add_argument("as_set", type=str, help="AS-SET to use for expanding IP prefixes.")
    parser.add_argument("customer_name", type=valid_customer_name, help="Customer name for file and prefix naming.")
    args = parser.parse_args()

    # Existing functionality to expand IPv4 and IPv6 sets and generate prefix lists
    ipv4_data = expand_ipv4_as_set(args.as_set)
    ipv6_data = expand_ipv6_as_set(args.as_set)
    ipv4_prefixes = parse_prefixes(ipv4_data) if ipv4_data else []
    ipv6_prefixes = parse_prefixes(ipv6_data) if ipv6_data else []

    folder = 'generated_prefixes'
    vendors = ['cisco_xe', 'cisco_xr', 'juniper_junos', 'huawei_vrp', 'huawei_vrp_xpl', 'nokia_sros']

    for vendor in vendors:
        if ipv4_prefixes:
            ipv4_commands = generate_commands(vendor, args.asn, args.customer_name, ipv4_prefixes, False)
            ipv4_filename = f"AS{args.asn}-{args.customer_name}_{vendor}_ipv4.txt"
            write_to_file(folder, ipv4_filename, ipv4_commands)
            print(f"IPv4 commands for {vendor} written to {folder}/{ipv4_filename}")

        if ipv6_prefixes:
            ipv6_commands = generate_commands(vendor, args.asn, args.customer_name, ipv6_prefixes, True)
            ipv6_filename = f"AS{args.asn}-{args.customer_name}_{vendor}_ipv6.txt"
            write_to_file(folder, ipv6_filename, ipv6_commands)
            print(f"IPv6 commands for {vendor} written to {folder}/{ipv6_filename}")

    # Generate AS-path commands using bgpq3 with specified labels
    as_path_data = run_bgpq3_aspath(args.asn, args.as_set, args.customer_name)
    folder = 'generated_prefixes'
    write_vendor_commands(folder, args.asn, args.customer_name, as_path_data)

if __name__ == "__main__":
    main()
