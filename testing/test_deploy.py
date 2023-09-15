import boto3
import requests
import urllib3

# Disable SSL warnings for self-signed certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Boto3 clients
ec2_client = boto3.client('ec2')
elbv2_client = boto3.client('elbv2')

# Define the expected configurations
vpc_cidr = '10.0.0.0/16'
igw_attached = False
subnets = [
    {'az': 'us-east-1a', 'cidr': '10.0.0.0/24'},
    {'az': 'us-east-1b', 'cidr': '10.0.1.0/24'}
]
route_table_cidr = '0.0.0.0/0'

# Define the expected security group rules
http_ingress_rule = {
    'from_port': 80,
    'to_port': 80,
    'protocol': 'tcp',
    'cidr_blocks': ['0.0.0.0/0']
}

https_ingress_rule = {
    'from_port': 443,
    'to_port': 443,
    'protocol': 'tcp',
    'cidr_blocks': ['0.0.0.0/0']
}


def check_security_group_rule_exists(group_id, ingress_rule):
    response = ec2_client.describe_security_groups(GroupIds=[group_id])
    if 'SecurityGroups' in response:
        for group in response['SecurityGroups']:
            for ingress in group.get('IpPermissions', []):
                if (
                    ingress.get('FromPort') == ingress_rule['from_port'] and
                    ingress.get('ToPort') == ingress_rule['to_port'] and
                    ingress.get('IpProtocol') == ingress_rule['protocol'] and
                    any(ip_range['CidrIp'] in ingress_rule['cidr_blocks'] for ip_range in ingress.get('IpRanges', []))
                ):
                    return True
    return False

# Function to get the security group ID by tag or name
def get_security_group_id():
    response = ec2_client.describe_security_groups(Filters=[
        {'Name': 'tag:project', 'Values': ['erict-challenge']},
        {'Name': 'group-name', 'Values': ['erict-challenge-sg']}
    ])
    if 'SecurityGroups' in response:
        for group in response['SecurityGroups']:
            return group['GroupId']
    return None

# Function to check if EC2 instances with the specified tag 'project: erict-challenge' and state 'running' exist
def check_running_instances_exist():
    response = ec2_client.describe_instances(Filters=[
        {'Name': 'tag:project', 'Values': ['erict-challenge']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ])
    instances = response.get('Reservations', [])
    if len(instances) >= 2:
        return True
    return False

# Function to check if a VPC with the specified CIDR block and tag exists
def check_vpc_exists():
    response = ec2_client.describe_vpcs(Filters=[
        {'Name': 'tag:project', 'Values': ['erict-challenge']},
        {'Name': 'cidr', 'Values': [vpc_cidr]}
    ])
    return len(response['Vpcs']) > 0

# Function to check if an Internet Gateway is associated with the VPC
def check_igw_exists(vpc_id):
    response = ec2_client.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
    return len(response['InternetGateways']) > 0

# Function to check if subnets with the specified CIDR blocks exist
def check_subnets_exist(vpc_id):
    response = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    existing_subnets = set(subnet['CidrBlock'] for subnet in response['Subnets'])
    
    for expected_subnet in subnets:
        if expected_subnet['cidr'] not in existing_subnets:
            return False
    return True

# Function to check if a route table with the specified CIDR block and Internet Gateway exists
def check_route_table_exists(vpc_id):
    response = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    
    for route_table in response['RouteTables']:
        for route in route_table['Routes']:
            if route.get('DestinationCidrBlock') == route_table_cidr and 'GatewayId' in route:
                return True
    return False


def check_http_ingress_rule_exists(group_id):
    return check_security_group_rule_exists(group_id, http_ingress_rule)


def check_https_ingress_rule_exists(group_id):
    return check_security_group_rule_exists(group_id, https_ingress_rule)

# Function to check the load balancer endpoint
def check_load_balancer_endpoint():
    try:
        # Get the load balancer DNS name dynamically
        lb_response = elbv2_client.describe_load_balancers(Names=['erict-challenge-lb'])
        if 'LoadBalancers' in lb_response:
            load_balancer_dns_name = lb_response['LoadBalancers'][0]['DNSName']

            endpoint_url = f"https://{load_balancer_dns_name}/we_are.html"

            # Check if the endpoint responds with a 200 OK status code using HTTPS
            response = requests.get(endpoint_url, verify=False)
            if response.status_code != 200:
                print("Load balancer endpoint check failed: HTTPS status code is not 200.")
                return False

            # Load the expected HTML content from a local file and close the file
            with open('app/we_are.html', 'r') as file:
                expected_html = file.read()

            # Check if the endpoint responds with the expected HTML body
            if response.text.strip() != expected_html.strip():
                print("Load balancer endpoint check failed: HTTPS response body does not match the expected HTML.")
                return False

            # Check if the HTTP redirect responds with the same HTML body
            http_response = requests.get(endpoint_url.replace('https://', 'http://'), verify=False)
            if http_response.text.strip() != expected_html.strip():
                print("Load balancer endpoint check failed: HTTP response body does not match the expected HTML.")
                return False

            return True
        else:
            print("Load balancer with tag 'project: erict-challenge' not found.")
            return False
    except Exception as e:
        print("Error checking load balancer endpoint:", str(e))
        return False

# Get the security group ID
security_group_id = get_security_group_id()

# Check if the VPC exists
if check_vpc_exists() and security_group_id:
    vpc_id = ec2_client.describe_vpcs(Filters=[{'Name': 'tag:project', 'Values': ['erict-challenge']}])['Vpcs'][0]['VpcId']
    
    # Check if an Internet Gateway is associated with the VPC
    igw_attached = check_igw_exists(vpc_id)
    
    # Check if subnets with the specified CIDR blocks exist
    subnets_exist = check_subnets_exist(vpc_id)
    
    # Check if a route table with the specified CIDR block and Internet Gateway exists
    route_table_exists = check_route_table_exists(vpc_id)
    
    # Check if the HTTP security group rule exists
    http_rule_exists = check_http_ingress_rule_exists(security_group_id)
    
    # Check if the HTTPS security group rule exists
    https_rule_exists = check_https_ingress_rule_exists(security_group_id)
    
    # Check if two running instances with the same tag 'project: erict-challenge' exist
    instances_exist = check_running_instances_exist()

    # Check the load balancer endpoints
    conditions = {
        'VPC exists': check_vpc_exists(),
        'Internet Gateway attached': igw_attached,
        'Subnets exist': subnets_exist,
        'Route table exists': route_table_exists,
        'HTTP security group rule exists': http_rule_exists,
        'HTTPS security group rule exists': https_rule_exists,
        'Running instances exist': instances_exist,
        'Load balancer endpoint checks passed': check_load_balancer_endpoint()
    }

    for condition, condition_met in conditions.items():
        if not condition_met:
            print("Condition '{}' failed.".format(condition))

    if all(conditions.values()):
        print("All conditions are met. AWS objects, security group rules, and load balancer endpoints created by Terraform are verified, and running instances are healthy.")
    else:
        print("Verification failed for one or more conditions.")
else:
    print("VPC with CIDR block {} and tag 'project: erict-challenge' or security group with name 'erict-challenge-sg' does not exist.".format(vpc_cidr))
