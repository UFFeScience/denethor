# AWS Environment Setup

For the execution of the commands below, we assume that the user already has an AWS account and is in possession of the `AWS Access Key ID` and `AWS Secret Access Key`. Otherwise, it will be necessary to create an AWS account and obtain the access credentials.

## Configure access via AWS CLI on the local machine

> **Note:** You must already have an AWS account and possess your `AWS Access Key ID` and `AWS Secret Access Key`. If not, create an AWS account and obtain your credentials.

## 1. Configure AWS CLI Access on Your Local Machine

Download and install the AWS CLI:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version
# Example output:
# aws-cli/2.13.37 Python/3.11.6 Linux/6.2.0-36-generic exe/x86_64.ubuntu.22 prompt/off
# aws-cli/2.14.5 Python/3.11.6 Windows/10 exe/AMD64 prompt/off
```

Configure your credentials:

```bash
aws configure
```

Expected output:

```text
AWS Access Key ID: ...............
AWS Secret Access Key: ...........................
Default region name: sa-east-1
Default output format: json
```

---

## 2. Essential AWS CLI Commands

This is a quick reference for AWS CLI commands to test your environment and list key services.

### 2.1 Test Connectivity and Verify Credentials

Ensure your AWS CLI credentials are configured and you can communicate with AWS endpoints. The following command confirms your identity (user or role):

```bash
aws sts get-caller-identity
```

If the command returns your `UserId`, `Account`, and `Arn`, your connectivity is working.

---

### 2.2 List Resources for Key Services

The following commands help you get an overview of provisioned resources. The `--query` flag formats the output for readability.

#### Amazon S3 (Simple Storage Service)
List all S3 buckets:

```bash
aws s3api list-buckets --query "Buckets[].Name" --output text
```

#### Amazon EC2 (Elastic Compute Cloud)
List EC2 instances (ID, type, state, and "Name" tag):

```bash
aws ec2 describe-instances --query "Reservations[*].Instances[*].{ID:InstanceId, Type:InstanceType, State:State.Name, Name:Tags[?Key=='Name']|[0].Value}" --output table
```

#### Amazon RDS (Relational Database Service)
List RDS database instances:

```bash
aws rds describe-db-instances --query "DBInstances[*].{ID:DBInstanceIdentifier, Engine:Engine, Class:DBInstanceClass, Status:DBInstanceStatus}" --output table
```

#### AWS Lambda
List Lambda functions (name and runtime):

```bash
aws lambda list-functions --query "Functions[*].{Name:FunctionName, Runtime:Runtime}" --output table
```

#### Amazon VPC (Virtual Private Cloud)
List VPCs (ID, CIDR block, default status):

```bash
aws ec2 describe-vpcs --query "Vpcs[*].{ID:VpcId, CIDRBlock:CidrBlock, IsDefault:IsDefault}" --output table
```

#### Security Groups
List Security Groups (firewalls for your resources):

```bash
aws ec2 describe-security-groups --query "SecurityGroups[*].{Name:GroupName, ID:GroupId, VPC:VpcId}" --output table
```

> **Tip:** Add `--region your-region` (e.g., `--region us-east-1`) to any command to specify a region.

```bash
aws configure
```

Expected output:

```bash
AWS Access Key ID: ...............
AWS Secret Access Key: ...........................
Default region name: sa-east-1
Default output format: json
```

Essential AWS CLI Commands
This is a quick reference guide for AWS CLI commands to test your environment's connectivity and list key services in use.

1. Test Connectivity and Verify Credentials
First, it's crucial to ensure your AWS CLI credentials are configured correctly and that you can communicate with AWS endpoints. The get-caller-identity command is perfect for this, as it requires no special permissions and confirms the identity (user or role) being used.

aws sts get-caller-identity

If the command returns your UserId, Account, and Arn, your connectivity is working perfectly.

2. List Resources for Key Services
The following commands help you get an overview of the provisioned resources in your account. For most of them, using the --query flag helps format the output to be more readable.

Amazon S3 (Simple Storage Service)
To list all of your S3 buckets:

aws s3api list-buckets --query "Buckets[].Name" --output text

Amazon EC2 (Elastic Compute Cloud)
To list important information about your EC2 instances, such as ID, type, state, and the "Name" tag:

aws ec2 describe-instances --query "Reservations[*].Instances[*].{ID:InstanceId, Type:InstanceType, State:State.Name, Name:Tags[?Key=='Name']|[0].Value}" --output table

Amazon RDS (Relational Database Service)
To list your RDS database instances:

aws rds describe-db-instances --query "DBInstances[*].{ID:DBInstanceIdentifier, Engine:Engine, Class:DBInstanceClass, Status:DBInstanceStatus}" --output table

AWS Lambda
To list all your Lambda functions, showing the function name and runtime:

aws lambda list-functions --query "Functions[*].{Name:FunctionName, Runtime:Runtime}" --output table

Amazon VPC (Virtual Private Cloud)
To list the VPCs in your account, including the CIDR block and whether it's the default VPC:

aws ec2 describe-vpcs --query "Vpcs[*].{ID:VpcId, CIDRBlock:CidrBlock, IsDefault:IsDefault}" --output table

Security Groups
To list the Security Groups, which act as firewalls for your resources:

aws ec2 describe-security-groups --query "SecurityGroups[*].{Name:GroupName, ID:GroupId, VPC:VpcId}" --output table

Tip: You can add the --region your-region flag (e.g., --region us-east-1) to any of these commands to run them in a specific region.

