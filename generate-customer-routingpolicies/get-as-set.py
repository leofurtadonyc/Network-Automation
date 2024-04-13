# This is a simple script that interacts with PeeringDB's API. 
# Its main purpose is to check the provided Autonomous System Number (ASN) in PeeringDB, with a special emphasis on the AS-SET field. 
# This information can then be used by other scripts to generate prefix-lists and route-filter-lists for routing security policies.

import argparse
import requests
import sys

BASE_URL = "https://peeringdb.com/api"


def get_asn_data(asn):
    """Get the ASN data from PeeringDB."""
    response = requests.get(f"{BASE_URL}/net?asn={asn}")
    data = response.json()
    return data['data'][0] if data['data'] else None


def get_org_data(org_id):
    """Get the organization's data in PeeringDB."""
    response = requests.get(f"{BASE_URL}/org/{org_id}")
    data = response.json()
    return data['data'][0] if data['data'] else None


def main():
    parser = argparse.ArgumentParser(description="Query ASN details on PeeringDB.")
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    args = parser.parse_args()

    asn_str = f"AS{args.asn}"
    asn_data = get_asn_data(args.asn)

    if not asn_data:
        print(f"The ASN {asn_str} was not found in PeeringDB.")
        sys.exit(1)

    org_data = get_org_data(asn_data['org_id'])

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
        print("\nThe ASN does not have an AS-SET registered in PeeringDB and therefore, "
              "this task cannot be completed. The prefix validation will have to be done "
              "manually. Aborting the operation.")
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
