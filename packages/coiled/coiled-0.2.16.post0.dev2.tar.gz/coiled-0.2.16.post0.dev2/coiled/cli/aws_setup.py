import json
import time
import traceback
from typing import Optional

import boto3
import botocore
import click
import coiled
import dask
import jsondiff
from rich import print
from rich.prompt import Confirm

from .utils import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--iam-user",
    default="coiled",
    help="IAM User to create in your AWS account",
)
@click.option(
    "--setup-policy",
    default=None,
    help="Non-default name for the setup IAM Policy, default `{iam-user}-setup`",
)
@click.option(
    "--ongoing-policy",
    default=None,
    help="Non-default name for the ongoing IAM Policy, default `{iam-user}-ongoing`",
)
@click.option(
    "--profile",
    default=None,
    envvar="AWS_PROFILE",
    help="AWS profile to use from your local AWS credentials file",
)
@click.option(
    "--update-policies",
    default=False,
    is_flag=True,
    help="Only update existing IAM Policies",
)
@click.option(
    "--region", default=None, help="AWS region to use when setting up your VPC/subnets"
)
@click.option(
    "-y",
    "--yes",
    default=False,
    is_flag=True,
    help="Don't prompt for confirmation, just do it!",
)
def aws_setup(
    iam_user: str,
    setup_policy: Optional[str],
    ongoing_policy: Optional[str],
    profile: Optional[str],
    update_policies: bool,
    region: Optional[str],
    yes: bool,
):
    if not do_setup(
        aws_profile=profile,
        slug=iam_user,
        setup_name=setup_policy,
        ongoing_name=ongoing_policy,
        just_update_policies=update_policies,
        region=region,
        yes=yes,
    ):
        pass
        # print("[red]The setup process didn't finish.[/red]")


DEFAULT_REGION = "us-east-1"

TAGS = [{"Key": "owner", "Value": "coiled"}]

PROMPTS = {
    "initial": "Proceed with IAM setup for Coiled?",
    "replace_access_key": (
        "Too many access keys already exist for user "
        "[green]{user_name}[/green]. "
        "Unable to retrieve secret for an existing key. "
        "Delete key [green]{key_id}[/green] and create a new key?"
    ),
}

SCRIPT_REQUIRED_IAM = [
    "iam:GetPolicy",
    "iam:ListAccessKeys",
    "iam:CreateUser",
    "iam:TagUser",
    "iam:CreatePolicy",
    "iam:CreatePolicyVersion",
    "iam:AttachUserPolicy",
    "iam:GetPolicyVersion",
    "iam:CreateAccessKey",
    "iam:DeleteAccessKey",
]

setup_doc = """{
   "Statement": [
      {
         "Sid": "Setup",
         "Effect": "Allow",
         "Resource": "*",
         "Action": [
            "ec2:AllocateAddress",
            "ec2:AssociateRouteTable",
            "ec2:AttachInternetGateway",
            "ec2:CreateInternetGateway",
            "ec2:CreateRoute",
            "ec2:CreateRouteTable",
            "ec2:CreateSubnet",
            "ec2:CreateVpc",
            "ec2:DeleteInternetGateway",
            "ec2:DeleteRoute",
            "ec2:DeleteRouteTable",
            "ec2:DeleteSubnet",
            "ec2:DeleteVpc",
            "ec2:DeregisterImage",
            "ec2:DescribeAddresses",
            "ec2:DescribeInternetGateways",
            "ec2:DetachInternetGateway",
            "ec2:DisassociateAddress",
            "ec2:DisassociateRouteTable",
            "ec2:GetConsoleOutput",
            "ec2:ModifySubnetAttribute",
            "ec2:ModifyVpcAttribute",
            "ec2:ReleaseAddress",
            "iam:AddRoleToInstanceProfile",
            "iam:AttachRolePolicy",
            "iam:CreateRole",
            "iam:CreatePolicy",
            "iam:CreateServiceLinkedRole",
            "iam:CreateInstanceProfile",
            "iam:DeleteRole",
            "iam:ListPolicies",
            "iam:ListInstanceProfiles",
            "iam:ListAttachedRolePolicies",
            "iam:TagInstanceProfile",
            "iam:TagPolicy",
            "iam:TagRole",
            "secretsmanager:CreateSecret",
            "secretsmanager:DeleteSecret",
            "secretsmanager:DescribeSecret",
            "secretsmanager:GetSecretValue",
            "secretsmanager:TagResource"
         ]
      }
   ],
   "Version": "2012-10-17"
}"""

