# Cloud Deployment Guide for DataGuardian Pro

This guide provides instructions for deploying DataGuardian Pro to various cloud platforms.

## Common Preparation Steps

Regardless of which cloud provider you choose, complete these steps first:

1. Ensure your application is working correctly with Docker locally
2. Create an account with your chosen cloud provider
3. Install the cloud provider's CLI tools
4. Authenticate with your cloud provider

## Option 1: Azure Container Instances

Azure Container Instances (ACI) provides a simple way to run containers without managing infrastructure.

### Prerequisites

- Azure account
- Azure CLI installed and configured
- Docker installed locally

### Deployment Steps

1. **Create a resource group**:
   ```bash
   az group create --name dataguardian-rg --location westeurope
   ```

2. **Create an Azure Container Registry (ACR)**:
   ```bash
   az acr create --resource-group dataguardian-rg --name dataguardianregistry --sku Basic
   ```

3. **Log in to ACR**:
   ```bash
   az acr login --name dataguardianregistry
   ```

4. **Build and tag your image**:
   ```bash
   docker-compose build
   docker tag dataguardian-app:latest dataguardianregistry.azurecr.io/dataguardian-app:latest
   ```

5. **Push the image to ACR**:
   ```bash
   docker push dataguardianregistry.azurecr.io/dataguardian-app:latest
   ```

6. **Create an Azure Database for PostgreSQL**:
   ```bash
   az postgres server create \
     --resource-group dataguardian-rg \
     --name dataguardian-db \
     --location westeurope \
     --admin-user dataguardian \
     --admin-password <your-secure-password> \
     --sku-name GP_Gen5_2
   ```

7. **Create a database**:
   ```bash
   az postgres db create \
     --resource-group dataguardian-rg \
     --server-name dataguardian-db \
     --name dataguardian
   ```

8. **Allow Azure services to access the PostgreSQL server**:
   ```bash
   az postgres server firewall-rule create \
     --resource-group dataguardian-rg \
     --server-name dataguardian-db \
     --name AllowAllAzureIPs \
     --start-ip-address 0.0.0.0 \
     --end-ip-address 0.0.0.0
   ```

9. **Deploy container to ACI**:
   ```bash
   az container create \
     --resource-group dataguardian-rg \
     --name dataguardian-app \
     --image dataguardianregistry.azurecr.io/dataguardian-app:latest \
     --dns-name-label dataguardian \
     --ports 5000 \
     --registry-login-server dataguardianregistry.azurecr.io \
     --registry-username $(az acr credential show --name dataguardianregistry --query username --output tsv) \
     --registry-password $(az acr credential show --name dataguardianregistry --query passwords[0].value --output tsv) \
     --environment-variables \
       DATABASE_URL="postgresql://dataguardian:<your-secure-password>@dataguardian-db.postgres.database.azure.com:5432/dataguardian?sslmode=require" \
       PGHOST="dataguardian-db.postgres.database.azure.com" \
       PGUSER="dataguardian@dataguardian-db" \
       PGPASSWORD="<your-secure-password>" \
       PGDATABASE="dataguardian" \
       PGPORT=5432 \
       OPENAI_API_KEY="<your-openai-api-key>" \
       STRIPE_SECRET_KEY="<your-stripe-secret-key>" \
       STRIPE_PUBLISHABLE_KEY="<your-stripe-publishable-key>" \
       DEBUG="false" \
       ENVIRONMENT="production"
   ```

10. **Initialize the database**:
    ```bash
    az container exec \
      --resource-group dataguardian-rg \
      --name dataguardian-app \
      --exec-command "psql $DATABASE_URL -f /app/database/postgres-init.sql"
    ```

11. **Access your application**:
    ```bash
    echo "Application URL: http://dataguardian.<region>.azurecontainer.io:5000"
    ```

## Option 2: AWS Elastic Container Service (ECS)

AWS ECS allows you to run Docker containers without managing servers.

### Prerequisites

- AWS account
- AWS CLI installed and configured
- Docker installed locally

### Deployment Steps

1. **Create an Amazon ECR repository**:
   ```bash
   aws ecr create-repository --repository-name dataguardian-app
   ```

2. **Log in to ECR**:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(aws configure get region).amazonaws.com
   ```

3. **Build, tag, and push your image**:
   ```bash
   docker-compose build
   docker tag dataguardian-app:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(aws configure get region).amazonaws.com/dataguardian-app:latest
   docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(aws configure get region).amazonaws.com/dataguardian-app:latest
   ```

4. **Create an RDS PostgreSQL instance**:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier dataguardian-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username dataguardian \
     --master-user-password <your-secure-password> \
     --allocated-storage 20 \
     --db-name dataguardian
   ```

5. **Create an ECS cluster**:
   ```bash
   aws ecs create-cluster --cluster-name dataguardian-cluster
   ```

6. **Create a task definition** (save as task-definition.json):
   ```json
   {
     "family": "dataguardian-task",
     "networkMode": "awsvpc",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "dataguardian-app",
         "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/dataguardian-app:latest",
         "essential": true,
         "portMappings": [
           {
             "containerPort": 5000,
             "hostPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql://dataguardian:<your-secure-password>@<your-rds-endpoint>:5432/dataguardian"
           },
           {
             "name": "PGHOST",
             "value": "<your-rds-endpoint>"
           },
           {
             "name": "PGUSER",
             "value": "dataguardian"
           },
           {
             "name": "PGPASSWORD",
             "value": "<your-secure-password>"
           },
           {
             "name": "PGDATABASE",
             "value": "dataguardian"
           },
           {
             "name": "PGPORT",
             "value": "5432"
           },
           {
             "name": "DEBUG",
             "value": "false"
           },
           {
             "name": "ENVIRONMENT",
             "value": "production"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/dataguardian-task",
             "awslogs-region": "<your-region>",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ],
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512"
   }
   ```

