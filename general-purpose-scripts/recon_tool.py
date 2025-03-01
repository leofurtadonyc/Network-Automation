#!/usr/bin/env python3
import argparse
import subprocess
import webbrowser
import requests
import json

def run_command(cmd):
    """Run an external command and print its output.
       If the command fails (specifically for the decoy scan),
       provide extra insight about needing root privileges."""
    print(f"\n[*] Running command: {' '.join(cmd)}\n")
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        print(result.stdout)
        if result.stderr:
            print("[!] STDERR:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed: {e}")
        # If it's a decoy scan command, provide an additional explanation.
        if "nmap" in cmd[0] and "-sS" in cmd and "-D" in cmd:
            print("[!] Insight: The '-sS' decoy scan requires root privileges. "
                  "Try running the script with sudo (Linux/Mac) or as Administrator (Windows).")
    return

def get_bgp_info(target):
    """Fetch BGP information from bgp.he.net for the given IP address and extract key details."""
    url = f"https://bgp.he.net/ip/{target}"
    print(f"\n[*] Querying BGP information from {url}\n")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main header (should be the IP address)
            header = soup.find("h1")
            header_text = header.get_text(strip=True) if header else target
            print("[*] IP:", header_text)
            
            # Look for any string indicating hostname resolution ("resolves to")
            resolved_tag = soup.find(string=lambda s: "resolves to" in s)
            if resolved_tag:
                print("[*] " + resolved_tag.strip())
            else:
                print("[*] No hostname resolution info found.")
            
            # Extract "Announced By" table
            announced_table = None
            for table in soup.find_all("table"):
                if "Announced By" in table.get_text():
                    announced_table = table
                    break
            if announced_table:
                rows = announced_table.find_all("tr")
                print("\n[*] Announced By Information:")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    cell_text = [cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True)]
                    if cell_text:
                        print(" | ".join(cell_text))
            else:
                print("[*] No 'Announced By' information found.")
        else:
            print(f"[!] Error: Received status code {response.status_code} from bgp.he.net.")
    except requests.RequestException as e:
        print(f"[!] Error retrieving data from bgp.he.net: {e}")

def get_whois_info(target):
    """Fetch WHOIS information using the system's whois utility or, if unavailable, the python-whois library."""
    print(f"\n[*] Performing WHOIS lookup for {target}...\n")
    try:
        # Try the whois command
        result = subprocess.run(["whois", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        output = result.stdout.strip()
        if output:
            print(output)
        else:
            print("[!] whois command did not return any output.")
    except Exception as e:
        print(f"[!] whois command failed: {e}. Trying python-whois library...")
        try:
            import whois
            w = whois.whois(target)
            print(w)
        except Exception as e2:
            print(f"[!] python-whois lookup failed: {e2}")

def get_asn_from_ip(target):
    """Fetch ASN information using an online API."""
    url = f"https://api.hackertarget.com/aslookup/?q={target}"
    print(f"\n[*] Querying ASN information from {url}\n")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            asn_line = response.text.strip()
            if asn_line.lower().startswith("error"):
                print("[!] Error fetching ASN information: " + asn_line)
                return None
            print(f"[*] ASN info: {asn_line}")
            return asn_line
        else:
            print(f"[!] Error: Received status code {response.status_code} from the ASN lookup API.")
            return None
    except requests.RequestException as e:
        print(f"[!] Exception during ASN lookup: {e}")
        return None

def get_peeringdb_info(asn_info):
    """Fetch PeeringDB information for the given ASN."""
    try:
        # Parse the ASN info string to extract just the ASN number (second element)
        # Format: "IP","ASN","CIDR","Organization"
        parts = asn_info.split(',')
        if len(parts) >= 2:
            # Extract the ASN number (remove quotes if present)
            asn_num = parts[1].strip('"')
            
            url = f"https://api.peeringdb.com/api/net?asn={asn_num}"
            print(f"\n[*] Querying PeeringDB information from {url}\n")
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Pretty-print the JSON response
                print(json.dumps(data, indent=4))
            else:
                print(f"[!] Error: Received status code {response.status_code} from the PeeringDB API.")
        else:
            print("[!] Error: Could not parse ASN information correctly.")
    except requests.RequestException as e:
        print(f"[!] Error retrieving PeeringDB information: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Network Recon Tool: Executes Nmap scans, BGP lookup (bgp.he.net), WHOIS lookup, ASN lookup, PeeringDB query, and opens VPN check URLs."
    )
    parser.add_argument("target", help="Target IP address or domain")
    parser.add_argument("--os-scan", action="store_true",
                        help="Run OS detection scan (nmap -O)")
    parser.add_argument("--bgp", action="store_true",
                        help="Perform BGP lookup from bgp.he.net for the target IP")
    parser.add_argument("--whois", action="store_true",
                        help="Perform WHOIS lookup using the whois utility or python-whois library")
    parser.add_argument("--vpn-check", action="store_true",
                        help="Open VPN/IP check URLs in the browser")
    parser.add_argument("--decoy-scan", action="store_true",
                        help="Run nmap stealth scan with decoys (nmap -sS -D RND:10)")
    parser.add_argument("--peeringdb", action="store_true",
                        help="Fetch PeeringDB information for the ASN associated with the target IP")
    parser.add_argument("--all", action="store_true",
                        help="Run all available tasks")
    args = parser.parse_args()

    # If --all is selected, enable all tasks.
    if args.all:
        args.os_scan = args.bgp = args.whois = args.vpn_check = args.decoy_scan = args.peeringdb = True

    # OS Detection Scan with Nmap (-O)
    if args.os_scan:
        print("[*] Starting OS detection scan with nmap...")
        run_command(["nmap", "-O", args.target])

    # BGP lookup from bgp.he.net (replaces previous WHOIS lookup)
    if args.bgp:
        print("[*] Performing BGP lookup using bgp.he.net...")
        get_bgp_info(args.target)

    # WHOIS lookup using the whois utility or python-whois library
    if args.whois:
        get_whois_info(args.target)

    # Open VPN/IP Check URLs in the default web browser.
    if args.vpn_check:
        print("[*] Opening VPN/IP check URLs...")
        url1 = f"https://www.ipqualityscore.com/vpn-ip-address-check/lookup/{args.target}"
        url2 = "https://whoer.net/checkwhois"
        print(f"Opening: {url1}")
        webbrowser.open(url1)
        print(f"Opening: {url2}")
        webbrowser.open(url2)

    # Stealth scan with decoys (nmap -sS -D RND:10)
    if args.decoy_scan:
        print("[*] Starting stealth scan with decoys...")
        run_command(["nmap", "-sS", "-D", "RND:10", args.target])

    # ASN and PeeringDB lookup
    if args.peeringdb:
        print("[*] Fetching ASN and PeeringDB information...")
        asn = get_asn_from_ip(args.target)
        if asn:
            get_peeringdb_info(asn)
        else:
            print("[!] ASN information could not be retrieved; skipping PeeringDB query.")

if __name__ == "__main__":
    main()
