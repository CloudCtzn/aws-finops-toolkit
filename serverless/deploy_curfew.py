import boto3
import json
import time 
import zipfile
import os 

#----Configuration-----
AWS_REGION = 'us-east-1'
FUNCTION_NAME = 'AccountCurfewFunction'
ROLE_NAME = 'AccountCurfewRole'
FILE_TO_DEPLOY = 'lambda_account_curfew.py'
HANDLER = 'lambda_account_curfew.lambda_handler'
CRON_SCHEDULE = 'cron(0 1 * * ? *)' 
#-----------------------

iam = boto3.client('iam', region_name=AWS_REGION)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
events = boto3.client('events', region_name=AWS_REGION)

def create_iam_role():
    print(f"1. Creating IAM Role: {ROLE_NAME}...")
    
    # 1. The Trust Policy (Strictly for AssumeRole)
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        role_arn = role['Role']['Arn']
        print(f"   -> Role Created: {role_arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        print("   -> Role already exists. Fetching ARN...")
        role = iam.get_role(RoleName=ROLE_NAME)
        role_arn = role['Role']['Arn']

    # 2. Attach Permissions (What can this role do?)
    print("   -> Attaching permissions...")
    iam.attach_role_policy(RoleName=ROLE_NAME, PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess')
    iam.attach_role_policy(RoleName=ROLE_NAME, PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
    
    # CRITICAL: IAM roles take a few seconds to propagate.
    print("   -> Waiting 10s for role to propagate...")
    time.sleep(10) 
    return role_arn

def create_zip_file():
    print(f"2. Zipping Code: {FILE_TO_DEPLOY}...")
    zip_name = 'function.zip'
    with zipfile.ZipFile(zip_name, 'w') as z:
        z.write(FILE_TO_DEPLOY)
    return zip_name

def deploy_lambda(role_arn, zip_name):
    print(f"3. Deploying Lambda: {FUNCTION_NAME}...")
    
    with open(zip_name, 'rb') as f:
        zipped_code = f.read()

    try:
        response = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.14',  
            Role=role_arn,
            Handler=HANDLER,
            Code={'ZipFile': zipped_code},
            Timeout=10
        )
        print(f"--> Function Created: {response['FunctionArn']}")
        return response['FunctionArn']
    except lambda_client.exceptions.ResourceConflictException:
        print("--> Function already exists. Updating code....")
        lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zipped_code
        )
        return lambda_client.get_function(FunctionName=FUNCTION_NAME)['Configuration']['FunctionArn']
    
def setup_scheduler(function_arn):
    print("4. Setting up EventBridge Scheduler...")
    rule_name='DailyAccountCurfew'

    #1. Create Rule
    events.put_rule(
        Name=rule_name,
        ScheduleExpression=CRON_SCHEDULE,
        State='ENABLED'
    )

    # 2. Add Lambda as Target
    events.put_targets(
        Rule=rule_name,
        Targets=[{'Id': '1', 'Arn': function_arn}]
    )

    # 3. Grant Permissison (Allow EventBridge to invoke Lambda)
    try:
        lambda_client.add_permission(
            FunctionName=FUNCTION_NAME,
            StatementId='EventBridgeInvoke',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=f"arn:aws:events:{AWS_REGION}:{boto3.client('sts').get_caller_identity()['Account']}:rule/{rule_name}"
        )
    except lambda_client.exceptions.ResourceConflictException:
        pass # Permission already exists
    print("--> Scheduler Configured!")

#-------Execution-------
if __name__ == '__main__':
    if not os.path.exists(FILE_TO_DEPLOY):
        print(f"ERROR: Cannot find {FILE_TO_DEPLOY}. Make sure you are in the right folder..")
    else:
        role_arn = create_iam_role()
        zip_file = create_zip_file()
        func_arn = deploy_lambda(role_arn, zip_file)
        setup_scheduler(func_arn)

        #Clean up local zip
        if os.path.exists(zip_file):
            os.remove(zip_file)
        print("--- Deployment Complete ---")