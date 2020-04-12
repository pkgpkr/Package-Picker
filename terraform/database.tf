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
}
