# explanations/version_explanation.py

def explain_version(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for full version queries.
    """
    explanation = (
        "This command displays detailed version information for the device, including hardware, software, and uptime details.\n"
        "It is useful for verifying the device's software release and diagnosing issues related to version mismatches."
    )
    course = (
        "Actions:\n"
        "  - Review the version output to ensure the device is running the expected software.\n"
        "  - Check for any anomalies that might require a software upgrade or configuration adjustment."
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
