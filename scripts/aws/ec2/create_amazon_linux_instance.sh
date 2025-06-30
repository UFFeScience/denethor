#!/bin/bash

# Load environment variables
source ../load_env_vars.sh

# Check if key pair file exists
if [ ! -f "$key_path" ]; then
    echo "Key pair file not found: $key_path"
    exit 1
fi

# Check if the key pair exists
aws ec2 describe-key-pairs --key-names "$key_name" --region "$aws_region" 2>&1
if [ $? -ne 0 ]; then
  exit 1
fi

# Check if the VPC exists
aws ec2 describe-vpcs --vpc-ids "$vpc_id" --region "$aws_region" 2>&1
if [ $? -ne 0 ]; then
  echo "Available VPCs in the region:"
  aws ec2 describe-vpcs --region sa-east-1 --query "Vpcs[*].{ID:VpcId,Name:Tags[?Key=='Name']|[0].Value}" --output table
  exit 1
fi

# Check if the security group exists
security_group_id=$(aws ec2 describe-security-groups --filters Name=group-name,Values="$security_group_name" --query "SecurityGroups[0].GroupId" --output text --region "$aws_region" 2>/dev/null)
if [ -z "$security_group_id" ] || [ "$security_group_id" == "None" ]; then
  echo "Security group does not exist. Creating security group..."
  security_group_create=$(aws ec2 create-security-group --group-name "$security_group_name" --description "$security_group_description" --vpc-id "$vpc_id" --query "GroupId" --output text --region "$aws_region" 2>&1)
  if [ $? -ne 0 ]; then
    echo "$security_group_create"
    exit 1
  fi
  security_group_id="$security_group_create"
  echo "Security group created with ID: $security_group_id"

  # Authorize security group ingress
  security_group_ingress=$(aws ec2 authorize-security-group-ingress --group-id "$security_group_id" --ip-permissions '{"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' --region "$aws_region" 2>&1)
  if [ $? -ne 0 ]; then
    echo "$security_group_ingress"
    exit 1
  fi
  echo "Ingress rule added to security group $security_group_id"
else
  echo "Security group already exists with ID: $security_group_id"
fi





echo ""
echo "-------------------------------------------------------------------------------"
echo "Launching a free-tier EC2 instance with Amazon Linux in region '$aws_region'"
echo "-------------------------------------------------------------------------------"

# Run the instance
instance_run=$(aws ec2 run-instances --image-id "$ami_id" --instance-type "$ec2_instance_type" --key-name "$key_name" --network-interfaces "AssociatePublicIpAddress=true,DeviceIndex=0,Groups=[$security_group_id]" --credit-specification "CpuCredits=standard" --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$ec2_instance_name}]" --metadata-options "HttpEndpoint=enabled,HttpPutResponseHopLimit=2,HttpTokens=required" --private-dns-name-options "HostnameType=ip-name,EnableResourceNameDnsARecord=true,EnableResourceNameDnsAAAARecord=false" --count 1 --region "$aws_region" --query "Instances[0].InstanceId" --output text 2>&1)
if [ $? -ne 0 ]; then
  echo "Failed to launch EC2 instance with AMI ID: $ami_id and instance type: $ec2_instance_type"
  echo "$instance_run"
  exit 1
fi
instance_id="$instance_run"
echo "Lunched instance with ID: $instance_id"


# Wait for the instance to be in running state
echo "Waiting for the instance to be in running state..."
aws ec2 wait instance-running --instance-ids "$instance_id" --region "$aws_region"


# Get the public DNS of the instance
instance_dns=$(aws ec2 describe-instances --instance-ids "$instance_id" --region "$aws_region" --query "Reservations[0].Instances[0].PublicDnsName" --output text)
echo "Instance Public DNS: $instance_dns"

# Upgrade the instance
echo "Upgrading the instance..."
ssh -i "$key_path" $ec2_user@"$instance_dns" "sudo dnf upgrade -y"
ssh -i "$key_path" $ec2_user@"$instance_dns" "sudo dnf update -y"
ssh -i "$key_path" $ec2_user@"$instance_dns" "dnf upgrade --releasever=2023.6.20250303 -y"


# Install Python 3.11
echo "Installing Python 3.11..."
ssh -i "$key_path" $ec2_user@"$instance_dns" "sudo dnf install python3.11 -y"
ssh -i "$key_path" $ec2_user@"$instance_dns" "python3.11 -m --version || python3.11 -m ensurepip --upgrade || python3.11 -m pip install --upgrade pip"


# Create an AMI from the instance
ami_create=$(aws ec2 create-image --instance-id "$instance_id" --name "$ami_name" --no-reboot --region "$aws_region" --query "ImageId" --output text 2>&1)
if [ $? -ne 0 ]; then
  echo "Failed to create AMI from instance ID: $instance_id"
  echo "$ami_create"
  exit 1
fi
ami_id="$ami_create"
echo "AMI ID: $ami_id"


# Wait for the AMI to be available
aws ec2 wait image-available --image-ids "$ami_id" --region "$aws_region"
echo "AMI $ami_id is now available"