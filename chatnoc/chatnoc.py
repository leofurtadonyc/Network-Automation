#!/usr/bin/env python
import re
import json
import sys
import os
import yaml
import random
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import pyfiglet

from devices_inventory import DeviceInventory
from command_mapper import get_command
from netmiko_executor import execute_command
from llm_interface import get_llm

# Import specialized explanation functions.
from explanations.ospf_explanation import explain_ospf_neighbors
from explanations.bgp_explanation import explain_bgp_neighbors
from explanations.ldp_explanation import explain_ldp_neighbors, explain_ldp_label_binding
from explanations.route_explanation import explain_route
from explanations.general_explanation import explain_general

# Import health-check functions.
from healthcheck import run_health_check_for_device, print_health_check_results

# Global mode flags.
demo_mode = False
general_mode = False

# List of funny lines for empty queries.
funny_lines = [
    "Need some network wisdom? I've got packets of knowledge to share!",
    "Router troubles? Let's troubleshoot together - I promise not to byte!",
    "Got a networking puzzle? I'm your personal CLI whisperer!",
    "Lost in configuration? Don't worry, I'm your friendly neighborhood network guide!",
    "Questions about protocols? TCP/IP and chill!",
    "Network down? Keep calm and query on - I'm here!",
    "Forgot to ask something? I'm here to help!",
    "Have a question in mind? Go ahead and ask!",
    "Need routing assistance? I'll help you find the path of least resistance!",
    "BGP giving you grief? Let's peer into the problem together!",
    "OSPF acting up? Don't worry, we'll get your areas in order!",
    "Don't tell me your MPLS services are affected again! Nooooo!!"
]

def demo_execute_command(device, command):
    """
    In demo mode, load the command output from a file in the "demo" folder.
    Filename: demo/<device.name.lower()>/<normalized_command>.txt
    """
    normalized = command.strip().lower().replace(" ", "_").replace("|", "").replace(":", "")
    demo_file = os.path.join("demo", device.name.lower(), f"{normalized}.txt")
    print(f"DEBUG: Looking for demo file: {demo_file}")
    if os.path.isfile(demo_file):
        with open(demo_file, "r") as f:
            content = f.read()
        if not content.strip():
            return "[Demo file is empty]"
        return content
    else:
        return f"[Demo output not available for command: {command}]"

def load_approved_topics():
    """
    Load approved topics from baseline/index.yaml.
    Expected format:
      approved_topics:
        - routing
        - switching
        - network security
        - ospf
        - bgp
        - mpls
        - vpn
        - data center
        - wireless
        - network automation
    """
    try:
        with open("baseline/index.yaml", "r") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return data.get("approved_topics", [])
            else:
                print("Error: Index file format incorrect. Expected a mapping with 'approved_topics'.")
                return []
    except Exception as e:
        print(f"Error loading approved topics: {e}")
        return []

def contains_approved_topic(query, approved_topics):
    query_lower = query.lower()
    for topic in approved_topics:
        if topic.lower() in query_lower:
            return True
    return False

def contains_profanity(query):
    curses = ["damn", "hell", "shit", "fuck"]
    query_lower = query.lower()
    for word in curses:
        if word in query_lower:
            return True
    return False

def process_general_query(query, llm):
    """
    Handle open-ended networking questions.
    Loads approved topics from baseline/index.yaml and uses the LLM to generate an explanation
    if the query includes an approved topic; otherwise, it instructs the user to rephrase.
    Also handles profanity with a humorous response.
    """
    approved_topics = load_approved_topics()
    # Check for profanity.
    if contains_profanity(query):
        return "I'm here to help with networking, but please keep it professional. Let's stick to the tech talk!"

    # Check if the query mentions at least one approved topic.
    if contains_approved_topic(query, approved_topics):
        prompt = f"Explain the following network technology topic in detail: {query}"
        try:
            response = llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error generating explanation: {e}"
    else:
        return ("Sorry, I can only provide support for computer networking, your networks, and your customers. "
                "Please rephrase your question to focus on networking topics.\n"
                "For a list of approved topics, type 'approved topics'.")

