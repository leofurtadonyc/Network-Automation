# explanations/ospf_explanation.py

import re

def explain_ospf_neighbors(query, command, output, device_name="", baseline=None):
    """
    Generate a detailed explanation for OSPF neighbor queries.
    It parses the output to count the FULL adjacencies, compares them against expected neighbors
    from the baseline (if provided), and highlights any missing adjacencies.
    """
    # Split output into non-empty lines.
    lines = [line for line in output.splitlines() if line.strip()]
    # Assume neighbor ID is in the first column.
    actual_neighbors = [line.split()[0] for line in lines if line.split()]
    count = len(actual_neighbors)
    
    explanation = (
        f"This command displays OSPF neighbor adjacencies. The output shows {count} neighbor(s) in the FULL state: {', '.join(actual_neighbors)}.\n"
    )
    if baseline and baseline.get("backbone_interfaces"):
        expected_neighbors = [iface.get("peer") for iface in baseline.get("backbone_interfaces")
                              if iface.get("ospf_adjacency", "").lower() == "full"]
        explanation += f"Baseline expects these neighbors: {', '.join(expected_neighbors)}.\n"
        missing = [n for n in expected_neighbors if n not in actual_neighbors]
        if missing:
            explanation += f"Missing adjacencies: {', '.join(missing)}.\n"
        else:
            explanation += "All expected adjacencies are present.\n"
    course = (
        "Actions:\n"
        "  - If the number of FULL neighbors is lower than expected, verify physical connectivity and review OSPF configurations.\n"
        "  - Check OSPF logs for any error messages."
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
