import boto3


#-----Configuration-----
DRY_RUN = False
#-----------------------

ec2 = boto3.client('ec2', region_name='us-east-1')

response = ec2.describe_addresses()

print("-----Elastic IP Audit-------")

for eip in response['Addresses']:
    public_ip = eip['PublicIp']
    allocation_id = eip['AllocationId']

    # The Logic: Check if AssociationId exists in the dictionary
    if 'AssociationID' not in eip:
        print(f"Found Lonely IP: {public_ip}")

        if DRY_RUN:
            print(f" [DRY RUN] Would release {public_ip}")
        else:
            print(f" [ACTION] Releasing {public_ip} back to AWS pool....")
            try:
                # release_address uses ALlocationId not the IP Address 
                ec2.release_address(AllocationId=allocation_id)
                print(f" EIP: {public_ip} released.....")
            except Exception as e:
                print(f" --> Error: {e}")

    else:
        print(f" IP {public_ip} is attached to {eip.get('InstanceID')}. Keeping.")

print("---------------------------------")
