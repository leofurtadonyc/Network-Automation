# explanations/ldp_explanation.py

def explain_ldp_neighbors(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays LDP neighbor information. It lists the LDP sessions with peer devices, which are "
        "critical for establishing MPLS label distribution across the network."
    )
    course = (
        "Actions:\n"
        "  - Verify that all expected LDP sessions are established.\n"
        "  - If sessions are missing, review LDP configuration and connectivity between devices."
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

def explain_ldp_label_binding(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command retrieves the LDP label binding information for a specific destination prefix. "
        "It is used to verify that labels are correctly bound to routes for MPLS forwarding."
    )
    course = (
        "Actions:\n"
        "  - Check that the label binding exists and is correct.\n"
        "  - If the binding is missing or incorrect, review LDP session status and device configuration."
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
