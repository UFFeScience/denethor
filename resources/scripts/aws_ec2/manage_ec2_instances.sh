#!/bin/bash

# Load environment variables
source ./env_vars.sh

function list_instances() {
  #aws ec2 describe-instances --region "$aws_region" --query "Reservations[*].Instances[*].{ID:InstanceId,State:State.Name}" --output table
  echo "Listing instances in region $aws_region"
  aws ec2 describe-instances --region "$aws_region" --query "Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,State:State.Name,PublicDNS:PublicDnsName}" --output table

}

function start_instance() {
  instance_id=$1
  aws ec2 start-instances --instance-ids "$instance_id" --region "$aws_region"
  echo "Starting instance $instance_id"
}

function stop_instance() {
  instance_id=$1
  aws ec2 stop-instances --instance-ids "$instance_id" --region "$aws_region"
  echo "Stopping instance $instance_id"
}

function terminate_instance() {
  instance_id=$1
  aws ec2 terminate-instances --instance-ids "$instance_id" --region "$aws_region"
  echo "Terminating instance $instance_id"
}

function create_instance() {
  instance_id=$(aws ec2 run-instances --image-id "$ami_id" --instance-type "$ec2_instance_type" --key-name "$key_name" --security-group-ids "$sg_id" --region "$aws_region" --query "Instances[0].InstanceId" --output text)
  echo "Created instance with ID: $instance_id"
}

case $1 in
  list)
    list_instances
    ;;
  start)
    start_instance $2
    ;;
  stop)
    stop_instance $2
    ;;
  terminate)
    terminate_instance $2
    ;;
  create)
    create_instance
    ;;
  *)
    echo "Usage: $0 {list|start|stop|terminate|create} [instance-id]"
    ;;
esac