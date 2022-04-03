
resource "aws_iam_instance_profile" "my_ec2_iam_profile" {
  name = "my_ec2_iam_profile"
  role = aws_iam_role.my_ec2_iam_role.name
}

resource "aws_iam_role" "my_ec2_iam_role" {
  name               = "my_ec2_iam_role"
  assume_role_policy = data.aws_iam_policy_document.my_ec2_instance_role.json
}

resource "aws_iam_role_policy" "my_ec2_iam_role_policy" {
  name   = "my_ec2_iam_role_policy"
  role   = aws_iam_role.my_ec2_iam_role.id
  policy = data.aws_iam_policy_document.my_ec2_inline_policy.json
}

//--------------------------------------------------------------------
// Data Sources
data "aws_iam_policy_document" "my_ec2_instance_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "my_ec2_inline_policy" {
  statement {
    sid    = "1"
    effect = "Allow"

    actions = ["ec2:DescribeInstances"]

    resources = ["*"]
  }

  statement {
    sid    = "Autoscaling"
    effect = "Allow"
    actions = [
      "autoscaling:*"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "CloudWtach"
    effect = "Allow"
    actions = [
      "cloudwatch:PutMetricAlarm"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid    = "Ec2Details"
    effect = "Allow"

    actions = [
      "ec2:DescribeAccountAttributes",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeImages",
      "ec2:DescribeInstanceAttribute",
      "ec2:DescribeInstances",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeLaunchTemplateVersions",
      "ec2:DescribePlacementGroups",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSpotInstanceRequests",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcClassicLink"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "LoadBalancer"
    effect = "Allow"

    actions = [
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeTargetGroups"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid    = "uknown"
    effect = "Allow"
    actions = [
      "iam:CreateServiceLinkedRole"
    ]
    resources = [
      "*"
    ]

  }
}
