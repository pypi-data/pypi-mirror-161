import os
import sys
from contextlib import contextmanager
from importlib import find_loader, import_module

import click

from .deploy_flow import do_deploy


@click.group(help="Commands related to data pipelines and Prefect flows")
def pipeline():
    pass


@pipeline.command(
    help="Packages and deploys a pipeline to Prefect Cloud. The NAME argument is the name of the pipeline. Will look for './orchestration/pipeline_<name>.py"
)
@click.argument("name", required=True)
@click.option(
    "-a",
    "--aws-account-id",
    envvar="AWS_ACCOUNT_ID",
    help="The AWS account ID of the deployment target (defaults to env var AWS_ACCOUNT_ID)",
)
@click.option(
    "-r",
    "--aws-region",
    envvar="AWS_REGION",
    help="The AWS region of the deployment target(defaults to env var AWS_REGION)",
)
@click.option(
    "-c",
    "--client-code",
    envvar="CLIENT_CODE",
    help="The client's Datateer client code (defaults to env var CLIENT_CODE)",
)
@click.option(
    "-d",
    "--deploy-key-prefect-lib",
    envvar="DEPLOY_KEY_PREFECT_LIB",
    help="The GitHub deployment key for the datateer-prefect repository (defaults to env var DEPLOY_KEY_PREFECT_LIB)",
)
@click.option(
    "-e",
    "--environment",
    envvar="DATATEER_ENV",
    type=click.Choice(["prod", "stg", "qa", "int"], case_sensitive=False),
    required=True,
    help="The target Datateer environment (defaults to env var DATATEER_ENV)",
)
@click.option(
    "-p",
    "--prefect-cloud-api-key",
    envvar="PREFECT__CLOUD__API_KEY",
    help="API key to connect to Prefect Cloud API (defaults to env var PREFECT__CLOUD__API_KEY)",
)
def deploy(
    name,
    aws_account_id,
    aws_region,
    client_code,
    deploy_key_prefect_lib,
    environment,
    prefect_cloud_api_key,
):
    with modified_environ(
        DATATEER_ENV=environment,
        CLIENT_CODE=client_code,
        DEPLOY_KEY_PREFECT_LIB=deploy_key_prefect_lib,
        PREFECT__CLOUD__API_KEY=prefect_cloud_api_key,
    ):
        pipeline = import_pipeline(name=name)
        pipeline.name = f"{client_code}-{pipeline.name}-{environment}"
        custom_modules = list(get_custom_modules())
        click.echo(
            f"Deploying flow {pipeline.name} to the {environment} environment on {aws_region}"
        )
        do_deploy(
            pipeline,
            aws_account_id,
            aws_region,
            client_code,
            environment,
            custom_modules,
        )


@pipeline.command(
    help="Visualizes a pipeline's DAG of tasks. The NAME argument is the name of the pipeline. Will look for './orchestration/pipeline_<name>.py"
)
@click.argument("name", required=True)
def visualize(name):
    pipeline = import_pipeline(pipelines_dir="./orchestration", name=name)
    pipeline.visualize()


# @pipeline.command()
# @click.argument("name", required=True, help="The name of the pipeline. Will look for './orchestration/pipeline_<name>.py")
# def run(name):
#     # if aws_profile:
#     #     os.environ["AWS_PROFILE"] = aws_profile
#     try:
#         pipeline = import_pipeline(pipelines_dir='./orchestration', name=name)
#         pipeline.run(run_on_schedule=False)
#     except Exception as ex:
#         if "Secrets Manager can't find the specified secret" in str(ex):
#             log.error(
#                 f'Could not find the settings for environment {os.getenv("DATATEER_ENV")}. Have you run datateer push-config {os.getenv("DATATEER_ENV")}?'
#             )
#         else:
#             raise


def get_custom_modules(pipelines_dir="orchestration"):
    """Generator that returns all custom modules that can be added to a pipeline deployment
    See https://docs.prefect.io/api/latest/storage.html#docker

    Yields a tuple of full_path, relative_path
    """
    for root, dirs, files in os.walk(pipelines_dir):
        for filename in files:
            if (
                filename.endswith("__init__.py")
                or "pipeline_" in filename
                or not filename.endswith(".py")
            ):
                continue
            full_path = os.path.abspath(os.path.join(root, filename))
            rel_path = os.path.join(root, filename).replace(f"{pipelines_dir}/", "")
            yield full_path, rel_path


def import_pipeline(pipelines_dir="orchestration", name=None):
    # TODO: default to "pipeline.py and log message about it"
    name = f"pipeline_{name}" if name is not None else "pipeline"
    path = os.path.join(os.getcwd(), pipelines_dir)
    click.echo(f"Importing pipeline {name} from {path}")
    sys.path.insert(1, path)  # finds the pipeline here
    mod = import_module(name)
    return mod.flow

    # try:
    # TODO: remove this testing line
    # except ModuleNotFoundError as ex:
    #     print(f"ERROR: Could not find the module you requested: {ex}.")
    #     print("Are you in the pipeline project's root directory?")
    #     print('Have you activated the venv in the pipeline project? (Run "source venv/bin/activate")')


@contextmanager
def modified_environ(*remove, **update):
    """
    Temporarily updates the ``os.environ`` dictionary in-place.
    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.
    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # remove any None values
    for k, v in dict(update).items():
        if v is None:
            del update[k]

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]
