#!/usr/bin/env python3
"""
A submission tool for IRR that sends an RPSL object via the HTTP API.

Usage:
    python irr_rpsl_submit.py [options] <file>

Options:
    -s, --server     IRR server hostname (default depends on --instance)
    -p, --port       IRR server port (default depends on --instance)
    --db-type        Target IRR database type: RADB or ALTDB (default: ALTDB)
    --instance       Select the target IRR instance:
                       "irrd"   - your own IRRd instance (defaults to 127.0.0.1; HTTP API on port 8080)
                       "altdb"  - ALTDB (default, whois.altdb.net:43)
                       "radb"   - RADB (defaults to whois.radb.net:43)
    -o, --override   Override password if required
"""

import argparse
import json
import sys
import requests

def submit_rpsl_change(api_url, rpsl_text, passwords, action=None):
    """
    Submits an RPSL object change to the IRRd HTTP API using POST for most actions,
    and DELETE if the action is "delete".

    Args:
        api_url (str): The API endpoint URL.
        rpsl_text (str): The complete RPSL object as a string.
        passwords (list): List of passwords for authentication.
        action (str, optional): The action to perform, e.g. "delete".
        
    Returns:
        dict: JSON response from the API.
    """
    payload = {
        "objects": [{"object_text": rpsl_text}],
        "passwords": passwords
    }
    # If the action is delete, use HTTP DELETE.
    if action and action.lower() == "delete":
        method = requests.delete
    else:
        method = requests.post

    try:
        response = method(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "response": response.text if response else "No response"}

def main():
    parser = argparse.ArgumentParser(
        description="Submit an RPSL object to a chosen IRR server using the HTTP API."
    )
    parser.add_argument("file", help="File containing the RPSL object to submit (plain text or JSON)")
    parser.add_argument(
        "-s", "--server",
        default=None,
        help="IRR server hostname (overrides the default for the selected instance)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=None,
        help="IRR server port (overrides the default for the selected instance)"
    )
    parser.add_argument(
        "--db-type",
        choices=["RADB", "ALTDB"],
        default="ALTDB",
        help="Target IRR database type (default: ALTDB)"
    )
    parser.add_argument(
        "--instance",
        choices=["irrd", "altdb", "radb"],
        default="altdb",
        help="Select the target IRR instance. 'irrd' defaults to 127.0.0.1 (HTTP API on port 8080), 'altdb' to whois.altdb.net:43, and 'radb' to whois.radb.net:43 (default: altdb)"
    )
    parser.add_argument(
        "-o", "--override",
        help="Override password, if required"
    )
    args = parser.parse_args()

    # Set default server and port based on the chosen instance.
    if args.instance == "irrd":
        default_server, default_port = "127.0.0.1", 8043  # Raw TCP default, but we override for HTTP API.
    elif args.instance == "radb":
        default_server, default_port = "whois.radb.net", 43
    else:  # altdb
        default_server, default_port = "whois.altdb.net", 43

    server = args.server if args.server is not None else default_server
    port = args.port if args.port is not None else default_port

    # For the HTTP API, if instance is irrd, force port 8080.
    if args.instance == "irrd":
        port = 8080

    api_url = f"http://{server}:{port}/v1/submit/"

    # Read the file content.
    try:
        with open(args.file, "r") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
        sys.exit(1)

    # Parse file content as JSON if possible; otherwise assume plain text.
    action = None
    passwords = []
    rpsl_text = file_content
    try:
        parsed = json.loads(file_content)
        if isinstance(parsed, dict):
            action = parsed.get("action", None)
            if "data" in parsed:
                data = parsed["data"]
                if "object_text" in data:
                    rpsl_text = data["object_text"]
                if "passwords" in data:
                    passwords = data["passwords"]
    except json.JSONDecodeError:
        # Not JSON; assume plain text.
        pass

    if args.override:
        passwords = [args.override]

    print(f"Submitting RPSL object from '{args.file}' to {server}:{port} "
          f"(Instance: {args.instance}, DB type: {args.db_type}, Action: {action})...")
    result = submit_rpsl_change(api_url, rpsl_text, passwords, action)
    print("Response from server:")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
