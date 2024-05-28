import os
import pyfiglet
import requests
import argparse
import re
from datetime import datetime
import socket

IANA_URL = "https://www.wireshark.org/download/automated/data/manuf"

def print_banner():
    ascii_banner = pyfiglet.figlet_format("MAC FINDER")
    print(ascii_banner)
    print("https://github.com/leofurtadonyc/Network-Automation")

def fetch_iana_mac_vendors():
    try:
        response = requests.get(IANA_URL)
        response.raise_for_status()
        iana_data = response.text
        mac_vendors = {}
        for line in iana_data.splitlines():
            if line and not line.startswith("#"):
                parts = re.split(r'\s{2,}', line)
                if len(parts) > 1:
                    prefix = parts[0].replace("-", ":").lower()
                    vendor = parts[1]
                    mac_vendors[prefix] = vendor
        return mac_vendors
    except requests.RequestException:
        print("Failed to fetch IANA MAC vendors list.")
        return None

def get_mac_vendor(mac, mac_vendors):
    mac_prefix = ":".join(mac.split(":")[:3]).lower()
    return mac_vendors.get(mac_prefix, "Unknown")

def normalize_mac(mac):
    mac = mac.lower()
    mac = mac.replace("-", ":").replace(".", "").replace(" ", "")
    if len(mac) == 12:
        mac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))
    elif len(mac) == 14 and mac.count(":") == 2:
        mac = mac.replace(":", "")
        mac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))
    return mac

def validate_args():
    parser = argparse.ArgumentParser(description="MAC Address Vendor Finder")
    parser.add_argument("mac", help="MAC address to find the vendor for")
    args = parser.parse_args()

    normalized_mac = normalize_mac(args.mac)
    if re.match(r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$', normalized_mac):
        return normalized_mac
    else:
        print("Invalid MAC address format.")
        exit()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unknown"

def main():
    print_banner()
    mac = validate_args()
    user = os.getlogin()
    source_ip = get_local_ip()
    start_time = datetime.now()
    print("-" * 50)
    print(f"Querying MAC address vendor for: {mac} from Source: {source_ip} by user: {user}")
    print("Query started at: " + str(start_time))
    print("-" * 50)

    mac_vendors = fetch_iana_mac_vendors()
    if mac_vendors:
        vendor = get_mac_vendor(mac, mac_vendors)
        print(f"MAC Address: {mac} Vendor: {vendor}")

    end_time = datetime.now()
    duration = end_time - start_time
    print("-" * 50)
    print(f"Query completed in: {duration}")
    print("-" * 50)

if __name__ == "__main__":
    main()