ongoing_doc = """{"Statement": [
      {
         "Sid": "Ongoing",
         "Effect": "Allow",
         "Resource": "*",
         "Action": [
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:CreateFleet",
            "ec2:CreateImage",
            "ec2:CreateLaunchTemplate",
            "ec2:CreateLaunchTemplateVersion",
            "ec2:CreateRoute",
            "ec2:CreateSecurityGroup",
            "ec2:CreateTags",
            "ec2:DeleteFleets",
            "ec2:DeleteLaunchTemplate",
            "ec2:DeleteLaunchTemplateVersions",
            "ec2:DeleteSecurityGroup",
            "ec2:DescribeAvailabilityZones",
            "ec2:DescribeConversionTasks",
            "ec2:DescribeImages",
            "ec2:DescribeInstances",
            "ec2:DescribeInstanceTypeOfferings",
            "ec2:DescribeInstanceTypes",
            "ec2:DescribeInternetGateways",
            "ec2:DescribeKeyPairs",
            "ec2:DescribeLaunchTemplates",
            "ec2:DescribeNatGateways",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DescribeRegions",
            "ec2:DescribeRouteTables",
            "ec2:DescribeSecurityGroups",
            "ec2:DescribeSubnets",
            "ec2:DescribeVpcPeeringConnections",
            "ec2:DescribeVpcs",
            "ec2:ImportKeyPair",
            "ec2:RunInstances",
            "ec2:TerminateInstances",
            "ecr:BatchCheckLayerAvailability",
            "ecr:BatchGetImage",
            "ecr:CompleteLayerUpload",
            "ecr:CreateRepository",
            "ecr:DescribeImages",
            "ecr:DescribeRepositories",
            "ecr:GetAuthorizationToken",
            "ecr:GetDownloadUrlForLayer",
            "ecr:GetRepositoryPolicy",
            "ecr:InitiateLayerUpload",
            "ecr:ListImages",
            "ecr:PutImage",
            "ecr:UploadLayerPart",
            "iam:GetInstanceProfile",
            "iam:GetRole",
            "iam:ListAttachedRolePolicies",
            "iam:ListInstanceProfiles",
            "iam:ListPolicies",
            "iam:PassRole",
            "iam:TagRole",
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams",
            "logs:GetLogEvents",
            "logs:PutLogEvents",
            "logs:PutRetentionPolicy",
            "sts:GetCallerIdentity"
         ]
      }
   ],
   "Version": "2012-10-17"
}"""


def create_user(iam, name):
    arn = None
    try:
        r = iam.create_user(UserName=name, Tags=TAGS)
        arn = r["User"]["Arn"]
        coiled.add_interaction(action="CreateUser", success=True, arn=arn)
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"user [green]{name}[/green] already exists")
    return arn


def create_or_update_policy(iam, account, name, doc):
    try:
        r = iam.create_policy(PolicyName=name, PolicyDocument=doc)
        arn = r["Policy"]["Arn"]
        coiled.add_interaction(action="CreatePolicy", success=True, arn=arn)
    except iam.exceptions.EntityAlreadyExistsException:
        arn = f"arn:aws:iam::{account}:policy/{name}"
        update_policy(iam, account, name, doc)

    return arn


