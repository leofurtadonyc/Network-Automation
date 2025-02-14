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

# Import specialized explanation functions from the explanations folder.
from explanations.ospf_explanation import explain_ospf_neighbors
from explanations.bgp_explanation import explain_bgp_neighbors
from explanations.ldp_explanation import explain_ldp_neighbors, explain_ldp_label_binding
from explanations.route_explanation import explain_route
from explanations.general_explanation import explain_general

# Import health-check functions from your healthcheck module.
from healthcheck import run_health_check_for_device, print_health_check_results

def get_explanation_function(action):
    """
    Return the specialized explanation function based on the action.
    """
    if action in ["show_ospf_neighbors_full", "ospf_neighbors"]:
        return explain_ospf_neighbors
    elif action == "bgp_neighbors":
        return explain_bgp_neighbors
    elif action == "ldp_neighbors":
        return explain_ldp_neighbors
    elif action == "ldp_label_binding":
        return explain_ldp_label_binding
    elif action == "check_route":
        return explain_route
    else:
        return explain_general

def parse_operator_query(query, llm):
    """
    Translate the operator query into a JSON object.
    Expected JSON format:
      {
        "action": <action>,
        "target_device": <device name or comma-separated list or "all">,
        "destination_ip": <optional>,
        "source_ip": <optional>,
        "mask": <optional>
      }
    Possible actions include:
      show_interfaces_down, get_mgmt_ip, show_ospf_routes_count, check_route,
      show_uptime, show_ospf_neighbors_full, ping, traceroute, bgp_neighbors,
      ldp_label_binding, ldp_neighbors, healthcheck.
    """
    prompt = (
        "You are an assistant that translates network operator queries into a JSON object in the following format:\n"
        '{ "action": <action>, "target_device": <device name or comma-separated list or "all">, "destination_ip": <optional>, "source_ip": <optional>, "mask": <optional> }\n'
        "Possible actions include: show_interfaces_down, get_mgmt_ip, show_ospf_routes_count, check_route, "
        "show_uptime, show_ospf_neighbors_full, ping, traceroute, bgp_neighbors, ldp_label_binding, ldp_neighbors, healthcheck.\n\n"
        f"Query: {query}\n\n"
        "JSON:"
    )
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        if "Connection refused" in str(e):
            print("Error: Unable to connect to Ollama.")
            print("Ensure that your Ollama host has the correct IP bindings and is listening for incoming TCP connections on the expected IP addresses and ports.")
            return {}
        else:
            print("Error communicating with Ollama:", e)
            return {}
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
    
    # Define actions that do not require a destination IP.
    actions_no_dest_required = ["bgp_neighbors", "ldp_neighbors", "show_ospf_neighbors_full"]
    
    while True:
        try:
            query = session.prompt("Enter your query: ")
            if not query.strip():
                print("Forgot to ask something? I'm here to help!")
                continue
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
                    try:
                        with open("baseline/healthcheck_baseline.yaml", "r") as f:
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
                continue
            
            # For non-healthcheck queries:
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
                if action not in actions_no_dest_required and action in ["check_route", "ping", "traceroute", "ldp_label_binding"]:
                    extra_params["destination_ip"] = intent.get("destination_ip", "")
                    if not extra_params["destination_ip"]:
                        print("Destination IP address is required for this action.")
                        continue
                if action in ["ping", "traceroute"]:
                    extra_params["source_ip"] = intent.get("source_ip", "")
                if action in ["ldp_label_binding"]:
                    extra_params["mask"] = intent.get("mask", "")
                device_results = []
                baseline_data = None
                if action in ["bgp_neighbors", "ldp_neighbors", "show_ospf_neighbors_full"]:
                    try:
                        with open("baseline/healthcheck_baseline.yaml", "r") as f:
                            baseline_data = yaml.safe_load(f)
                    except Exception as e:
                        print(f"Error loading baseline file: {e}")
                for device in devices:
                    if action in ["ping", "traceroute"] and not extra_params.get("source_ip"):
                        extra_params["source_ip"] = device.loopback_address
                    cmd_result = get_command(action, device.device_type, **extra_params)
                    if not cmd_result:
                        print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
                        continue
                    if isinstance(cmd_result, list):
                        combined_output = ""
                        for cmd in cmd_result:
                            print(f"\nExecuting on {device.name} ({device.mgmt_address}): {cmd}")
                            out = execute_command(device, cmd)
                            combined_output += out + "\n"
                        # Use the specialized explanation function.
                        explain_func = get_explanation_function(action)
                        device_results.append({
                            "device_name": device.name,
                            "command": "; ".join(cmd_result),
                            "output": combined_output,
                            "baseline": baseline_data.get(device.name) if baseline_data and baseline_data.get(device.name) else None,
                            "explain_func": explain_func
                        })
                    else:
                        print(f"\nExecuting on {device.name} ({device.mgmt_address}): {cmd_result}")
                        out = execute_command(device, cmd_result)
                        explain_func = get_explanation_function(action)
                        device_results.append({
                            "device_name": device.name,
                            "command": cmd_result,
                            "output": out,
                            "baseline": baseline_data.get(device.name) if baseline_data and baseline_data.get(device.name) else None,
                            "explain_func": explain_func
                        })
                # For multi-device, combine explanations by calling each device's explain_func.
                explanations = []
                for result in device_results:
                    exp = result["explain_func"](query, result["command"], result["output"], result["device_name"], baseline=result.get("baseline"))
                    explanations.append(exp)
                divider = "\n" + ("-" * 80) + "\n"
                combined_explanation = divider.join(explanations)
                print("\n" + combined_explanation)
            else:
                if not target_device_str:
                    print("Target device not specified in the query. Please try again.")
                    continue
                device = inventory.get_device_by_name(target_device_str)
                if not device:
                    print(f"Device '{target_device_str}' not found in inventory.")
                    continue
                extra_params = {}
                if action not in actions_no_dest_required and action in ["check_route", "ping", "traceroute", "ldp_label_binding"]:
                    extra_params["destination_ip"] = intent.get("destination_ip", "")
                    if not extra_params["destination_ip"]:
                        print("Destination IP address is required for this action.")
                        continue
                if action in ["ping", "traceroute"]:
                    extra_params["source_ip"] = intent.get("source_ip", "")
                    if not extra_params["source_ip"]:
                        extra_params["source_ip"] = device.loopback_address
                if action in ["ldp_label_binding"]:
                    extra_params["mask"] = intent.get("mask", "")
                cmd_result = get_command(action, device.device_type, **extra_params)
                if not cmd_result:
                    print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
                    continue
                if isinstance(cmd_result, list):
                    combined_output = ""
                    for cmd in cmd_result:
                        print(f"\nExecuting on {device.name} ({device.mgmt_address}): {cmd}")
                        out = execute_command(device, cmd)
                        combined_output += out + "\n"
                    explain_func = get_explanation_function(action)
                    explanation_text = explain_func(query, "; ".join(cmd_result), combined_output, device_name=device.name, baseline=None)
                else:
                    print(f"\nExecuting on {device.name} ({device.mgmt_address}): {cmd_result}")
                    out = execute_command(device, cmd_result)
                    explain_func = get_explanation_function(action)
                    explanation_text = explain_func(query, cmd_result, out, device_name=device.name, baseline=None)
                print("\n" + explanation_text)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")

