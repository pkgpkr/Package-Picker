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
    aws_lb_listener.http,
    aws_lb_listener.https
  ]
}

// Task definition for web service

resource "aws_ecs_task_definition" "web" {
  execution_role_arn = aws_iam_role.execute_task.arn
  container_definitions = file("task-definitions/pkgpkr-web-container.json")
  memory = "512"
  family = "pkgpkr-web-task-definition"
  requires_compatibilities = [
    "FARGATE"
  ]
  network_mode = "awsvpc"
  cpu = "256"
}

// Task definition for ML pipeline service

resource "aws_ecs_task_definition" "pipeline" {
  execution_role_arn = aws_iam_role.execute_task.arn
  container_definitions = file("task-definitions/pkgpkr-pipeline-container.json")
  memory = "4096"
  family = "pkgpkr-ml-task-definition"
  requires_compatibilities = [
    "FARGATE"
  ]
  network_mode = "awsvpc"
  cpu = "2048"
}

// Write task definitions to local files for use by GitHub Actions

resource "local_file" "web-task-definition" {
  filename = "../webserver/pkgpkr/task-definition-ecs.json"
  content = <<PATTERN
{
  "executionRoleArn": "${aws_iam_role.execute_task.arn}",
  "containerDefinitions": ${file("task-definitions/pkgpkr-web-container.json")},
  "memory": "512",
  "family": "pkgpkr-web-task-definition",
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "networkMode": "awsvpc",
  "cpu": "256"
}
PATTERN
}

resource "local_file" "pipeline-task-definition" {
  filename = "../pipeline/task-definition-ecs.json"
  content = <<PATTERN
{
  "executionRoleArn": "${aws_iam_role.execute_task.arn}",
  "containerDefinitions": ${file("task-definitions/pkgpkr-pipeline-container.json")},
  "memory": "4096",
  "family": "pkgpkr-ml-task-definition",
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "networkMode": "awsvpc",
  "cpu": "2048"
}
PATTERN
}