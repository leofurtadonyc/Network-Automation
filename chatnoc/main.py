# main.py
import json
import re
from devices_inventory import DeviceInventory
from command_mapper import get_command
from netmiko_executor import execute_command
from llm_interface import get_llm
from explanation_generator import generate_explanation

import logging
import httpx

# # Enable debug logging for HTTPX and its dependencies
# logging.basicConfig(level=logging.DEBUG)
# httpx_log = logging.getLogger("httpx")
# httpx_log.setLevel(logging.DEBUG)

import json

def parse_operator_query(query, llm):
    """
    Use the LLM to parse the network operator query into a JSON intent.

    Expected JSON format:
      {
        "action": <action>,
        "target_device": <device hostname>,
        "destination_ip": <optional, only for check_route>
      }

    The prompt instructs the LLM to output ONLY valid JSON with no additional text.
    """
    prompt = (
        "You are an assistant that translates network operator queries into a JSON object in the following format:\n"
        "{ \"action\": <action>, \"target_device\": <device hostname>, \"destination_ip\": <optional> }\n"
        "Please output ONLY valid JSON with no additional explanation or commentary.\n"
        "Possible actions include: show_interfaces_down, get_mgmt_ip, show_ospf_routes_count, check_route, show_uptime, show_ospf_neighbors_full.\n\n"
        f"Query: {query}\n\n"
        "JSON:"
    )
    
    response = llm.invoke(prompt)
    # Debug: print the raw response (you can uncomment the following line for troubleshooting)
    # print("LLM raw response:", response)
    
    # Use a regular expression to extract a substring that looks like a JSON object.
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

def main():
    llm = get_llm()
    
    operator_query = input("Enter your query: ")
    intent = parse_operator_query(operator_query, llm)
    action = intent.get("action")
    target_device_name = intent.get("target_device")
    
    if not action or not target_device_name:
        print("Could not parse the query correctly. Please try again.")
        return
    
    # Retrieve the target device from the inventory
    inventory = DeviceInventory()
    device = inventory.get_device_by_name(target_device_name)
    if not device:
        print(f"No device found with the name '{target_device_name}'.")
        return
    
    # For check_route, we need a destination IP.
    extra_params = {}
    if action == "check_route":
        extra_params["destination_ip"] = intent.get("destination_ip", "")
        if not extra_params["destination_ip"]:
            print("Destination IP address is required for the check_route action.")
            return
    
    # Get the command template for this action/device type.
    command = get_command(action, device.device_type, **extra_params)
    if not command:
        print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
        return
    
    print(f"\nExecuting on {device.name} ({device.mgmt_address}): {command}")
    output = execute_command(device, command)
    print("Command Output:")
    print(output)
    
    explanation = generate_explanation(operator_query, command, output)
    print("\nExplanation:")
    print(explanation)

if __name__ == "__main__":
    main()
