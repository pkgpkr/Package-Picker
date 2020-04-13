variable "DB_USER" {}
variable "DB_PASSWORD" {}

resource "aws_db_instance" "default" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "11.5"
  instance_class       = "db.t2.small"
  name                 = "pkgpkr"
  username             = var.DB_USER
  password             = var.DB_PASSWORD
  parameter_group_name = "default.postgres11"
  publicly_accessible  = true
  skip_final_snapshot  = true
  db_subnet_group_name = aws_db_subnet_group.default.name
  vpc_security_group_ids = [
    aws_security_group.database.id
  ]
}

/**
 * Define security group for the database
 */

resource "aws_security_group" "database" {
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group_rule" "ingress_database" {
  type = "ingress"
   cidr_blocks = [
       "0.0.0.0/0"
   ]
  from_port = 5432
  to_port = 5432
  protocol = "tcp"
  security_group_id = aws_security_group.database.id
}