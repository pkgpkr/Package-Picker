/**
 * Set up CloudWatch resources
 */

// Log groups

resource "aws_cloudwatch_log_group" "web" {
  name = "/ecs/pkgpkr-web"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_stream" "web" {
  name = "pkgpkr-web"
  log_group_name = aws_cloudwatch_log_group.web.name
}

// Event rule for ML pipeline

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
  role_arn = aws_iam_role.invoke_step_function.arn
}