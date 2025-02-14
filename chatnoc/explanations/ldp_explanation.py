# explanations/ldp_explanation.py

import re

def explain_ldp_neighbors(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for LDP neighbor queries.
    It extracts neighbor identifiers from the output, counts them, and compares with expected neighbors from the baseline.
    """
    actual_neighbors = re.findall(r'Peer LDP Ident:\s*([\d\.]+):', output)
    count = len(actual_neighbors)
    
    explanation = (
        f"This command displays LDP neighbor sessions. The output shows {count} neighbor(s): {', '.join(actual_neighbors)}.\n"
    )
    if baseline and baseline.get("backbone_interfaces"):
        expected = [iface.get("peer") for iface in baseline.get("backbone_interfaces")
                    if iface.get("ldp_session", "").lower() == "established"]
        explanation += f"Baseline expects these LDP neighbors: {', '.join(expected)}.\n"
        missing = [n for n in expected if n not in actual_neighbors]
        if missing:
            explanation += f"Missing LDP sessions: {', '.join(missing)}.\n"
        else:
            explanation += "All expected LDP sessions are established.\n"
    course = (
        "Actions:\n"
        "  - If any expected LDP session is missing, verify LDP configuration and network connectivity."
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

def explain_ldp_label_binding(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for LDP label binding queries.
    If baseline data is provided, compare the output with expected label bindings.
    """
    explanation = (
        "This command retrieves the LDP label binding for the specified destination prefix. "
        "For Cisco IOS XE devices, the command includes the mask value for specificity.\n"
    )
    if baseline and baseline.get("ldp_expected"):
        expected = baseline.get("ldp_expected")
        explanation += f"Baseline expects LDP bindings for: {', '.join(expected)}.\n"
    explanation += "Review the output to verify that the correct label is assigned."
    
    course = (
        "Actions:\n"
        "  - If the label binding is missing or incorrect, check the LDP session status and review the device configuration."
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
