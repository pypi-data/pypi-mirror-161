# """

# """
# import os
# import subprocess
# import sys
# from importlib import find_loader, import_module
# from time import time
# from typing import Dict, List

# import boto3
# import click
# import yaml

# import datateer_cli.logging as log
# from datateer_cli.commands.pipeline import deploy_flow
# from datateer_cli.commands.docs import docs as docs_commands
# from datateer_cli.commands.pipeline import settings as pipeline_settings


# class DatateerContext:
#     def __init__(self):
#         self.config = None  # stores the config from .datateer/config.yml
#         self.flow = None  # stores the Flow between import and deploy


# @click.group()
# @click.pass_context
# def cli(ctx):
#     ctx.ensure_object(DatateerContext)
#     ctx.obj.config = pipeline_settings.load_config()
#     for k, v in ctx.obj.config.items():
#         os.environ[k.upper()] = str(v)


# @cli.command()
# @click.pass_context
# def tester(ctx):
#     print(ctx.obj.config["datateer_deploy_key_prefect_lib"])


# @cli.command(help="Displays a simple hello message")
# @click.option(
#     "-t",
#     "--text",
#     default="world",
#     help="Whatever you send in will get echoed back out to you",
# )
# def hello(text):
#     click.echo(f"hello1111, {text}")


# @cli.command(help="Display the version and exit")
# def version():
#     from datateer_cli import __version__

#     print(__version__)


# region agent


# @cli.group(help="For working with the Prefect agent that executes pipelines")
# def agent():
#     pass


# endregion

# region developer


# @cli.group(help="Commands to help the Datateer engineers with projects")
# def developer():
#     pass


# @developer.command(
#     help="Creates virtual environments; intended to be used at the repo root"
# )
# @click.pass_context
# @click.option(
#     "-v",
#     "--venv-root",
#     default="venv",
#     help="The name of the folder where you want your venvs",
# )
# @click.option(
#     "-r",
#     "--requirements-dir",
#     default="requirements",
#     help='The name of the directory that contains your requirements files. "requirements.txt" will be installed in the main venv at venv/ or the directory specified in --venv-root. "requirements-dev.txt" will also be installed at the venv root. All others named "requirements-<name>.txt will be installed in independent venvs at venv/<name>.',
# )
# def venvs(ctx, venv_root, requirements_dir):
#     from datateer_cli.developer_setup import setup

#     setup(venv_root, requirements_dir)


# @developer.command(
#     help="Initialize Terraform remote state. Should be run in the <client-code>-infrastructure repository root, because it modifies the main.tf file"
# )
# @click.option("-c", "--client-code", required=True)
# @click.option("-r", "--aws-region", default="us-east-1")
# @click.option("-p", "--aws-profile", required=True)
# def init_remote_state(aws_profile, client_code, aws_region):
#     os.environ["AWS_DEFAULT_REGION"] = aws_region
#     os.environ["CLIENT_CODE"] = client_code
#     from datateer_cli.terraform_util import configure_remote_state_backend

#     configure_remote_state_backend(aws_profile)
# endregion

# region docs


# @cli.group(help="For generating docs including erds and dbt docs")
# def docs():
#     pass


# @docs.command(help="Deploys erd-diagrams, intended to be used at the root")
# @click.pass_context
# def generate_erd(searchdir):

#     docs_commands.generate_erd(searchdir)


# @docs.command(
#     name="deploy",
#     help="Deploys docs including erd-diagrams and dbt docs, intended to be used at the root",
# )
# @click.pass_context
# @click.option(
#     "-m", "--dbt-models-dir", default="dbt/models", help="The dbt models directory."
# )
# @click.option("-t", "--target", default="prod")
# @click.option("-c", "--client-code", default=None)
# def deploy_docs(ctx, dbt_models_dir, target, client_code):
#     if client_code is None:
#         client_code = os.getenv("CLIENT_CODE")
#     if client_code is None:
#         raise click.ClickException("Client code not found.")
#     docs_commands.deploy_docs(dbt_models_dir, target, client_code)


# end region

