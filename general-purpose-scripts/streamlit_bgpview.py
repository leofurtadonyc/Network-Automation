import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime

BASE_URL = "https://api.bgpview.io"

def fetch_search_resources(query):
    url = f"{BASE_URL}/search"
    params = {"query_term": query}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

def fetch_ip_details(ip):
    url = f"{BASE_URL}/ip/{ip}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_ix_details(ix_id):
    url = f"{BASE_URL}/ix/{ix_id}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_prefix_details(prefix, length):
    url = f"{BASE_URL}/prefix/{prefix}/{length}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_asn_downstreams(asn):
    url = f"{BASE_URL}/asn/{asn}/downstreams"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_asn_upstreams(asn):
    url = f"{BASE_URL}/asn/{asn}/upstreams"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_asn_peers(asn):
    url = f"{BASE_URL}/asn/{asn}/peers"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_asn_prefixes(asn):
    url = f"{BASE_URL}/asn/{asn}/prefixes"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def fetch_asn_details(asn):
    url = f"{BASE_URL}/asn/{asn}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def plot_asn_prefixes(prefix_data):
    ipv4_prefixes = prefix_data['data']['ipv4_prefixes']
    ipv6_prefixes = prefix_data['data']['ipv6_prefixes']

    labels = 'IPv4 Prefixes', 'IPv6 Prefixes'
    sizes = [len(ipv4_prefixes), len(ipv6_prefixes)]
    explode = (0.1, 0)  # explode the 1st slice (IPv4)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=140)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

def plot_asn_network(data, title, key):
    fig, ax = plt.subplots()
    elements = data['data'].get(key, [])
    if elements:
        asns = [element['asn'] for element in elements]
        counts = {asn: asns.count(asn) for asn in set(asns)}
        ax.bar(counts.keys(), counts.values())
    else:
        ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    
    ax.set_xlabel('ASNs')
    ax.set_ylabel(f'Number of {key.capitalize()}')
    ax.set_title(title)

    st.pyplot(fig)

def plot_search_resources(data):
    asns = data['data']['asns']
    ipv4_prefixes = data['data']['ipv4_prefixes']
    ipv6_prefixes = data['data']['ipv6_prefixes']
    internet_exchanges = data['data']['internet_exchanges']

    fig, ax = plt.subplots()
    categories = ['ASNs', 'IPv4 Prefixes', 'IPv6 Prefixes', 'Internet Exchanges']
    counts = [len(asns), len(ipv4_prefixes), len(ipv6_prefixes), len(internet_exchanges)]
    ax.bar(categories, counts)
    ax.set_xlabel('Categories')
    ax.set_ylabel('Counts')
    ax.set_title('Search Resource Distribution')

    st.pyplot(fig)

