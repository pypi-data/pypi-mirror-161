import click


@click.command(help="Echoes the text you send. Useful for testing")
@click.argument("text", default="world")
def echo(text):
    click.echo(f"hello, {text}")
