from influxdb_client import InfluxDBClient, BucketsApi, BucketRetentionRules

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
buckets_api.create_bucket(bucket_name=influxdb_bucket, retention_rules=retention_rules, org_id=client.organizations_api().find_organizations(org=influxdb_org)[0].id)

print(f"Bucket '{influxdb_bucket}' has been reset.")
