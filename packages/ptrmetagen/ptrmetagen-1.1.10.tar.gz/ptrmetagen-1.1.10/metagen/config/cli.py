import click
from metagen.main import CONFIG

@click.group()
@click.version_option()
def main():
    """
    Ptr-Metagen Congiguration
    """
    pass


@main.group('Register', invoke_without_command=True)
@click.option('--show', '-s', 'show', is_flag=True,
              help='Show actual Register configuration')
def config(show):
    """Metagen configuration"""
    if show:
        click.echo(CONFIG)


if __name__ == "__main__":
    main()