7. **Register the task definition**:
   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

8. **Create a security group**:
   ```bash
   aws ec2 create-security-group --group-name dataguardian-sg --description "DataGuardian Pro security group"
   ```

9. **Add inbound rules to the security group**:
   ```bash
   aws ec2 authorize-security-group-ingress --group-name dataguardian-sg --protocol tcp --port 5000 --cidr 0.0.0.0/0
   ```

10. **Run the service**:
    ```bash
    aws ecs create-service \
      --cluster dataguardian-cluster \
      --service-name dataguardian-service \
      --task-definition dataguardian-task:1 \
      --desired-count 1 \
      --launch-type FARGATE \
      --network-configuration "awsvpcConfiguration={subnets=[<subnet-id>],securityGroups=[<security-group-id>],assignPublicIp=ENABLED}"
    ```

11. **Initialize the database**:
    Run this on a machine with PostgreSQL client:
    ```bash
    psql postgresql://dataguardian:<your-secure-password>@<your-rds-endpoint>:5432/dataguardian -f database/postgres-init.sql
    ```

## Option 3: Google Cloud Run

Google Cloud Run is a managed compute platform that automatically scales stateless containers.

### Prerequisites

- Google Cloud account
- Google Cloud SDK installed and configured
- Docker installed locally

### Deployment Steps

1. **Set up environment variables**:
   ```bash
   export PROJECT_ID=$(gcloud config get-value project)
   export REGION=us-central1
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com
   ```

3. **Build and push your image to Container Registry**:
   ```bash
   docker-compose build
   docker tag dataguardian-app:latest gcr.io/$PROJECT_ID/dataguardian-app:latest
   docker push gcr.io/$PROJECT_ID/dataguardian-app:latest
   ```

4. **Create a Cloud SQL PostgreSQL instance**:
   ```bash
   gcloud sql instances create dataguardian-db \
     --tier=db-f1-micro \
     --region=$REGION \
     --database-version=POSTGRES_13 \
     --root-password=<your-secure-password>
   ```

5. **Create a database**:
   ```bash
   gcloud sql databases create dataguardian --instance=dataguardian-db
   ```

6. **Create a user**:
   ```bash
   gcloud sql users create dataguardian \
     --instance=dataguardian-db \
     --password=<your-secure-password>
   ```

7. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy dataguardian-app \
     --image gcr.io/$PROJECT_ID/dataguardian-app:latest \
     --platform managed \
     --region $REGION \
     --allow-unauthenticated \
     --set-env-vars="DATABASE_URL=postgresql://dataguardian:<your-secure-password>@/dataguardian?host=/cloudsql/$PROJECT_ID:$REGION:dataguardian-db" \
     --set-env-vars="PGHOST=/cloudsql/$PROJECT_ID:$REGION:dataguardian-db" \
     --set-env-vars="PGUSER=dataguardian" \
     --set-env-vars="PGPASSWORD=<your-secure-password>" \
     --set-env-vars="PGDATABASE=dataguardian" \
     --set-env-vars="DEBUG=false" \
     --set-env-vars="ENVIRONMENT=production" \
     --add-cloudsql-instances $PROJECT_ID:$REGION:dataguardian-db
   ```

8. **Initialize the database**:
   ```bash
   gcloud sql import sql dataguardian-db gs://<your-bucket>/postgres-init.sql \
     --database=dataguardian
   ```
   
   Note: You need to upload the postgres-init.sql file to a Google Cloud Storage bucket first.

9. **Access your application**:
   ```bash
   gcloud run services describe dataguardian-app --platform managed --region $REGION --format 'value(status.url)'
   ```

## Security Considerations for Cloud Deployment

1. **Use managed secrets**:
   - Azure: Azure Key Vault
   - AWS: AWS Secrets Manager
   - GCP: Google Secret Manager

2. **Configure private networking**:
   - Limit public access to containers
   - Use VPC/VNET for communication between services

3. **Enable encryption**:
   - At-rest encryption for databases
   - SSL/TLS for data in transit

4. **Set up monitoring and logging**:
   - Azure: Azure Monitor
   - AWS: CloudWatch
   - GCP: Cloud Monitoring and Cloud Logging

5. **Implement IAM best practices**:
   - Use least privilege access
   - Rotate credentials regularly
   - Enable MFA for cloud accounts

## Cost Optimization

1. **Right-size resources**:
   - Start with smaller instances and scale up as needed
   - Monitor usage patterns

2. **Use serverless options where possible**:
   - Azure Container Instances
   - AWS Fargate
   - Google Cloud Run

3. **Implement auto-scaling**:
   - Scale down during low-usage periods
   - Scale up during peak times

4. **Use spot/preemptible instances for non-critical workloads**

5. **Set up budget alerts**:
   - Azure: Cost Management + Billing
   - AWS: AWS Budgets
   - GCP: Cloud Billing Budget Alerts