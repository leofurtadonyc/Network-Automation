# explanations/route_explanation.py

def explain_route(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for route lookup queries.
    
    This explanation distinguishes between a route found and no route found, and provides
    recommendations accordingly.
    
    The optional baseline parameter is ignored here, but is accepted for consistency.
    """
    if "Routing entry" in output:
        explanation = (
            "The routing table contains an entry for the destination IP.\n"
            "This indicates that the device has learned a route (via BGP, OSPF, etc.), suggesting that data plane connectivity may be available.\n"
            "Examine route details (administrative distance, metric, next-hop) to assess its reliability."
        )
        course = (
            "Actions:\n"
            "  - Verify that the route's metric and administrative distance are within expected ranges.\n"
            "  - Confirm that the next-hop is reachable and that the route matches your network design.\n"
            "  - If connectivity issues persist, investigate upstream advertisements and route flaps."
        )
    else:
        explanation = (
            "No valid route to the destination IP was found in the routing table.\n"
            "This suggests that the device does not have a known path to the destination."
        )
        course = (
            "Actions:\n"
            "  - Review the device's routing configuration and ensure that the correct routes are being advertised upstream.\n"
            "  - Verify that the destination IP is correct and that all required routing protocols are active."
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
    # Test when a route is found
    sample_query = "can device p1 reach 1.1.1.1"
    sample_command = "show ip route 1.1.1.1"
    sample_output = (
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
    print("Test (Route Found):")
    print(explain_route(sample_query, sample_command, sample_output, device_name="P1"))
    
    print("\n" + ("=" * 80) + "\n")
    
    # Test when a route is not found
    sample_query_nf = "can device p1 reach 8.8.8.8"
    sample_command_nf = "show ip route 8.8.8.8"
    sample_output_nf = "% Network not in table"
    print("Test (Route Not Found):")
    print(explain_route(sample_query_nf, sample_command_nf, sample_output_nf, device_name="P1"))
