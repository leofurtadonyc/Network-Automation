import os
import datetime
from typing import Dict, Any

def create_audit_log_entry(operator: str, operator_ip: str, **kwargs: Any) -> Dict[str, Any]:
    entry = {
        'operator': operator,
        'operator_ip': operator_ip,
        'is_deactivate': kwargs.get('is_deactivate', False)
    }
    entry.update(kwargs)
    return entry

def write_audit_log(customer_name: str, audit_entries: list) -> str:
    audit_dir = 'audit_logs'
    os.makedirs(audit_dir, exist_ok=True)
    audit_file_name = f"{customer_name}_config_deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_audit.txt"
    audit_file_path = os.path.join(audit_dir, audit_file_name)

    with open(audit_file_path, 'w') as file:
        file.write(f"Operator: {audit_entries[0].get('operator', 'Unknown Operator')} from IP {audit_entries[0].get('operator_ip', 'Unknown IP')}\n")
        file.write(f"Completed at: {audit_entries[0].get('timestamp')}\n")
        file.write("--------------------------------------------------\n")
        for entry in audit_entries:
            file.write(f"Duration of execution: {entry.get('elapsed_time')}\n")
            file.write(f"Device: {entry.get('device_name', 'Unknown Device')} ({entry.get('device_type', 'unknown')})\n")
            file.write(f"Generated config file: {entry.get('configuration_path', 'No Path Available')}\n")
            file.write(f"Deployed config file: {entry.get('deployed_config_path', 'No Path Available')}\n")
            file.write(f"Deployment result: {'Success' if 'diff_results' in entry else 'Failure'}\n")

            diff = entry.get('diff_results', 'No changes detected.')
            if entry.get('is_deactivate', False):
                activation_status = "Deactivation"
            elif "No previous configuration to compare." in diff:
                activation_status = "First-time customer activation (no previous configuration found)."
            elif "No changes detected." in diff:
                activation_status = "Re-activation"
            else:
                activation_status = "Re-activation with service changes"

            file.write(f"Activation status: {activation_status}\n")
            file.write("Configuration differences:\n")
            file.write(f"{diff}\n")
            file.write("--------------------------------------------------\n")

    return audit_file_path

