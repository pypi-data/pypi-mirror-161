import click


def info(msg: str) -> None:
    click.echo(msg)


def error(msg: str) -> None:
    click.echo(click.style(msg, fg="red"))


def success(msg: str) -> None:
    click.echo(click.style(msg, fg="green"))


def warn(msg: str) -> None:
    click.echo(click.style(msg, fg="yellow"))
