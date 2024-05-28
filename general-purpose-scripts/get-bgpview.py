import argparse
import requests
import json
import sys
import pyfiglet
from datetime import datetime

BASE_URL = "https://api.bgpview.io"

def fetch_search_resources(query):
    url = f"{BASE_URL}/search"
    params = {"query_term": query}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching search resources")
        sys.exit(1)

def fetch_ip_details(ip):
    url = f"{BASE_URL}/ip/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching IP details")
        sys.exit(1)

def fetch_ix_details(ix_id):
    url = f"{BASE_URL}/ix/{ix_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching IX details")
        sys.exit(1)

def fetch_prefix_details(prefix, length):
    url = f"{BASE_URL}/prefix/{prefix}/{length}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching prefix details")
        sys.exit(1)

def fetch_asn_downstreams(asn):
    url = f"{BASE_URL}/asn/{asn}/downstreams"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching ASN downstreams")
        sys.exit(1)

def fetch_asn_upstreams(asn):
    url = f"{BASE_URL}/asn/{asn}/upstreams"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching ASN upstreams")
        sys.exit(1)

def fetch_asn_peers(asn):
    url = f"{BASE_URL}/asn/{asn}/peers"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching ASN peers")
        sys.exit(1)

def fetch_asn_prefixes(asn):
    url = f"{BASE_URL}/asn/{asn}/prefixes"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching ASN prefixes")
        sys.exit(1)

def fetch_asn_details(asn):
    url = f"{BASE_URL}/asn/{asn}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching ASN details")
        sys.exit(1)

