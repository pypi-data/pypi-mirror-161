import os
import subprocess
import sys
import traceback
from time import time

import boto3
import yaml

import datateer_cli.logging as log


def generate_erd(searchdir: str) -> None:
    """
    Generates entity relationship diagrams for upload to the client's site

    Parameters
    ----------
    searchdir: str
        The directory to search for dbt model configuration files. Will recursively search this directory.
    """
    from datateer_cli.commands.docs.generate_erd import generate, searchdir

    generate(searchdir)


def build_dbt_docs_command(target: str) -> None:
    """
    Runs the dbt docs generate command to create the html that will be uploaded to the client's site.

    Parameters
    ----------
    target: str
        The target database environment to use to generate the dbt docs.
    """

    command = f"dbt docs generate --target {target}".split()
    try:
        subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        return command
    except Exception:
        print(sys.exc_info())


def build_aws_s3_sync_command(client_code: str) -> None:
    """
    Uploads newly created documentation to the client's S3 bucket and removes older files.

    Parameters
    ----------
    client_code: str
        The three-character client code.
    """
    command = f"aws s3 cp dbt/target/ s3://dbt.{client_code}.datateer.com --recursive --profile admin-{client_code}".split()
    try:
        subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        return command
    except Exception:
        print(sys.exc_info())


def invalidate_cloudfront_cache() -> None:
    """
    Invalidates the cloudfront cache.

    """
    name = "docs_site_cloudfront_distribution_id"
    client = boto3.client("ssm")
    res = client.get_parameter(Name=name)["Parameter"]["Value"]
    client = boto3.client("cloudfront")
    client.create_invalidation(
        DistributionId=res,
        InvalidationBatch={
            "Paths": {
                "Quantity": 1,
                "Items": ["/*"],
            },
            "CallerReference": str(time()).replace(".", ""),
        },
    )


def deploy_docs(searchdir: str, target: str, client_code: str) -> None:
    """
    Generates documentation and deploys it to the client's documentation site.

    Parameters
    ----------
    searchdir: str
        The directory to search for dbt model configuration files. Will recursively search this directory.
    target: str
        The target database environment to use to generate the dbt docs.
    client_code: str
        The three-character client code.
    """

    generate_erd(searchdir)
    build_dbt_docs_command(target)
    build_aws_s3_sync_command(client_code)
    invalidate_cloudfront_cache()
