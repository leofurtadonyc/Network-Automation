# explanations/mpls_traffic_eng_explanation.py

def explain_mpls_traffic_eng(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for MPLS Traffic Engineering tunnels queries.
    """
    explanation = (
        "This command displays MPLS Traffic Engineering tunnels, which show the established tunnels used for optimized traffic routing.\n"
        "It provides insight into tunnel status, labels, and associated metrics."
    )
    course = (
        "Actions:\n"
        "  - Verify that the MPLS TE tunnels are operational and configured as expected.\n"
        "  - Check for any tunnels that are down or misconfigured."
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
