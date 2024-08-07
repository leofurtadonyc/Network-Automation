import argparse
import getpass
from influxdb_client import InfluxDBClient, BucketRetentionRules

def load_settings():
    """Load settings from the settings.yaml file."""
    import yaml
    try:
        with open('settings/settings.yaml', 'r') as file:
            settings = yaml.safe_load(file)
            return settings
    except FileNotFoundError:
        print("settings.yaml file not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing settings.yaml file: {e}")
        return {}

def display_warning_banner():
    """Display a warning banner."""
    banner = """
******************************************************
* WARNING: This operation will delete the entire     *
* InfluxDB 'netprovision' bucket and recreate it.    *
* This action is irreversible.                       *
******************************************************
"""
    print(banner)

def confirm_deletion(password):
    """Confirm deletion by requiring the operator to type 'YES' and the password again."""
    confirmation = input("Type 'YES' to confirm: ")
    if confirmation != "YES":
        print("Operation aborted.")
        return False

    confirm_password = getpass.getpass("Please type your password again to confirm: ")
    if confirm_password != password:
        print("Password does not match. Operation aborted.")
        return False

    return True

def reset_influxdb_bucket(username, password):
    settings = load_settings()
    influxdb_url = settings['influxdb']['url']
    influxdb_token = settings['influxdb']['token']
    influxdb_org = settings['influxdb']['org']
    influxdb_bucket = settings['influxdb']['bucket']

    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    buckets_api = client.buckets_api()

    # Delete the bucket
    bucket = buckets_api.find_bucket_by_name(influxdb_bucket)
    if bucket:
        buckets_api.delete_bucket(bucket)

    # Recreate the bucket with a 30-day retention policy
    retention_rules = BucketRetentionRules(type="expire", every_seconds=30*24*60*60)
    org_id = client.organizations_api().find_organizations(org=influxdb_org)[0].id
    buckets_api.create_bucket(bucket_name=influxdb_bucket, retention_rules=retention_rules, org_id=org_id)

    print(f"Bucket '{influxdb_bucket}' has been reset.")

def main():
    parser = argparse.ArgumentParser(description="Reset InfluxDB netprovision bucket.")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")

    args = parser.parse_args()
    password = args.password

    if not password:
        password = getpass.getpass("Password: ")

    display_warning_banner()

    if confirm_deletion(password):
        reset_influxdb_bucket(args.username, password)
    else:
        print("Operation not confirmed. Exiting.")

if __name__ == "__main__":
    main()