def get_policy_diff(iam, account, name, doc):
    existing_arn, changes = None, None

    arn = f"arn:aws:iam::{account}:policy/{name}"

    try:
        policy = iam.get_policy(PolicyArn=arn)
        existing_arn = arn
    except iam.exceptions.ClientError as e:
        error_code = e.response["Error"].get("Code")

        if error_code == "NoSuchEntity":
            return existing_arn, changes
        else:
            raise

    policy_version = iam.get_policy_version(
        PolicyArn=arn, VersionId=policy["Policy"]["DefaultVersionId"]
    )
    existing_doc = policy_version["PolicyVersion"]["Document"]

    doc_diff = jsondiff.diff(existing_doc, json.loads(doc), syntax="symmetric")

    if doc_diff:
        changes = doc_diff

    return existing_arn, changes


def show_policy_diff(doc_diff):
    if doc_diff:
        if "Statement" in doc_diff and len(doc_diff) == 1:
            if 0 in doc_diff["Statement"] and len(doc_diff["Statement"]) == 1:
                if (
                    "Action" in doc_diff["Statement"][0]
                    and len(doc_diff["Statement"][0]) == 1
                ):
                    action_changes = doc_diff["Statement"][0]["Action"]
                    line_changes = []

                    if jsondiff.symbols.insert in action_changes:
                        line_changes.extend(
                            [
                                (i, "+", n)
                                for (i, n) in action_changes[jsondiff.symbols.insert]
                            ]
                        )
                    if jsondiff.symbols.delete in action_changes:
                        line_changes.extend(
                            [
                                (i, "-", n)
                                for (i, n) in action_changes[jsondiff.symbols.delete]
                            ]
                        )

                    for i, change, line in sorted(line_changes):
                        line_color = "red" if change == "-" else "green"
                        print(f" [{line_color}][bold]{change}[/bold] ({i}) {line}")

                    return

        # if we couldn't print the short version, just print the raw diff object
        print(doc_diff)


def update_policy(iam, account, name, doc):
    policy_arn = f"arn:aws:iam::{account}:policy/{name}"
    try:
        r = iam.create_policy_version(
            PolicyArn=policy_arn, PolicyDocument=doc, SetAsDefault=True
        )
        coiled.add_interaction(
            action="CreatePolicyVersion", success=True, arn=policy_arn
        )
        new_version = r["PolicyVersion"]["VersionId"]
        print(
            f"Updated Policy [green]{policy_arn}[/green] is [bold]{new_version}[/bold]"
        )
        print()
    except Exception as e:
        coiled.add_interaction(
            action="CreatePolicyArn",
            success=False,
            arn=policy_arn,
            error_message=str(e),
        )
        # TODO check if we need to delete old policy version
        print("[red]Unable to update existing policy[/red]:")
        print(f"  [red]{e}[/red]")
        print()


def attach_policy(iam, user, policy_arn):
    # idempotent
    iam.attach_user_policy(UserName=user, PolicyArn=policy_arn)
    coiled.add_interaction(action="AttachUserPolicy", success=True, arn=policy_arn)


def make_access_key(iam, user, retry=0):
    try:
        r = iam.create_access_key(UserName=user)
        coiled.add_interaction(action="CreateAccessKey", success=True, user=user)

        key_id = r["AccessKey"]["AccessKeyId"]
        key_secret = r["AccessKey"]["SecretAccessKey"]

        return key_id, key_secret

    except iam.exceptions.LimitExceededException:
        coiled.add_interaction(
            action="CreateAccessKey",
            success=False,
            user=user,
            error_message="LimitExceededException",
        )
        if retry:
            print("[red]already retried, giving up[/red]")
            return None, None

        # FIXME let user select which key to delete
        # if Confirm.ask(PROMPTS["replace_access_key"].format(user_name=user, key_id=key_id), default=True):
        if delete_access_key(iam, user):
            return make_access_key(iam, user, retry + 1)

    return None, None


