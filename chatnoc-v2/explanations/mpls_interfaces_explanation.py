# explanations/mpls_interfaces_explanation.py

def explain_mpls_interfaces(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays MPLS interfaces on the device. It shows which interfaces are MPLS-enabled "
        "and may also provide details about associated labels."
    )
    course = (
        "Actions:\n"
        "  - Verify that the expected interfaces are MPLS-enabled.\n"
        "  - If any interfaces are missing or misconfigured, review the MPLS configuration on the device."
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
