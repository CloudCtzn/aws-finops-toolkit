import boto3
from datetime import datetime, timedelta, timezone

#-----CONFIGURATION-----
REGION = 'us-east-1'
DRY_RUN = True
IDLE_THRESHOLD_PERCENT = 2.0
#----------------------------

def get_max_cpu(cw.client, instance_id):
    """
    Queries CloudWatch for the MAX CPU utilization over the last 24 hours.
    Returns 0.o if no data is found.
    """
    # 1. TIME MATH: Always use UTC to match AWS backend
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=24)

    # 2. THE API CALL: Ask for 1-hour chunks (Period=3600)
    response = cw_client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceID', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=now,
        Period=3600,
        Statistics=['Maximum']
    )
    
    # 3. DEFENSIVE PARSING: Handle empty return
    datapoints = response.get('Datapoints', [])

    # 4. EXTRACTION: Find the highest peak in the last 24 hours
    max_cpu = max([dp['Maximum'] for dp in datapoints])
    return max_cpu
