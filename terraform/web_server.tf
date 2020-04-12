/**
 * Set up ECS cluster, web service, and load balancer
 */

resource "aws_ecs_cluster" "pkgpkr" {
  name = "pkgpkr"
}

resource "aws_ecs_service" "web" {
  name = "pkgpkr-web"
  cluster = aws_ecs_cluster.pkgpkr.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count = 1
  launch_type = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.main_1a.id,
      aws_subnet.main_1b.id
    ]

    security_groups = [
      aws_security_group.ecs.id
    ]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name = "nginx"
    container_port = 80
  }

  depends_on = [
    aws_lb_listener.web
  ]
}

resource "aws_ecs_task_definition" "web" {
  execution_role_arn = aws_iam_role.execute_task.arn
  container_definitions = file("task-definitions/pkgpkr-web-service.json")
  memory = "512"
  family = "pkgpkr-web-task-definition"
  requires_compatibilities = [
    "FARGATE"
  ]
  network_mode = "awsvpc"
  cpu = "256"
}

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

resource "aws_cloudwatch_log_group" "web" {
  name = "/ecs/pkgpkr-web"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_stream" "web" {
  name = "pkgpkr-web"
  log_group_name = aws_cloudwatch_log_group.web.name
}
