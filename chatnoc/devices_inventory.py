# devices_inventory.py
import os
import yaml

class NetworkDevice:
    def __init__(self, name, device_role, device_type, mgmt_address, loopback_address):
        self.name = name
        self.device_role = device_role
        self.device_type = device_type
        self.mgmt_address = mgmt_address
        self.loopback_address = loopback_address

    def __repr__(self):
        return (f"NetworkDevice(name={self.name}, device_type={self.device_type}, "
                f"mgmt_address={self.mgmt_address})")

class DeviceInventory:
    def __init__(self, inventory_file="devices.yaml"):
        self.inventory_file = inventory_file
        self.devices = self.load_inventory()

    def load_inventory(self):
        if not os.path.exists(self.inventory_file):
            raise FileNotFoundError(f"Device inventory file {self.inventory_file} not found.")
        with open(self.inventory_file, "r") as f:
            data = yaml.safe_load(f)
        devices = []
        for name, attributes in data.items():
            device = NetworkDevice(
                name=name,
                device_role=attributes.get("device_role"),
                device_type=attributes.get("device_type"),
                mgmt_address=attributes.get("mgmt_address"),
                loopback_address=attributes.get("loopback_address")
            )
            devices.append(device)
        return devices

    def get_devices_by_role(self, role):
        return [device for device in self.devices if device.device_role.lower() == role.lower()]

    def get_device_by_name(self, name):
        """Search for a device with the matching hostname (name)."""
        for device in self.devices:
            if device.name.lower() == name.lower():
                return device
        return None

if __name__ == "__main__":
    inventory = DeviceInventory()
    print("All devices:")
    for device in inventory.devices:
        print(device)
