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

resource "aws_lb_listener" "web" {
  load_balancer_arn = aws_lb.web.id
  port = "80"
  protocol = "HTTP"

  // TODO: Set up SSL and a separate listener on 443, then redirect this to 443
  /*default_action {
    type = "redirect"

    redirect {
      port = "443"
      protocol = "HTTPS"
      status_code = "HTTP_301"
    }
  }*/
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}
