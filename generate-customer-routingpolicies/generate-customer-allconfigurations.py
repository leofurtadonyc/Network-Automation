import subprocess
import argparse

def run_script(script_path, args):
    """This script runs all the other necessary scripts to build the customer's configurations."""
    """Run a script using Python's subprocess module with additional arguments."""
    try:
        # Building the command with arguments
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
    parser = argparse.ArgumentParser(description="Run scripts in sequence with shared arguments.")
    parser.add_argument("asn", type=int, help="Autonomous System Number (ASN).")
    parser.add_argument("as_set", type=str, help="AS-SET to use for expanding IP prefixes.")
    parser.add_argument("customer_name", type=str, help="Customer name for file and prefix naming.")
    args = parser.parse_args()

    # List of scripts to run and their corresponding arguments
    scripts = [
        ('get-as-set.py', [str(args.asn)]),  # Only the ASN for the first script
        ('generate-customer-prefixes.py', [str(args.asn), args.as_set, args.customer_name]),
        ('generate-customer-routingpolicies.py', [str(args.asn), args.as_set, args.customer_name])
    ]

    # Running scripts in sequence
    for script_path, script_args in scripts:
        run_script(script_path, script_args)

if __name__ == "__main__":
    main()
