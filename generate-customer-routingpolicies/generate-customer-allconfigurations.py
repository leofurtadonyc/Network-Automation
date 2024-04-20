"""
Module: Generate Customer Routing Policies
https://github.com/leofurtadonyc/Network-Automation/wiki

This script automates the creation of customer-specific BGP routing policies based on predefined templates and customer input.
It integrates best practices from MANRS (Mutually Agreed Norms for Routing Security) to enhance network security and efficiency.

The script fetches necessary ASN and AS-SET information using external APIs such as PeeringDB, RADB, and AS Rank, and
generates routing policies in various router vendor syntaxes using bgpq3.

Outputs:
- Prefix lists and AS-Path lists are generated and stored in `generated_prefixes/`.
- Routing policies are customized per customer and vendor requirements and saved in `generated_policies/`.
- Jinja2 templates are used for the routing policy generation. Ensure to modify them to suit your needs.

Requirements:
- Python 3.6+
- External libraries: subprocess, os, time, argparse
- External tools: bgpq3 for generating prefix lists and AS-Path lists, whois for whois checking.
"""

import subprocess
import argparse
import sys
import os
import time

def run_script(script_path, args):
    """Run scripts using Python's subprocess module with additional arguments."""
    try:
        command = ['python', script_path] + args
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"\nOutput from {script_path}:\n{result.stdout}")
        if result.stderr:
            print(f"Error from {script_path}:\n{result.stderr}")
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        sys.exit(1)

def extract_as_set_name(output):
    """Extract the AS-SET name from the WHOIS output."""
    lines = output.split('\n')
    for line in lines:
        if line.startswith('as-set:'):
            return line.split(':')[1].strip()
    return "AS-SET not found"

def get_as_set_from_peeringdb(asn):
    """Retrieve the AS-SET from PeeringDB using the ASN."""
    output, _ = run_script('get-as-set.py', [str(asn)])
    as_set_found = "No"  # Default to no AS-SET found
    if "IRR as-set/route-set:" in output:
        as_set = output.split("IRR as-set/route-set: ")[1].split("\n")[0].strip()
        if as_set == "N/A":
            print("\nNo AS-SET registered for this ASN in PeeringDB; manual prefix validation required.")
            sys.exit(1)
        as_set_found = "Yes"
        return as_set, as_set_found
    print("No AS-SET information found in output.")
    return None, as_set_found

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Generate BGP customer service activation configurations. "
                    "This script orchestrates the generation of BGP customer service activation configurations. "
                    "This automation encompasses your routing policies and BGP session configurations for your customer cone. "
                    "It incorporates some of the best practices recommended by MANRS, such as prefix and AS-Path filtering. "
                    "This script does that by invoking five other scripts in a specific order. "
                    "The package fetches ASN and AS-SET information using PeeringDB, Whois, and AS Rank APIs and display these outputs to the operator. "
                    "It then uses the reported AS-SET to generate prefix lists, AS-Path lists, and routing policies across multiple supported vendor syntaxes using bgpq3. "
                    "Outputs are stored in generated_prefixes/ and generated_policies/ folders. "
                    "Templates are located in templates/. Modify them to suit your needs. "
                    "This script requires Whois and BGPQ3 to run properly. ",
        epilog="Example usage: python3 generate-customer-allconfigurations.py 16509 AS16509:AS-AMAZON AMAZON"
    )
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    parser.add_argument("--as-set", type=str, default=None, help="Optional: AS-SET to use for expanding IP prefixes.")
    parser.add_argument("customer_name", type=str, help="Customer name for file and prefix naming.")
    args = parser.parse_args()

    as_set_found_in_peeringdb = "Not Searched"

    if not args.as_set:
        args.as_set, as_set_found_in_peeringdb = get_as_set_from_peeringdb(args.asn)

    scripts = [
        ('get-whois.py', [str(args.asn), args.as_set]),
        ('get-as-rank.py', [str(args.asn)]),
        ('generate-customer-prefixes.py', [str(args.asn), args.as_set, args.customer_name]),
        ('generate-customer-routingpolicies.py', [str(args.asn), args.as_set, args.customer_name])
    ]

    for script_path, script_args in scripts:
        stdout, stderr = run_script(script_path, script_args)
        if script_path == 'get-whois.py':
            as_set_name = extract_as_set_name(stdout)

    print("\n--- Execution Report ---")
    print(f"User: {os.getlogin()}")
    print(f"AS-SET found in PeeringDB: {as_set_found_in_peeringdb}")
    print(f"AS-SET found in RADB: {as_set_name}")
    if as_set_name == "AS-SET not found":
        print("\nWARNING: Prefix-lists were NOT generated and as-path lists will deny everything because the customer's AS-SET was not found in RADB.")
    print(f"Total Execution Time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
