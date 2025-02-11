# explanation_generator.py

def generate_explanation(query, command, output, device_name=""):
    """
    Generate a structured explanation with the following sections:
      - Device Output: The raw output returned by the device.
      - Command issued: The command ChatNOC ran on the target device.
      - Explanation: A detailed description of what the command does and its use cases.
      - Course of action: Recommended next steps, potential issues, and further verifications.
      - Summary: A recap including the original query and the command executed (with the device name if provided).
    
    The output is structured so that the device output appears first.
    """
    lower_query = query.lower()
    cmd_section = f"{command}"
    
    # Initialize the Explanation and Course sections.
    explanation_section = ""
    course_section = ""
    
    if "interfaces are down" in lower_query:
        explanation_section = (
            "This command retrieves the interface status and filters for interfaces that are down. "
            "It is used to quickly identify interfaces that are not operational—typically due to being administratively shut down."
        )
        course_section = (
            "Recommended actions:\n"
            "  1. Verify whether the shutdown was intentional by reviewing change management records or maintenance notifications.\n"
            "  2. Check for alarm notifications or error logs for these interfaces to detect underlying issues.\n"
            "  3. If unplanned, consult your organization's procedures before re-enabling the interfaces.\n"
            "  4. Consider testing connectivity or inspecting hardware if a physical fault is suspected."
        )
    elif "management ip address" in lower_query:
        explanation_section = (
            "This command displays the management IP address of the device, used for out-of-band management and troubleshooting."
        )
        course_section = (
            "Recommended actions:\n"
            "  - Ensure the management IP is configured correctly, is reachable, and is documented in your asset management system."
        )
    elif "ospf routes" in lower_query:
        explanation_section = (
            "This command lists the OSPF routes known to the device, providing insight into the health of the OSPF routing domain. "
            "In our network, proper IGP (OSPF) routes to all Loopback interfaces are critical because label switching depends on LDP sessions "
            "and BGP NEXT_HOP recursion relies on these routes."
        )
        course_section = (
            "Recommended actions:\n"
            "  - If routes are missing or unexpected, review the OSPF configuration, verify neighbor adjacencies, and check for topology changes."
        )
    elif "show ip route" in command:
        if "100.65.255." in command or "100.65.255." in output:
            if "Routing entry" in output:
                explanation_section = (
                    "This command checks for a valid route to the specified destination IP within the 100.65.255.0/24 range. "
                    "Proper IGP (OSPF) routes to all Loopback interfaces are critical because label switching depends on LDP sessions "
                    "and BGP NEXT_HOP recursion relies on these routes."
                )
                course_section = (
                    "Since the routing entry exists, the device can reach all destinations on and behind that prefix. "
                    "No further action is needed unless connectivity issues are observed."
                )
            else:
                explanation_section = (
                    "This command attempts to find a valid route to the specified destination IP within the 100.65.255.0/24 range. "
                    "Proper IGP (OSPF) routes are essential for network connectivity, label switching, and BGP next-hop resolution."
                )
                course_section = (
                    "No route was found. Recommended actions:\n"
                    "  1. Verify device connectivity and check point-to-point links with neighboring devices.\n"
                    "  2. Review OSPF interface configurations.\n"
                    "  3. Confirm that OSPF neighbor adjacencies are established."
                )
        else:
            explanation_section = (
                "This command checks for a valid route to the specified destination IP address."
            )
            course_section = (
                "If no route is found, review the device's routing configuration and ensure that any relevant route advertisements "
                "from upstream devices are being received."
            )
    elif "uptime" in lower_query:
        explanation_section = (
            "This command retrieves the device's uptime, indicating how long the device has been operational since its last reboot."
        )
        course_section = (
            "A high uptime suggests stability. However, if uptime is unexpectedly low, further investigation into reboot events or issues is recommended."
        )
    elif "ospf neighbor" in lower_query:
        explanation_section = (
            "This command displays OSPF neighbor adjacencies, showing which neighbors have completed the exchange of routing information."
        )
        if "how many" in lower_query or "number" in lower_query:
            lines = [line for line in output.splitlines() if line.strip()]
            count = len(lines)
            explanation_section += f" The output indicates that there are {count} neighbor(s) in the FULL state."
            course_section = (
                "If the number of FULL neighbors is lower than expected, verify physical connectivity, review OSPF configurations, "
                "and check for error messages that may indicate neighbor issues."
            )
        else:
            course_section = (
                "If you observe fewer FULL neighbors than expected, verify connectivity and configuration on the device interfaces "
                "and with the OSPF neighbors."
            )
    else:
        explanation_section = (
            "This command retrieves network information based on the query."
        )
        course_section = (
            "Review the output and, if necessary, verify the device's configuration for any inconsistencies."
        )
    
    structured_output = (
        "Device Output:\n"
        f"{output}\n\n"
        "------------------------------\n\n"
        "Command issued:\n"
        f"{cmd_section}\n\n"
        "Explanation:\n"
        f"{explanation_section}\n\n"
        "Course of action:\n"
        f"{course_section}\n\n"
        "Summary:\n"
        f"Input Query: {query}\n"
        f"Command Executed: {command}" + (f" on device(s) {device_name}" if device_name else "") + "\n"
    )
    return structured_output

def generate_explanation_multi(query, device_results):
    """
    Generate structured explanations for multiple devices.
    
    Parameters:
      query (str): The original operator query.
      device_results (list): A list of dictionaries, each with keys:
                             "device_name", "command", and "output".
                             
    Returns:
      A single string that concatenates each device's structured explanation, separated by a divider.
    """
    explanations = []
    for result in device_results:
        exp = generate_explanation(query, result["command"], result["output"], result["device_name"])
        explanations.append(exp)
    divider = "\n" + ("-" * 80) + "\n"
    return divider.join(explanations)

if __name__ == "__main__":
    # Example tests:
    sample_query = "does device p1 have a route to destination IP address 100.65.255.14?"
    sample_command = "show ip route 100.65.255.14"
    sample_output = (
        "Routing entry for 100.65.255.14/32\n"
        "  Known via \"ospf 1\", distance 110, metric 4, type intra area\n"
        "  Last update from 100.65.0.22 on Ethernet0/1, 04:02:39 ago\n"
        "  Routing Descriptor Blocks:\n"
        "  * 100.65.0.22, from 100.65.255.14, 04:02:39 ago, via Ethernet0/1\n"
        "      Route metric is 4, traffic share count is 1"
    )
    print("Test Single Device:")
    print(generate_explanation(sample_query, sample_command, sample_output, device_name="P1"))
    
    print("\n" + ("=" * 80) + "\n")
    
    device_results = [
        {
            "device_name": "P1",
            "command": sample_command,
            "output": sample_output,
        },
        {
            "device_name": "PE-4",
            "command": sample_command,
            "output": sample_output,
        },
    ]
    print("Test Multiple Devices:")
    print(generate_explanation_multi(sample_query, device_results))