def display_search_resources(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("Search Resources:")
        if "data" in data:
            if "asns" in data["data"]:
                print("ASNs:")
                for asn in data["data"]["asns"]:
                    print(f"  ASN: {asn.get('asn', 'N/A')}")
                    print(f"  Name: {asn.get('name', 'N/A')}")
                    print(f"  Description: {asn.get('description', 'N/A')}")
                    print(f"  Country Code: {asn.get('country_code', 'N/A')}")
                    print(f"  Email Contacts: {', '.join(asn.get('email_contacts', []))}")
                    print(f"  Abuse Contacts: {', '.join(asn.get('abuse_contacts', []))}")
                    print(f"  RIR Name: {asn.get('rir_name', 'N/A')}")
                    print()

            if "ipv4_prefixes" in data["data"]:
                print("IPv4 Prefixes:")
                for prefix in data["data"]["ipv4_prefixes"]:
                    print(f"  Prefix: {prefix.get('prefix', 'N/A')}")
                    print(f"  IP: {prefix.get('ip', 'N/A')}")
                    print(f"  CIDR: {prefix.get('cidr', 'N/A')}")
                    print(f"  Name: {prefix.get('name', 'N/A')}")
                    print(f"  Country Code: {prefix.get('country_code', 'N/A')}")
                    print(f"  Description: {prefix.get('description', 'N/A')}")
                    print(f"  Email Contacts: {', '.join(prefix.get('email_contacts', []))}")
                    print(f"  Abuse Contacts: {', '.join(prefix.get('abuse_contacts', []))}")
                    print(f"  RIR Name: {prefix.get('rir_name', 'N/A')}")
                    print(f"  Parent Prefix: {prefix.get('parent_prefix', 'N/A')}")
                    print(f"  Parent IP: {prefix.get('parent_ip', 'N/A')}")
                    print(f"  Parent CIDR: {prefix.get('parent_cidr', 'N/A')}")
                    print()

            if "ipv6_prefixes" in data["data"]:
                print("IPv6 Prefixes:")
                for prefix in data["data"]["ipv6_prefixes"]:
                    print(f"  Prefix: {prefix.get('prefix', 'N/A')}")
                    print(f"  IP: {prefix.get('ip', 'N/A')}")
                    print(f"  CIDR: {prefix.get('cidr', 'N/A')}")
                    print(f"  Name: {prefix.get('name', 'N/A')}")
                    print(f"  Country Code: {prefix.get('country_code', 'N/A')}")
                    print(f"  Description: {prefix.get('description', 'N/A')}")
                    print(f"  Email Contacts: {', '.join(prefix.get('email_contacts', []))}")
                    print(f"  Abuse Contacts: {', '.join(prefix.get('abuse_contacts', []))}")
                    print(f"  RIR Name: {prefix.get('rir_name', 'N/A')}")
                    print(f"  Parent Prefix: {prefix.get('parent_prefix', 'N/A')}")
                    print(f"  Parent IP: {prefix.get('parent_ip', 'N/A')}")
                    print(f"  Parent CIDR: {prefix.get('parent_cidr', 'N/A')}")
                    print()

            if "internet_exchanges" in data["data"]:
                print("Internet Exchanges:")
                for ix in data["data"]["internet_exchanges"]:
                    print(f"  Name: {ix.get('name', 'N/A')}")
                    print(f"  Full Name: {ix.get('name_full', 'N/A')}")
                    print(f"  Website: {ix.get('website', 'N/A')}")
                    print(f"  Tech Email: {ix.get('tech_email', 'N/A')}")
                    print(f"  Tech Phone: {ix.get('tech_phone', 'N/A')}")
                    print(f"  Policy Email: {ix.get('policy_email', 'N/A')}")
                    print(f"  Policy Phone: {ix.get('policy_phone', 'N/A')}")
                    print(f"  City: {ix.get('city', 'N/A')}")
                    print(f"  Country Code: {ix.get('country_code', 'N/A')}")
                    print(f"  URL Stats: {ix.get('url_stats', 'N/A')}")
                    print(f"  Members Count: {ix.get('members_count', 'N/A')}")
                    print("  Members:")
                    for member in ix.get('members', []):
                        print(f"    ASN: {member.get('asn', 'N/A')}")
                        print(f"    Name: {member.get('name', 'N/A')}")
                        print(f"    Description: {member.get('description', 'N/A')}")
                        print(f"    Country Code: {member.get('country_code', 'N/A')}")
                        print(f"    IPv4 Address: {member.get('ipv4_address', 'N/A')}")
                        print(f"    IPv6 Address: {member.get('ipv6_address', 'N/A')}")
                        print(f"    Speed: {member.get('speed', 'N/A')}")
                        print()
        else:
            print("No data found")

def display_ip_details(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("IP Details:")
        if "data" in data:
            ip_data = data["data"]
            print(f"- IP Address: {ip_data['ip']}")
            
            if 'ptr_record' in ip_data and ip_data['ptr_record']:
                print(f"  PTR Record: {ip_data['ptr_record']}")

            if 'prefixes' in ip_data:
                print("  Prefixes:")
                for prefix in ip_data['prefixes']:
                    print(f"    - Prefix: {prefix.get('prefix', 'N/A')}")
                    print(f"      IP: {prefix.get('ip', 'N/A')}")
                    print(f"      CIDR: {prefix.get('cidr', 'N/A')}")
                    print(f"      ASN: {prefix['asn'].get('asn', 'N/A')}")
                    print(f"      ASN Name: {prefix['asn'].get('name', 'N/A')}")
                    print(f"      ASN Description: {prefix['asn'].get('description', 'N/A')}")
                    print(f"      ASN Country Code: {prefix['asn'].get('country_code', 'N/A')}")
                    print(f"      Name: {prefix.get('name', 'N/A')}")
                    print(f"      Description: {prefix.get('description', 'N/A')}")
                    print(f"      Country Code: {prefix.get('country_code', 'N/A')}")
                    print()

            if 'rir_allocation' in ip_data:
                rir = ip_data['rir_allocation']
                print("  RIR Allocation:")
                print(f"    RIR Name: {rir.get('rir_name', 'N/A')}")
                print(f"    Country Code: {rir.get('country_code', 'N/A')}")
                print(f"    IP: {rir.get('ip', 'N/A')}")
                print(f"    CIDR: {rir.get('cidr', 'N/A')}")
                print(f"    Prefix: {rir.get('prefix', 'N/A')}")
                print(f"    Date Allocated: {rir.get('date_allocated', 'N/A')}")
                print(f"    Allocation Status: {rir.get('allocation_status', 'N/A')}")
                print()

            if 'iana_assignment' in ip_data:
                iana = ip_data['iana_assignment']
                print("  IANA Assignment:")
                print(f"    Assignment Status: {iana.get('assignment_status', 'N/A')}")
                print(f"    Description: {iana.get('description', 'N/A')}")
                print(f"    WHOIS Server: {iana.get('whois_server', 'N/A')}")
                print(f"    Date Assigned: {iana.get('date_assigned', 'N/A')}")
                print()

            if 'maxmind' in ip_data:
                maxmind = ip_data['maxmind']
                print("  MaxMind GeoIP:")
                print(f"    Country Code: {maxmind.get('country_code', 'N/A')}")
                print(f"    City: {maxmind.get('city', 'N/A')}")
                print()
        else:
            print("No data found")

def display_ix_details(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("IX Details:")
        if "data" in data:
            ix_data = data["data"]
            print(f"- Name: {ix_data['name']}")
            print(f"  Full Name: {ix_data.get('name_full', 'N/A')}")
            print(f"  Website: {ix_data.get('website', 'N/A')}")
            print(f"  Tech Email: {ix_data.get('tech_email', 'N/A')}")
            print(f"  Tech Phone: {ix_data.get('tech_phone', 'N/A')}")
            print(f"  Policy Email: {ix_data.get('policy_email', 'N/A')}")
            print(f"  Policy Phone: {ix_data.get('policy_phone', 'N/A')}")
            print(f"  City: {ix_data.get('city', 'N/A')}")
            print(f"  Country Code: {ix_data.get('country_code', 'N/A')}")
            print(f"  URL Stats: {ix_data.get('url_stats', 'N/A')}")
            print(f"  Members Count: {ix_data.get('members_count', 'N/A')}")
            print("  Members:")
            for member in ix_data.get('members', []):
                print(f"    ASN: {member.get('asn', 'N/A')}")
                print(f"    Name: {member.get('name', 'N/A')}")
                print(f"    Description: {member.get('description', 'N/A')}")
                print(f"    Country Code: {member.get('country_code', 'N/A')}")
                print(f"    IPv4 Address: {member.get('ipv4_address', 'N/A')}")
                print(f"    IPv6 Address: {member.get('ipv6_address', 'N/A')}")
                print(f"    Speed: {member.get('speed', 'N/A')}")
                print()
        else:
            print("No data found")

def display_prefix_details(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("Prefix Details:")
        if "data" in data:
            prefix_data = data["data"]
            print(f"- Prefix: {prefix_data['prefix']}")
            print(f"  IP: {prefix_data['ip']}")
            print(f"  CIDR: {prefix_data['cidr']}")
            
            if 'asns' in prefix_data:
                print("  ASNs:")
                for asn in prefix_data['asns']:
                    print(f"    - ASN: {asn.get('asn', 'N/A')}")
                    print(f"      Name: {asn.get('name', 'N/A')}")
                    print(f"      Description: {asn.get('description', 'N/A')}")
                    print(f"      Country Code: {asn.get('country_code', 'N/A')}")
                    print("      Prefix Upstreams:")
                    for upstream in asn.get('prefix_upstreams', []):
                        print(f"        - ASN: {upstream.get('asn', 'N/A')}")
                        print(f"          Name: {upstream.get('name', 'N/A')}")
                        print(f"          Description: {upstream.get('description', 'N/A')}")
                        print(f"          Country Code: {upstream.get('country_code', 'N/A')}")
                        print()
            
            print(f"  Name: {prefix_data.get('name', 'N/A')}")
            print(f"  Short Description: {prefix_data.get('description_short', 'N/A')}")
            print(f"  Full Description: {', '.join(prefix_data.get('description_full', []))}")
            print(f"  Email Contacts: {', '.join(prefix_data.get('email_contacts', []))}")
            print(f"  Abuse Contacts: {', '.join(prefix_data.get('abuse_contacts', []))}")
            print(f"  Owner Address: {', '.join(prefix_data.get('owner_address', []))}")
            
            if 'country_codes' in prefix_data:
                country_codes = prefix_data['country_codes']
                print("  Country Codes:")
                print(f"    WHOIS Country Code: {country_codes.get('whois_country_code', 'N/A')}")
                print(f"    RIR Allocation Country Code: {country_codes.get('rir_allocation_country_code', 'N/A')}")
                print(f"    MaxMind Country Code: {country_codes.get('maxmind_country_code', 'N/A')}")
                print()
            
            if 'rir_allocation' in prefix_data:
                rir = prefix_data['rir_allocation']
                print("  RIR Allocation:")
                print(f"    RIR Name: {rir.get('rir_name', 'N/A')}")
                print(f"    Country Code: {rir.get('country_code', 'N/A')}")
                print(f"    IP: {rir.get('ip', 'N/A')}")
                print(f"    CIDR: {rir.get('cidr', 'N/A')}")
                print(f"    Prefix: {rir.get('prefix', 'N/A')}")
                print(f"    Date Allocated: {rir.get('date_allocated', 'N/A')}")
                print(f"    Allocation Status: {rir.get('allocation_status', 'N/A')}")
                print()
            
            if 'iana_assignment' in prefix_data:
                iana = prefix_data['iana_assignment']
                print("  IANA Assignment:")
                print(f"    Assignment Status: {iana.get('assignment_status', 'N/A')}")
                print(f"    Description: {iana.get('description', 'N/A')}")
                print(f"    WHOIS Server: {iana.get('whois_server', 'N/A')}")
                print(f"    Date Assigned: {iana.get('date_assigned', 'N/A')}")
                print()
            
            if 'maxmind' in prefix_data:
                maxmind = prefix_data['maxmind']
                print("  MaxMind GeoIP:")
                print(f"    Country Code: {maxmind.get('country_code', 'N/A')}")
                print(f"    City: {maxmind.get('city', 'N/A')}")
                print()

            if 'related_prefixes' in prefix_data:
                print("  Related Prefixes:")
                for related in prefix_data['related_prefixes']:
                    print(f"    - Prefix: {related.get('prefix', 'N/A')}")
                    print(f"      IP: {related.get('ip', 'N/A')}")
                    print(f"      CIDR: {related.get('cidr', 'N/A')}")
                    print(f"      ASN: {related.get('asn', 'N/A')}")
                    print(f"      Name: {related.get('name', 'N/A')}")
                    print(f"      Description: {related.get('description', 'N/A')}")
                    print(f"      Country Code: {related.get('country_code', 'N/A')}")
                    print()
            
            print(f"  Date Updated: {prefix_data.get('date_updated', 'N/A')}")
        else:
            print("No data found")

def display_asn_downstreams(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("ASN Downstreams:")
        if "data" in data:
            downstream_data = data["data"]
            
            if 'ipv4_downstreams' in downstream_data:
                print("  IPv4 Downstreams:")
                for downstream in downstream_data['ipv4_downstreams']:
                    print(f"    - ASN: {downstream.get('asn', 'N/A')}")
                    print(f"      Name: {downstream.get('name', 'N/A')}")
                    print(f"      Description: {downstream.get('description', 'N/A')}")
                    print(f"      Country Code: {downstream.get('country_code', 'N/A')}")
                    print()
            
            if 'ipv6_downstreams' in downstream_data:
                print("  IPv6 Downstreams:")
                for downstream in downstream_data['ipv6_downstreams']:
                    print(f"    - ASN: {downstream.get('asn', 'N/A')}")
                    print(f"      Name: {downstream.get('name', 'N/A')}")
                    print(f"      Description: {downstream.get('description', 'N/A')}")
                    print(f"      Country Code: {downstream.get('country_code', 'N/A')}")
                    print()
        else:
            print("No data found")

def display_asn_upstreams(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("ASN Upstreams:")
        if "data" in data:
            upstream_data = data["data"]
            
            if 'ipv4_upstreams' in upstream_data:
                print("  IPv4 Upstreams:")
                for upstream in upstream_data['ipv4_upstreams']:
                    print(f"    - ASN: {upstream.get('asn', 'N/A')}")
                    print(f"      Name: {upstream.get('name', 'N/A')}")
                    print(f"      Description: {upstream.get('description', 'N/A')}")
                    print(f"      Country Code: {upstream.get('country_code', 'N/A')}")
                    print()
            
            if 'ipv6_upstreams' in upstream_data:
                print("  IPv6 Upstreams:")
                for upstream in upstream_data['ipv6_upstreams']:
                    print(f"    - ASN: {upstream.get('asn', 'N/A')}")
                    print(f"      Name: {upstream.get('name', 'N/A')}")
                    print(f"      Description: {upstream.get('description', 'N/A')}")
                    print(f"      Country Code: {upstream.get('country_code', 'N/A')}")
                    print()
            
            print(f"  IPv4 Graph: {upstream_data.get('ipv4_graph', 'N/A')}")
            print(f"  IPv6 Graph: {upstream_data.get('ipv6_graph', 'N/A')}")
            print(f"  Combined Graph: {upstream_data.get('combined_graph', 'N/A')}")
        else:
            print("No data found")

def display_asn_peers(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("ASN Peers:")
        if "data" in data:
            peer_data = data["data"]
            
            if 'ipv4_peers' in peer_data:
                print("  IPv4 Peers:")
                for peer in peer_data['ipv4_peers']:
                    print(f"    - ASN: {peer.get('asn', 'N/A')}")
                    print(f"      Name: {peer.get('name', 'N/A')}")
                    print(f"      Description: {peer.get('description', 'N/A')}")
                    print(f"      Country Code: {peer.get('country_code', 'N/A')}")
                    print()
            
            if 'ipv6_peers' in peer_data:
                print("  IPv6 Peers:")
                for peer in peer_data['ipv6_peers']:
                    print(f"    - ASN: {peer.get('asn', 'N/A')}")
                    print(f"      Name: {peer.get('name', 'N/A')}")
                    print(f"      Description: {peer.get('description', 'N/A')}")
                    print(f"      Country Code: {peer.get('country_code', 'N/A')}")
                    print()
        else:
            print("No data found")

def display_asn_prefixes(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("ASN Prefixes:")
        if "data" in data:
            prefix_data = data["data"]
            
            if 'ipv4_prefixes' in prefix_data:
                print("  IPv4 Prefixes:")
                for prefix in prefix_data['ipv4_prefixes']:
                    print(f"    - Prefix: {prefix.get('prefix', 'N/A')}")
                    print(f"      IP: {prefix.get('ip', 'N/A')}")
                    print(f"      CIDR: {prefix.get('cidr', 'N/A')}")
                    print(f"      ROA Status: {prefix.get('roa_status', 'N/A')}")
                    print(f"      Name: {prefix.get('name', 'N/A')}")
                    print(f"      Description: {prefix.get('description', 'N/A')}")
                    print(f"      Country Code: {prefix.get('country_code', 'N/A')}")
                    
                    if 'parent' in prefix:
                        parent = prefix['parent']
                        print("      Parent Prefix:")
                        print(f"        Prefix: {parent.get('prefix', 'N/A')}")
                        print(f"        IP: {parent.get('ip', 'N/A')}")
                        print(f"        CIDR: {parent.get('cidr', 'N/A')}")
                        print(f"        RIR Name: {parent.get('rir_name', 'N/A')}")
                        print(f"        Allocation Status: {parent.get('allocation_status', 'N/A')}")
                        print()
            
            if 'ipv6_prefixes' in prefix_data:
                print("  IPv6 Prefixes:")
                for prefix in prefix_data['ipv6_prefixes']:
                    print(f"    - Prefix: {prefix.get('prefix', 'N/A')}")
                    print(f"      IP: {prefix.get('ip', 'N/A')}")
                    print(f"      CIDR: {prefix.get('cidr', 'N/A')}")
                    print(f"      ROA Status: {prefix.get('roa_status', 'N/A')}")
                    print(f"      Name: {prefix.get('name', 'N/A')}")
                    print(f"      Description: {prefix.get('description', 'N/A')}")
                    print(f"      Country Code: {prefix.get('country_code', 'N/A')}")
                    
                    if 'parent' in prefix:
                        parent = prefix['parent']
                        print("      Parent Prefix:")
                        print(f"        Prefix: {parent.get('prefix', 'N/A')}")
                        print(f"        IP: {parent.get('ip', 'N/A')}")
                        print(f"        CIDR: {parent.get('cidr', 'N/A')}")
                        print(f"        RIR Name: {parent.get('rir_name', 'N/A')}")
                        print(f"        Allocation Status: {parent.get('allocation_status', 'N/A')}")
                        print()
        else:
            print("No data found")

def display_asn_details(data, json_output=False):
    if json_output:
        print(json.dumps(data, indent=4))
    else:
        print("ASN Details:")
        if "data" in data:
            asn_data = data["data"]
            print(f"- ASN: {asn_data['asn']}")
            print(f"  Name: {asn_data.get('name', 'N/A')}")
            print(f"  Short Description: {asn_data.get('description_short', 'N/A')}")
            print(f"  Full Description: {', '.join(asn_data.get('description_full', []))}")
            print(f"  Country Code: {asn_data.get('country_code', 'N/A')}")
            print(f"  Website: {asn_data.get('website', 'N/A')}")
            print(f"  Email Contacts: {', '.join(asn_data.get('email_contacts', []))}")
            print(f"  Abuse Contacts: {', '.join(asn_data.get('abuse_contacts', []))}")
            print(f"  Looking Glass: {asn_data.get('looking_glass', 'N/A')}")
            print(f"  Traffic Estimation: {asn_data.get('traffic_estimation', 'N/A')}")
            print(f"  Traffic Ratio: {asn_data.get('traffic_ratio', 'N/A')}")
            print(f"  Owner Address: {', '.join(asn_data.get('owner_address', []))}")

            if 'rir_allocation' in asn_data:
                rir = asn_data['rir_allocation']
                print("  RIR Allocation:")
                print(f"    RIR Name: {rir.get('rir_name', 'N/A')}")
                print(f"    Country Code: {rir.get('country_code', 'N/A')}")
                print(f"    Date Allocated: {rir.get('date_allocated', 'N/A')}")
                print(f"    Allocation Status: {rir.get('allocation_status', 'N/A')}")
                print()

            if 'iana_assignment' in asn_data:
                iana = asn_data['iana_assignment']
                print("  IANA Assignment:")
                print(f"    Assignment Status: {iana.get('assignment_status', 'N/A')}")
                print(f"    Description: {iana.get('description', 'N/A')}")
                print(f"    WHOIS Server: {iana.get('whois_server', 'N/A')}")
                print(f"    Date Assigned: {iana.get('date_assigned', 'N/A')}")
                print()

            print(f"  Date Updated: {asn_data.get('date_updated', 'N/A')}")
        else:
            print("No data found")

def main():
    print_banner = pyfiglet.figlet_format("BGPVIEW CLI")
    print(print_banner)
    print("https://github.com/leofurtadonyc/Network-Automation")
    print()

    parser = argparse.ArgumentParser(description="BGPView CLI Tool")
    parser.add_argument("--search", help="Search resources by ASN, IP, prefix, name, or description", type=str)
    parser.add_argument("--ip-details", help="Fetch details for a specific IP address", type=str)
    parser.add_argument("--ix", help="Fetch details for a specific IX ID", type=int)
    parser.add_argument("--prefix", help="Fetch details for a specific prefix", nargs=2)
    parser.add_argument("--asn-downstreams", help="Fetch downstreams for a specific ASN", type=int)
    parser.add_argument("--asn-upstreams", help="Fetch upstreams for a specific ASN", type=int)
    parser.add_argument("--asn-peers", help="Fetch peers for a specific ASN", type=int)
    parser.add_argument("--asn-prefixes", help="Fetch prefixes for a specific ASN", type=int)
    parser.add_argument("--asn-details", help="Fetch details for a specific ASN", type=int)
    parser.add_argument("--json", help="Display raw JSON output", action="store_true")
    args = parser.parse_args()

    start_time = datetime.now()

    if args.search:
        data = fetch_search_resources(args.search)
        display_search_resources(data, args.json)
    elif args.ip_details:
        data = fetch_ip_details(args.ip_details)
        display_ip_details(data, args.json)
    elif args.ix:
        data = fetch_ix_details(args.ix)
        display_ix_details(data, args.json)
    elif args.prefix:
        data = fetch_prefix_details(args.prefix[0], args.prefix[1])
        display_prefix_details(data, args.json)
    elif args.asn_downstreams:
        data = fetch_asn_downstreams(args.asn_downstreams)
        display_asn_downstreams(data, args.json)
    elif args.asn_upstreams:
        data = fetch_asn_upstreams(args.asn_upstreams)
        display_asn_upstreams(data, args.json)
    elif args.asn_peers:
        data = fetch_asn_peers(args.asn_peers)
        display_asn_peers(data, args.json)
    elif args.asn_prefixes:
        data = fetch_asn_prefixes(args.asn_prefixes)
        display_asn_prefixes(data, args.json)
    elif args.asn_details:
        data = fetch_asn_details(args.asn_details)
        display_asn_details(data, args.json)
    else:
        print("Please provide a valid argument. Use --help for more information.")

    end_time = datetime.now()
    duration = end_time - start_time
    print("-" * 50)
    print(f"Query completed in: {duration}")
    print("-" * 50)

if __name__ == "__main__":
    main()
