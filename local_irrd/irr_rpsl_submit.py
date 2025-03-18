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
import ipaddress
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
    
    If the handle already appears valid (no spaces and contains a dash), return uppercase.
    """
    if " " not in handle and "-" in handle:
        return handle.upper()
    else:
        new_handle = handle.replace(" ", "-")
        allowed = set(string.ascii_letters + string.digits + "-")
        new_handle = "".join(ch for ch in new_handle if ch in allowed)
        return new_handle.upper()

def process_txt_file(txt_filename):
    """
    Processes a human-friendly .txt file.
    Expects the first few non-comment, non-empty lines to declare header metadata:
      - "action:" is required.
      - Optionally "password:" and "multiple_routes:" may appear.
    The remainder of the file forms the RPSL object text.
    
    It automatically sanitizes the values for "admin-c" and "tech-c" fields.
    
    Returns a tuple: (json_dict, object_type, identifier)
    where json_dict is the JSON representation to be submitted.
    """
    with open(txt_filename, "r") as f:
        lines = f.readlines()

    # Remove trailing whitespace.
    lines = [line.rstrip() for line in lines]

    # Filter out empty and comment lines.
    non_comment_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    if not non_comment_lines:
        raise Exception("No non-comment content found in file.")

    # Initialize header values.
    action = None
    password = None
    multiple_routes = False

    header_keys = {"action", "password", "multiple_routes"}
    content_start = 0
    for i, line in enumerate(non_comment_lines):
        parts = line.split(":", 1)
        if len(parts) == 2:
            key = parts[0].strip().lower()
            if key in header_keys:
                if key == "action":
                    action = parts[1].strip()
                elif key == "password":
                    password = parts[1].strip()
                elif key == "multiple_routes":
                    value = parts[1].strip().lower()
                    multiple_routes = (value == "true")
                continue
        content_start = i
        break

    # The remaining lines form the RPSL object text.
    rpsl_text_lines = non_comment_lines[content_start:]
    if not rpsl_text_lines:
        raise Exception("No RPSL content found after header.")

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
        "action": action.lower() if action else "",
        "data": {
            "object_text": rpsl_text,
            "identifier": identifier,
            "passwords": [password] if password else []
        },
        "status": "pending"
    }
    # Store the multiple_routes flag at top level (outside "data")
    json_dict["multiple_routes"] = multiple_routes

    return json_dict, object_type, identifier

def generate_route_subobjects(rpsl_text, object_type):
    """
    For a route or route6 object, generates a list of route object texts that includes:
      - The original object.
      - Additional objects subdividing the network.
    
    For IPv4 ("route"), subdivisions are generated from (original.prefixlen + 1) up to /24.
    For IPv6 ("route6"), subdivisions are generated from (original.prefixlen + 1) up to /36.
    If the original prefix is already at the maximum (or, for IPv6, if it is greater than /36),
    an error is raised for IPv6 or no subdivisions are generated for IPv4.
    
    Returns a list of RPSL object texts.
    """
    import ipaddress

    lines = rpsl_text.splitlines()
    new_objects = []
    # Determine the keyword based on object_type.
    keyword = "route6:" if object_type == "route6" else "route:"
    # Find the route line.
    route_line = None
    for line in lines:
        if line.lower().startswith(keyword):
            route_line = line
            break
    if route_line is None:
        raise Exception(f"No {keyword} line found in RPSL text.")
    parts = route_line.split(":", 1)
    if len(parts) != 2:
        raise Exception("Invalid route line format.")
    route_val = parts[1].strip()
    try:
        if object_type == "route6":
            network = ipaddress.IPv6Network(route_val, strict=False)
            max_prefix = 36
        else:
            network = ipaddress.IPv4Network(route_val, strict=False)
            max_prefix = 24
    except Exception as e:
        raise Exception(f"Error parsing route value '{route_val}': {e}")

    # For route6, ensure that the original prefix is not longer than /36.
    if object_type == "route6" and network.prefixlen > max_prefix:
        raise Exception(f"multiple_routes not allowed for {object_type} prefixes longer than /{max_prefix}.")

    # Always include the original object.
    new_objects.append(rpsl_text)
    
    # If the original prefix is less than the maximum, generate subdivisions.
    if network.prefixlen < max_prefix:
        for new_plen in range(network.prefixlen + 1, max_prefix + 1):
            for subnet in network.subnets(new_prefix=new_plen):
                new_lines = []
                for line in lines:
                    if line.lower().startswith(keyword):
                        new_lines.append(f"{keyword:<12} {subnet}")
                    else:
                        new_lines.append(line)
                new_objects.append("\n".join(new_lines))
    return new_objects

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

def submit_rpsl_change(api_url, objects_list, passwords, action=None):
    """
    Submits one or more RPSL object changes to the IRRd HTTP API.
    Uses POST for most actions and DELETE if action is "delete".

    Args:
        api_url (str): The API endpoint URL.
        objects_list (list): A list of RPSL object texts.
        passwords (list): List of passwords for authentication.
        action (str, optional): The action to perform, e.g., "delete".

    Returns:
        dict: JSON response from the API.
    """
    payload = {
        "objects": [{"object_text": obj} for obj in objects_list],
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
        default_server, default_port = "127.0.0.1", 8043  # Raw TCP default, but override for HTTP API.
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
        base_rpsl_text = json_dict["data"]["object_text"]
        action = json_dict.get("action", None)
        passwords = json_dict["data"].get("passwords", [])
        # Retrieve the multiple_routes flag from top-level.
        multiple_routes = json_dict.get("multiple_routes", False)
        if multiple_routes and object_type in ("route", "route6"):
            try:
                generated_objects = generate_route_subobjects(base_rpsl_text, object_type)
                # Add generated objects to JSON for record-keeping.
                json_dict["generated_objects"] = generated_objects
                objects_to_submit = generated_objects
            except Exception as e:
                print(f"Error generating multiple route objects: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            objects_to_submit = [base_rpsl_text]
    else:
        try:
            with open(args.file, "r") as f:
                file_content = f.read()
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
        action = None
        passwords = []
        base_rpsl_text = file_content
        try:
            parsed = json.loads(file_content)
            if isinstance(parsed, dict):
                action = parsed.get("action", None)
                if "data" in parsed:
                    data = parsed["data"]
                    if "object_text" in data:
                        base_rpsl_text = data["object_text"]
                    if "passwords" in data:
                        passwords = data["passwords"]
        except json.JSONDecodeError:
            pass
        objects_to_submit = [base_rpsl_text]

    if args.override:
        passwords = [args.override]

    print(f"Submitting RPSL object(s) from '{args.file}' to {server}:{port} "
          f"(Instance: {args.instance}, DB type: {args.db_type}, Action: {action})...")
    result = submit_rpsl_change(api_url, objects_to_submit, passwords, action)
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
