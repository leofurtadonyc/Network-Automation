# explanations/bgp_explanation.py

import re

def explain_bgp_neighbors(query, command, output, device_name="", baseline=None):
    """
    Generate a detailed explanation for BGP neighbor queries.
    It extracts neighbor IPs from the output, counts them, and—if baseline data is provided—
    compares them with expected BGP peers.
    """
    # Assume lines starting with an IP address represent BGP neighbor entries.
    lines = [line for line in output.splitlines() if line.strip() and re.match(r'\d+\.\d+\.\d+\.\d+', line)]
    actual_neighbors = [line.split()[0] for line in lines]
    count = len(actual_neighbors)
    
    explanation = (
        f"This command displays the BGP neighbor summary. The output shows {count} neighbor(s): {', '.join(actual_neighbors)}.\n"
    )
    if baseline and baseline.get("bgp_peers"):
        expected = baseline.get("bgp_peers")
        explanation += f"Baseline expects these BGP neighbors: {', '.join(expected)}.\n"
        missing = [n for n in expected if n not in actual_neighbors]
        if missing:
            explanation += f"Missing BGP sessions: {', '.join(missing)}.\n"
        else:
            explanation += "All expected BGP sessions are established.\n"
    course = (
        "Actions:\n"
        "  - If any expected BGP session is missing or not established, review BGP configurations and underlying connectivity."
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
