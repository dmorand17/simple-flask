# dockerized-flask

## Build

Local build

```bash
docker build -t dockerized-flask .
```

Multi-arch builds

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION:-us-east-1} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION:-us-east-1}.amazonaws.com

# Build for amd64 and arm64
docker buildx build -t "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION:-us-east-1}.amazonaws.com/dockerized-flask:latest" --platform linux/amd64,linux/arm64 --push .
```

## Test

```bash
docker run -itd --name dockerized-flask -p 5000:5000 dockerized-flask
```

## AWS Deployment

1. Create ECR repository

```bash
aws ecr create-repository \
--repository-name dockerized-flask \
--image-scanning-configuration scanOnPush=true \
--region us-east-1
```

1. Create new ECS cluster

```bash
aws ecs create-cluster \
--cluster-name MultiArchCluster
```

2. Add IAM roles

```bash

```

1. Create task definition

```bash
# Create task definition(s)
aws ecs register-task-definition --cli-input-json file://aws/ecs-task-definition-fargate-arm64.json
aws ecs register-task-definition --cli-input-json file://aws/ecs-task-definition-fargate-x86_64.json
```

1. Create services

```bash
aws ecs create-service \
    --cluster MultiArchCluster \
    --service-name DockerFlask-ARM64 \
    --task-definition dockerized-flask-arm64 \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-05879663ec53b5775,subnet-031c93cffa8b58491],securityGroups=[sg-03f0220e12fdbace3],assignPublicIp=ENABLED}"

aws ecs create-service \
    --cluster MultiArchCluster \
    --service-name DockerFlask-x86_64 \
    --task-definition dockerized-flask-x86_64 \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-05879663ec53b5775,subnet-031c93cffa8b58491],securityGroups=[sg-03f0220e12fdbace3],assignPublicIp=ENABLED}"
```

1. Update service (examples)

```bash
# Enable execute command
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition dockerized-flask-ARM64 \
    --service DockerFlask-ARM64 \
    --enable-execute-command \
    --force-new-deployment

# Add ALB
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition dockerized-flask-x86_64 \
    --service DockerFlask-x86_64 \
    --force-new-deployment \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:152539975130:targetgroup/alb-ecs-dockerized-flask-x86-64/a81b52e7686e1b83,loadBalancerName=alb-ecs-dockerized-flask,containerName=flask-app,containerPort=5000"

# Update networking configuration
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition dockerized-flask-x86_64 \
    --service DockerFlask-x86_64 \
    --force-new-deployment \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-05879663ec53b5775,subnet-031c93cffa8b58491],securityGroups=[sg-03f0220e12fdbace3],assignPublicIp=ENABLED}"

```