def get_user_access_keys(iam, user):
    try:
        r = iam.list_access_keys(UserName=user)
        coiled.add_interaction(action="ListAccessKeys", success=True, user=user)
        return True, r["AccessKeyMetadata"]
    except iam.exceptions.ClientError as e:
        error_code = e.response["Error"].get("Code")

        if error_code == "NoSuchEntity":
            coiled.add_interaction(
                action="ListAccessKeys",
                success=False,
                user=user,
                error_message=str(e),
            )
            return False, []
        else:
            raise


def delete_access_key(iam, user):
    r = iam.list_access_keys(UserName=user)
    key_id = r["AccessKeyMetadata"][0]["AccessKeyId"]

    # NOTE: --yes doesn't apply to this since currently
    if Confirm.ask(
        PROMPTS["replace_access_key"].format(user_name=user, key_id=key_id),
        default=True,
    ):
        coiled.add_interaction(action="prompt:DeleteAccessKey", success=True, user=user)
        iam.delete_access_key(UserName=user, AccessKeyId=key_id)
        coiled.add_interaction(
            action="DeleteAccessKey", success=True, user=user, key_id=key_id
        )
        print(f"    Deleted access key [green]{key_id}[/green]")
        print()
        return True
    else:
        coiled.add_interaction(
            action="prompt:DeleteAccessKey", success=False, user=user
        )

    return False


def wait_till_key_works(iam, key, secret):
    print("Waiting until access key is ready", end="")
    t0 = time.time()

    while t0 + 10 > time.time():
        try:
            coiled.utils.verify_aws_credentials(key, secret)
            # a little extra wait here also seems to help, otherwise we *still* yet error sometimes when trying to use
            print(".", end="")
            time.sleep(1)
            print()

            return True
        except iam.exceptions.ClientError as e:
            error_code = e.response["Error"].get("Code")
            if error_code == "InvalidClientTokenId":
                print(".", end="")
                time.sleep(1)
                continue

    print(
        "\nAccess key is still not ready. Please manually set up your Coiled account with AWS."
    )
    return False


def do_intro(sts, iam, region):
    print("This uses your local AWS credentials to setup AWS to use Coiled.\n")

    try:
        # get_caller_identity doesn't require any specific IAM rights
        identity = sts.get_caller_identity()
        account = identity.get("Account")
        identity_as = identity.get("Arn").split(":")[-1]

        coiled.add_interaction(
            action="GetCallerIdentity",
            success=True,
            account=account,
            identity_as=identity_as,
        )

        try:
            r = iam.list_account_aliases()
            account_alias = r.get("AccountAliases", [])[0]
            alias_string = f" ([green]{account_alias}[/green])"
            coiled.add_interaction(
                action="ListAccountAliases",
                success=True,
                account=account,
                alias=alias_string,
            )
        except Exception:
            # doesn't matter much if we can't get account alias
            alias_string = ""

        print(f"Current local AWS credentials:\t[green]{identity_as}[/green]")
        print(
            f"Proposed region for Coiled:\t[green]{region}[/green]\t(use `--region` to change)"
        )
        print(f"Proposed account for Coiled:\t[green]{account}[/green]{alias_string}")
        print(
            "If this not correct then please stop and select a different profile "
            "from your AWS credentials file using the `--profile` argument.\n"
        )
        print()

        return account
    except botocore.exceptions.NoCredentialsError:
        coiled.add_interaction(
            action="GetCallerIdentity",
            success=False,
            error_message="NoCredentialsError",
        )

        print("[red]Your local AWS credentials are not configured.[/red]")

        # is aws cli installed?
        # get_aws_cli_version = subprocess.run(["aws", "--version"], capture_output=True)
        # has_aws_cli = get_aws_cli_version.returncode == 0

        # explain cloudshell
        server_arg = (
            f"--server {dask.config.get('coiled.server', coiled.utils.COILED_SERVER)} \\ "
            if dask.config.get("coiled.server", coiled.utils.COILED_SERVER)
            is not coiled.utils.COILED_SERVER
            else ""
        )
        token_arg = f"--token {dask.config.get('coiled.token')} && \\"

        cli_lines = [
            "pip3 install coiled && \\ ",
            "coiled login \\ ",
            server_arg,
            token_arg,
            "coiled setup aws",
        ]
        cli_command = "\n  ".join(cli_lines)

        print(
            "\nYou can run Coiled setup from AWS CloudShell, which already has the AWS CLI installed and configured "
            "with your AWS credentials:"
        )
        print("1. Go to [link]https://console.aws.amazon.com/cloudshell[/link]")
        print(
            "2. Sign in to your AWS account (if you usually switch role or profile, you should do this)"
        )
        print(
            "3. Run the following command in CloudShell to continue the Coiled setup process:\n"
        )
        print(f"  [green]{cli_command}\n")

    except Exception as e:
        coiled.add_interaction(
            action="GetCallerIdentity", success=False, error_message=str(e)
        )
        print("Error determining your AWS account:")
        print(f"    [red]{e}[/red]")

    return None


