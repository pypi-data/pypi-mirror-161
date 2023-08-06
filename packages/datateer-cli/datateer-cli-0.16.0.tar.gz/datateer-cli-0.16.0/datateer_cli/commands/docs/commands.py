import click

from .docs import deploy_docs


@click.group(help="Commands related to documentation")
def docs():
    pass


@docs.command(
    help="Deploys docs including erd-diagrams and dbt docs, intended to be used at the root of a pipeline repository"
)
@click.option(
    "-m",
    "--dbt-models-dir",
    default="dbt/models",
    help="The dbt models directory",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    envvar="DATATEER_ENV",
    type=click.Choice(["prod", "stg", "qa", "int"], case_sensitive=False),
    required=True,
    help="The Datateer environment to use to generate the docs (defaults to env var DATATEER_ENV)",
)
@click.option(
    "-c",
    "--client-code",
    envvar="CLIENT_CODE",
    required=True,
    help="(defaults to env var CLIENT_CODE)",
)
def deploy(client_code, dbt_models_dir, target):
    deploy_docs(dbt_models_dir, target, client_code)
