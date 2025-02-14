# explanations/route_explanation.py

def explain_route(query, command, output, device_name=""):
    """
    Generate an explanation for route lookup queries.
    This explanation distinguishes between a route found and no route found, and provides recommendations accordingly.
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
            "  - Confirm that the next-hop is reachable and that the route aligns with your network design.\n"
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
            "  - Verify that the destination IP is correct and that all necessary routing protocols are active."
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