def display_search_resources(data):
    st.subheader("Search Results")
    if "data" in data:
        if "asns" in data["data"]:
            st.markdown("### ASNs")
            for asn in data["data"]["asns"]:
                st.markdown(f"""
                **ASN:** {asn.get('asn', 'N/A')}
                - **Name:** {asn.get('name', 'N/A')}
                - **Description:** {asn.get('description', 'N/A')}
                - **Country Code:** {asn.get('country_code', 'N/A')}
                - **Email Contacts:** {', '.join(asn.get('email_contacts', []))}
                - **Abuse Contacts:** {', '.join(asn.get('abuse_contacts', []))}
                - **RIR Name:** {asn.get('rir_name', 'N/A')}
                """)

        if "ipv4_prefixes" in data["data"]:
            st.markdown("### IPv4 Prefixes")
            for prefix in data["data"]["ipv4_prefixes"]:
                st.markdown(f"""
                **Prefix:** {prefix.get('prefix', 'N/A')}
                - **IP:** {prefix.get('ip', 'N/A')}
                - **CIDR:** {prefix.get('cidr', 'N/A')}
                - **Name:** {prefix.get('name', 'N/A')}
                - **Country Code:** {prefix.get('country_code', 'N/A')}
                - **Description:** {prefix.get('description', 'N/A')}
                - **Email Contacts:** {', '.join(prefix.get('email_contacts', []))}
                - **Abuse Contacts:** {', '.join(prefix.get('abuse_contacts', []))}
                - **RIR Name:** {prefix.get('rir_name', 'N/A')}
                - **Parent Prefix:** {prefix.get('parent_prefix', 'N/A')}
                - **Parent IP:** {prefix.get('parent_ip', 'N/A')}
                - **Parent CIDR:** {prefix.get('parent_cidr', 'N/A')}
                """)

        if "ipv6_prefixes" in data["data"]:
            st.markdown("### IPv6 Prefixes")
            for prefix in data["data"]["ipv6_prefixes"]:
                st.markdown(f"""
                **Prefix:** {prefix.get('prefix', 'N/A')}
                - **IP:** {prefix.get('ip', 'N/A')}
                - **CIDR:** {prefix.get('cidr', 'N/A')}
                - **Name:** {prefix.get('name', 'N/A')}
                - **Country Code:** {prefix.get('country_code', 'N/A')}
                - **Description:** {prefix.get('description', 'N/A')}
                - **Email Contacts:** {', '.join(prefix.get('email_contacts', []))}
                - **Abuse Contacts:** {', '.join(prefix.get('abuse_contacts', []))}
                - **RIR Name:** {prefix.get('rir_name', 'N/A')}
                - **Parent Prefix:** {prefix.get('parent_prefix', 'N/A')}
                - **Parent IP:** {prefix.get('parent_ip', 'N/A')}
                - **Parent CIDR:** {prefix.get('parent_cidr', 'N/A')}
                """)

        if "internet_exchanges" in data["data"]:
            st.markdown("### Internet Exchanges")
            for ix in data["data"]["internet_exchanges"]:
                st.markdown(f"""
                **Name:** {ix.get('name', 'N/A')}
                - **Full Name:** {ix.get('name_full', 'N/A')}
                - **Website:** {ix.get('website', 'N/A')}
                - **Tech Email:** {ix.get('tech_email', 'N/A')}
                - **Tech Phone:** {ix.get('tech_phone', 'N/A')}
                - **Policy Email:** {ix.get('policy_email', 'N/A')}
                - **Policy Phone:** {ix.get('policy_phone', 'N/A')}
                - **City:** {ix.get('city', 'N/A')}
                - **Country Code:** {ix.get('country_code', 'N/A')}
                - **URL Stats:** {ix.get('url_stats', 'N/A')}
                - **Members Count:** {ix.get('members_count', 'N/A')}
                **Members:**
                """)
                for member in ix.get('members', []):
                    st.markdown(f"""
                    - **ASN:** {member.get('asn', 'N/A')}
                    - **Name:** {member.get('name', 'N/A')}
                    - **Description:** {member.get('description', 'N/A')}
                    - **Country Code:** {member.get('country_code', 'N/A')}
                    - **IPv4 Address:** {member.get('ipv4_address', 'N/A')}
                    - **IPv6 Address:** {member.get('ipv6_address', 'N/A')}
                    - **Speed:** {member.get('speed', 'N/A')}
                    """)

