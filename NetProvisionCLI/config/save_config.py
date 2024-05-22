import os
import datetime

def save_deployed_config(customer_name: str, device_name: str, configuration: str) -> str:
    deployed_dir = 'deployed_configs'
    os.makedirs(deployed_dir, exist_ok=True)
    filename = f"{customer_name}_{device_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.join(deployed_dir, filename)
    with open(file_path, 'w') as file:
        file.write(configuration)
    return file_path
