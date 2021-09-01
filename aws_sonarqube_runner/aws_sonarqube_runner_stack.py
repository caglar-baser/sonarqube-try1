from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core
from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs,
                     aws_ecs_patterns as ecs_patterns)




class AwsSonarqubeRunnerStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        vpc = ec2.Vpc(self, "Vpc", max_azs=2,subnet_configuration=[
            ec2.SubnetConfiguration(
            name = 'Public-Subnet',
            subnet_type = ec2.SubnetType.PUBLIC,
            cidr_mask = 26
            ),
            ],

            )     # default is all AZs in region

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)


        security_group = ec2.SecurityGroup(
                self,
                "SonarQube-SecGroup",
                vpc=vpc,
                allow_all_outbound=True
            )

        security_group.add_ingress_rule(
                ec2.Peer.any_ipv4(),
                ec2.Port.tcp(9000)
            )

        security_group.add_ingress_rule(
                ec2.Peer.any_ipv4(),
                ec2.Port.tcp(80)
            )

        
        task_definiton = ecs.FargateTaskDefinition(self, "Taskdef",
            memory_limit_mib = 2048,
            cpu = 256,
            
            )

        container = task_definiton.add_container("sonarqube",
            image = ecs.ContainerImage.from_registry("sonarqube:community"),

            )

        container.add_port_mappings(
                ecs.PortMapping(
                    container_port=9000,
                )
            )
          


        service = ecs.FargateService(self,"Service",
         cluster=cluster,
         task_definition = task_definiton,
         assign_public_ip = True,
         desired_count = 1,
         vpc_subnets = { 'subnet_type':ec2.SubnetType.PUBLIC},
         security_group = security_group
         )
        


        #ecs_patterns.ApplicationLoadBalancedFargateService(self, "FargateService",
         #  cluster=cluster,            # Required
          # cpu=256,                    # Default is 256
           #desired_count=1,            # Default is 1
            #task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
             #   image=ecs.ContainerImage.from_registry("sonarqube:community"),
              #  container_port=9000),
            #assign_public_ip = True,
            #memory_limit_mib=1024,      # Default is 512
            #public_load_balancer=True)  # Default is False