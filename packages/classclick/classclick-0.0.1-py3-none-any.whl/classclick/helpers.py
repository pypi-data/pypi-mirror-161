import click


def echo(text, *args, **kwargs):
    def func():
        click.echo(text, *args, **kwargs)
    return func
