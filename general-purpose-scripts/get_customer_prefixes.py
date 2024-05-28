# https://github.com/leofurtadonyc/Network-Automation/wiki
import argparse
import requests
import json
import subprocess
import pyfiglet

def get_peeringdb_data(asn):
    """Check the ASN details on PeeringDB"""
    url = f"https://peeringdb.com/api/net?asn={asn}"
    response = requests.get(url)
    data = response.json()
    
    if 'data' in data and data['data']:
        return data['data'][0]
    else:
        print(f"API Response: {data}")
        return None

def get_prefixes_from_bgpq3(as_set, ip_version):
    """Obtain the prefixes using bgpq3"""
    if ip_version == 4:
        cmd = ["bgpq3", "-j", "-4", "-m", "24", "-S", "RADB", as_set]
    elif ip_version == 6:
        cmd = ["bgpq3", "-j", "-6", "-m", "48", "-S", "RADB", as_set]
    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to decode JSON. The command output was:")
        print(result.stdout)
        return {}

def check_as_set_existence(as_set):
    """Check the existence of the AS-SET in the RADB using the whois command."""
    cmd = ["whois", "-h", "whois.radb.net", as_set]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if "%  No entries found for the selected source(s)." in result.stdout:
        return False, result.stdout
    return True, result.stdout

def main(asn):
    print_banner = pyfiglet.figlet_format("Get Prefixes")
    print(print_banner)
    print("https://github.com/leofurtadonyc/Network-Automation")
    print()
    data = get_peeringdb_data(asn)
    if not data:
        print(f"The reported ASN does not have a record in PeeringDB, prefix validation will be aborted. Contact and resolve the problem directly with the customer.")
        return

    print(f"Details of ASN in PeeringDB:\n")
    print(f"Organization: {data['name']}")
    print(f"Company Website: {data['website']}")
    print(f"ASN: AS{data['asn']}")
    print(f"IRR as-set/route-set: {data['irr_as_set']}")
    print(f"Route Server URL: {data['route_server']}")
    print(f"Looking Glass URL: {data['looking_glass']}")
    print(f"Network Type: {data['info_type']}")
    print(f"IPv4 Prefixes: {data['info_unicast']}")
    print(f"IPv6 Prefixes: {data['info_ipv6']}")
    print(f"Geographic Scope: {data['info_scope']}")
    print(f"Protocols Supported: {'IPv6 & IPv4' if data['info_ipv6'] else 'IPv4'}")
    print(f"Last Updated: {data['updated']}")

    as_set = data['irr_as_set']
    if not as_set or as_set.strip() == "":
        print(f"The reported ASN does not have an AS-SET registered in PeeringDB and therefore, this task cannot be completed. Prefix validation will have to be done manually. Aborting the operation.")
        return

    exists, whois_output = check_as_set_existence(as_set)
    print(f"\nWhois data for {as_set}:\n{whois_output}")
    if not exists:
        print(f"The reported ASN has a record in PeeringDB and also an AS-SET mentioned in the 'IRR as-set/route-set' field. However, this AS-SET does not exist or was not found in the RADB base. Prefix validation cannot be performed, aborting the task. Please contact the customer for resolution.")
        return

    print("\nIPv4 prefixes derived from AS-SET:")
    ipv4_prefixes = get_prefixes_from_bgpq3(as_set, 4)
    if 'NN' in ipv4_prefixes:
        for prefix in ipv4_prefixes['NN']:
            print(prefix['prefix'])
    else:
        print("No IPv4 prefix found or unexpected JSON structure.")

    print("\nIPv6 prefixes derived from the AS-SET:")
    ipv6_prefixes = get_prefixes_from_bgpq3(as_set, 6)
    if 'NN' in ipv6_prefixes:
        for prefix in ipv6_prefixes['NN']:
            print(prefix['prefix'])
    else:
        print("No IPv6 prefix found or unexpected JSON structure.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script uses PeeringDB and whois (RADB) data sources, along with bgpq3, to obtain customer IPv4 and IPv6 prefix information.')
    parser.add_argument('asn', type=int, help='ASN number without the "AS" prefix.')
    args = parser.parse_args()

    main(args.asn)