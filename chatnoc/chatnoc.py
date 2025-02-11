#!/usr/bin/env python
import re
import json
import sys
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import pyfiglet

# Import your modules.
from devices_inventory import DeviceInventory
from command_mapper import get_command
from netmiko_executor import execute_command
from llm_interface import get_llm
from explanation_generator import generate_explanation, generate_explanation_multi

# Import health-check functions from your healthcheck module.
from healthcheck import run_health_check_for_device, print_health_check_results

def parse_operator_query(query, llm):
    """
    Translate the operator query into a JSON object.
    Expected JSON format:
      {
        "action": <action>,
        "target_device": <device name or comma-separated list or "all">,
        "destination_ip": <optional>
      }
    Possible actions include:
      show_interfaces_down, get_mgmt_ip, show_ospf_routes_count, check_route,
      show_uptime, show_ospf_neighbors_full, healthcheck.
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

def main_cli():
    banner = pyfiglet.figlet_format("ChatNOC")
    print(banner)
    print("Welcome to ChatNOC interactive shell. Type 'exit' or 'quit' to exit.\n")
    
    session = PromptSession(
        history=FileHistory('chatnoc_history.txt'),
        auto_suggest=AutoSuggestFromHistory()
    )
    llm = get_llm()
    inventory = DeviceInventory()
    
    while True:
        try:
            query = session.prompt("Enter your query: ")
            if query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            intent = parse_operator_query(query, llm)
            if not intent or not intent.get("action"):
                print("Could not parse the query correctly. Please try again.")
                continue
            
            action = intent.get("action").lower()
            target_device_str = intent.get("target_device", "")
            
            # Healthcheck branch.
            if action == "healthcheck":
                # Split target if multiple devices (by comma or "and").
                if any(sep in target_device_str.lower() for sep in [",", " and "]):
                    device_names = [name.strip() for name in re.split(r',|\band\b', target_device_str, flags=re.IGNORECASE)]
                else:
                    device_names = [target_device_str.strip()]
                
                for name in device_names:
                    device = inventory.get_device_by_name(name)
                    if not device:
                        print(f"Device '{name}' not found in inventory.")
                        continue
                    print(f"\nPerforming health check on device {device.name} ({device.mgmt_address})...")
                    # Load baseline data from healthcheck_baseline.yaml.
                    try:
                        with open("healthcheck_baseline.yaml", "r") as f:
                            baseline_data = yaml.safe_load(f)
                    except Exception as e:
                        print(f"Error loading baseline file: {e}")
                        continue
                    baseline_for_device = baseline_data.get(device.name)
                    if not baseline_for_device:
                        print(f"No baseline defined for device '{device.name}'. Skipping health check for this device.")
                        continue
                    results = run_health_check_for_device(device, baseline_for_device)
                    print_health_check_results(device.name, results)
                    print("\n" + "-" * 80 + "\n")
                continue  # Skip further processing for healthcheck queries.
            
            # For non-healthcheck queries:
            # Check if multiple devices are specified.
            if any(sep in target_device_str.lower() for sep in [",", " and "]):
                device_names = [name.strip() for name in re.split(r',|\band\b', target_device_str, flags=re.IGNORECASE)]
                devices = []
                for name in device_names:
                    device_obj = inventory.get_device_by_name(name)
                    if device_obj:
                        devices.append(device_obj)
                    else:
                        print(f"Device '{name}' not found in inventory.")
                if not devices:
                    print("No valid devices found in the target list.")
                    continue
                extra_params = {}
                if action == "check_route":
                    extra_params["destination_ip"] = intent.get("destination_ip", "")
                    if not extra_params["destination_ip"]:
                        print("Destination IP address is required for the check_route action.")
                        continue
                device_results = []
                for device in devices:
                    command = get_command(action, device.device_type, **extra_params)
                    if not command:
                        print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
                        continue
                    print(f"\nExecuting on {device.name} ({device.mgmt_address}): {command}")
                    output = execute_command(device, command)
                    device_results.append({
                        "device_name": device.name,
                        "command": command,
                        "output": output
                    })
                combined_explanation = generate_explanation_multi(query, device_results)
                print("\n" + combined_explanation)
            else:
                # Single-device path.
                if not target_device_str:
                    print("Target device not specified in the query. Please try again.")
                    continue
                device = inventory.get_device_by_name(target_device_str)
                if not device:
                    print(f"Device '{target_device_str}' not found in inventory.")
                    continue
                extra_params = {}
                if action == "check_route":
                    extra_params["destination_ip"] = intent.get("destination_ip", "")
                    if not extra_params["destination_ip"]:
                        print("Destination IP address is required for the check_route action.")
                        continue
                command = get_command(action, device.device_type, **extra_params)
                if not command:
                    print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
                    continue
                print(f"\nExecuting on {device.name} ({device.mgmt_address}): {command}")
                output = execute_command(device, command)
                explanation_text = generate_explanation(query, command, output, device_name=device.name)
                print("\n" + explanation_text)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main_cli()
