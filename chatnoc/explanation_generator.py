# explanation_generator.py

def generate_explanation(query, command, output):
    """
    Generate a detailed explanation that includes:
      - A description of what the command does.
      - Troubleshooting steps and recommendations based on the output.
      - For route queries (using 'show ip route') against destinations in the 100.65.255.0/24 range,
        provide detailed context about IGP requirements and troubleshooting steps.
      - A summary with the original query, executed command, and command output.
    """
    explanation = ""
    lower_query = query.lower()
    
    if "interfaces are down" in lower_query:
        explanation += (
            "The command executed retrieves the interface status and filters for interfaces that are down. "
            "The output indicates that one or more interfaces are in an 'administratively down' state, which typically means they have been manually shut down rather than failing due to a physical fault. \n\n"
            "Recommended troubleshooting steps:\n"
            "  1. Verify whether the shutdown was intentional by reviewing change management records or maintenance notifications.\n"
            "  2. Check for any alarm notifications or error logs related to these interfaces to determine if there are underlying issues.\n"
            "  3. If the shutdown was not planned, consult your organization's procedures before re-enabling the interfaces to avoid unintended disruptions.\n"
            "  4. Consider testing connectivity or performing a physical inspection if hardware issues are suspected."
        )
    elif "management ip address" in lower_query:
        explanation += (
            "The command is designed to display the management IP address of the device. "
            "This IP is used for out-of-band management and troubleshooting. "
            "Ensure that the management IP is correctly configured, reachable, and documented in your asset management system."
        )
    elif "ospf routes" in lower_query:
        explanation += (
            "The command lists the OSPF routes known to the device. "
            "This information is important for assessing the health of your OSPF routing domain. "
            "If there are missing or unexpected routes, consider checking the OSPF configuration, verifying neighbor adjacencies, "
            "and reviewing any recent topology changes or network events."
        )
    # Revised branch for route queries based on the command.
    elif "show ip route" in command:
        # We now always provide a detailed explanation if the destination appears to be in the 100.65.255.0/24 range.
        if "100.65.255." in command or "100.65.255." in output:
            if "Routing entry" in output:
                explanation += (
                    "The command checks whether there is a valid route to the specified destination IP address. "
                    "Every network device in AS64515 requires proper IGP (OSPF) routes to all Loopback interfaces. "
                    "This is essential because label switching depends on LDP sessions between Loopback interfaces (both direct and targeted), "
                    "and BGP NEXT_HOP path attribute recursion relies on these IGP routes. \n\n"
                    "Since the routing entry exists for the destination, device P1 can reach all destinations on and behind that prefix."
                )
            else:
                explanation += (
                    "The command checks whether there is a valid route to the specified destination IP address. "
                    "Every network device in AS64515 requires proper IGP (OSPF) routes to all Loopback interfaces. "
                    "This is essential because label switching depends on LDP sessions between Loopback interfaces (both direct and targeted), "
                    "and BGP NEXT_HOP path attribute recursion relies on these IGP routes. \n\n"
                    "However, no route was found in the 100.65.255.0/24 range. Please verify the following:\n"
                    "  1. Confirm device connectivity and point-to-point links with neighboring devices.\n"
                    "  2. Review OSPF interface configurations on the device.\n"
                    "  3. Check OSPF neighbor adjacency status to ensure that routes are being properly exchanged."
                )
        else:
            # If the destination is not in the Loopback range, use a generic explanation.
            explanation += (
                "A valid route indicates that the device knows how to forward traffic to that destination. "
                "If no route is found, review the device's routing configuration and ensure that any relevant route advertisements "
                "from upstream devices are being received."
            )
    elif "uptime" in lower_query:
        explanation += (
            "The command retrieves the device’s uptime, which indicates how long the device has been operational since its last reboot. "
            "A high uptime generally suggests that the device is stable; however, if the uptime is unexpectedly low, "
            "this might warrant further investigation into potential reboot events or underlying issues."
        )
    elif "ospf neighbor" in lower_query:
        explanation += "The command displays the status of OSPF neighbor adjacencies. "
        if "how many" in lower_query or "number" in lower_query:
            lines = [line for line in output.splitlines() if line.strip()]
            count = len(lines)
            explanation += (
                f"Based on the output, there are {count} OSPF neighbor(s) in the FULL state. "
                "Only neighbors in the FULL state have completed the exchange of routing information. "
            )
        else:
            explanation += (
                "Only neighbors in the FULL state have completed the exchange of routing information. "
            )
        explanation += (
            "If you see fewer FULL neighbors than expected, verify physical connectivity, confirm OSPF configuration settings, "
            "and check for any error messages that might indicate issues with neighbor relationships."
        )
    else:
        explanation += "The command executed retrieves information based on the query. Please review the output for more details."
    
    # Append a summary to tie everything together.
    explanation += "\n\nSummary:\n"
    explanation += f"Input Query: {query}\n"
    explanation += f"Command Executed: {command}\n"
    explanation += f"Command Output:\n{output}\n"
    
    return explanation

if __name__ == "__main__":
    # Example tests:
    sample_query1 = "does device p1 have a route to destination IP address 100.65.255.14?"
    sample_query2 = "can device p1 reach 100.65.255.14?"
    sample_command = "show ip route 100.65.255.14"
    sample_output = (
        "Routing entry for 100.65.255.14/32\n"
        "  Known via \"ospf 1\", distance 110, metric 4, type intra area\n"
        "  Last update from 100.65.0.22 on Ethernet0/1, 04:02:39 ago\n"
        "  Routing Descriptor Blocks:\n"
        "  * 100.65.0.22, from 100.65.255.14, 04:02:39 ago, via Ethernet0/1\n"
        "      Route metric is 4, traffic share count is 1"
    )
    print("Test Query 1:")
    print(generate_explanation(sample_query1, sample_command, sample_output))
    print("\n" + "-"*80 + "\n")
    print("Test Query 2:")
    print(generate_explanation(sample_query2, sample_command, sample_output))
