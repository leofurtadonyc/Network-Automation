# https://github.com/leofurtadonyc/Network-Automation/wiki
import subprocess
import argparse

def fetch_whois_data(query_type, query_value):
    """Fetch whois data for given type (ASN or AS-SET)."""
    command = ['whois', '-h', 'whois.radb.net', query_value]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Failed to fetch whois data: {e}"

def main():
    parser = argparse.ArgumentParser(description="Fetch WHOIS data for ASN and AS-SET.")
    parser.add_argument("asn", type=str, help="Autonomous System Number (ASN).")
    parser.add_argument("as_set", type=str, help="AS-SET name.")
    args = parser.parse_args()

    # Fetching WHOIS data for ASN
    asn_data = fetch_whois_data('asn', f'AS{args.asn}')
    print(f"WHOIS data for ASN {args.asn}:\n{asn_data}")

    # Fetching WHOIS data for AS-SET
    as_set_data = fetch_whois_data('as-set', args.as_set)
    print(f"WHOIS data for AS-SET {args.as_set}:\n{as_set_data}")

if __name__ == "__main__":
    main()