def display_ip_details(data):
    st.subheader("IP Details")
    if "data" in data:
        ip_data = data["data"]
        st.markdown(f"""
        **IP Address:** {ip_data['ip']}
        """)
        
        if 'ptr_record' in ip_data and ip_data['ptr_record']:
            st.markdown(f"**PTR Record:** {ip_data['ptr_record']}")

        if 'prefixes' in ip_data:
            st.markdown("**Prefixes:**")
            for prefix in ip_data['prefixes']:
                st.markdown(f"""
                - **Prefix:** {prefix.get('prefix', 'N/A')}
                - **IP:** {prefix.get('ip', 'N/A')}
                - **CIDR:** {prefix.get('cidr', 'N/A')}
                - **ASN:** {prefix['asn'].get('asn', 'N/A')}
                - **ASN Name:** {prefix['asn'].get('name', 'N/A')}
                - **ASN Description:** {prefix['asn'].get('description', 'N/A')}
                - **ASN Country Code:** {prefix['asn'].get('country_code', 'N/A')}
                - **Name:** {prefix.get('name', 'N/A')}
                - **Description:** {prefix.get('description', 'N/A')}
                - **Country Code:** {prefix.get('country_code', 'N/A')}
                """)

        if 'rir_allocation' in ip_data:
            rir = ip_data['rir_allocation']
            st.markdown(f"""
            **RIR Allocation:**
            - **RIR Name:** {rir.get('rir_name', 'N/A')}
            - **Country Code:** {rir.get('country_code', 'N/A')}
            - **IP:** {rir.get('ip', 'N/A')}
            - **CIDR:** {rir.get('cidr', 'N/A')}
            - **Prefix:** {rir.get('prefix', 'N/A')}
            - **Date Allocated:** {rir.get('date_allocated', 'N/A')}
            - **Allocation Status:** {rir.get('allocation_status', 'N/A')}
            """)

        if 'iana_assignment' in ip_data:
            iana = ip_data['iana_assignment']
            st.markdown(f"""
            **IANA Assignment:**
            - **Assignment Status:** {iana.get('assignment_status', 'N/A')}
            - **Description:** {iana.get('description', 'N/A')}
            - **WHOIS Server:** {iana.get('whois_server', 'N/A')}
            - **Date Assigned:** {iana.get('date_assigned', 'N/A')}
            """)

        if 'maxmind' in ip_data:
            maxmind = ip_data['maxmind']
            st.markdown(f"""
            **MaxMind GeoIP:**
            - **Country Code:** {maxmind.get('country_code', 'N/A')}
            - **City:** {maxmind.get('city', 'N/A')}
            """)
    else:
        st.error("No data found")

def display_ix_details(data):
    st.subheader("IX Details")
    if "data" in data:
        ix_data = data["data"]
        st.markdown(f"""
        **Name:** {ix_data['name']}
        - **Full Name:** {ix_data.get('name_full', 'N/A')}
        - **Website:** {ix_data.get('website', 'N/A')}
        - **Tech Email:** {ix_data.get('tech_email', 'N/A')}
        - **Tech Phone:** {ix_data.get('tech_phone', 'N/A')}
        - **Policy Email:** {ix_data.get('policy_email', 'N/A')}
        - **Policy Phone:** {ix_data.get('policy_phone', 'N/A')}
        - **City:** {ix_data.get('city', 'N/A')}
        - **Country Code:** {ix_data.get('country_code', 'N/A')}
        - **URL Stats:** {ix_data.get('url_stats', 'N/A')}
        - **Members Count:** {ix_data.get('members_count', 'N/A')}
        """)
        st.markdown("**Members:**")
        for member in ix_data.get('members', []):
            st.markdown(f"""
            - **ASN:** {member.get('asn', 'N/A')}
            - **Name:** {member.get('name', 'N/A')}
            - **Description:** {member.get('description', 'N/A')}
            - **Country Code:** {member.get('country_code', 'N/A')}
            - **IPv4 Address:** {member.get('ipv4_address', 'N/A')}
            - **IPv6 Address:** {member.get('ipv6_address', 'N/A')}
            - **Speed:** {member.get('speed', 'N/A')}
            """)
    else:
        st.error("No data found")

