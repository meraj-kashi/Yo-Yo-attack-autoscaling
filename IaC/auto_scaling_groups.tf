
resource "aws_launch_template" "image_flask_app_ec2_instance" {
  name_prefix   = "no-detection-"
  image_id      = "ami-0c903705914b8a994"
  instance_type = "t2.micro"
  key_name      = "uni"
}

resource "aws_alb_target_group" "flask_app_ec2_target_group" {
  name     = "no-detection-group"
  vpc_id   = data.aws_vpc.default.id
  protocol = "HTTP"
  port     = 80
}

resource "aws_autoscaling_group" "flask_app_autoscaling_group" {
  name               = "flask_app_autoscaling_group"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  target_group_arns  = [aws_alb_target_group.flask_app_ec2_target_group.arn]

  default_cooldown          = 60
  health_check_grace_period = 60
  health_check_type         = "ELB"

  desired_capacity = 1
  force_delete     = true
  max_size         = 2
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

resource "aws_autoscaling_policy" "autoscaling_policy_by_requests" {
  name                   = "autoscaling-policy-by-requests"
  autoscaling_group_name = aws_autoscaling_group.flask_app_autoscaling_group.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    target_value = 4000

    predefined_metric_specification {
      predefined_metric_type = "ASGAverageNetworkOut"
    }
  }
}
