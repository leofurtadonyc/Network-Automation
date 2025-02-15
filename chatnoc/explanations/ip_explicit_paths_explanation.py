# explanations/ip_explicit_paths_explanation.py

def explain_ip_explicit_paths(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for IP explicit paths queries.
    """
    explanation = (
        "This command displays explicit paths for routing, which show the specific path a packet will follow through the network.\n"
        "It is useful for verifying and troubleshooting routing policies and path selection."
    )
    course = (
        "Actions:\n"
        "  - Verify that the explicit paths align with your routing policies.\n"
        "  - Check for any discrepancies that may indicate misconfiguration."
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
