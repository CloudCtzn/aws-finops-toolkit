import boto3
import datetime

#----------Configuration---------------
DRY_RUN = False # Set to False to actually delete
RETENTION_DAYS = -1 # How many days to keep snapshots

ec2 = boto3.client('ec2', region_name='us-east-1')

def calculate_age(creation_date):
    # 1. Get "now" in UTC (so it matches AWS time)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - creation_date).days

# 3. Now to ONLY get the snapshots 
response = ec2.describe_snapshots(OwnerIds=['self'])

print("----Snapshot Reaper Started----")

for snapshot in response['Snapshots']:
    snap_id = snapshot['SnapshotId']
    age = calculate_age(snapshot['StartTime'])

    print(f"Checking {snap_id} ({age} days old)...")

    # 4. The logic gate
    if age > RETENTION_DAYS:
        if DRY_RUN:
            print(f" [DRY RUN] Would delete {snap_id} (Older than {RETENTION_DAYS} days....)")
        else:
            print(f" [ACTION] Deleting {snap_id}.....")

            # The API call for deletion
            try:
                ec2.delete_snapshot(SnapshotId=snap_id)
                print(f"{snap_id} successfully deleted......")
            except Exception as e:
                print(f" --> ERROR {e}")

    else:
        print(f" [SKIP] Newer than {RETENTION_DAYS} days....")



print("------------------------------------------------------------")