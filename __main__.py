from pulumi import export, ResourceOptions
import pulumi_aws as aws
import json

# New VPC with two subnets in different AZ. Internet Gateway and public internet access.

vpc = aws.ec2.Vpc("main", cidr_block="10.0.0.0/16")

subnet_a = aws.ec2.Subnet("subnet-a", vpc_id=vpc.id, cidr_block="10.0.1.0/24", availability_zone='us-east-1a' )
subnet_b = aws.ec2.Subnet("subnet-b", vpc_id=vpc.id, cidr_block="10.0.2.0/24", availability_zone='us-east-1b' )

igw = aws.ec2.InternetGateway("ig-main", vpc_id=vpc.id)

# Add internet gateway to main_route_table

inet_route = aws.ec2.Route("inet-route", route_table_id=vpc.main_route_table_id, destination_cidr_block="0.0.0.0/0", gateway_id=igw.id)

# Security group for public web access

sg_web = aws.ec2.SecurityGroup('public-web', vpc_id=vpc.id, description='Public HTTP access', 
	ingress=[aws.ec2.SecurityGroupIngressArgs(protocol='tcp', from_port=80, to_port=80, cidr_blocks=['0.0.0.0/0'])],
  	egress=[aws.ec2.SecurityGroupEgressArgs(protocol='-1', from_port=0, to_port=0, cidr_blocks=['0.0.0.0/0'] )],
)

# Application Load balancer on port 80

alb = aws.lb.LoadBalancer('app-lb', security_groups=[sg_web.id], subnets=[subnet_a.id, subnet_b.id])
atg = aws.lb.TargetGroup('app-tg', port=80, protocol='HTTP', target_type='ip', vpc_id=vpc.id)
wl = aws.lb.Listener('web', load_balancer_arn=alb.arn, port=80, default_actions=[aws.lb.ListenerDefaultActionArgs(type='forward', target_group_arn=atg.arn)])


# ECS Cluster for Fargate

cluster = aws.ecs.Cluster('cluster')

# Create an IAM role that can be used by our service's task.
role = aws.iam.Role('task-exec-role',	assume_role_policy=json.dumps({		'Version': '2008-10-17', 'Statement': [{'Sid': '','Effect': 'Allow', 'Principal': {'Service': 'ecs-tasks.amazonaws.com'	},'Action': 'sts:AssumeRole' }]	}))

rpa = aws.iam.RolePolicyAttachment('task-exec-policy', role=role.name, policy_arn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy')

# Spin up a load balanced service running our container image.

task_definition = aws.ecs.TaskDefinition('app-task', family='fargate-task-definition', cpu='256', memory='512',
    network_mode='awsvpc', requires_compatibilities=['FARGATE'], execution_role_arn=role.arn, 
    container_definitions=json.dumps([{ 'name': 'my-app', 'image': 'nginx', 'portMappings': [{ 'containerPort': 80, 'hostPort': 80, 'protocol': 'tcp' }] }])
)

# Three instances running
service = aws.ecs.Service('app-svc', cluster=cluster.arn, desired_count=3, launch_type='FARGATE', task_definition=task_definition.arn, network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(	assign_public_ip=True, subnets=[subnet_a.id, subnet_b.id], security_groups=[sg_web.id]),
    load_balancers=[aws.ecs.ServiceLoadBalancerArgs(target_group_arn=atg.arn, container_name='my-app', container_port=80, )],
    opts=ResourceOptions(depends_on=[wl]),
)

# Print the FQDN for my-app
export('url', alb.dns_name)