def get_explanation_function(action):
    """
    Return the appropriate explanation function based on the action.
    """
    if action in ["show_ospf_neighbors_full", "ospf_neighbors"]:
        return explain_ospf_neighbors
    elif action == "bgp_neighbors":
        return explain_bgp_neighbors
    elif action == "ldp_neighbors":
        return explain_ldp_neighbors
    elif action == "ldp_label_binding":
        return explain_ldp_label_binding
    elif action == "check_route":
        return explain_route
    else:
        return explain_general

def explain_general(query, command, output, device_name="", baseline=None):
    """
    A fallback general explanation function.
    """
    explanation = (
        "This command retrieves network information based on the query.\n"
        "Review the output for any inconsistencies or unexpected information."
    )
    course = (
        "Actions:\n"
        "  - If the output is not as expected, verify the device's configuration and relevant settings."
    )
    summary = (
        f"Input Query: {query}\n"
        f"Command Executed: {command} on device(s) {device_name}\n"
    )
    return (
        f"Device Output:\n{output}\n\n"
        "------------------------------\n\n"
        f"Command issued:\n{command}\n\n"
        f"Explanation:\n{explanation}\n\n"
        f"Course of action:\n{course}\n\n"
        f"Summary:\n{summary}"
    )

if __name__ == "__main__":
    main_cli()
