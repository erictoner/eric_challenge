variable "aws_region" {
    type = string
    description = "AWS Region"
    default = "us-east-1"
}

variable "availability_zone_1" {
    type = string
    description = "Availability Zone 1 - must be part of aws_region and differ from zone 2"
    default = "us-east-1a"
}

variable "availability_zone_2" {
    type = string
    description = "Availability Zone - must be part of aws_region and differ from zone 1"
    default = "us-east-1b"
}

variable "ssh_allowed_cidr" {
    type = string
    description = "CIDR block of SSH allowed IP addresses"
    default = null
}

variable certificate_arn {
    type = string
    description = "Amazon Certificate Manager - Cert ARN"
    default = null
}

variable instance_count {
    type = number
    description = "Number of AWS Instances"
    default = 2
}

variable ami {
    type = string
    description = "Amazon Machine Image ID"
    default = "ami-0247010a20d170178" # Ubuntu 20.04 LTS AMI ID in us-east-1
}

variable instance_type {
    type = string
    description = "EC2 Instance Type (see https://aws.amazon.com/ec2/instance-types/)"
    default = "t2.micro"
}

variable instance_public_key_path {
    type = string
    description = "Path to a public key to allow SSH connection. Must be a key pair with instance_connection_private_key_path"
    default = null
}

variable instance_connection_private_key_path {
    type = string
    description = "Path to a private key used to establish an SSH connection"
    default = null
}

variable instance_connection_user {
  type = string
  description = "SSH user when connecting to instances via provisioners"
  default = "ubuntu"
}

variable "tags" {
    type = map
    description = "resource tags"
    default = null
}