def do_coiled_setup(iam, user_name, region, yes):
    key, secret = make_access_key(iam, user_name)

    success = False

    if key and secret:
        print("[bold]You can setup Coiled to use the AWS credentials you just created.")
        print(
            "This AWS access key will go to Coiled, where it will be stored securely and "
            "used to create clusters in your AWS account on your behalf."
        )
        print(
            "This will also create infrastructure in your account like a VPC and subnets "
            "none of which has a standing cost."
        )
        print()
        if yes or Confirm.ask(
            "Setup your Coiled account to use the AWS credentials you just created?",
            default=True,
        ):
            coiled.add_interaction(action="prompt:CoiledSetup", success=True)
            # wait on this for a bit till we don't get InvalidClientTokenId error
            if wait_till_key_works(iam, key, secret):
                print("Setting up Coiled to use your AWS account...")
                coiled.set_backend_options(
                    backend="aws",
                    aws_access_key_id=key,
                    aws_secret_access_key=secret,
                    aws_region=region,
                )
                success = True
                coiled.add_interaction(action="CoiledSetup", success=True)
            else:
                coiled.add_interaction(action="CoiledSetup", success=False)
                print(
                    "[red]Access key is still not ready. You need to complete Coiled setup manually."
                )
                print()
        else:
            coiled.add_interaction(action="prompt:CoiledSetup", success=False)

        if not success:
            with coiled.Cloud() as cloud:
                coiled_account = cloud.default_account
            print(
                "You'll need these credentials when setting up your Coiled account "
                f"at [link]https://coiled.cloud.io/{coiled_account}/account[/link]:"
            )
            print(f"    access key id: [green]{key}[/green]")
            print(f"    secret access key: [green]{secret}[/green]")


