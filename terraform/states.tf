/**
 * Set up daily trigger of the ML pipeline
 */

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

// State machine which manages the execution of our ML pipeline
resource "aws_sfn_state_machine" "run_ml_pipeline" {
  name = "RunMLPipelineDaily"
  role_arn = aws_iam_role.run_ml_pipeline.arn
  definition = <<PATTERN
{
  "StartAt": "RunTask",
  "Comment": "Run ML Pipeline",
  "States": {
    "RunTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "${aws_ecs_cluster.pkgpkr.arn}",
        "TaskDefinition": "${aws_ecs_task_definition.pipeline.arn}",
        "TaskDefinition": "arn:aws:ecs:${data.aws_region.current}:${data.aws_caller_identity.current}:task-definition/${aws_ecs_task_definition.pipeline.family}",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "Subnets": [
              "${aws_subnet.main_1a.id}",
              "${aws_subnet.main_1b.id}"
            ],
            "AssignPublicIp": "ENABLED",
            "SecurityGroups": [
              "${aws_security_group.ecs.id}"
            ]
          }
        }
      },
      "End": true
    }
  }
}
PATTERN
}
