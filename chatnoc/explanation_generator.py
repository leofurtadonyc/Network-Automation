# explanation_generator.py

def generate_explanation(query, command, output, device_name=""):
    """
    Generate a structured explanation with these sections:
      - Device Output: The raw output from the device.
      - Command issued: The command that was executed.
      - Explanation: Detailed description of what the command does and why it was used.
      - Course of action: Recommended next steps or further verifications.
      - Summary: Recap of the query and command executed (including device(s)).
    """
    lower_query = query.lower()
    cmd_section = f"{command}"
    explanation_section = ""
    course_section = ""

    if "interfaces are down" in lower_query:
        explanation_section = (
            "This command retrieves interface status and filters for interfaces that are down. "
            "It quickly identifies interfaces that are administratively shut down."
        )
        course_section = (
            "Actions:\n"
            "  1. Verify if the shutdown was intentional (check change management records).\n"
            "  2. Check for alarms or logs related to these interfaces.\n"
            "  3. If unplanned, consult procedures before re-enabling.\n"
            "  4. Test connectivity or inspect hardware if necessary."
        )
    elif "management ip address" in lower_query:
        explanation_section = (
            "This command displays the management IP address used for out-of-band management and troubleshooting."
        )
        course_section = (
            "Actions:\n"
            "  - Ensure the management IP is correctly configured, reachable, and documented."
        )
    elif "ospf routes" in lower_query:
        explanation_section = (
            "This command lists the OSPF routes known to the device, providing insight into the OSPF routing domain."
        )
        course_section = (
            "Actions:\n"
            "  - If routes are missing or unexpected, review OSPF configurations and neighbor adjacencies."
        )
    elif "show ip route" in command:
        if "100.65.255." in command or "100.65.255." in output:
            if "Routing entry" in output:
                explanation_section = (
                    "This command checks for a valid route to a destination IP within the 100.65.255.0/24 range.\n"
                    "Proper IGP routes to Loopback interfaces are crucial for label switching and BGP next-hop recursion."
                )
                course_section = (
                    "Actions:\n"
                    "  - The routing entry exists; the destination is reachable. No further action is needed unless issues occur."
                )
            else:
                explanation_section = (
                    "This command attempts to find a valid route to a destination IP within the 100.65.255.0/24 range."
                )
                course_section = (
                    "Actions:\n"
                    "  1. Verify device connectivity and point-to-point links with neighbors.\n"
                    "  2. Review OSPF interface configurations and neighbor adjacencies."
                )
        else:
            explanation_section = (
                "This command checks for a valid route to the specified destination IP."
            )
            course_section = (
                "Actions:\n"
                "  - If no route is found, review the routing configuration and upstream route advertisements."
            )
    elif "uptime" in lower_query:
        explanation_section = (
            "This command retrieves the device's uptime, indicating how long it has been operational since its last reboot."
        )
        course_section = (
            "Actions:\n"
            "  - High uptime indicates stability; if low, investigate recent reboots or issues."
        )
    elif "ospf neighbor" in lower_query:
        explanation_section = (
            "This command displays OSPF neighbor adjacencies, showing which neighbors have completed routing information exchange."
        )
        if "how many" in lower_query or "number" in lower_query:
            lines = [line for line in output.splitlines() if line.strip()]
            count = len(lines)
            explanation_section += f" The output indicates {count} neighbor(s) in the FULL state."
            course_section = (
                "Actions:\n"
                "  - If the number is lower than expected, verify connectivity and OSPF configurations."
            )
        else:
            course_section = (
                "Actions:\n"
                "  - If fewer FULL neighbors are observed than expected, review connectivity and device configurations."
            )
    elif "ping" in lower_query:
        explanation_section = (
            "This command sends ICMP echo requests (pings) from the specified source to the destination IP to verify data plane connectivity."
        )
        course_section = (
            "Actions:\n"
            "  - Examine the ping results; high packet loss or no replies indicate connectivity issues. "
            "    Verify the correctness and reachability of the source IP."
        )
    elif "traceroute" in lower_query:
        explanation_section = (
            "This command performs a traceroute from the specified source to the destination IP, mapping the network path."
        )
        course_section = (
            "Actions:\n"
            "  - Review the traceroute output for timeouts or unreachable hops, which may indicate routing issues. "
            "    Verify the source configuration and routing path if issues are observed."
        )
    elif "bgp neighbor" in lower_query or "bgp neighbors" in lower_query:
        explanation_section = (
            "This command displays the BGP neighbor summary for the device, listing the BGP peers and their connection status."
        )
        course_section = (
            "Actions:\n"
            "  - Review the output for any peers not in an 'established' state. "
            "    For those not established, check the BGP configuration and underlying connectivity."
        )
    elif "ldp label binding" in lower_query or "ldp binding" in lower_query:
        explanation_section = (
            "This command retrieves the LDP label binding for the specified destination prefix. "
            "For Cisco IOS XE devices, a specialized command that includes the mask value is used."
        )
        course_section = (
            "Actions:\n"
            "  - Verify that the label binding exists and that the correct label is assigned. "
            "    If not, review the LDP session status and device configuration."
        )
    else:
        explanation_section = (
            "This command retrieves network information based on the query."
        )
        course_section = (
            "Actions:\n"
            "  - Review the output and verify the device's configuration for any inconsistencies."
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
      query (str): The operator's query.
      device_results (list): A list of dictionaries with keys:
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
