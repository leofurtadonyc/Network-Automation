import argparse
import requests
import sys
import pyfiglet

BASE_URL = "https://peeringdb.com/api"

def get_asn_data(asn):
    """Get the ASN data from PeeringDB."""
    try:
        response = requests.get(f"{BASE_URL}/net?asn={asn}")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        if not data['data']:
            return None
        return data['data'][0]
    except requests.RequestException as e:
        print(f"Error fetching data for ASN {asn}: {e}")
        sys.exit(1)


def get_org_data(org_id):
    """Get the organization's data in PeeringDB."""
    try:
        response = requests.get(f"{BASE_URL}/org/{org_id}")
        response.raise_for_status()
        data = response.json()
        if not data['data']:
            return None
        return data['data'][0]
    except requests.RequestException as e:
        print(f"Error fetching organization data for Org ID {org_id}: {e}")
        sys.exit(1)


def main():
    print_banner = pyfiglet.figlet_format("Get AS-SET")
    print(print_banner)
    print("https://github.com/leofurtadonyc/Network-Automation")
    print()
    parser = argparse.ArgumentParser(description="Query ASN details on PeeringDB.")
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    args = parser.parse_args()

    asn_str = f"AS{args.asn}"
    asn_data = get_asn_data(args.asn)

    if not asn_data:
        print(f"No data found for ASN {asn_str} in PeeringDB.")
        sys.exit(1)

    org_data = get_org_data(asn_data['org_id'])
    if not org_data:
        print(f"Organization data not found for ASN {asn_str}.")
        sys.exit(1)

    network_type_mapping = {
        "Content": "Content",
        "NSP": "Network Service Provider",
        "IXP": "Internet Exchange Point",
        "Enterprise": "Enterprise"
    }

    supported_protocols = []
    if asn_data.get('info_ipv6', False):
        supported_protocols.append("IPv6")
    if asn_data.get('info_unicast', False):
        supported_protocols.append("IPv4")

    print("\nDetails of ASN in PeeringDB:")
    print("----------------------------\n")
    print(f"Organization: {org_data.get('name', 'N/A')}")
    print(f"Company Website: {asn_data.get('website', 'N/A')}")
    print(f"ASN: {asn_str}")
    print(f"IRR as-set/route-set: {asn_data.get('irr_as_set', 'N/A')}")
    if not asn_data.get('irr_as_set'):
        print("\nNo AS-SET registered for this ASN in PeeringDB; manual prefix validation required.")
        sys.exit(1)
    print(f"Route Server URL: {asn_data.get('route_server', 'N/A')}")
    print(f"Looking Glass URL: {asn_data.get('looking_glass', 'N/A')}")
    print(f"Network Type: {network_type_mapping.get(asn_data.get('info_type', 'N/A'), 'N/A')}")
    print(f"IPv4 Prefixes: {asn_data.get('info_prefixes4', 'N/A')}")
    print(f"IPv6 Prefixes: {asn_data.get('info_prefixes6', 'N/A')}")
    print(f"Geographic Scope: {asn_data.get('info_scope', 'N/A').capitalize() if asn_data.get('info_scope') else 'N/A'}")
    print(f"Protocols Supported: {' & '.join(supported_protocols)}")
    print(f"Last Updated: {asn_data.get('updated', 'N/A')}")

if __name__ == "__main__":
    main()
