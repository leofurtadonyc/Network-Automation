#!/usr/bin/env python
import json
import re
import sys
import yaml
import argparse

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import pyfiglet

# Import your existing modules
from devices_inventory import DeviceInventory
from command_mapper import get_command
from netmiko_executor import execute_command
from llm_interface import get_llm
from explanation_generator import generate_explanation

# Import health-check functions from your healthcheck module.
# These functions are defined in your healthcheck.py script.
from healthcheck import run_health_check_for_device, print_health_check_results

def parse_operator_query(query, llm):
    """
    Use the LLM to parse the network operator query into a JSON intent.
    The expected JSON format includes an action which now may be one of:
      - show_interfaces_down
      - get_mgmt_ip
      - show_ospf_routes_count
      - check_route
      - show_uptime
      - show_ospf_neighbors_full
      - healthcheck
    And, if action=="healthcheck", a "target_device" field which can be a single device,
    a comma-separated list of devices, or "all".
    
    The prompt instructs the LLM to output ONLY valid JSON.
    """
    prompt = (
        "You are an assistant that translates network operator queries into a JSON object in the following format:\n"
        '{ "action": <action>, "target_device": <device name or comma-separated list or "all">, "destination_ip": <optional> }\n'
        "Possible actions include: show_interfaces_down, get_mgmt_ip, show_ospf_routes_count, check_route, "
        "show_uptime, show_ospf_neighbors_full, healthcheck.\n\n"
        f"Query: {query}\n\n"
        "JSON:"
    )
    response = llm.invoke(prompt)
    # Uncomment the next line to debug the raw LLM response.
    # print("LLM raw response:", response)
    
    # Extract the first valid JSON object using regex.
    match = re.search(r'(\{.*\})', response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            structured_intent = json.loads(json_str)
            return structured_intent
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
    print("Error parsing LLM response, defaulting to empty intent.")
    return {}

def run_healthcheck_for_targets(target_spec, inventory, baseline_path="healthcheck_baseline.yaml"):
    """
    Given a target specification from the LLM (which might be "all" or a comma-separated list),
    load the baseline file, identify the corresponding devices from the inventory, and run the health check.
    """
    # Load the baseline YAML.
    try:
        with open(baseline_path, "r") as f:
            baseline_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading baseline file: {e}")
        return

    # Determine which devices to check.
    devices_to_check = []
    if target_spec.lower() == "all":
        for dev in baseline_data:
            device_obj = inventory.get_device_by_name(dev)
            if device_obj:
                devices_to_check.append(device_obj)
            else:
                print(f"Warning: Device '{dev}' defined in baseline not found in inventory.")
    else:
        # Assume comma-separated list.
        device_names = [name.strip() for name in target_spec.split(",")]
        for dev in device_names:
            device_obj = inventory.get_device_by_name(dev)
            if device_obj:
                devices_to_check.append(device_obj)
            else:
                print(f"Device '{dev}' not found in inventory.")
    
    # Run health check for each device.
    for device in devices_to_check:
        baseline_for_device = baseline_data.get(device.name)
        if not baseline_for_device:
            print(f"No baseline defined for device '{device.name}'. Skipping health check for this device.")
            continue
        print(f"\nPerforming health check on device {device.name} ({device.mgmt_address})...")
        results = run_health_check_for_device(device, baseline_for_device)
        print_health_check_results(device.name, results)
        print("\n" + "-" * 80 + "\n")

def main_cli():
    # Print a banner using pyfiglet.
    banner = pyfiglet.figlet_format("ChatNOC")
    print(banner)
    print("Welcome to ChatNOC interactive shell. Type 'exit' or 'quit' to exit.\n")
    
    # Initialize prompt_toolkit session.
    session = PromptSession(
        history=FileHistory('chatnoc_history.txt'),
        auto_suggest=AutoSuggestFromHistory()
    )
    
    # Initialize LLM interface and device inventory.
    llm = get_llm()
    inventory = DeviceInventory()

    while True:
        try:
            query = session.prompt("Enter your query: ")
            if query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # Parse the query using the LLM.
            intent = parse_operator_query(query, llm)
            if not intent or not intent.get("action"):
                print("Could not parse the query correctly. Please try again.")
                continue

            action = intent.get("action").lower()

            if action == "healthcheck":
                # For healthcheck queries, use the "target_device" field.
                target_spec = intent.get("target_device", "all")
                run_healthcheck_for_targets(target_spec, inventory)
                continue  # Skip the rest of the loop; go back to prompt.
            
            # For non-healthcheck queries, process as before.
            if not intent.get("target_device"):
                print("Target device not specified in the query. Please try again.")
                continue
            
            target_device_name = intent.get("target_device")
            # Retrieve the target device from inventory.
            device = inventory.get_device_by_name(target_device_name)
            if not device:
                print(f"Device '{target_device_name}' not found in inventory.")
                continue

            # For actions like check_route, extra parameters may be needed.
            extra_params = {}
            if action == "check_route":
                extra_params["destination_ip"] = intent.get("destination_ip", "")
                if not extra_params["destination_ip"]:
                    print("Destination IP address is required for the check_route action.")
                    continue

            # Lookup the command for the given action and device type.
            command = get_command(action, device.device_type, **extra_params)
            if not command:
                print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
                continue

            print(f"\nExecuting on {device.name} ({device.mgmt_address}): {command}")
            output = execute_command(device, command)
            print("Command Output:")
            print(output)

            explanation = generate_explanation(query, command, output)
            print("\nExplanation:")
            print(explanation)
            print("\n" + "-" * 80 + "\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main_cli()
