variable "DOMAIN_NAME" {}

resource "aws_lb" "web" {
  subnets = [
    aws_subnet.main_1a.id,
    aws_subnet.main_1b.id
  ]

  security_groups = [
    aws_security_group.alb.id
  ]
}

resource "aws_lb_target_group" "web" {
  target_type = "ip"
  port = 80
  protocol = "HTTP"
  vpc_id = aws_vpc.main.id
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.web.id
  port = "80"
  protocol = "HTTP"
 
  default_action {
    // If DOMAIN_NAME is defined, redirect to HTTPS, otherwise forward to the target group
    type = var.DOMAIN_NAME == "pkgpkr.com" ? "redirect" : "forward"
    target_group_arn = var.DOMAIN_NAME == "pkgpkr.com" ? null : aws_lb_target_group.web.arn

    redirect {
      port = "443"
      protocol = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.web.id
  port = "443"
  protocol = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-2016-08"
  certificate_arn = "arn:aws:acm:us-east-1:392133285793:certificate/8968fe98-ba47-4736-ba06-498d18ef1a8d"

  // Only create an HTTPS listener if DOMAIN_NAME is defined
  count = var.DOMAIN_NAME == "pkgpkr.com" ? 1 : 0

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.web.arn

    redirect {
      port = "80"
      protocol = "HTTP"
      status_code = "HTTP_301"
    }
  }
}
