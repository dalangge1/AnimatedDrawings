# TASK ROLE: ALLOWS CONTAINERS TO ACCESS AWS RESOURCES(ie: s3, efs)
resource "aws_iam_role" "devops_role" {
  name = "ecr_task_iam_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs.amazonaws.com"
        }
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "batch.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "s3.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
    ]
  })

  tags = {
    env = "model-testing"
  }
}

## TASK ROLE POLICY
resource "aws_iam_policy" "task_role_policy" {
  name        = "ecs_task_policy_${var.environment}"
  path        = "/"
  description = "Necessary DevOps Permissions for Maintenance and Testing. ECS Full Access is needed to maintain, test, monitor Fargate Clusters"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ec2:Describe*",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action = [
          "s3:ListBucket",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action = [
          "ecs:*",
        ],
        Effect   = "Allow",
        Resource = "*",
    }]
  })
}

resource "aws_iam_policy_attachment" "devops-policy-attach" {
  name       = "ec2-instance-policy-attachment"
  roles      = [aws_iam_role.devops_role.name]
  policy_arn = aws_iam_policy.task_role_policy.arn
}


## TASK EXECUTION ROLE: ALLOWS ECS TO PULL IMAGES FROM ECR
resource "aws_iam_role" "task_execution_role" {
  name = "task_execution_role_${var.environment}"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs.amazonaws.com"
        }
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "batch.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "s3.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "iam.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
    ]
  })

  tags = {
    env = "model-testing"
  }
}
resource "aws_iam_policy" "task_ecr_policy" {
  name = "task_ecr_policy_${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_policy_attachment" "ecr_policy_attach" {
  name       = "ecr-policy-attachment"
  roles      = [aws_iam_role.task_execution_role.name]
  policy_arn = aws_iam_policy.task_ecr_policy.arn

}

resource "aws_iam_policy_attachment" "TaskExecution_role_policy_attach" {
  name  = "task_execution-policy-attachment"
  roles = [aws_iam_role.task_execution_role.name]

  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    "arn:aws:iam::aws:policy/EC2InstanceProfileForImageBuilderECRContainerBuilds",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentAdminPolicy"
  ])

  policy_arn = each.value

}

resource "aws_cloudwatch_log_group" "log_group" {
  name = "/ecs/sketch-animation-${var.environment}"
}

##  ECS CLUSTER
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "${var.environment}_cluster"
  #capacity_providers = [aws_ecs_capacity_provider.detectron_ecs_cp.name]

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}


