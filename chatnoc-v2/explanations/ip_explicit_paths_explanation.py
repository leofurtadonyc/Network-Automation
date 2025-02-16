# explanations/ip_explicit_paths_explanation.py

def explain_ip_explicit_paths(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays explicit paths for routing. It shows the specific path a packet will take through the network, "
        "which is helpful for verifying routing policies and path selection."
    )
    course = (
        "Actions:\n"
        "  - Verify that the explicit paths match your routing policies.\n"
        "  - Check for any discrepancies that may indicate misconfiguration."
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
