import boto3

ec2_client_calgary = boto3.client('ec2', region_name="ca-west-1")
ec2_resource_calgary = boto3.resource('ec2', region_name="ca-west-1")

ec2_client_oregon = boto3.client('ec2', region_name="us-west-2")
ec2_resource_oregon = boto3.resource('ec2', region_name="us-west-2")

instance_ids_calgary = []
instance_ids_oregon = []

reservations_calgary = ec2_client_calgary.describe_instances()['Reservations']
for res in reservations_calgary:
    instances = res['Instances']
    for ins in instances:
        instance_ids_calgary.append(ins['InstanceId'])


response = ec2_resource_calgary.create_tags(
    Resources=instance_ids_calgary,
    Tags=[
        {
            'Key': 'environment',
            'Value': 'prod'
        },
    ]
)

reservations_oregon = ec2_client_oregon.describe_instances()['Reservations']
for res in reservations_oregon:
    instances = res['Instances']
    for ins in instances:
        instance_ids_oregon.append(ins['InstanceId'])


response = ec2_resource_oregon.create_tags(
    Resources=instance_ids_oregon,
    Tags=[
        {
            'Key': 'environment',
            'Value': 'dev'
        },
    ]
)
