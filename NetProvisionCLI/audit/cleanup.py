import os
import json
from typing import Optional
from audit.audit_log import create_audit_log_entry

def cleanup_generated_configs(customer_name: str, audit_entries: list, operator: str, operator_ip: str, directory: str = 'generated_configs') -> None:
    for filename in os.listdir(directory):
        if filename.startswith(customer_name) and (filename.endswith(".txt") or filename.endswith(".json")):
            os.remove(os.path.join(directory, filename))
            audit_entries.append(create_audit_log_entry(operator, operator_ip, action='Removed', file=filename))

def check_for_error_logs(customer_name: str, directory: str = 'generated_configs') -> Optional[dict]:
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    if os.path.exists(error_path):
        with open(error_path, 'r') as file:
            return json.load(file)
    return None
