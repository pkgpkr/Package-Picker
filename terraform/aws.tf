provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

// Policy permitting someone to invoke a step function
resource "aws_iam_role_policy" "invoke_step_function" {
  role = aws_iam_role.invoke_step_function.id
  policy = <<PATTERN
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "states:StartExecution",
            "Resource": "arn:aws:states:us-east-1:392133285793:stateMachine:MyStateMachine"
        }
    ]
}
PATTERN
}

// Role permitting our state machine to be executed
resource "aws_iam_role" "invoke_step_function" {
  assume_role_policy = <<PATTERN
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "events.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
PATTERN
}

// Rule to trigger a run of our ML pipeline once per day
resource "aws_cloudwatch_event_rule" "run_ml_pipeline" {
  role_arn = aws_iam_role.invoke_step_function.arn
  description = "Run the pkgpkr ML Pipeline every day"
  schedule_expression = "rate(1 day)"
}

// Event target which glues our CloudWatch rule to our State Machine
resource "aws_cloudwatch_event_target" "run_ml_pipeline" {
  rule = aws_cloudwatch_event_rule.run_ml_pipeline.name
  arn = aws_sfn_state_machine.run_ml_pipeline.id
  role_arn = aws_iam_role.run_ml_pipeline.arn
}

// Role which allows our state machine to manage a task in ECS
resource "aws_iam_role" "run_ml_pipeline" {
  assume_role_policy = <<PATTERN
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "states.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
PATTERN
}

// Permission which allows a role to manage a task in ECS
resource "aws_iam_role_policy" "run_ml_pipeline" {
  role = aws_iam_role.run_ml_pipeline.id
  policy = <<PATTERN
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask",
                "ecs:StopTask",
                "ecs:DescribeTasks"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "events:PutTargets",
                "events:PutRule",
                "events:DescribeRule"
            ],
            "Resource": [
                "arn:aws:events:us-east-1:392133285793:rule/StepFunctionsGetEventsForECSTaskRule"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "arn:aws:iam::392133285793:role/ecsTaskExecutionRole"
            ]
        }
    ]
}
PATTERN
}

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
        "Cluster": "arn:aws:ecs:us-east-1:392133285793:cluster/default",
        "TaskDefinition": "arn:aws:ecs:us-east-1:392133285793:task-definition/pkgpkr-ml-task-definition",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "Subnets": [
              "subnet-026cbcabb97c47674"
            ],
            "AssignPublicIp": "ENABLED",
            "SecurityGroups": [
              "sg-0d4030427b648e2bd"
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