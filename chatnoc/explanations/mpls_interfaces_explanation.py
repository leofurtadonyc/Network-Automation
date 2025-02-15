# explanations/mpls_interfaces_explanation.py

def explain_mpls_interfaces(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for MPLS interfaces queries.
    """
    explanation = (
        "This command displays MPLS interfaces on the device.\n"
        "It provides information about which interfaces are MPLS-enabled and may show associated labels."
    )
    course = (
        "Actions:\n"
        "  - Review the output to verify that MPLS is enabled on the expected interfaces.\n"
        "  - If interfaces are missing, verify the MPLS configuration."
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
