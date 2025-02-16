# inventory/devices_inventory.py
import os
import yaml

class Device:
    def __init__(self, name, device_role, device_type, mgmt_address, loopback_address, ssh_port=22):
        self.name = name.lower()  # normalize to lowercase
        self.device_role = device_role
        self.device_type = device_type
        self.mgmt_address = mgmt_address
        self.loopback_address = loopback_address
        self.ssh_port = ssh_port

    def __repr__(self):
        return f"<Device {self.name}: {self.device_type} at {self.mgmt_address}, port {self.ssh_port}>"

class DeviceInventory:
    def __init__(self, filename="inventory/devices.yaml"):
        self.devices = {}
        self.filename = filename
        self.load_devices()

    def load_devices(self):
        if os.path.isfile(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = yaml.safe_load(f)
                    for name, info in data.items():
                        device = Device(
                            name=name,
                            device_role=info.get("device_role", ""),
                            device_type=info.get("device_type", ""),
                            mgmt_address=info.get("mgmt_address", ""),
                            loopback_address=info.get("loopback_address", ""),
                            ssh_port=info.get("ssh_port", 22)
                        )
                        self.devices[name.lower()] = device
            except Exception as e:
                print(f"Error loading devices from {self.filename}: {e}")
        else:
            print(f"Devices file {self.filename} not found.")

    def get_device_by_name(self, name):
        return self.devices.get(name.lower())

    def get_all_devices(self):
        return list(self.devices.values())