def display_prefix_details(data):
    st.subheader("Prefix Details")
    if "data" in data:
        prefix_data = data["data"]
        st.markdown(f"""
        **Prefix:** {prefix_data['prefix']}
        - **IP:** {prefix_data['ip']}
        - **CIDR:** {prefix_data['cidr']}
        """)
        
        if 'asns' in prefix_data:
            st.markdown("**ASNs:**")
            for asn in prefix_data['asns']:
                st.markdown(f"""
                - **ASN:** {asn.get('asn', 'N/A')}
                - **Name:** {asn.get('name', 'N/A')}
                - **Description:** {asn.get('description', 'N/A')}
                - **Country Code:** {asn.get('country_code', 'N/A')}
                **Prefix Upstreams:**
                """)
                for upstream in asn.get('prefix_upstreams', []):
                    st.markdown(f"""
                    - **ASN:** {upstream.get('asn', 'N/A')}
                    - **Name:** {upstream.get('name', 'N/A')}
                    - **Description:** {upstream.get('description', 'N/A')}
                    - **Country Code:** {upstream.get('country_code', 'N/A')}
                    """)

        st.markdown(f"""
        - **Name:** {prefix_data.get('name', 'N/A')}
        - **Short Description:** {prefix_data.get('description_short', 'N/A')}
        - **Full Description:** {', '.join(prefix_data.get('description_full', []))}
        - **Email Contacts:** {', '.join(prefix_data.get('email_contacts', []))}
        - **Abuse Contacts:** {', '.join(prefix_data.get('abuse_contacts', []))}
        - **Owner Address:** {', '.join(prefix_data.get('owner_address', []))}
        """)

        if 'country_codes' in prefix_data:
            country_codes = prefix_data['country_codes']
            st.markdown(f"""
            **Country Codes:**
            - **WHOIS Country Code:** {country_codes.get('whois_country_code', 'N/A')}
            - **RIR Allocation Country Code:** {country_codes.get('rir_allocation_country_code', 'N/A')}
            - **MaxMind Country Code:** {country_codes.get('maxmind_country_code', 'N/A')}
            """)

        if 'rir_allocation' in prefix_data:
            rir = prefix_data['rir_allocation']
            st.markdown(f"""
            **RIR Allocation:**
            - **RIR Name:** {rir.get('rir_name', 'N/A')}
            - **Country Code:** {rir.get('country_code', 'N/A')}
            - **IP:** {rir.get('ip', 'N/A')}
            - **CIDR:** {rir.get('cidr', 'N/A')}
            - **Prefix:** {rir.get('prefix', 'N/A')}
            - **Date Allocated:** {rir.get('date_allocated', 'N/A')}
            - **Allocation Status:** {rir.get('allocation_status', 'N/A')}
            """)

        if 'iana_assignment' in prefix_data:
            iana = prefix_data['iana_assignment']
            st.markdown(f"""
            **IANA Assignment:**
            - **Assignment Status:** {iana.get('assignment_status', 'N/A')}
            - **Description:** {iana.get('description', 'N/A')}
            - **WHOIS Server:** {iana.get('whois_server', 'N/A')}
            - **Date Assigned:** {iana.get('date_assigned', 'N/A')}
            """)

        if 'maxmind' in prefix_data:
            maxmind = prefix_data['maxmind']
            st.markdown(f"""
            **MaxMind GeoIP:**
            - **Country Code:** {maxmind.get('country_code', 'N/A')}
            - **City:** {maxmind.get('city', 'N/A')}
            """)

        if 'related_prefixes' in prefix_data:
            st.markdown("**Related Prefixes:**")
            for related in prefix_data['related_prefixes']:
                st.markdown(f"""
                - **Prefix:** {related.get('prefix', 'N/A')}
                - **IP:** {related.get('ip', 'N/A')}
                - **CIDR:** {related.get('cidr', 'N/A')}
                - **ASN:** {related.get('asn', 'N/A')}
                - **Name:** {related.get('name', 'N/A')}
                - **Description:** {related.get('description', 'N/A')}
                - **Country Code:** {related.get('country_code', 'N/A')}
                """)

        st.markdown(f"**Date Updated:** {prefix_data.get('date_updated', 'N/A')}")
    else:
        st.error("No data found")

