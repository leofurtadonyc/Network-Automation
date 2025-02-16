# healthcheck/healthcheck.py

def run_health_check_for_device(device, baseline):
    """
    Run health check on the given device based on the provided baseline.
    For demonstration purposes, this function simulates checking if expected strings
    (e.g. interface statuses, neighbor states) from the baseline are present in the device's
    last output. In a real scenario, you would parse and compare specific values.
    """
    # For example, we assume the baseline is a dict with expected keywords.
    # We'll simulate by checking if each expected keyword appears in device.last_output.
    # (Assume device.last_output is set after a previous command.)
    results = {}
    device_output = getattr(device, "last_output", "")
    for check, expected in baseline.items():
        if expected in device_output:
            results[check] = "OK"
        else:
            results[check] = "Issue detected"
    return results

def print_health_check_results(device_name, results):
    """
    Print health check results in a formatted manner.
    """
    print(f"Health Check Results for {device_name}:")
    for category, status in results.items():
        print(f"  - {category}: {status}")