def do_full_setup(iam, user_name, account, region, setup_name, ongoing_name, yes):
    # Check for existing user
    user_exists, user_keys = get_user_access_keys(iam, user_name)
    if user_exists:
        print(
            f"IAM User [green]{user_name}[/green] already exists and has {len(user_keys)} access keys."
        )
        if len(user_keys) > 1:
            print(
                "Unable to create a new access key for this user without deleting an existing key."
            )
            # print("If you proceed, you'll be able to select which existing access key to delete. (TODO)")
        print(
            "To create a different user, stop now and specify a different name "
            "with the `--iam-user` argument."
        )
        print()

    # Check for existing policies
    setup_arn, setup_diff = get_policy_diff(iam, account, setup_name, setup_doc)
    ongoing_arn, ongoing_diff = get_policy_diff(iam, account, ongoing_name, ongoing_doc)

    print("Attempting to create/update the following resources in your AWS account:")

    if not user_exists:
        print(f"  Create IAM User:\t[green]{user_name}[/green]")
    print(f"  Create Access Key for user [green]{user_name}[/green]")

    if not setup_arn:
        print(f"  Create IAM Policy:\t[green]{setup_name}")
    if setup_diff:
        print(f"  Update IAM Policy:\t[green]{setup_name}")

    if not ongoing_arn:
        print(f"  Create IAM Policy:\t[green]{ongoing_name}")
    if ongoing_diff:
        print(f"  Update IAM Policy:\t[green]{ongoing_name}")

    print()

    if setup_diff:
        print(
            f"Proposed changes to the existing [green]{setup_name}[/green] IAM Policy:"
        )
        show_policy_diff(setup_diff)
        print()

    if ongoing_diff:
        print(
            f"Proposed changes to the existing [green]{ongoing_diff}[/green] IAM Policy:"
        )
        show_policy_diff(ongoing_diff)
        print()

    if not setup_arn or not ongoing_arn:
        print(
            "Documentation for IAM Policies at "
            "[link]https://docs.coiled.io/user_guide/aws_configure.html#create-iam-policies[/link]"
        )
        print()

    if not yes and not Confirm.ask(PROMPTS["initial"], default=True):
        coiled.add_interaction(action="prompt:Setup_AWS", success=False)
        return False

    coiled.add_interaction(action="prompt:Setup_AWS", success=True)

    create_arns = []

    if not user_exists:
        user_arn = create_user(iam, user_name)
        if user_arn:
            create_arns.append(user_arn)

    if not setup_arn:
        setup_arn = create_or_update_policy(iam, account, setup_name, setup_doc)
        create_arns.append(setup_arn)
    elif setup_diff:
        setup_arn = create_or_update_policy(iam, account, setup_name, setup_doc)

    if not ongoing_arn:
        ongoing_arn = create_or_update_policy(iam, account, ongoing_name, ongoing_doc)
        create_arns.append(ongoing_arn)
    elif ongoing_diff:
        ongoing_arn = create_or_update_policy(iam, account, ongoing_name, ongoing_doc)

    attach_policy(iam, user_name, setup_arn)
    attach_policy(iam, user_name, ongoing_arn)

    print()
    if create_arns:
        print("The following resources were created in your AWS account:")
        for arn in create_arns:
            print(f"  {arn}")
    print(
        f"IAM User [green]{user_name}[/green] is now setup with IAM Policies attached."
    )
    print()

    do_coiled_setup(iam, user_name, region, yes)


def do_just_update_policies(iam, account, setup_name, ongoing_name, yes):

    # Check for existing policies
    setup_arn, setup_diff = get_policy_diff(iam, account, setup_name, setup_doc)
    ongoing_arn, ongoing_diff = get_policy_diff(iam, account, ongoing_name, ongoing_doc)

    if not setup_arn:
        print(
            f"[red]WARNING[/red]: No IAM Policy named [green]{setup_name}[/green] found."
        )
        print(
            "Use `--setup-name` to specify a different name for the existing setup policy."
        )
        print()

    if not ongoing_arn:
        print(
            f"[red]WARNING[/red]: No IAM Policy named [green]{ongoing_name}[/green] found"
        )
        print(
            "Use `--ongoing-name` to specify a different name for the existing setup policy."
        )
        print()

    if setup_diff:
        print(
            f"Proposed changes to the existing [green]{setup_name}[/green] IAM Policy:"
        )
        show_policy_diff(setup_diff)
        print()

    if ongoing_diff:
        print(
            f"Proposed changes to the existing [green]{ongoing_diff}[/green] IAM Policy:"
        )
        show_policy_diff(ongoing_diff)
        print()

    if setup_arn and ongoing_arn and not setup_diff and not ongoing_diff:
        print("Your AWS IAM Policies are up-to-date")
    elif setup_arn and not setup_diff:
        print("Your [bold]setup[/bold] IAM Policy is up-to-date")
        print("You may need to update your [bold]ongoing[/bold] IAM Policy.")
    elif ongoing_arn and not ongoing_diff:
        print("Your [bold]ongoing[/bold] IAM Policy is up-to-date")
        print("You may need to update your [bold]setup[/bold] IAM Policy.")

    elif not yes and not Confirm.ask(PROMPTS["initial"], default=True):
        return False

    if setup_diff:
        update_policy(iam, account, setup_name, setup_doc)

    if ongoing_diff:
        update_policy(iam, account, ongoing_name, ongoing_doc)


