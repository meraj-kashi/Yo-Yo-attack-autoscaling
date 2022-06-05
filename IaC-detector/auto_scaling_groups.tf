
resource "aws_launch_template" "image_flask_app_ec2_instance" {
  name_prefix          = "detection-"
  image_id             = "ami-0e1cc85a7019bbca1"
  instance_type        = "t2.micro"
  key_name             = "uni"
  security_group_names = [aws_security_group.security_group_ec2_instances.name]
  iam_instance_profile {
    name = aws_iam_instance_profile.my_ec2_iam_profile.name
  }
  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    var1 = "test"
  }))
}

resource "aws_alb_target_group" "flask_app_ec2_target_group" {
  name                 = "detection-group"
  vpc_id               = data.aws_vpc.default.id
  protocol             = "HTTP"
  port                 = 80
  deregistration_delay = 60
}

resource "aws_autoscaling_group" "flask_app_autoscaling_group" {
  name               = "flask_app_autoscaling_group"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  target_group_arns  = [aws_alb_target_group.flask_app_ec2_target_group.arn]

  default_cooldown          = 30
  health_check_grace_period = 30
  health_check_type         = "ELB"

  #enabled_metrics = ["GroupInServiceInstances"]

  desired_capacity = 1
  force_delete     = true
  max_size         = 5
  min_size         = 1

  launch_template {
    id      = aws_launch_template.image_flask_app_ec2_instance.id
    version = "$Latest"
  }

  tag {
    key                 = "asg"
    value               = "flask_app_autoscaling_group"
    propagate_at_launch = true
  }
}

###############################################
resource "aws_autoscaling_policy" "web_policy_up" {
  name                   = "web_policy_up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 60
  autoscaling_group_name = aws_autoscaling_group.flask_app_autoscaling_group.name
}

resource "aws_cloudwatch_metric_alarm" "web_request_alarm_up" {
  alarm_name          = "web_request_alarm_up"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "RequestCount"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1000"

  dimensions = {
    LoadBalancer = aws_lb.flask_app_load_balancer.arn_suffix
  }

  alarm_description = "This metric monitor EC2 instance request utilization"
  alarm_actions     = [aws_autoscaling_policy.web_policy_up.arn]
}

##################################################

resource "aws_autoscaling_policy" "web_policy_down" {
  name                   = "web_policy_down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 60
  autoscaling_group_name = aws_autoscaling_group.flask_app_autoscaling_group.name
}

resource "aws_cloudwatch_metric_alarm" "web_request_alarm_down" {
  alarm_name          = "web_request_alarm_down"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "RequestCount"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "100"

  dimensions = {
    LoadBalancer = aws_lb.flask_app_load_balancer.arn_suffix
  }

  alarm_description = "This metric monitor EC2 instance request utilization"
  alarm_actions     = [aws_autoscaling_policy.web_policy_down.arn]
}
