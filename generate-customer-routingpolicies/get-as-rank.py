# This script is a slight modification of the original asrank-download-asn.py script; it uses tabulate to display the returned data instead of JSON.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import argparse
import sys
import requests
from tabulate import tabulate

URL = "https://api.asrank.caida.org/v2/graphql"

def create_parser():
    parser = argparse.ArgumentParser(description='Look up ASN details using AS Rank API.')
    parser.add_argument("asn", type=int, help="ASN we are looking up")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.asn is None:
        parser.print_help()
        sys.exit(1)

    data = get_asn_data(args.asn)
    if data:
        print_formatted_results(data)
    else:
        print(f"Failed to retrieve data for ASN {args.asn}. Does it even exist? Please check the ASN and try again.")
        sys.exit(1)

def get_asn_data(asn):
    query = asn_query(asn)
    try:
        response = requests.post(URL, json={'query': query})
        response.raise_for_status()  # Checks HTTP request for errors
        data = response.json()
        return data if data.get('data', {}).get('asn') else None
    except requests.RequestException as e:
        print(f"Error fetching data for ASN {asn}: {e}")
        return None
    except ValueError:
        print("Failed to decode JSON response.")
        return None

def print_formatted_results(data):
    asn_data = data['data']['asn']
    table_data = [
        ["ASN", asn_data.get('asn')],
        ["ASN Name", asn_data.get('asnName')],
        ["Rank", asn_data.get('rank')],
        ["Organization ID", asn_data['organization']['orgId']],
        ["Organization Name", asn_data['organization']['orgName']],
        ["Clique Member", asn_data.get('cliqueMember')],
        ["Seen", asn_data.get('seen')],
        ["Location", f"{asn_data.get('latitude')}, {asn_data.get('longitude')}"],
        ["Country", f"{asn_data['country']['name']} ({asn_data['country']['iso']})"],
        ["Cone ASNs", asn_data['cone']['numberAsns']],
        ["Cone Prefixes", asn_data['cone']['numberPrefixes']],
        ["Cone Addresses", asn_data['cone']['numberAddresses']],
        ["Degree", f"Provider: {asn_data['asnDegree']['provider']}, Peer: {asn_data['asnDegree']['peer']}, Customer: {asn_data['asnDegree']['customer']}"],
        ["Announcing Prefixes", asn_data['announcing']['numberPrefixes']],
        ["Announcing Addresses", asn_data['announcing']['numberAddresses']]
    ]
    print("\nDetails of ASN from CAIDA's AS Rank API:")
    print("----------------------------------------\n")
    print(tabulate(table_data, headers=["Field", "Value"], tablefmt="grid"))

def asn_query(asn):
    return """{
        asn(asn:"%i") {
            asn
            asnName
            rank
            organization {
                orgId
                orgName
            }
            cliqueMember
            seen
            longitude
            latitude
            cone {
                numberAsns
                numberPrefixes
                numberAddresses
            }
            country {
                iso
                name
            }
            asnDegree {
                provider
                peer
                customer
                total
                transit
                sibling
            }
            announcing {
                numberPrefixes
                numberAddresses
            }
        }
    }""" % (asn)

if __name__ == "__main__":
    main()
