provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
}

/**
 * Define subnets for the VPC
 */

resource "aws_subnet" "main_1a" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.0.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_subnet" "main_1b" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1b"
}

resource "aws_db_subnet_group" "default" {
  name       = "main"
  subnet_ids = ["${aws_subnet.main_1a.id}", "${aws_subnet.main_1b.id}"]
}

/**
 * Define internet gateway for the VPC
 */

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}


/**
 * Define route table for the VPC
 */

resource "aws_route_table" "table" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "subnet_1a" {
    subnet_id = aws_subnet.main_1a.id
    route_table_id = aws_route_table.table.id
}

resource "aws_route_table_association" "subnet_1b" {
    subnet_id = aws_subnet.main_1b.id
    route_table_id = aws_route_table.table.id
}

/**
 * Define security group for the load balancer
 */

resource "aws_security_group" "alb" {
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group_rule" "ingress_alb_http" {
  type = "ingress"
   cidr_blocks = [
       "0.0.0.0/0"
   ]
  from_port = 80
  to_port = 80
  protocol = "tcp"
  security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "ingress_alb_https" {
  type = "ingress"
   cidr_blocks = [
       "0.0.0.0/0"
   ]
  from_port = 443
  to_port = 443
  protocol = "tcp"
  security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "egress_alb" {
  type = "egress"
   cidr_blocks = [
       "0.0.0.0/0"
   ]
  from_port = 1
  to_port = 65535
  protocol = "all"
  security_group_id = aws_security_group.alb.id
}

/**
 * Define security group for the ECS cluster
 */

 resource "aws_security_group" "ecs" {
   vpc_id = aws_vpc.main.id
 }

 resource "aws_security_group_rule" "ingress_ecs_http" {
   type = "ingress"
   cidr_blocks = [
       "0.0.0.0/0"
   ]
   from_port = 80
   to_port = 80
   protocol = "tcp"
   security_group_id = aws_security_group.ecs.id
 }

 resource "aws_security_group_rule" "ingress_ecs_any" {
   type = "ingress"
   from_port = 1
   to_port = 65535
   protocol = "tcp"
   source_security_group_id = aws_security_group.alb.id
   security_group_id = aws_security_group.ecs.id
 }

 resource "aws_security_group_rule" "egress_ecs" {
   type = "egress"
   cidr_blocks = [
       "0.0.0.0/0"
   ]
   from_port = 1
   to_port = 65535
   protocol = "all"
   security_group_id = aws_security_group.ecs.id
 }