def do_setup(
    aws_profile, slug, setup_name, ongoing_name, just_update_policies, region, yes=False
):
    try:
        import getpass
        import socket

        local_user = f"{getpass.getuser()}@{socket.gethostname()}"
    except Exception:
        local_user = ""

    # TODO check for Coiled login, explain that we need this to automatically do Coiled setup, but they can do manually
    # call coiled.Cloud() here if we want to ensure/force log in -- is there way to just check?
    coiled.add_interaction(
        action="CliSetupAws",
        success=True,
        local_user=local_user,
        # use keys that match the cli args
        profile=aws_profile,
        iam_user=slug,
        setup_policy=setup_name,
        ongoing_policy=ongoing_name,
        update_policies=just_update_policies,
        region=region,
        yes=yes,
    )

    try:
        try:
            session = boto3.Session(profile_name=aws_profile)
            coiled.add_interaction(
                action="BotoSession",
                success=True,
                profile=aws_profile,
                region_name=session.region_name,
            )
        except botocore.exceptions.ProfileNotFound:
            coiled.add_interaction(
                action="BotoSession",
                success=False,
                profile=aws_profile,
                error_message="ProfileNotFound",
            )
            print()
            print(
                f"[red]The profile `{aws_profile}` is not configured in your local AWS credentials."
            )
            print(
                "If this isn't the correct AWS identity or account, you can specify a different profile "
                "from your AWS credentials file using the `--profile` argument."
            )
            return False

        region = region or session.region_name or DEFAULT_REGION

        user_name = slug
        setup_name = setup_name or f"{slug}-setup"
        ongoing_name = ongoing_name or f"{slug}-ongoing"

        iam = session.client("iam")
        sts = session.client("sts")

        try:

            account = do_intro(sts, iam, region=region)
            if not account:
                return False

            if just_update_policies:
                do_just_update_policies(iam, account, setup_name, ongoing_name, yes=yes)
            else:
                do_full_setup(
                    iam, user_name, account, region, setup_name, ongoing_name, yes=yes
                )

        except iam.exceptions.ClientError as e:
            error_code = e.response["Error"].get("Code")
            error_msg = e.response["Error"].get("Message")
            error_op = e.operation_name

            coiled.add_interaction(
                action=error_op, success=False, error_message=error_msg
            )

            if "AccessDenied" in str(e):
                print()
                print(
                    f"Insufficient permissions to [green]{error_op}[/green] using current AWS profile/user."
                )
                print(
                    "You may want to try with a different AWS profile that has different permissions."
                )
                print()
                print(f"[red]{error_msg}[/red]")
                print()
                print(
                    "To run this setup script you'll need the following IAM permissions:"
                )
                for permission in SCRIPT_REQUIRED_IAM:
                    print(f"- {permission}")
                print(
                    "If you don't have access to an AWS profile with these permissions, you may need to ask "
                    "someone with administrative access to your AWS account to help you create the IAM User "
                    "and IAM Policies described in our documentation: "
                    "[link]https://docs.coiled.io/user_guide/aws_configure.html[/link]"
                )
                return False
            else:
                print()
                print(f"Something went wrong when trying to [green]{error_op}[/green].")
                print()
                print(f"[red][bold]{error_code}[/bold]: {error_msg}[/red]")
                print()
                return False

    # catch all so we make sure all errors are tracked
    except KeyboardInterrupt as e:
        tb = "\n".join(traceback.format_tb(e.__traceback__))
        coiled.add_interaction(
            action="KeyboardInterrupt", success=False, error_message=tb
        )
        raise

    except Exception as e:
        msg = traceback.format_exc()
        coiled.add_interaction(action="Unknown", success=False, error_message=msg)
        # TODO
        print()
        print("[red]An unhandled exception happened!")
        print(e)
        return False

    return True
