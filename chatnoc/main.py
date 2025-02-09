# main.py
import json
from devices_inventory import DeviceInventory
from command_mapper import get_command
from netmiko_executor import execute_command
from llm_interface import get_llm
from explanation_generator import generate_explanation

def parse_operator_query(query, llm):
    """
    Use the LLM to parse the operator query into a structured intent.
    
    Expected JSON format:
        { "action": <action>, "target_role": <device role or hostname> }
        
    For example, the query:
        "Show me the interface status on the access router."
    might return:
        { "action": "show_interface_status", "target_role": "access" }
    """
    prompt = (
        "You are an assistant that translates network operator queries into a JSON with the following format:\n"
        '{ "action": <action>, "target_role": <device role or hostname> }\n'
        "Possible actions include: show_interface_status, show_routing_table.\n"
        "For the query below, provide the corresponding JSON:\n\n"
        f"Query: {query}\n\n"
        "JSON:"
    )
    response = llm.invoke(prompt)  # Using .invoke() instead of direct call.
    try:
        structured_intent = json.loads(response)
    except json.JSONDecodeError:
        # Fallback default if parsing fails
        structured_intent = {"action": "show_interface_status", "target_role": "access"}
    return structured_intent

def main():
    # Initialize the LLM interface
    llm = get_llm()
    
    # Get operator query input (for now, from standard input)
    operator_query = input("Enter your query: ")
    
    # Use the LLM to parse the query into a structured intent
    intent = parse_operator_query(operator_query, llm)
    action = intent.get("action")
    target_identifier = intent.get("target_role")  # Could be a role or a hostname

    # Load device inventory and filter devices by role first
    inventory = DeviceInventory()
    target_devices = inventory.get_devices_by_role(target_identifier)
    
    # If no devices match the role, try matching by device name
    if not target_devices:
        device = inventory.get_device_by_name(target_identifier)
        if device:
            target_devices = [device]
        else:
            print(f"No devices found for role or hostname '{target_identifier}'.")
            return
    
    # Process each device: map the intent to a command and execute it
    for device in target_devices:
        command = get_command(action, device.device_type)
        if not command:
            print(f"No command mapping found for action '{action}' on device type '{device.device_type}'.")
            continue
        
        print(f"\nExecuting on {device.name} ({device.mgmt_address}): {command}")
        output = execute_command(device, command)
        print("Command Output:")
        print(output)
        
        # Generate an explanation to educate the operator
        explanation = generate_explanation(operator_query, command, output)
        print("\nExplanation:")
        print(explanation)

if __name__ == "__main__":
    main()
