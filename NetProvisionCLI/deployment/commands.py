def prepare_device_commands(device_type: str, configuration: str) -> list:
    return {
        'cisco_xe': ['config terminal', configuration, 'end', 'write memory', 'exit'],
        'cisco_xr': ['config terminal', configuration, 'commit', 'end', 'exit'],
        'juniper_junos': ['edit', configuration, 'commit', 'commit and-quit'],
        'huawei_vrp': ['system-view', configuration, 'return', 'save', 'Y', 'quit']
    }.get(device_type, [])
