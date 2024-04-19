# https://github.com/leofurtadonyc/Network-Automation/wiki
import subprocess
import argparse
import sys

def run_script(script_path, args):
    """Run a script using Python's subprocess module with additional arguments."""
    try:
        command = ['python', script_path] + args
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"\nOutput from {script_path}:\n{result.stdout}\n")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        print("Output:", e.stdout.strip() if e.stdout else "No output")
        print("Error:", e.stderr.strip() if e.stderr else "No error information")
        sys.exit(1)

def get_as_set_from_peeringdb(asn):
    """Retrieve the AS-SET from PeeringDB using the ASN."""
    output = run_script('get-as-set.py', [str(asn)])
    print(f"PeeringDB output for ASN {asn}: {output}")  # Ensure all output is printed
    if "IRR as-set/route-set:" in output:
        as_set = output.split("IRR as-set/route-set: ")[1].split("\n")[0].strip()
        if as_set == "N/A":
            print("\nNo AS-SET registered for this ASN in PeeringDB; manual prefix validation required.")
            sys.exit(1)
        return as_set
    print("No AS-SET information found in output.")
    return None

def main():
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
    parser.add_argument("--as-set", type=str, default=None, help="Optional: AS-SET to use for expanding IP prefixes. If not provided, will attempt to retrieve from PeeringDB.")
    parser.add_argument("customer_name", type=str, help="Customer name for file and prefix naming.")
    args = parser.parse_args()

    if not args.as_set:
        args.as_set = get_as_set_from_peeringdb(args.asn)
    
    scripts = [
        ('get-whois.py', [str(args.asn), args.as_set]),
        ('get-as-rank.py', [str(args.asn)]),
        ('generate-customer-prefixes.py', [str(args.asn), args.as_set, args.customer_name]),
        ('generate-customer-routingpolicies.py', [str(args.asn), args.as_set, args.customer_name])
    ]

    """ Executing each script in sequence """
    for script_path, script_args in scripts:
        run_script(script_path, script_args)

if __name__ == "__main__":
    main()
