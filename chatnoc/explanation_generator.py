# explanation_generator.py

def generate_explanation(query, command, output, device_name="", baseline=None):
    """
    Generate a structured explanation with these sections:
      - Device Output: The raw output from the device.
      - Command issued: The command that was executed.
      - Explanation: Detailed description of what the command does and why it was used.
      - Course of action: Recommended next steps and verifications.
      - Summary: Recap of the query and command executed (including device name if provided).

    If a baseline dictionary is provided (from healthcheck_baseline.yaml),
    additional information will be included for BGP, OSPF, or LDP neighbor queries.
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
            "  - Ensure the IP is correctly configured, reachable, and documented."
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
                    "The routing table contains an entry for the destination IP within the 100.65.255.0/24 range. "
                    "This indicates that the device has learned a route (via BGP, OSPF, etc.) and data plane connectivity may be available.\n"
                    "Examine the route details (administrative distance, metric, next-hop) to assess its reliability."
                )
                course_section = (
                    "Actions:\n"
                    "  - Verify that the route's metric and administrative distance meet expectations.\n"
                    "  - Confirm the next-hop is reachable and that the route aligns with your network design.\n"
                    "  - If connectivity issues persist despite the route, investigate upstream advertisements and route flaps."
                )
            else:
                explanation_section = (
                    "No valid route to the destination IP was found in the routing table. "
                    "This suggests that the device lacks a known path to the destination."
                )
                course_section = (
                    "Actions:\n"
                    "  - Review the device's routing configuration and ensure correct routes are being advertised upstream.\n"
                    "  - Verify that the destination IP is correct and required routing protocols are active."
                )
        else:
            explanation_section = (
                "This command checks for a valid route to the specified destination IP."
            )
            course_section = (
                "Actions:\n"
                "  - If no route is found, review the routing configuration and route advertisements from upstream devices."
            )
    elif "uptime" in lower_query:
        explanation_section = (
            "This command retrieves the device's uptime, indicating how long it has been operational since its last reboot."
        )
        course_section = (
            "Actions:\n"
            "  - High uptime indicates stability; if low, investigate recent reboots or issues."
        )
    elif "ospf neighbor" in lower_query or "ospf neighbors" in lower_query:
        explanation_section = (
            "This command displays OSPF neighbor adjacencies, indicating which neighbors have fully exchanged routing information."
        )
        # Attempt to count FULL state neighbors from the output.
        lines = [line for line in output.splitlines() if line.strip()]
        count = len(lines)
        explanation_section += f" The output shows {count} neighbor(s) in the FULL state."
        if baseline and baseline.get("backbone_interfaces"):
            expected = [iface.get("peer") for iface in baseline.get("backbone_interfaces") if iface.get("ospf_adjacency", "").lower() == "full"]
            explanation_section += f" Baseline expects these neighbors: {', '.join(expected)}."
        course_section = (
            "Actions:\n"
            "  - If the number of FULL neighbors is lower than expected, verify connectivity and review OSPF configurations."
        )
    elif "ping" in lower_query:
        explanation_section = (
            "This command sends ICMP echo requests (pings) from the specified source to the destination IP to verify data plane connectivity."
        )
        course_section = (
            "Actions:\n"
            "  - Examine the ping results; high packet loss or no replies indicate connectivity issues.\n"
            "  - Verify that the source IP is correct and reachable."
        )
    elif "traceroute" in lower_query:
        explanation_section = (
            "This command performs a traceroute from the specified source to the destination IP, mapping the network path."
        )
        course_section = (
            "Actions:\n"
            "  - Review the traceroute output for timeouts or unreachable hops, which may indicate routing issues.\n"
            "  - Verify the source configuration and network path if problems are observed."
        )
    elif "bgp neighbor" in lower_query or "bgp neighbors" in lower_query:
        explanation_section = (
            "This command displays the BGP neighbor summary, listing BGP peers and their connection status."
        )
        if baseline and baseline.get("bgp_peers"):
            expected = baseline.get("bgp_peers")
            explanation_section += f" Baseline expects BGP neighbors: {', '.join(expected)}."
        course_section = (
            "Actions:\n"
            "  - Review the output for any peers not in an 'established' state.\n"
            "  - For peers that are missing or not established, verify BGP configurations and underlying connectivity."
        )
    elif "ldp label binding" in lower_query or "ldp binding" in lower_query:
        explanation_section = (
            "This command retrieves the LDP label binding for the specified destination prefix. "
            "For Cisco IOS XE devices, the command includes the mask value for specificity."
        )
        if baseline and baseline.get("ldp_expected"):
            expected = baseline.get("ldp_expected")
            explanation_section += f" Baseline expects LDP bindings for: {', '.join(expected)}."
        course_section = (
            "Actions:\n"
            "  - Verify that the label binding exists and that the correct label is assigned.\n"
            "  - If missing or incorrect, review LDP session status and device configuration."
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
      device_results (list): A list of dictionaries with keys: "device_name", "command", and "output".
      
    Returns:
      A single string concatenating each device's structured explanation, separated by a divider.
    """
    explanations = []
    for result in device_results:
        exp = generate_explanation(query, result["command"], result["output"], result["device_name"])
        explanations.append(exp)
    divider = "\n" + ("-" * 80) + "\n"
    return divider.join(explanations)

if __name__ == "__main__":
    # Example tests:
    sample_query_found = "can device p1 reach 1.1.1.1"
    sample_command_found = "show ip route 1.1.1.1"
    sample_output_found = (
        "Routing entry for 1.1.1.0/24\n"
        "  Known via \"bgp 64515\", distance 20, metric 0\n"
        "  Tag 64513, type external\n"
        "  Last update from 100.64.1.1, 00:42:37 ago\n"
        "Routing Descriptor Blocks:\n"
        "  - 100.64.1.1, from 100.64.1.1, 00:42:37 ago\n"
        "    Route metric is 0, traffic share count is 1\n"
        "    AS Hops 2, Route tag 64513\n"
        "    MPLS label: none"
    )
    sample_query_not_found = "can device p1 reach 8.8.8.8"
    sample_command_not_found = "show ip route 8.8.8.8"
    sample_output_not_found = "% Network not in table"
    
    print("Test (Route Found):")
    print(generate_explanation(sample_query_found, sample_command_found, sample_output_found, device_name="P1"))
    
    print("\n" + ("=" * 80) + "\n")
    
    print("Test (Route Not Found):")
    print(generate_explanation(sample_query_not_found, sample_command_not_found, sample_output_not_found, device_name="P1"))
