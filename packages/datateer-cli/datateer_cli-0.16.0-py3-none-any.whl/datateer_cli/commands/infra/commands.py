import click


@click.group(help="Commands related to client infrastructure")
def infra():
    pass


@infra.command(
    help="Initialize Terraform remote state for the client's infrastructure. Should be run in the <client-code>-infrastructure repository root, because it modifies the main.tf file by injecting a 'backend S3' resource block. See more at https://www.terraform.io/language/settings/backends/s3"
)
@click.option(
    "-p",
    "--aws-profile",
    envvar="AWS_PROFILE",
    required=True,
    help="(defaults to env var AWS_PROFILE)",
)
@click.option(
    "-r",
    "--aws-region",
    envvar="AWS_REGION",
    required=True,
    help="(defaults to env var AWS_REGION)",
)
@click.option(
    "-c",
    "--client-code",
    envvar="CLIENT_CODE",
    required=True,
    help="(defaults to env var CLIENT_CODE)",
)
def init_remote_state(aws_profile, aws_region, client_code):
    from datateer_cli.commands.infra.terraform_util import (
        configure_remote_state_backend,
    )

    configure_remote_state_backend(aws_profile, aws_region, client_code)