# region pipeline
# def import_pipeline(pipelines_dir="orchestration", name=None):
#     try:
#         sys.path.insert(1, os.getcwd())  # finds the pipeline here
#         # todo: I would like to be able to avoid installing datateer into the project's requirements, and just run the global version. But if I do that,
#         # then it cannot import correctly within the venv
#         # sys.path.insert(1, os.path.abspath('venv/lib/python3.8/site-packages/')) # finds prefect here
#         # sys.path.insert(1, os.path.abspath('venv/src/datateer-prefect')) # finds datateer.prefect here
#         # print(sys.prefix)
#         # print('-----', sys.path)
#         path = f"pipeline_{name}" if name is not None else "pipeline"
#         mod = import_module(f"{pipelines_dir}.{path}")
#         return mod.flow
#     except ModuleNotFoundError as ex:
#         print(f"ERROR: Could not find the module you requested: {ex}.")
#         print("Are you in the pipeline project's root directory?")
#         print(
#             'Have you activated the venv in the pipeline project? (Run "source venv/bin/activate")'
#         )


# @cli.group(help="For working with pipelines")
# @click.pass_context
# @click.option(
#     "-n",
#     "--name",
#     default=None,
#     help='The name of the pipeline. e.g. pipeline_<name>.py. If not provided, "pipeline.py" will be used as the pipeline file name',
# )
# @click.option(
#     "-p",
#     "--pipelines-dir",
#     default="orchestration",
#     help='The name of the directory that contains your pipeline files. The default is "orchestration"',
# )
# @click.option(
#     "-e",
#     "--environment",
#     default="local",
#     help="The name of the environment. Loads the pipeline in context of that environment, including environment variables",
#     type=click.Choice(["local", "prod", "staging"], case_sensitive=False),
# )
# def pipeline(ctx, name, pipelines_dir, environment="local"):
#     ctx.ensure_object(DatateerContext)
#     os.environ["DATATEER_ENV"] = environment
#     pipeline = import_pipeline(pipelines_dir=pipelines_dir, name=name)
#     ctx.obj.flow = pipeline


# @pipeline.command(
#     help="push environment settings into secure storage so that it can be used at runtime."
# )
# @click.option(
#     "-c",
#     "--config-dir",
#     default=".datateer",
#     help="Relative path to the configuration directory. Defaults to .datateer",
# )
# @click.option(
#     "-s",
#     "--settings-file",
#     help="Relative path to a settings file containing environment variables. Defaults to .env",
# )
# def push_settings(config_dir, settings_file=None):
#     environment = os.getenv("DATATEER_ENV")
#     settings_file = pipeline_settings.determine_settings_file(
#         environment, settings_file
#     )
#     settings = pipeline_settings.load_settings(settings_file)
#     pipeline_settings.push_settings(settings, environment)
#     pipeline_settings.push_config(config_dir, environment)


# @pipeline.command()
# @click.option("-c", "--config-dir", default=".datateer")
# def pull_config(config_dir):
#     environment = os.environ["DATATEER_ENV"]
#     pipeline_settings.pull_config(config_dir, environment)


# @pipeline.command()
# @click.pass_context
# def debug(ctx):
#     from pathlib import Path

#     path = Path(__file__)
#     print("This is the debug function for testing things out")
#     print("parent: ", path.parent)
#     print(ctx.obj.flow)


# @pipeline.command(help="packages and deploys a pipeline")
# @click.option("--debug", is_flag=True)
# @click.pass_context
# def deploy(ctx, debug):
#     ctx.ensure_object(DatateerContext)
#     environment = os.environ["DATATEER_ENV"]
#     ctx.obj.flow.name += "-" + environment
#     click.echo(f"Deploying flow {ctx.obj.flow.name} to the {environment} environment")
#     deploy_flow.do_deploy(ctx.obj.flow, environment=environment, debug=debug)


# @pipeline.command()
# @click.pass_context
# def visualize(ctx):
#     ctx.ensure_object(DatateerContext)
#     ctx.obj.flow.visualize()


# endregion


# if __name__ == "__main__":
#     cli()