def display_asn_downstreams(data):
    st.subheader("ASN Downstreams")
    if "data" in data:
        downstream_data = data["data"]
        
        if 'ipv4_downstreams' in downstream_data:
            st.markdown("**IPv4 Downstreams:**")
            for downstream in downstream_data['ipv4_downstreams']:
                st.markdown(f"""
                - **ASN:** {downstream.get('asn', 'N/A')}
                - **Name:** {downstream.get('name', 'N/A')}
                - **Description:** {downstream.get('description', 'N/A')}
                - **Country Code:** {downstream.get('country_code', 'N/A')}
                """)
        
        if 'ipv6_downstreams' in downstream_data:
            st.markdown("**IPv6 Downstreams:**")
            for downstream in downstream_data['ipv6_downstreams']:
                st.markdown(f"""
                - **ASN:** {downstream.get('asn', 'N/A')}
                - **Name:** {downstream.get('name', 'N/A')}
                - **Description:** {downstream.get('description', 'N/A')}
                - **Country Code:** {downstream.get('country_code', 'N/A')}
                """)
    else:
        st.error("No data found")

def display_asn_upstreams(data):
    st.subheader("ASN Upstreams")
    if "data" in data:
        upstream_data = data["data"]
        
        if 'ipv4_upstreams' in upstream_data:
            st.markdown("**IPv4 Upstreams:**")
            for upstream in upstream_data['ipv4_upstreams']:
                st.markdown(f"""
                - **ASN:** {upstream.get('asn', 'N/A')}
                - **Name:** {upstream.get('name', 'N/A')}
                - **Description:** {upstream.get('description', 'N/A')}
                - **Country Code:** {upstream.get('country_code', 'N/A')}
                """)
        
        if 'ipv6_upstreams' in upstream_data:
            st.markdown("**IPv6 Upstreams:**")
            for upstream in upstream_data['ipv6_upstreams']:
                st.markdown(f"""
                - **ASN:** {upstream.get('asn', 'N/A')}
                - **Name:** {upstream.get('name', 'N/A')}
                - **Description:** {upstream.get('description', 'N/A')}
                - **Country Code:** {upstream.get('country_code', 'N/A')}
                """)
        
        st.markdown(f"""
        - **IPv4 Graph:** {upstream_data.get('ipv4_graph', 'N/A')}
        - **IPv6 Graph:** {upstream_data.get('ipv6_graph', 'N/A')}
        - **Combined Graph:** {upstream_data.get('combined_graph', 'N/A')}
        """)
    else:
        st.error("No data found")

def display_asn_peers(data):
    st.subheader("ASN Peers")
    if "data" in data:
        peer_data = data["data"]
        
        if 'ipv4_peers' in peer_data:
            st.markdown("**IPv4 Peers:**")
            for peer in peer_data['ipv4_peers']:
                st.markdown(f"""
                - **ASN:** {peer.get('asn', 'N/A')}
                - **Name:** {peer.get('name', 'N/A')}
                - **Description:** {peer.get('description', 'N/A')}
                - **Country Code:** {peer.get('country_code', 'N/A')}
                """)
        
        if 'ipv6_peers' in peer_data:
            st.markdown("**IPv6 Peers:**")
            for peer in peer_data['ipv6_peers']:
                st.markdown(f"""
                - **ASN:** {peer.get('asn', 'N/A')}
                - **Name:** {peer.get('name', 'N/A')}
                - **Description:** {peer.get('description', 'N/A')}
                - **Country Code:** {peer.get('country_code', 'N/A')}
                """)
    else:
        st.error("No data found")

