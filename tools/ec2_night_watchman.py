import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

dev_filter = [{
      'Name': 'tag:Environment',
      'Values': ['Dev']
}]
# 1. Get the big blob of data 
response = ec2.describe_instances(Filters=dev_filter)

# 2. Loop 1: Go through the "Reservations" (The groups)
for reservation in response['Reservations']:
   for instance in reservation['Instances']:
      # 1. Grab the ID while inside the loop 
      inst_id = instance["InstanceId"]

      # 2. Announce it 
      print(f"Stopping Dev Instances: {inst_id}")

      # 3. Stop the instance(s) (This happens immediately, one by one)
      ec2.stop_instances(InstanceIds=[inst_id])

      print("----Dev Servers have been stopped for the evening----")
