ssh_allowed_cidr = "" # Public CIDR IP of the device running Terraform, e.g. 100.2.3.4/32
certificate_arn = "" # ARN of the Certificate
instance_public_key_path = "" # Public key path used to configure SSH access to ec2 instances, e.g. ~/.ssh/id_rsa_eric_challenge.pub
instance_connection_private_key_path = "" # Private key used to connect to EC2 instances, e.g. "~/.ssh/id_rsa_eric_challenge"

tags = {
    env = "dev"
    project = "erict-challenge"
}