def display_asn_prefixes(data):
    st.subheader("ASN Prefixes")
    if "data" in data:
        prefix_data = data["data"]
        
        if 'ipv4_prefixes' in prefix_data:
            st.markdown("**IPv4 Prefixes:**")
            for prefix in prefix_data['ipv4_prefixes']:
                st.markdown(f"""
                - **Prefix:** {prefix.get('prefix', 'N/A')}
                - **IP:** {prefix.get('ip', 'N/A')}
                - **CIDR:** {prefix.get('cidr', 'N/A')}
                - **ROA Status:** {prefix.get('roa_status', 'N/A')}
                - **Name:** {prefix.get('name', 'N/A')}
                - **Description:** {prefix.get('description', 'N/A')}
                - **Country Code:** {prefix.get('country_code', 'N/A')}
                """)
                if 'parent' in prefix and any(prefix['parent'].values()):
                    parent = prefix['parent']
                    st.markdown(f"""
                    **Parent Prefix:**
                    - **Prefix:** {parent.get('prefix', 'N/A')}
                    - **IP:** {parent.get('ip', 'N/A')}
                    - **CIDR:** {parent.get('cidr', 'N/A')}
                    - **RIR Name:** {parent.get('rir_name', 'N/A')}
                    - **Allocation Status:** {parent.get('allocation_status', 'N/A')}
                    """)
        
        if 'ipv6_prefixes' in prefix_data:
            st.markdown("**IPv6 Prefixes:**")
            for prefix in prefix_data['ipv6_prefixes']:
                st.markdown(f"""
                - **Prefix:** {prefix.get('prefix', 'N/A')}
                - **IP:** {prefix.get('ip', 'N/A')}
                - **CIDR:** {prefix.get('cidr', 'N/A')}
                - **ROA Status:** {prefix.get('roa_status', 'N/A')}
                - **Name:** {prefix.get('name', 'N/A')}
                - **Description:** {prefix.get('description', 'N/A')}
                - **Country Code:** {prefix.get('country_code', 'N/A')}
                """)
                if 'parent' in prefix and any(prefix['parent'].values()):
                    parent = prefix['parent']
                    st.markdown(f"""
                    **Parent Prefix:**
                    - **Prefix:** {parent.get('prefix', 'N/A')}
                    - **IP:** {parent.get('ip', 'N/A')}
                    - **CIDR:** {parent.get('cidr', 'N/A')}
                    - **RIR Name:** {parent.get('rir_name', 'N/A')}
                    - **Allocation Status:** {parent.get('allocation_status', 'N/A')}
                    """)
    else:
        st.error("No data found")

def display_asn_details(data):
    st.subheader("ASN Details")
    if "data" in data:
        asn_data = data["data"]
        st.markdown(f"""
        **ASN:** {asn_data['asn']}
        - **Name:** {asn_data.get('name', 'N/A')}
        - **Short Description:** {asn_data.get('description_short', 'N/A')}
        - **Full Description:** {', '.join(asn_data.get('description_full', []))}
        - **Country Code:** {asn_data.get('country_code', 'N/A')}
        - **Website:** {asn_data.get('website', 'N/A')}
        - **Email Contacts:** {', '.join(asn_data.get('email_contacts', []))}
        - **Abuse Contacts:** {', '.join(asn_data.get('abuse_contacts', []))}
        - **Looking Glass:** {asn_data.get('looking_glass', 'N/A')}
        - **Traffic Estimation:** {asn_data.get('traffic_estimation', 'N/A')}
        - **Traffic Ratio:** {asn_data.get('traffic_ratio', 'N/A')}
        - **Owner Address:** {', '.join(asn_data.get('owner_address', []))}
        """)

        if 'rir_allocation' in asn_data:
            rir = asn_data['rir_allocation']
            st.markdown(f"""
            **RIR Allocation:**
            - **RIR Name:** {rir.get('rir_name', 'N/A')}
            - **Country Code:** {rir.get('country_code', 'N/A')}
            - **Date Allocated:** {rir.get('date_allocated', 'N/A')}
            - **Allocation Status:** {rir.get('allocation_status', 'N/A')}
            """)

        if 'iana_assignment' in asn_data:
            iana = asn_data['iana_assignment']
            st.markdown(f"""
            **IANA Assignment:**
            - **Assignment Status:** {iana.get('assignment_status', 'N/A')}
            - **Description:** {iana.get('description', 'N/A')}
            - **WHOIS Server:** {iana.get('whois_server', 'N/A')}
            - **Date Assigned:** {iana.get('date_assigned', 'N/A')}
            """)

        st.markdown(f"**Date Updated:** {asn_data.get('date_updated', 'N/A')}")
    else:
        st.error("No data found")

