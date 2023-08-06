import json
import os
from pathlib import Path
from typing import Dict

import boto3
import botocore
import click
import yaml
from botocore.exceptions import ClientError

# DATATEER_CONFIG_DIR = './datateer'
DEPLOY_CONFIG_FILE = "./.datateer/config.yml"
# DOCKERFILE = './datateer/Dockerfile'

DEFAULTS = {
    "DBT_EXECUTABLE": "/datateer/venv/dbt/bin/dbt",  # 'venv/dbt/bin/dbt',
    "DBT_PROFILES_DIR": "/datateer/.datateer/dbt/",  # '.datateer/dbt',
    "MELTANO_EXECUTABLE": "/datateer/venv/meltano/bin/meltano",  # 'venv/meltano/bin/meltano'
}

REQUIREDS = [
    "S3_RAW_BUCKET",
    "S3_PREPPED_BUCKET",
    "S3_PREFECT_RESULTS_BUCKET",
    "SERVICE_DESK_CUSTOMER_ID",
]

DEFAULT_REGION = "us-east-1"

# flake8: noqa: E402
import datateer_cli.logging as log


def determine_settings_file(environment: str, settings_file: str = None) -> str:
    """Determines which settings file to use, and returns a path to it"""
    if settings_file:
        if not Path(settings_file).exists():
            raise ValueError(f"Could not find file {settings_file}")
        return settings_file

    path = f".datateer/.env.{environment}"
    if not Path(path).exists():
        raise ValueError(f"Could not find file {path}")
    return path


def load_settings(path) -> Dict[str, str]:
    with open(path) as f:
        lines = [
            line.lstrip("export ")
            for line in f.read().splitlines()
            if not line.startswith("#") and "=" in line
        ]
        settings = {
            key: val for key, val in (line.split("=", 1) for line in lines)
        }  # os.getenv(key)
    log.info(f"Loaded {len(settings)} settings from {path}")
    return settings


def apply_defaults(settings: dict):
    defaults = 0
    for key in DEFAULTS:
        if key not in settings:
            # log.info(f'Did not find setting "{key}", using default value "{DEFAULTS[key]}"')
            settings[key] = DEFAULTS[key]
            defaults += 1
    if defaults:
        log.info(f"Using {defaults} defaults that were not set explicitly")


def verify_requireds(settings: dict):
    missings = [key for key in REQUIREDS if key not in settings]
    if missings:
        log.error(f'Missing {len(missings)} required settings: {", ".join(missings)}')
        raise click.Abort()


def push_config(config_dir: str, aws_region, environment):
    """Pushed a configuration up into the S3 config bucket. Puts it into a top-level folder with the name of the environment"""
    session = boto3.session.Session(region_name=aws_region)
    delete_config(environment, session)
    config_bucket = get_parameter("/pipeline/config_bucket", session=session)
    bucket = session.resource("s3").Bucket(config_bucket)

    file_count = 0
    for root, dirs, files in os.walk(config_dir):
        for file in files:
            dir = os.path.relpath(root, config_dir)
            if (
                dir == "."
                or file.lower().startswith("readme")
                or file.lower().endswith(".example")
                or file.lower().startswith(".env")
            ):
                continue
            if dir == ".":
                path = os.path.join(environment, file)
            else:
                path = os.path.join(environment, dir, file)
            # print(f'uploading file {path}')
            bucket.upload_file(os.path.join(root, file), path)
            file_count += 1
    log.success(f"Uploaded {file_count} files to bucket {config_bucket}/{environment}")


def pull_config(
    config_dir: str, aws_region, environment, session=None, config_bucket=None
):
    """Pulls a configuration down from S3. Intended to be used by the CI pipeline, but could be used to pull the config to a local folder for insepction"""
    session = session or boto3.session.Session(region_name=aws_region)
    config_bucket = config_bucket or get_parameter(
        "/pipeline/config_bucket", session=session
    )
    bucket = session.resource("s3").Bucket(config_bucket)
    file_count = 0
    for obj in bucket.objects.filter(Prefix=environment):
        if obj.key.endswith("/"):
            continue
        path = os.path.join(config_dir, "/".join(obj.key.split("/")[1:]))
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        bucket.Object(obj.key).download_file(path)
        file_count += 1
    log.success(
        f"Downloaded {file_count} files into {config_dir} from bucket {config_bucket}/{environment}"
    )


def delete_config(environment: str, session=None):
    """Deletes an environment's configuration. Used by "push_config" to clear things out before uploading an updated configuration"""
    config_bucket = get_parameter("/pipeline/config_bucket", session)
    bucket = session.resource("s3").Bucket(config_bucket)

    bucket.objects.filter(Prefix=environment).delete()


# def push_settings(settings: dict, environment: str):
#     apply_defaults(settings)
#     verify_requireds(settings)
#     client = boto3.client("secretsmanager")
#     name = f"datateer-pipeline-settings-{environment}"
#     value = json.dumps(settings)
#     try:
#         client.create_secret(
#             Name=name,
#             Description="Managed by Datateer. A collection of settings intended to be injected into a data pipeline as environment variables.",
#             SecretString=value,
#         )
#     except client.exceptions.ResourceExistsException as ex:
#         pass
#     client.put_secret_value(SecretId=name, SecretString=value)
#     log.success(f"Wrote {len(settings)} settings to secret {name}")
#     # print(json.dumps(settings, indent=4, sort_keys=True))


# def load_config(path: str = None) -> Dict[str, str]:
#     path = path or DEPLOY_CONFIG_FILE
#     config = {}

#     if not os.path.exists(path):
#         log.warn(
#             f"Could not find configuration file at {path}; Will attempt to use environment variables"
#         )
#         # raise click.Abort()
#     else:
#         with open(path) as f:
#             config = yaml.load(f, Loader=yaml.FullLoader)

#         if "aws_default_region" not in config:
#             log.warn(
#                 f'Did not find "aws_default_region" in {path}. Defaulting to region "{DEFAULT_REGION}".'
#             )
#             config["aws_default_region"] = DEFAULT_REGION

#         expected_props = ["client_code", "aws_account_id"]
#         for prop in expected_props:
#             missing = 0
#             if prop not in config:
#                 log.error(f'Missing required configuration property "{prop}" in {path}')
#                 missing += 1
#             if missing:
#                 raise click.Abort()

#     return config


def get_parameter(name: str, session=None) -> str:
    if not session:
        session = boto3
    client = session.client("ssm")
    try:
        value = client.get_parameter(Name=name, WithDecryption=True)
    except ClientError:
        return None

    return value["Parameter"]["Value"]
