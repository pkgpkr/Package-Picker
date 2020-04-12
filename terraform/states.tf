/**
 * Set up daily trigger of the ML pipeline
 */

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
        "TaskDefinition": "${format("arn:aws:ecs:%s:%s:task-definition/%s", data.aws_region.current.name, data.aws_caller_identity.current.account_id, aws_ecs_task_definition.pipeline.family)}",
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
