# This script is a slight modification of the original asrank-download-asn.py script; it uses tabulate to display the returned data instead of JSON.
import re
import argparse
import sys
import json
import requests
from tabulate import tabulate

URL = "https://api.asrank.caida.org/v2/graphql"

def print_help():
    print(sys.argv[0], "-u as-rank.caida.org/api/v1")

parser = argparse.ArgumentParser()
parser.add_argument("asn", type=int, help="ASN we are looking up")
args = parser.parse_args()

def main():
    if args.asn is None:
        parser.print_help()
        sys.exit()
    query = AsnQuery(args.asn)
    request = requests.post(URL, json={'query': query})
    if request.status_code == 200:
        data = request.json()
        print_formatted_results(data)
    else:
        print("Query failed to run returned code of %d." % request.status_code)

def print_formatted_results(data):
    print("\nDetails of ASN from CAIDA's AS Rank API:")
    print("----------------------------------------\n")
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
    print(tabulate(table_data, headers=["Field", "Value"], tablefmt="grid"))

def AsnQuery(asn): 
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
