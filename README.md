# Demo Flask API
This repository contains a demo of a secure and scalable static web application using Terraform and nginx.

## Getting Started
Follow these instructions to set up and use terraform to deploy this demo application to AWS.

### Prerequisites
- terraform
- tflint
- aws (CLI tool)
- Certificate set up in Amazon Certificate Manager

### Key Setup
1. Generate a PEM encoded SSL certificate with domain information and import it into Amazon Certificate Manager. See https://docs.aws.amazon.com/acm/latest/userguide/import-certificate-prerequisites.html
2. Generate an SSH key pair to be used for SSH based provisioning

### Local Config
1. Update the variable `certificate_arn` in `terraform.tfvars` with the ARN of the imported certificate or an otherwise valid certificate. This is used for the load balancer SSL certificate. Tests allow unsigned certificates.
2. Update the `ssh_allowed_cidr` with your public IPv4 address in CIDR notation using a /32 subnet. This updates the firewall rule to allow only your IP to have SSH access to EC2 instances.
3. Use the generated ssh key pair paths and update the `instance_public_key_path` and private key path `instance_connection_private_key_path` in `terraform.tfvars`

### Deployment 
1. Run `terraform init`
2. Run `ci/terraform_deploy.sh`

### Testing
1. Install python packages via `pip install -r testing/requirements.txt`.
2. Test via `python3 testing/test_deploy.py`

```
Tip: You may want to use a python virtual environment, I prefer a combination of pyenv to get a clean python binary and pyvenv for a directory specfic iteration.
`python3 -m venv env/`
`source env/bin/activate`
`pip3 install -r testing/requirements.txt`
`python3 testing/test_deploy.py`
```

## Todo
 - [ ] Harden outbound rules?
 - [ ] Automate Key generation for SSH access to ec2 instances
 - [ ] Automate ACM SSL certificate generation for nginx
 - [ ] Consider ansible for config management of ec2 app related config, terraform to continue to network and clean ec2 provisioning. Consider custom AMI.
 - [ ] Add Checkov static code analysis tool for Terraform