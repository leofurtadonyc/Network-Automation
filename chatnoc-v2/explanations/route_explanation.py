# explanations/route_explanation.py

def explain_route(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the routing information for a specific destination IP. "
        "It shows which route the device is using and details such as administrative distance, metric, and next-hop."
    )
    course = (
        "Actions:\n"
        "  - Verify that the route exists and matches expected parameters.\n"
        "  - If the route is missing or incorrect, check routing configurations and upstream advertisements."
    )
    summary = (
        f"Input Query: {query}\n"
        f"Command Executed: {command} on device(s) {device_name}\n"
    )
    return (
        f"Device Output:\n{output}\n\n------------------------------\n\n"
        f"Command issued:\n{command}\n\n"
        f"Explanation:\n{explanation}\n\n"
        f"Course of action:\n{course}\n\n"
        f"Summary:\n{summary}"
    )
