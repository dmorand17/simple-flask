# simple-flask

A Simple flask application to test out various technologies:

- Containers (docker)
- AWS CodeBuild | AWS CodePipeline
- Amazon ECR
- Amazon ECS

This project references two deployment strategies for building multi-architecture docker images

1.  Using multiple CodeBuild projects (**standard**)
    1.  ARM64
    2.  X86
    3.  Manifest
2.  Using a single CodeBuild project utilizing buildx to build multi-architecture iamges (**multi-arch**)

**References:**

- Building multi-architecture docker images
  https://aws.amazon.com/blogs/devops/creating-multi-architecture-docker-images-to-support-graviton2-using-aws-codebuild-and-aws-codepipeline/

- Using buildx for multi-architecture images
  https://aws.amazon.com/blogs/compute/how-to-quickly-setup-an-experimental-environment-to-run-containers-on-x86-and-aws-graviton2-based-amazon-ec2-instances-effort-to-port-a-container-based-application-from-x86-to-graviton2/

- Deploying Load Balancer for ECS https://sakyasumedh.medium.com/deploy-backend-application-to-aws-ecs-with-application-load-balancer-step-by-step-guide-part-3-b8125ca27177

## Build

Local build

```bash
docker build -t simple-flask .
```

### Multi-arch build

Building image for x86_64 and arm64

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION:-us-east-1} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION:-us-east-1}.amazonaws.com

# Build for amd64 and arm64
docker buildx build -t "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION:-us-east-1}.amazonaws.com/${IMAGE_REPO_NAME}:${IMAGE_TAG:latest}" --platform linux/amd64,linux/arm64 --push .
```

## Testing

Used for local testing

```bash
# Launch container
docker run -itd --name simple-flask --label "simple-flask" -p 5000:5000 simple-flask

# Kill container
docker container kill $(docker ps --filter "label=simple-flask" -q)
```

## ECR Deployment

1. Create ECR repository

```bash
aws ecr create-repository \
--repository-name simple-flask \
--image-scanning-configuration scanOnPush=true \
--region us-east-1
```

## ECS Deployment

2. Create new ECS cluster

```bash
aws ecs create-cluster \
--cluster-name MultiArchCluster
```

2. Add IAM roles

```bash

```

3. Create task definition

Create task definitions

```bash
# Create task definition(s)

# Simple-flask definitions (latest:arm64, latest:amd64)
aws ecs register-task-definition --cli-input-json file://resources/aws/ecs-task-definition-fargate-arm64.json
aws ecs register-task-definition --cli-input-json file://resources/aws/ecs-task-definition-fargate-x86_64.json

# Multi-arch definitions
aws ecs register-task-definition --cli-input-json file://resources/aws/ecs-task-definition-fargate-multi-arch-arm64.json
aws ecs register-task-definition --cli-input-json file://resources/aws/ecs-task-definition-fargate-multi-arch-x86_64.json
```

1. Create services for **standard** deployment

```bash
aws ecs create-service \
    --cluster MultiArchCluster \
    --service-name DockerFlask-ARM64 \
    --task-definition simple-flask-arm64 \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-05879663ec53b5775,subnet-031c93cffa8b58491],securityGroups=[sg-03f0220e12fdbace3],assignPublicIp=ENABLED}"

aws ecs create-service \
    --cluster MultiArchCluster \
    --service-name DockerFlask-x86_64 \
    --task-definition simple-flask-x86_64 \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-05879663ec53b5775,subnet-031c93cffa8b58491],securityGroups=[sg-03f0220e12fdbace3],assignPublicIp=ENABLED}"
```

5. Create Target Group

**Reference**: https://docs.aws.amazon.com/AmazonECS/latest/userguide/create-application-load-balancer.html

- Create Target group(s) using IP address, but don't enter one as ECS will take care of associating IPs to the Target Group
- The Port should be the internal port to map to (e.g. 5000)

1. Create ALB

### Update service CLI examples

```bash
# Enable execute command
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition simple-flask-ARM64 \
    --service DockerFlask-ARM64 \
    --enable-execute-command \
    --force-new-deployment

# Add ALB - x86_64
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition simple-flask-x86_64 \
    --service DockerFlask-x86_64 \
    --force-new-deployment \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:152539975130:targetgroup/tg-simple-flask-x86/26a40e83948a05c1,containerName=flask-app,containerPort=5000"

# Add ALB - arm64
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition simple-flask-ARM64 \
    --service DockerFlask-ARM64 \
    --force-new-deployment \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:152539975130:targetgroup/tg-simple-flask-arm64/3d30a4fc868f18b3,containerName=flask-app,containerPort=5000"

# Update networking configuration
aws ecs update-service \
    --cluster MultiArchCluster  \
    --task-definition simple-flask-x86_64 \
    --service DockerFlask-x86_64 \
    --force-new-deployment \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-05879663ec53b5775,subnet-031c93cffa8b58491],securityGroups=[sg-03f0220e12fdbace3],assignPublicIp=ENABLED}"
```

## Amazon IAM Details

See https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html for details

Example statement to allow CodeBuild to push to ECR

```json
    {
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:CompleteLayerUpload",
        "ecr:DescribeImages",
        "ecr:DescribeRepositories",
        "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": "*",
      "Effect": "Allow"
    },
```