st.title("BGPView CLI Web Interface")

option = st.selectbox("Select Query Type", 
                      ("Search Resources", "IP Details", "IX Details", "Prefix Details", 
                       "ASN Downstreams", "ASN Upstreams", "ASN Peers", "ASN Prefixes", "ASN Details"))

query = st.text_input("Enter your query")

json_output = st.checkbox("Display raw JSON output")

if st.button("Submit"):
    start_time = datetime.now()
    
    try:
        if option == "Search Resources":
            data = fetch_search_resources(query)
        elif option == "IP Details":
            data = fetch_ip_details(query)
        elif option == "IX Details":
            data = fetch_ix_details(int(query))
        elif option == "Prefix Details":
            try:
                prefix, length = query.split("/")
                data = fetch_prefix_details(prefix, length)
            except ValueError:
                st.error("Please enter the prefix in the format 'prefix/length'")
                data = None
        elif option == "ASN Downstreams":
            try:
                data = fetch_asn_downstreams(int(query))
            except ValueError:
                st.error("Please enter a valid ASN.")
                data = None
        elif option == "ASN Upstreams":
            try:
                data = fetch_asn_upstreams(int(query))
            except ValueError:
                st.error("Please enter a valid ASN.")
                data = None
        elif option == "ASN Peers":
            try:
                data = fetch_asn_peers(int(query))
            except ValueError:
                st.error("Please enter a valid ASN.")
                data = None
        elif option == "ASN Prefixes":
            data = fetch_asn_prefixes(int(query))
        elif option == "ASN Details":
            data = fetch_asn_details(int(query))
        else:
            data = None

        end_time = datetime.now()
        duration = end_time - start_time

        if data:
            if json_output:
                st.json(data)
            else:
                if option == "Search Resources":
                    display_search_resources(data)
                elif option == "IP Details":
                    display_ip_details(data)
                elif option == "IX Details":
                    display_ix_details(data)
                elif option == "Prefix Details":
                    display_prefix_details(data)
                elif option == "ASN Downstreams":
                    display_asn_downstreams(data)
                elif option == "ASN Upstreams":
                    display_asn_upstreams(data)
                elif option == "ASN Peers":
                    display_asn_peers(data)
                elif option == "ASN Prefixes":
                    display_asn_prefixes(data)
                elif option == "ASN Details":
                    display_asn_details(data)

            if option in ["ASN Prefixes", "ASN Downstreams", "ASN Upstreams", "ASN Peers", "Search Resources"]:
                if option == "ASN Prefixes":
                    st.subheader("Prefix Distribution")
                    plot_asn_prefixes(data)
                elif option == "ASN Downstreams":
                    st.subheader("Downstreams Distribution")
                    plot_asn_network(data, "ASN Downstreams Network", "ipv4_downstreams")
                elif option == "ASN Upstreams":
                    st.subheader("Upstreams Distribution")
                    plot_asn_network(data, "ASN Upstreams Network", "ipv4_upstreams")
                elif option == "ASN Peers":
                    st.subheader("Peers Distribution")
                    plot_asn_network(data, "ASN Peers Network", "ipv4_peers")
                elif option == "Search Resources":
                    st.subheader("Search Resources Distribution")
                    plot_search_resources(data)

            st.write(f"Query completed in: {duration}")
        else:
            st.error("Error fetching data")
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.sidebar.markdown("""
# To run the Streamlit app, save the code above to `streamlit_app.py`
# and run `streamlit run streamlit_app.py` in your terminal.
""")

# To run the Streamlit app, save the code above to streamlit_app.py
# and run `streamlit run streamlit_app.py` in your terminal.
