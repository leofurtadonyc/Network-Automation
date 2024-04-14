# https://github.com/leofurtadonyc/Network-Automation/wiki
import subprocess
import argparse

def run_script(script_path, args):
    """This script runs all the other necessary scripts to build the customer's configurations."""
    """Run a script using Python's subprocess module with additional arguments."""
    try:
        command = ['python3', script_path] + args
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Output from {script_path}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Error:", e.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="This script orchestrates the generation of BGP customer service activation configurations. "
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
    parser.add_argument("as_set", type=str, help="AS-SET to use for expanding IP prefixes.")
    parser.add_argument("customer_name", type=str, help="Customer name for file and prefix naming.")
    args = parser.parse_args()

    scripts = [
        ('get-as-set.py', [str(args.asn)]),
        ('get-whois.py', [str(args.asn), args.as_set]),
        ('get-as-rank.py', [str(args.asn)]),
        ('generate-customer-prefixes.py', [str(args.asn), args.as_set, args.customer_name]),
        ('generate-customer-routingpolicies.py', [str(args.asn), args.as_set, args.customer_name])
    ]

    for script_path, script_args in scripts:
        run_script(script_path, script_args)

if __name__ == "__main__":
    main()
