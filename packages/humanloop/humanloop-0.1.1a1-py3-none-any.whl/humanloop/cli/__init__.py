import click


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.pass_context
@click.version_option()
def humanloop(ctx):
    pass
