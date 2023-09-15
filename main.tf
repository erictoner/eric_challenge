terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~>5.16.0"
    }
    null = {
      source = "hashicorp/null"
      version = "~>3.2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Create a VPC
resource "aws_vpc" "erict_challenge_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
  tags = var.tags
}

# output "erict_challenge_vpc_id" {
#   value = aws_vpc.erict_challenge_vpc.id
# }

resource "aws_internet_gateway" "erict_challenge_internet_gateway" {
  vpc_id             = aws_vpc.erict_challenge_vpc.id
}

resource "aws_subnet" "erict_challenge_subnet_az1" {
  vpc_id                  = aws_vpc.erict_challenge_vpc.id
  cidr_block              = "10.0.0.0/24"
  availability_zone       = var.availability_zone_1
  map_public_ip_on_launch = true
  tags = var.tags
}

resource "aws_subnet" "erict_challenge_subnet_az2" {
  vpc_id                  = aws_vpc.erict_challenge_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.availability_zone_2
  map_public_ip_on_launch = true
  tags = var.tags
}

resource "aws_route_table" "erict_challenge_rt" {
  vpc_id = aws_vpc.erict_challenge_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.erict_challenge_internet_gateway.id
  }
  tags = var.tags
}

resource "aws_route_table_association" "prod-crta-public-subnet-1" {
  subnet_id      = aws_subnet.erict_challenge_subnet_az1.id
  route_table_id = aws_route_table.erict_challenge_rt.id
}

resource "aws_route_table_association" "prod-crta-public-subnet-2" {
  subnet_id      = aws_subnet.erict_challenge_subnet_az2.id
  route_table_id = aws_route_table.erict_challenge_rt.id
}

# Create a security group
resource "aws_security_group" "erict_challenge_sg" {
  name        = "erict-challenge-sg"
  description = "Security Group for erict-challenge"
  vpc_id      = aws_vpc.erict_challenge_vpc.id

  ingress {
    from_port   = 80  # Allow HTTP traffic from anywhere
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443  # Allow HTTPS traffic from anywhere
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  # Outbound rules (allow all outbound traffic)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# Create a key pair
resource "aws_key_pair" "erict_challenge_ec2_key" {
  key_name   = "erict-challenge-ec2-key"
  public_key = file(var.instance_public_key_path)
}

# Create a load balancer
resource "aws_lb" "erict_challenge_lb" {
  name               = "erict-challenge-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [
    aws_subnet.erict_challenge_subnet_az1.id,
    aws_subnet.erict_challenge_subnet_az2.id
  ]

  enable_deletion_protection = false
  enable_http2               = true

  security_groups = [aws_security_group.erict_challenge_sg.id]

  tags = var.tags
}

resource "aws_lb_target_group" "erict_challenge_target_group" {
  name     = "erict-challenge-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.erict_challenge_vpc.id

  health_check {
    path                = "/we_are.html"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    port                = 80
  }
}

# Redirect 80 to 443
resource "aws_lb_listener" "erict_challenge_http_listener" {
  load_balancer_arn = aws_lb.erict_challenge_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Create an HTTPS listener
resource "aws_lb_listener" "erict_challenge_https_listener" {
  load_balancer_arn = aws_lb.erict_challenge_lb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.erict_challenge_target_group.arn
  }

  certificate_arn = var.certificate_arn
}

# Attach the HTTPS listener to the HTTPS target group
resource "aws_lb_listener_rule" "https_redirect_rule" {
  listener_arn = aws_lb_listener.erict_challenge_https_listener.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.erict_challenge_target_group.arn
  }

  condition {
    path_pattern {
      values = ["/"]
    }
  }
}

resource "aws_instance" "erict_challenge_instance" {
  count         = var.instance_count
  ami           = var.ami
  instance_type = var.instance_type
  key_name      = aws_key_pair.erict_challenge_ec2_key.key_name
  security_groups = [aws_security_group.erict_challenge_sg.id]
  subnet_id     = aws_subnet.erict_challenge_subnet_az1.id

  tags = var.tags
}

resource "aws_lb_target_group_attachment" "erict_challenge_target_group_attachment" {
  count           = var.instance_count
  target_group_arn = aws_lb_target_group.erict_challenge_target_group.arn
  target_id       = aws_instance.erict_challenge_instance[count.index].id
}

resource "null_resource" "erict_challenge_provisioner" {
  count = var.instance_count

  triggers = {
    we_are_html = filebase64("app/we_are.html")
    nginx_config = filebase64("app/nginx-config")
  }

  provisioner "file" {
    source      = "app"  # Local path to your NGINX config file
    destination = "/tmp"            # Destination path on the EC2 instance

    connection {
      type        = "ssh"
      user        = var.instance_connection_user
      private_key = file(var.instance_connection_private_key_path)
      host        = aws_instance.erict_challenge_instance[count.index].public_ip
    }
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y nginx",
      "sudo rm -f /etc/nginx/sites-enabled/default",
      "sudo mv /tmp/app/nginx-config /etc/nginx/sites-available/nginx-config",
      "sudo ln -s /etc/nginx/sites-available/nginx-config /etc/nginx/sites-enabled/",
      "sudo mv /tmp/app/we_are.html /var/www/html/we_are.html",
      "sudo systemctl restart nginx"
    ]

    connection {
      type        = "ssh"
      user        = var.instance_connection_user
      private_key = file(var.instance_connection_private_key_path)
      host        = aws_instance.erict_challenge_instance[count.index].public_ip
    }
  }

  depends_on = [aws_instance.erict_challenge_instance]
}