from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_iam as iam


from constructs import Construct

class SaasStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. VPC
        self.vpc = ec2.Vpc(
            self, "SaasVpc",
            max_azs=2,  # default is all AZs in the region
            nat_gateways=1
        )

        # Security Groups
        self.alb_sg = ec2.SecurityGroup(self, "AlbSG", vpc=self.vpc, description="Allow public access to ALB", allow_all_outbound=True)
        self.web_sg = ec2.SecurityGroup(self, "WebSG", vpc=self.vpc, description="Allow traffic to WebApp", allow_all_outbound=True)
        self.api_sg = ec2.SecurityGroup(self, "ApiSG", vpc=self.vpc, description="Allow traffic to Django API", allow_all_outbound=True)
        self.celery_sg = ec2.SecurityGroup(self, "CelerySG", vpc=self.vpc, description="Celery worker SG", allow_all_outbound=True)
        self.redis_sg = ec2.SecurityGroup(self, "RedisSG", vpc=self.vpc, description="Redis access SG", allow_all_outbound=True)
        self.db_sg = ec2.SecurityGroup(self, "DbSG", vpc=self.vpc, description="PostgreSQL access SG", allow_all_outbound=True)
        
        # 2. ECS Cluster
        self.cluster = ecs.Cluster(
            self, "SaasCluster",
            vpc=self.vpc
        )

        # 3. PostgreSQL RDS
        db_secret = rds.DatabaseSecret(
            self, "DBSecret",
            username="saasuser"
        )
        
        self.db_instance = rds.DatabaseInstance(
            self, "SaasPostgres",
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            credentials=rds.Credentials.from_secret(db_secret),
            vpc=self.vpc,
            security_groups=[self.db_sg],
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            deletion_protection=False,
            publicly_accessible=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        # API and Celery talk to DB
        self.db_sg.add_ingress_rule(self.api_sg, ec2.Port.tcp(5432), "Allow API access to DB")
        self.db_sg.add_ingress_rule(self.celery_sg, ec2.Port.tcp(5432), "Allow Celery access to DB")

        # 4. Redis (containerized as Fargate service)
        redis_task_def = ecs.FargateTaskDefinition(self, "RedisTaskDef", cpu=256, memory_limit_mib=512)
        redis_container = redis_task_def.add_container(
            "RedisContainer",
            image=ecs.ContainerImage.from_registry("redis:7"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="redis")
        )
        redis_container.add_port_mappings(ecs.PortMapping(container_port=6379))

        self.redis_service = ecs.FargateService(
            self, "RedisService",
            cluster=self.cluster,
            task_definition=redis_task_def,
            desired_count=1,
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        self.redis_service.connections.add_security_group(self.redis_sg)
        # API and Celery talk to Redis
        self.redis_sg.add_ingress_rule(self.api_sg, ec2.Port.tcp(6379), "Allow API access to Redis")
        self.redis_sg.add_ingress_rule(self.celery_sg, ec2.Port.tcp(6379), "Allow Celery access to Redis")


        # 5. Django API Task Definition
        api_task_def = ecs.FargateTaskDefinition(self, "ApiTaskDef", cpu=512, memory_limit_mib=1024)

        api_container = api_task_def.add_container(
            "ApiContainer",
            image=ecs.ContainerImage.from_asset("../django"),  # adjust if needed
            logging=ecs.LogDriver.aws_logs(stream_prefix="api"),
            environment={
                "DEBUG": "False",
                "DJANGO_ALLOWED_HOSTS": "*",
                "CACHE_REDIS_URL": "redis://redis:6379/2",
                "DATABASE_NAME": "saasdb",
                "DATABASE_USER": "saasuser",
                "DATABASE_HOST": self.db_instance.db_instance_endpoint_address,
                "DATABASE_PORT": "5432",
                "CELERY_BROKER_URL": "redis://redis:6379/0",
                "CELERY_RESULT_BACKEND": "redis://redis:6379/1",
            },
            secrets={
                "DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(self.db_instance.secret, field="password"),
                "SECRET_KEY": ecs.Secret.from_secrets_manager(self.db_instance.secret),
            }
        )
        api_container.add_port_mappings(ecs.PortMapping(container_port=8000))

        # 6. Django API Service
        self.api_service = ecs.FargateService(
            self, "ApiService",
            cluster=self.cluster,
            task_definition=api_task_def,
            desired_count=1,
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        self.api_service.connections.add_security_group(self.api_sg)
        # WebApp talks to API
        self.api_sg.add_ingress_rule(self.web_sg, ec2.Port.tcp(8000), "Allow traffic from WebApp")

        # Allow ECS task to pull DB secret
        api_task_def.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[self.db_instance.secret.secret_arn]
            )
        )

        # 7. Celery Worker Task Definition
        celery_task_def = ecs.FargateTaskDefinition(self, "CeleryTaskDef", cpu=512, memory_limit_mib=1024)

        celery_container = celery_task_def.add_container(
            "CeleryContainer",
            image=ecs.ContainerImage.from_asset("../django"),  # same build as API
            command=["celery", "-A", "main_project", "worker", "--loglevel=info"],
            logging=ecs.LogDriver.aws_logs(stream_prefix="celery"),
            environment={
                "DEBUG": "False",
                "DJANGO_ALLOWED_HOSTS": "*",
                "CACHE_REDIS_URL": "redis://redis:6379/2",
                "DATABASE_NAME": "saasdb",
                "DATABASE_USER": "saasuser",
                "DATABASE_HOST": self.db_instance.db_instance_endpoint_address,
                "DATABASE_PORT": "5432",
                "CELERY_BROKER_URL": "redis://redis:6379/0",
                "CELERY_RESULT_BACKEND": "redis://redis:6379/1",
            },
            secrets={
                "DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(self.db_instance.secret, field="password"),
                "SECRET_KEY": ecs.Secret.from_secrets_manager(self.db_instance.secret),
            }
        )

        # 8. Celery Worker Service
        self.celery_service = ecs.FargateService(
            self, "CeleryService",
            cluster=self.cluster,
            task_definition=celery_task_def,
            desired_count=1,
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        self.celery_service.connections.add_security_group(self.celery_sg)

        celery_task_def.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[self.db_instance.secret.secret_arn]
            )
        )

        # 9. Web (Next.js) Frontend Task Definition
        
        web_task_def = ecs.FargateTaskDefinition(self, "WebTaskDef", cpu=512, memory_limit_mib=1024)

        web_container = web_task_def.add_container(
            "WebContainer",
            image=ecs.ContainerImage.from_asset("../web_app"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="web"),
            environment={
                "API_BASE_URL": f"http://{self.api_service.service_name}:8000"
            }
        )
        web_container.add_port_mappings(ecs.PortMapping(container_port=3000))

        # 10. Web Service with Public Load Balancer
        self.web_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WebAppService",
            cluster=self.cluster,
            task_definition=web_task_def,
            public_load_balancer=True,
            desired_count=1,
            listener_port=80,
        )

        self.web_service.service.connections.add_security_group(self.web_sg)
        self.web_service.load_balancer.add_security_group(self.alb_sg)

        # ALB forwards traffic to WebApp
        self.web_sg.add_ingress_rule(self.alb_sg, ec2.Port.tcp(3000), "Allow traffic from ALB")
        # 2. Ingress Rules
        # ALB should accept public traffic on HTTP (HTTPS to be added)
        self.alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP traffic")


