import yaml

def load_yaml(yaml_path: str) -> dict:
    """Load device data from a YAML file."""
    try:
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
            return data['devices']
    except FileNotFoundError:
        print(f"YAML file {yaml_path} not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {yaml_path}: {e}")
        return {}
