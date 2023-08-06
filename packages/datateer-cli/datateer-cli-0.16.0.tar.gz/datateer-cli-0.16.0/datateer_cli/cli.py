import click

from . import __version__
from .commands.config.commands import config
from .commands.docs.commands import docs
from .commands.echo.echo_commands import echo
from .commands.infra.commands import infra
from .commands.pipeline.commands import pipeline

name = "Datateer CLI"


@click.group()
@click.pass_context
@click.version_option(
    version=__version__
)  # note this version param should not be necessary according to https://click.palletsprojects.com/en/8.0.x/api/#click.version_option
def main(ctx):
    pass


main.add_command(config)
main.add_command(docs)
main.add_command(echo)
main.add_command(infra)
main.add_command(pipeline)
