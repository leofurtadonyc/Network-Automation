# explanations/mpls_forwarding_explanation.py

def explain_mpls_forwarding(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the MPLS forwarding table. It indicates how the device forwards labeled packets "
        "and shows the label-to-next-hop mappings."
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
        f"Device Output:\n{output}\n\n------------------------------\n\n"
        f"Command issued:\n{command}\n\n"
        f"Explanation:\n{explanation}\n\n"
        f"Course of action:\n{course}\n\n"
        f"Summary:\n{summary}"
    )
