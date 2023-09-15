#!/bin/bash
#
# Terraform Deployment Script
# This script validates and deploys a Terraform configuration.
#
# Prerequisites:
# - tflint
# - terraform
# - aws (CLI)
#
# Usage:
# - Run the script: ./deploy.sh [--auto]
#   - --auto: Use this flag to automatically approve the Terraform apply (e.g., ./deploy.sh --auto)

# Exit script on non-zero exit codes
set -e

required_tools=("tflint" "terraform" "aws")

# Check for the presence of each required tool
for tool in "${required_tools[@]}"; do
  if ! command -v "$tool" &> /dev/null; then
    echo "The $tool CLI tool is not installed. Please install $tool and ensure it's in your PATH."
    exit 1
  fi
done

auto_approve=false

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --auto)
      auto_approve=true
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Lint with tflint
echo "Linting Terraform configuration..."
tflint

# Perform Terraform validation
echo "Validating Terraform configuration..."
terraform validate

# If validation succeeded, deploy the infrastructure
echo "Deploying Terraform configuration..."
if [ "$auto_approve" = true ]; then
  terraform apply -auto-approve
else
  terraform apply
fi