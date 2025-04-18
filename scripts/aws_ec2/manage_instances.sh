#!/bin/bash

# Load environment variables
source ./env_vars.sh

function get_instance_id() {
  local id_param=${1:-$ec2_instance_id}
  if [ -z "$1" ]; then
    echo "No instance ID provided. Using default instance ID from environment variable: $ec2_instance_id" >&2
  fi
  echo "$id_param"
}

function list_instances() {
  #aws ec2 describe-instances --region "$aws_region" --query "Reservations[*].Instances[*].{ID:InstanceId,State:State.Name}" --output table
  echo "Listing instances in region $aws_region"
  aws ec2 describe-instances --region "$aws_region" --query "Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,State:State.Name,PublicDNS:PublicDnsName}" --output table

}

function start_instance() {
  id_param=$(get_instance_id $1)
  aws ec2 start-instances --instance-ids "$id_param" --region "$aws_region"
  echo "Starting instance $id_param"
}

function stop_instance() {
  id_param=$(get_instance_id $1)
  aws ec2 stop-instances --instance-ids "$id_param" --region "$aws_region"
  echo "Stopping instance $id_param"
}

function terminate_instance() {
  id_param=$(get_instance_id $1)
  aws ec2 terminate-instances --instance-ids "$id_param" --region "$aws_region"
  echo "Terminating instance $id_param"
}

function create_instance() {
  id_param=$(aws ec2 run-instances --image-id "$ami_id" --instance-type "$ec2_instance_type" --key-name "$key_name" --security-group-ids "$sg_id" --region "$aws_region" --query "Instances[0].InstanceId" --output text)
  echo "Created instance with ID: $id_param"
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
    echo "Usage: $0 {list | start | stop | terminate | create} [instance-id]"
    ;;
esac