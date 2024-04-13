import argparse
import requests
import sys
from tabulate import tabulate

# Constants for API Endpoints
PEERINGDB_API = "https://peeringdb.com/api"
ASRANK_API = "https://api.asrank.caida.org/v2/graphql"

def get_asn_data_from_peeringdb(asn):
    """Get ASN data from PeeringDB."""
    response = requests.get(f"{PEERINGDB_API}/net?asn={asn}")
    data = response.json()
    return data['data'][0] if data['data'] else None

def get_org_data(org_id):
    """Get organization data from PeeringDB."""
    response = requests.get(f"{PEERINGDB_API}/org/{org_id}")
    data = response.json()
    return data['data'][0] if data['data'] else None

def fetch_asn_data_from_asrank(asn):
    """Fetch ASN data from AS Rank API."""
    query = """
    {{
        asn(asn:"{asn}") {{
            asn
            asnName
            rank
            organization {{
                orgId
                orgName
            }}
            cliqueMember
            seen
            longitude
            latitude
            cone {{
                numberAsns
                numberPrefixes
                numberAddresses
            }}
            country {{
                iso
                name
            }}
            asnDegree {{
                provider
                peer
                customer
                total
                transit
                sibling
            }}
            announcing {{
                numberPrefixes
                numberAddresses
            }}
        }}
    }}""".format(asn=asn)
    response = requests.post(ASRANK_API, json={'query': query})
    if response.status_code == 200:
        return response.json()['data']['asn']
    else:
        sys.exit("Query to AS Rank API failed with status code: {}".format(response.status_code))

def print_asrank_results(data):
    """Print formatted ASN data from AS Rank using tabulate."""
    table_data = [
        ["ASN", data['asn']],
        ["ASN Name", data.get('asnName')],
        ["Rank", data.get('rank')],
        ["Organization ID", data['organization']['orgId']],
        ["Organization Name", data['organization']['orgName']],
        ["Clique Member", data.get('cliqueMember')],
        ["Seen", data.get('seen')],
        ["Location", "{}, {}".format(data.get('latitude'), data.get('longitude'))],
        ["Country", "{} ({})".format(data['country']['name'], data['country']['iso'])],
        ["Cone ASNs", data['cone']['numberAsns']],
        ["Cone Prefixes", data['cone']['numberPrefixes']],
        ["Cone Addresses", data['cone']['numberAddresses']],
        ["Degree", "Provider: {}, Peer: {}, Customer: {}".format(data['asnDegree']['provider'], data['asnDegree']['peer'], data['asnDegree']['customer'])],
        ["Announcing Prefixes", data['announcing']['numberPrefixes']],
        ["Announcing Addresses", data['announcing']['numberAddresses']]
    ]
    print(tabulate(table_data, headers=["Field", "Value"], tablefmt="grid"))

def main():
    parser = argparse.ArgumentParser(description="Query ASN details on PeeringDB and AS Rank.")
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    args = parser.parse_args()

    # Fetch data from PeeringDB
    asn_data_peeringdb = get_asn_data_from_peeringdb(args.asn)
    if not asn_data_peeringdb:
        print(f"ASN AS{args.asn} was not found in PeeringDB.")
        sys.exit(1)

    # Print PeeringDB data
    org_data = get_org_data(asn_data_peeringdb['org_id'])
    print("\nDetails of ASN in PeeringDB:")
    print(f"Organization: {org_data.get('name', 'N/A')}")
    print(f"Company Website: {asn_data_peeringdb.get('website', 'N/A')}")
    print(f"ASN: AS{args.asn}")
    print(f"IRR as-set/route-set: {asn_data_peeringdb.get('irr_as_set', 'N/A')}")
    print(f"Route Server URL: {asn_data_peeringdb.get('route_server', 'N/A')}")
    print(f"Looking Glass URL: {asn_data_peeringdb.get('looking_glass', 'N/A')}")
    print(f"Network Type: {asn_data_peeringdb.get('info_type', 'N/A')}")
    print(f"IPv4 Prefixes: {asn_data_peeringdb.get('info_prefixes4', 'N/A')}")
    print(f"IPv6 Prefixes: {asn_data_peeringdb.get('info_prefixes6', 'N/A')}")
    print(f"Geographic Scope: {asn_data_peeringdb.get('info_scope', 'N/A').capitalize() if asn_data_peeringdb.get('info_scope') else 'N/A'}")
    print(f"Protocols Supported: {' & '.join(['IPv6' if asn_data_peeringdb.get('info_ipv6', False) else '', 'IPv4' if asn_data_peeringdb.get('info_unicast', False) else '']).strip()}")

    # Fetch and print data from AS Rank
    asn_data_asrank = fetch_asn_data_from_asrank(args.asn)
    print("\nDetails from AS Rank (Caida):")
    print_asrank_results(asn_data_asrank)

if __name__ == "__main__":
    main()