def display_help():
    help_file = "help.txt"
    if os.path.isfile(help_file):
        with open(help_file, "r") as f:
            print(f.read())
    else:
        print("No help file found.")

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
    global demo_mode, general_mode
    mode_prompt = lambda: "demo-mode > " if demo_mode else ("general-mode > " if general_mode else "ChatNOC > ")
    banner = pyfiglet.figlet_format("ChatNOC")
    print(banner)
    print("Welcome to ChatNOC interactive shell.")
    print("Type 'help' for usage instructions.")
    print("Type 'demo' to enter demo mode (dry-run with pre-saved outputs).")
    print("Type 'general' to enter general mode for open-ended networking topics.")
    print("In demo or general mode, type 'exit demo' or 'exit general' to return to normal mode.")
    print("In normal mode, 'exit' or 'quit' will terminate the program.\n")
    
    session = PromptSession(
        history=FileHistory('chatnoc_history.txt'),
        auto_suggest=AutoSuggestFromHistory()
    )
    llm = get_llm()
    inventory = DeviceInventory()
    
    # Define actions that do not require a destination IP.
    actions_no_dest_required = ["bgp_neighbors", "ldp_neighbors", "show_ospf_neighbors_full"]
    # List of device-specific actions.
    device_actions = ["show_interfaces_down", "get_mgmt_ip", "show_ospf_routes_count",
                      "check_route", "show_uptime", "show_ospf_neighbors_full",
                      "ping", "traceroute", "bgp_neighbors", "ldp_label_binding", "ldp_neighbors", "healthcheck"]
    
    while True:
        try:
            query = session.prompt(mode_prompt())
            # Help command.
            if query.strip().lower() == "help":
                display_help()
                continue
            # Mode switching commands.
            if query.strip().lower() == "demo":
                demo_mode = True
                general_mode = False
                print("\nDemo mode enabled. In demo mode, no live device connections will be made; pre-saved outputs will be used.")
                print("Available demo devices: P1 to P8 (Cisco IOS), PE1-Junos (Juniper), PE2-IOSXR (Cisco IOS XR), PE3-Huawei (NE40E), and PE4-Nokia (Nokia 7750 SR).\n")
                continue
            if query.strip().lower() == "general":
                general_mode = True
                demo_mode = False
                print("\nGeneral mode enabled. In general mode, device-specific commands will NOT be executed.")
                print("You can ask open-ended networking questions. Use 'exit general' to return to normal mode.\n")
                continue
            if demo_mode and query.strip().lower() == "exit demo":
                demo_mode = False
                print("\nExiting demo mode. Now operating in normal mode.\n")
                continue
            if general_mode and query.strip().lower() == "exit general":
                general_mode = False
                print("\nExiting general mode. Now operating in normal mode.\n")
                continue
            # In normal mode, 'exit' terminates the program.
            if not demo_mode and not general_mode and query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not query.strip():
                print(random.choice(funny_lines))
                continue

            # Check if user wants to see approved topics.
            if general_mode and query.strip().lower() in ["approved topics", "list approved topics"]:
                topics = load_approved_topics()
                if topics:
                    print("\nApproved Topics:")
                    for topic in topics:
                        print(f"  - {topic}")
                else:
                    print("No approved topics found.")
                continue

            # If in general mode, process as a general networking query.
            if general_mode:
                result = process_general_query(query, llm)
                print("\n" + result)
                continue

            # In normal mode, exit or quit terminates the program.
            if not demo_mode and not general_mode and query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not query.strip():
                print(random.choice(funny_lines))
                continue

            # First, check if the query is a general networking topic (if not device-specific).
            # Normalize the action and target.
            intent = parse_operator_query(query, llm)
            if not intent or not intent.get("action"):
                print("Could not parse the query correctly. Please try again.")
                continue

            action = intent.get("action").lower()
            normalized_action = action.replace("-", "").replace(" ", "")
            target_device_str = intent.get("target_device", "")

            # Healthcheck branch.
            if normalized_action == "healthcheck":
                # If target is "all", then run healthchecks on all devices.
                if target_device_str.strip().lower() == "all":
                    devices_to_check = inventory.get_all_devices()  # Ensure your inventory class provides this method.
                else:
                    # Support comma-separated list as well.
                    if any(sep in target_device_str.lower() for sep in [",", " and "]):
                        device_names = [name.strip() for name in re.split(r',|\band\b', target_device_str, flags=re.IGNORECASE)]
                    else:
                        device_names = [target_device_str.strip()]
                    devices_to_check = []
                    for name in device_names:
                        device = inventory.get_device_by_name(name)
                        if device:
                            devices_to_check.append(device)
                        else:
                            print(f"Device '{name}' not found in inventory.")
                    if not devices_to_check:
                        print("No valid devices found for healthcheck.")
                        continue

                for device in devices_to_check:
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

                    # Optionally, you may first check connectivity (as shown previously).
                    print(f"Checking connectivity on {device.name}...")
                    connectivity_output = execute_command(device, "show version")
                    if "Failed to execute command" in connectivity_output:
                        print(f"Error: Unable to connect to {device.name}: {connectivity_output}")
                        continue

                    results = run_health_check_for_device(device, baseline_for_device)
                    print_health_check_results(device.name, results)
                    print("\n" + "-" * 80 + "\n")
                continue  # Skip further processing.

            # If the action is not one of the device-specific actions, assume it's a general networking query.
            device_actions = ["show_interfaces_down", "get_mgmt_ip", "show_ospf_routes_count",
                              "check_route", "show_uptime", "show_ospf_neighbors_full",
                              "ping", "traceroute", "bgp_neighbors", "ldp_label_binding", "ldp_neighbors"]
            if normalized_action not in [a.replace("-", "").replace(" ", "") for a in device_actions]:
                result = process_general_query(query, llm)
                print("\n" + result)
                continue

            # Otherwise, process device-specific queries.
            target_device_str = intent.get("target_device", "")
            if not target_device_str or target_device_str.strip().lower() == "all":
                print("Please specify a specific device for this action. For general networking questions, switch to general mode.")
                continue
            
            # Process device-specific queries.
            if any(sep in target_device_str.lower() for sep in [",", " and "]):
                # Multi-device branch.
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
                            out = demo_execute_command(device, cmd) if demo_mode else execute_command(device, cmd)
                            combined_output += out + "\n"
                        device_results.append({
                            "device_name": device.name,
                            "command": "; ".join(cmd_result),
                            "output": combined_output,
                            "baseline": baseline_data.get(device.name) if baseline_data and baseline_data.get(device.name) else None,
                            "explain_func": get_explanation_function(action)
                        })
                    else:
                        print(f"\nExecuting on {device.name} ({device.mgmt_address}): {cmd_result}")
                        out = demo_execute_command(device, cmd_result) if demo_mode else execute_command(device, cmd_result)
                        device_results.append({
                            "device_name": device.name,
                            "command": cmd_result,
                            "output": out,
                            "baseline": baseline_data.get(device.name) if baseline_data and baseline_data.get(device.name) else None,
                            "explain_func": get_explanation_function(action)
                        })
                explanations = []
                for result in device_results:
                    if "Failed to execute command" in result["output"]:
                        error_msg = (
                            f"Error executing command on {result['device_name']}: {result['output']}\n"
                            "Troubleshooting suggestions:\n"
                            "  1. Verify that the device is powered on and reachable.\n"
                            "  2. Check the hostname/IP address and TCP port.\n"
                            "  3. Ensure that no firewall is blocking the connection."
                        )
                        explanations.append(error_msg)
                    else:
                        exp = result["explain_func"](query, result["command"], result["output"], result["device_name"], baseline=result.get("baseline"))
                        explanations.append(exp)
                divider = "\n" + ("-" * 80) + "\n"
                combined_explanation = divider.join(explanations)
                print("\n" + combined_explanation)
            else:
                # Single device branch.
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
                        out = demo_execute_command(device, cmd) if demo_mode else execute_command(device, cmd)
                        combined_output += out + "\n"
                    explain_func = get_explanation_function(action)
                    if "Failed to execute command" in combined_output:
                        print(f"\nError executing command on {device.name}: {combined_output}")
                    else:
                        explanation_text = explain_func(query, "; ".join(cmd_result), combined_output, device_name=device.name, baseline=None)
                        print("\n" + explanation_text)
                else:
                    print(f"\nExecuting on {device.name} ({device.mgmt_address}): {cmd_result}")
                    out = demo_execute_command(device, cmd_result) if demo_mode else execute_command(device, cmd_result)
                    explain_func = get_explanation_function(action)
                    if "Failed to execute command" in out:
                        print(f"\nError executing command on {device.name}: {out}")
                    else:
                        explanation_text = explain_func(query, cmd_result, out, device_name=device.name, baseline=None)
                        print("\n" + explanation_text)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main_cli()
