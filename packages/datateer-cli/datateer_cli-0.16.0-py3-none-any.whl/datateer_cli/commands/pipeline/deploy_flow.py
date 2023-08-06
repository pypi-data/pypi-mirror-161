import glob
import logging
import os
import tempfile
from importlib import find_loader, import_module
from pathlib import Path
from shutil import copy, copytree, ignore_patterns
from typing import Dict

import boto3
import click
import pathspec
import yaml

from datateer_cli.commands.config import operations

DOCKERFILE_TEMPLATES_DIR = Path(__file__).parent.joinpath("flow")


def do_deploy(
    flow,
    aws_account_id,
    aws_region,
    client_code,
    environment,
    custom_modules=[],  # list of tuples: full_path, rel_path
    prefect_api_key=None,
    deploy_key_prefect_lib=None,
    prefect_results_bucket=None,
    debug=False,
):
    deploy_key_prefect_lib = deploy_key_prefect_lib or os.getenv(
        "DEPLOY_KEY_PREFECT_LIB"
    )
    if deploy_key_prefect_lib is None:
        raise Exception("deploy_key_prefect_lib is None but is required in do_deploy")

    prefect_api_key = prefect_api_key or os.getenv("PREFECT__CLOUD__API_KEY")
    if prefect_api_key is None:
        raise Exception(
            "prefect_api_key is required, either through a CLI parameter or an environment variable PREFECT__CLOUD__API_KEY"
        )

    if prefect_results_bucket is None:
        click.echo(
            "prefect_results_bucket in do_deploy is None, so the results of this flow's run will not be captured anywhere"
        )
    if os.getenv("MELTANO_DATABASE_URI") is None:
        print(
            "MELTANO_DATABASE_URI is None, so this flow will not attempt to connect to a meltano database"
        )
    else:
        print(
            f'MELTANO_DATABASE_URI is populated with value {os.getenv("MELTANO_DATABASE_URI")[0:12]}***'
        )

    # expensive loads, so defer until now
    from prefect.client.client import Client
    from prefect.executors import LocalExecutor

    # from prefect.environments import LocalEnvironment
    from prefect.run_configs import ECSRun
    from prefect.storage import Docker

    dockerfile_path = copy(os.path.join(DOCKERFILE_TEMPLATES_DIR, "Dockerfile"), ".")
    copy(os.path.join(DOCKERFILE_TEMPLATES_DIR, ".dockerignore"), ".")

    flow.storage = Docker(
        registry_url=image_registry_url(aws_account_id, aws_region),
        python_dependencies=["boto3"],
        dockerfile=dockerfile_path,
        image_tag="latest",
        files={
            full_path: os.path.join("/datateer/modules", module_path)
            for full_path, module_path in custom_modules
        },
        env_vars={
            "DATATEER_ENV": environment,
            "PYTHONPATH": "$PYTHONPATH:/datateer/modules/",
        },
        build_kwargs={
            "buildargs": {
                # during the build process, the build script runs "meltano install." By default, this command runs against an internal Sqlite database
                # To make sure this runs against the production meltano database, we ensure this env var exists and contains the connection string
                "MELTANO_DATABASE_URI": os.getenv("MELTANO_DATABASE_URI"),
                "DEPLOY_KEY_PREFECT_LIB": deploy_key_prefect_lib,
            }
        },
    )

    task_definition = {
        "networkMode": "awsvpc",
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "1 vcpu",
        "memory": "8 GB",
        "executionRoleArn": f"arn:aws:iam::{aws_account_id}:role/ecsTaskExecutionRole",
        "taskRoleArn": f"arn:aws:iam::{aws_account_id}:role/ecsTaskRole",
        "containerDefinitions": [
            {
                "name": "flow"
                # "logConfiguration": { # this won't create the log group, so we can't reference it until we have some mechanism to create it
                #     "logDriver": "awslogs",
                #     "options": {
                #         "awslogs-group": f"/datateer/pipelines/{flow.name}",
                #         "awslogs-region": os.environ["AWS_DEFAULT_REGION"],
                #         "awslogs-stream-prefix": "prefect-agent",
                #     },
                # },
            }
        ],
    }
    env_vars = {"DATATEER_ENV": environment, "AWS_DEFAULT_REGION": aws_region}
    if prefect_results_bucket is not None:
        env_vars["S3_PREFECT_RESULTS_BUCKET"] = prefect_results_bucket
    subnets = operations.get_parameter("/pipeline/allowed_subnets")

    if subnets:
        subnets = subnets.split(",")
    else:
        subnets = [
            operations.get_parameter("/pipeline/subnet_1"),
            operations.get_parameter("/pipeline/subnet_2"),
        ]

    flow.run_config = ECSRun(
        task_definition=task_definition,
        env=env_vars,
        run_task_kwargs={
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": subnets,
                    "securityGroups": [
                        operations.get_parameter("/pipeline/security_group")
                    ],
                    "assignPublicIp": "DISABLED",
                }
            }
        },
    )

    flow.executor = LocalExecutor()

    Client().create_project(client_code)
    register(flow, environment, client_code)


def register(flow, environment, client_code):
    import datateer_cli.docker_util as d

    d.docker_login()
    d.ensure_repository_exists(flow.name)
    flow.register(
        project_name=client_code,
        # add the environment label and the client label to restrict which agents will run this
        labels=[environment, client_code],
    )


def image_registry_url(aws_account_id, aws_region, include_https=False):
    """Builds a well formed docker registry URL
    Arguments:
        aws_account_id {string} -- the AWS account ID
        aws_region {string} -- the AWS region e.g. us-east-1 or eu-west-1

    Keyword Arguments:
        include_https {bool} -- True to include the https:// prefix, false to leave off (default: {False})

    Returns:
        string -- A well formed docker registry URL
    """
    # aws_account_id = boto3.client("sts").get_caller_identity()["Account"]
    registry = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
    return f"https://{registry}" if include_https else registry


# def validate_environment(ctx, name, environment):
#     path = '.env' if environment == 'local' else f'.env.{environment}'
#     if not os.path.exists(path):
#         raise click.BadParameter(f'Could not locate an .env file at {path}')
#     return environment
