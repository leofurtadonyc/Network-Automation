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
                       "altdb"  - ALTDB (defaults to whois.altdb.net:43)
                       "radb"   - RADB (defaults to whois.radb.net:43)
                       "tc"     - TC IRR (defaults to whois.tc.net:43)
    -o, --override   Override password if required
"""

import argparse
import json
import os
import sys
import requests
import string

def sanitize_nic_handle(handle):
    """
    Transform the given handle into a valid NIC handle.
    
    If the handle contains spaces, replace them with dashes,
    remove any characters that are not alphanumeric or dash,
    and convert the result to uppercase.
    
    If the handle already has no spaces and includes a dash,
    simply return its uppercase version.
    """
    # If no spaces and already contains a dash, assume it's valid.
    if " " not in handle and "-" in handle:
        return handle.upper()
    else:
        # Replace spaces with dashes.
        new_handle = handle.replace(" ", "-")
        # Remove any characters that are not alphanumeric or dash.
        allowed = set(string.ascii_letters + string.digits + "-")
        new_handle = "".join(ch for ch in new_handle if ch in allowed)
        return new_handle.upper()

def process_txt_file(txt_filename):
    """
    Processes a human-friendly .txt file.
    Expects the first non-comment, non-empty line to declare the action (e.g. "action: add").
    The remainder of the file should contain the RPSL object text with fields supported by IRRd/ALTDB.
    
    It will automatically sanitize the values for "admin-c" and "tech-c" fields.
    
    Returns a tuple: (json_dict, object_type, identifier)
    where json_dict is the JSON representation to be submitted.
    """
    with open(txt_filename, "r") as f:
        lines = f.readlines()

    # Remove newline characters and trailing whitespace.
    lines = [line.rstrip() for line in lines]

    # Filter out empty lines and comment lines (starting with "#")
    non_comment_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    if not non_comment_lines:
        raise Exception("No non-comment content found in file.")

    # First non-comment line declares the action.
    first_line = non_comment_lines[0].strip()
    if first_line.lower().startswith("action:"):
        action = first_line.split(":", 1)[1].strip()
    else:
        action = first_line.strip()

    # The remainder of the lines form the RPSL object text.
    rpsl_text_lines = non_comment_lines[1:]
    if not rpsl_text_lines:
        raise Exception("No RPSL content found after the action declaration.")

    # Sanitize admin-c and tech-c fields.
    processed_lines = []
    for line in rpsl_text_lines:
        lower_line = line.lower()
        if lower_line.startswith("admin-c:"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                handle = parts[1].strip()
                sanitized = sanitize_nic_handle(handle)
                processed_lines.append(f"{parts[0]}: {sanitized}")
            else:
                processed_lines.append(line)
        elif lower_line.startswith("tech-c:"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                handle = parts[1].strip()
                sanitized = sanitize_nic_handle(handle)
                processed_lines.append(f"{parts[0]}: {sanitized}")
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    rpsl_text = "\n".join(processed_lines).strip()

    # Derive the object type and identifier from the first non-empty RPSL line.
    rpsl_non_empty = [line for line in rpsl_text.splitlines() if line.strip()]
    if not rpsl_non_empty:
        raise Exception("No RPSL lines found after processing.")
    first_rpsl_line = rpsl_non_empty[0].strip()
    if ":" not in first_rpsl_line:
        raise Exception("The first RPSL line is not in the expected 'attribute: value' format.")
    attr, value = first_rpsl_line.split(":", 1)
    object_type = attr.strip().lower()  # e.g., "aut-num", "as-set", "route", "route6"
    identifier = value.strip()           # Typically the key value for the object

    json_dict = {
        "object_type": object_type,
        "action": action.lower(),
        "data": {
            "object_text": rpsl_text,
            "identifier": identifier,
            "passwords": []  # To be filled via command-line override if needed.
        },
        "status": "pending"
    }
    return json_dict, object_type, identifier

def save_json_object(json_data, object_type, identifier):
    """
    Save the JSON data to a file inside the "objects/" folder.
    The filename is derived from the object type and identifier.
    """
    if not os.path.exists("objects"):
        os.makedirs("objects")
    safe_identifier = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in identifier)
    filename = os.path.join("objects", f"{object_type}_{safe_identifier}.json")
    with open(filename, "w") as f:
        json.dump(json_data, f, indent=4)
    return filename

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
    parser.add_argument("file", help="File containing the RPSL object to submit (full path; can be plain text, JSON, or .txt)")
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
        choices=["irrd", "altdb", "radb", "tc"],
        default="altdb",
        help="Select the target IRR instance. 'irrd' defaults to 127.0.0.1 (HTTP API on port 8080), 'altdb' to whois.altdb.net:43, 'radb' to whois.radb.net:43, and 'tc' to whois.tc.net:43 (default: altdb)"
    )
    parser.add_argument(
        "-o", "--override",
        help="Override password, if required"
    )
    args = parser.parse_args()

    # Set default server and port based on the chosen instance.
    if args.instance == "irrd":
        default_server, default_port = "127.0.0.1", 8043  # Raw TCP default, but we'll override for HTTP API.
    elif args.instance == "radb":
        default_server, default_port = "whois.radb.net", 43
    elif args.instance == "tc":
        default_server, default_port = "whois.tc.net", 43
    else:
        default_server, default_port = "whois.altdb.net", 43

    server = args.server if args.server is not None else default_server
    port = args.port if args.port is not None else default_port

    # For the HTTP API, if instance is irrd, force port 8080.
    if args.instance == "irrd":
        port = 8080

    api_url = f"http://{server}:{port}/v1/submit/"

    file_ext = os.path.splitext(args.file)[1].lower()
    if file_ext == ".txt":
        txt_filename = args.file
        try:
            json_dict, object_type, identifier = process_txt_file(txt_filename)
        except Exception as e:
            print(f"Error processing TXT file: {e}", file=sys.stderr)
            sys.exit(1)
        json_filename = save_json_object(json_dict, object_type, identifier)
        print(f"Generated JSON file: {json_filename}")
        rpsl_text = json_dict["data"]["object_text"]
        action = json_dict.get("action", None)
        passwords = json_dict["data"].get("passwords", [])
    else:
        try:
            with open(args.file, "r") as f:
                file_content = f.read()
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
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
            pass

    if args.override:
        passwords = [args.override]

    print(f"Submitting RPSL object from '{args.file}' to {server}:{port} "
          f"(Instance: {args.instance}, DB type: {args.db_type}, Action: {action})...")
    result = submit_rpsl_change(api_url, rpsl_text, passwords, action)
    print("Response from server:")
    print(json.dumps(result, indent=4))

    # If submission was successful and the input was a TXT file,
    # update the generated JSON file's "status" field to "submitted".
    if file_ext == ".txt" and result.get("summary", {}).get("successful", 0) > 0:
        json_dict["status"] = "submitted"
        with open(json_filename, "w") as f:
            json.dump(json_dict, f, indent=4)
        print(f"Updated JSON file '{json_filename}' with status 'submitted'.")

if __name__ == "__main__":
    main()
