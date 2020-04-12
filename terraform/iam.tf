/**
 * Roles and permissions
 */

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
            "Resource": "${aws_sfn_state_machine.run_ml_pipeline.id}"
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

resource "aws_iam_role" "execute_task" {
  assume_role_policy = <<PATTERN
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
PATTERN
}

resource "aws_iam_role_policy" "execute_task" {
  role = aws_iam_role.execute_task.id
  policy = <<PATTERN
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
PATTERN
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
                "ecs:DescribeTasks",
                "events:PutTargets",
                "events:PutRule",
                "events:DescribeRule"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "${aws_iam_role.execute_task.arn}"
            ]
        }
    ]
}
PATTERN
}