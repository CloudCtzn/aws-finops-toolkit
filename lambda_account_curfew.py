import boto3

#Intialize the Client

ec2 = boto3.client('ec2', region_name='us-east-1')

def lambda_handler(event, context):
    print("-----The ACOUNT CURFEW has started------")


    # 1. The filter: Targeting EVERYTHING that is currently running in a particular account
    # We are not checking for tags, if its on, then its a target. 
    running_filter = [
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]
    
    # 2. Find the violators
    response = ec2.describe_instances(Filters=running_filter)

    violators = []
    # 3. Build the list 
    for reservation in response['Reservation']:
        for instance in reservation['Instance']:
            violators.append(instance['InstanceId'])

    # 4. Enforce the curfew 
    if violators:
        print(f"Found {len(violators)} run instances: {violators}")
        print("Enforcing curfew now....")

        # Stop them all in ONE API call
        ec2.stop_instance(InstanceIds=violators)

        msg = f"Curfew enforced. {len(violators)} instances have been stopped"
        print(msg)
        return{"statusCode": 200, "body": msg}
    
    else:
        print("Account is silent. No instances running")
        return{"statusCode": 200, "body": "All quiet on the Eastern Front"}





