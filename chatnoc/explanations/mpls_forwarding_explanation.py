# explanations/mpls_forwarding_explanation.py

def explain_mpls_forwarding(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for MPLS forwarding-table queries.
    """
    explanation = (
        "This command displays the MPLS forwarding table on the device.\n"
        "It shows how incoming labeled packets are forwarded based on MPLS labels."
    )
    course = (
        "Actions:\n"
        "  - Verify that the MPLS forwarding table contains the expected label mappings.\n"
        "  - Check for any missing or unexpected entries that might indicate a configuration issue."
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
