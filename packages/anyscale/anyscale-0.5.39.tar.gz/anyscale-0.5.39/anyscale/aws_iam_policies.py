# Used for data-gplane role.
AMAZON_S3_FULL_ACCESS_POLICY_ARN = "arn:aws:iam::aws:policy/AmazonS3FullAccess"

AMAZON_ECR_READONLY_ACCESS_POLICY_ARN = (
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
)

# Used for control-plane role.
ANYSCALE_IAM_PERMISSIONS_EC2_STEADY_STATE = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "IAM",
            "Effect": "Allow",
            "Action": ["iam:PassRole", "iam:GetInstanceProfile"],
            "Resource": "*",
        },
        {
            "Sid": "RetrieveGenericAWSResources",
            "Effect": "Allow",
            "Action": [
                # Populates metadata about what is available
                # in the account.
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeInstanceTypes",
                "ec2:DescribeRegions",
            ],
            "Resource": "*",
        },
        {
            "Sid": "DescribeRunningResources",
            "Effect": "Allow",
            "Action": [
                # Determines cluster/configuration status.
                "ec2:DescribeInstances",
                "ec2:DescribeSubnets",
                "ec2:DescribeRouteTables",
                "ec2:DescribeSecurityGroups",
            ],
            "Resource": "*",
        },
        {
            "Sid": "InstanceManagementCore",
            "Effect": "Allow",
            "Action": [
                # Minimal Permissions to Run Instances on Anyscale.
                "ec2:RunInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:TerminateInstances",
            ],
            "Resource": "*",
        },
        {
            "Sid": "InstanceTagMangement",
            "Effect": "Allow",
            "Action": ["ec2:CreateTags", "ec2:DeleteTags"],
            "Resource": "*",
        },
        {
            "Sid": "InstanceManagementSpot",
            "Effect": "Allow",
            "Action": [
                # Extended Permissions to Run Instances on Anyscale.
                "ec2:CancelSpotInstanceRequests",
                "ec2:ModifyImageAttribute",
                "ec2:ModifyInstanceAttribute",
                "ec2:RequestSpotInstances",
            ],
            "Resource": "*",
        },
        {
            "Sid": "ResourceManagementExtended",
            "Effect": "Allow",
            "Action": [
                # Volume management
                "ec2:AttachVolume",
                "ec2:CreateVolume",
                "ec2:DeleteVolume",
                "ec2:DescribeVolumes",
                # IAMInstanceProfiles
                "ec2:AssociateIamInstanceProfile",
                "ec2:DisassociateIamInstanceProfile",
                "ec2:ReplaceIamInstanceProfileAssociation",
                # Placement groups
                "ec2:CreatePlacementGroup",
                "ec2:DeletePlacementGroup",
                # Address Management
                "ec2:AllocateAddress",
                "ec2:ReleaseAddress",
                # Additional DescribeResources
                "ec2:DescribeIamInstanceProfileAssociations",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribePlacementGroups",
                "ec2:DescribePrefixLists",
                "ec2:DescribeReservedInstancesOfferings",
                "ec2:DescribeSpotInstanceRequests",
                "ec2:DescribeSpotPriceHistory",
            ],
            "Resource": "*",
        },
    ],
}

ANYSCALE_IAM_PERMISSIONS_EC2_INITIAL_RUN = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SetupEC2",
            "Effect": "Allow",
            "Action": [
                # Anyscale runs this on the first time a cloud is configured.
                "ec2:CreateSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                # For configuring VPCs
                "ec2:DescribeVpcs",
                "ec2:CreateVpc",
                "ec2:ModifyVpcAttribute",
                "ec2:CreateVpcEndpoint",
                # Add subnets
                "ec2:CreateSubnet",
                "ec2:ModifySubnetAttribute",
                # Add InternetGateway
                "ec2:CreateInternetGateway",
                "ec2:AttachInternetGateway",
                "ec2:DescribeInternetGateways",
                # Connect InternetGateway to Internet
                "ec2:CreateRouteTable",
                "ec2:AssociateRouteTable",
                "ec2:CreateRoute",
                "ec2:ReplaceRoute",
                # NAT Gateway Setup
                "ec2:CreateNatGateway",
                "ec2:DescribeNatGateways",
            ],
            "Resource": "*",
        },
        {
            "Sid": "CleanupEC2",
            "Effect": "Allow",
            "Action": [
                # Anyscale runs this on the first time a cloud is configured.
                "ec2:DeleteSecurityGroup",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                # Remove VPC
                "ec2:DeleteVpc",
                "ec2:DeleteVpcEndpoints",
                # Remove subnets
                "ec2:DeleteSubnet",
                # Remove InternetGateway
                "ec2:DeleteInternetGateway",
                "ec2:DetachInternetGateway",
                # Disconnect InternetGateway
                "ec2:DeleteRouteTable",
                "ec2:DisassociateRouteTable",
                "ec2:DeleteRoute",
                # Remove NATGateway
                "ec2:DeleteNatGateway",
            ],
            "Resource": "*",
        },
    ],
}

# Used for experimental readonly access to SSM
ANYSCALE_SSM_READONLY_ACCESS_POLICY_DOCUMENT = {
    "Version": "2012-10-17",
    "Statement": {
        "Sid": "SecretsManagerReadOnly",
        "Effect": "Allow",
        "Action": [
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret",
            "secretsmanager:ListSecrets",
        ],
        "Resource": "*",
    },
}

# Used for experimental read and write access to SSM
ANYSCALE_SSM_READ_WRITE_ACCESS_POLICY_DOCUMENT = {
    "Version": "2012-10-17",
    "Statement": {
        "Sid": "SecretsManagerReadWrite",
        "Effect": "Allow",
        "Action": [
            "secretsmanager:CreateSecret",
            "secretsmanager:PutSecretValue",
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret",
            "secretsmanager:ListSecrets",
        ],
        "Resource": "*",
    },
}
