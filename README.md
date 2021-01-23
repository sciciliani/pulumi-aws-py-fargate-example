# Pulumi project in Python to deploy NGINX webserver in containers using AWS ECS Fargate

## Prerequisites

* [Install Pulumi](https://www.pulumi.com/docs/get-started/install/)
* [Configure Pulumi to Use AWS](https://www.pulumi.com/docs/intro/cloud-providers/aws/setup/) (if your AWS CLI is configured, no further changes are required)
* Clone repo and run the following commands

    ```bash
    git clone https://github.com/sciciliani/pulumi-aws-py-fargate-example
    cd pulumi-aws-py-fargate-example
    pulumi stack init dev
    pulumi config set aws:region us-east-1 # any valid AWS region will work
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

## Running the Example

1. Deploy everything with a single `pulumi up` command. 

    ```bash
    $ pulumi up
    ```

    After being prompted and selecting "yes", your deployment will begin. It'll complete in a few minutes:

    ```bash
    Updating (dev):
         Type                             Name                Status
     +   pulumi:pulumi:Stack              aws-py-fargate-dev  created     
     +   ├─ aws:iam:Role                  task-exec-role      created     
     +   ├─ aws:ec2:Vpc                   main                created     
     +   ├─ aws:ecs:Cluster               cluster             created     
     +   ├─ aws:ecs:TaskDefinition        app-task            created     
     +   ├─ aws:iam:RolePolicyAttachment  task-exec-policy    created     
     +   ├─ aws:ec2:InternetGateway       ig-main             created     
     +   ├─ aws:ec2:Subnet                subnet-a            created     
     +   ├─ aws:ec2:Subnet                subnet-b            created     
     +   ├─ aws:ec2:SecurityGroup         public-web          created     
     +   ├─ aws:lb:TargetGroup            app-tg              created     
     +   ├─ aws:ec2:Route                 inet-route          created     
     +   ├─ aws:lb:LoadBalancer           app-lb              created     
     +   ├─ aws:lb:Listener               web                 created     
     +   └─ aws:ecs:Service               app-svc             created     
 
    Outputs:
        url: "app-lb-ad43707-1433933240.us-west-2.elb.amazonaws.com"

    Resources:
        + 15 created

    Duration: 2m56s

    ```

   Notice that the automatically assigned load-balancer URL is printed as a stack output.

2. Open a browser to the output url. In example: `app-lb-ad43707-1433933240.us-west-2.elb.amazonaws.com`
   
3. Once you are done, you can destroy all of the resources, and the stack:

    ```bash
    $ pulumi destroy
    $ pulumi stack rm
    ```
