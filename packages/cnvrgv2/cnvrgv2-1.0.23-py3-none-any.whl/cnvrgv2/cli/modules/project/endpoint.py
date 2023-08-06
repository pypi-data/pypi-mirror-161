import click
from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command


@click.group(name='endpoint')
def endpoint_group():
    pass


@endpoint_group.command()
@click.option('-s', '--slug', default=None, help=messages.ENDPOINT_SLUG)
@click.option('-n', '--name', prompt=messages.ENDPOINT_PROMPT_METRIC_NAME, help=messages.ENDPOINT_METRIC_NAME)
@click.option('-x', '--x', prompt=messages.ENDPOINT_PROMPT_METRIC_X, help=messages.ENDPOINT_METRIC_X)
@click.option('-y', '--y', prompt=messages.ENDPOINT_PROMPT_METRIC_Y, help=messages.ENDPOINT_METRIC_Y)
@prepare_command()
def log_metric(endpoint, logger, slug, name, y, x):
    """
        logs a metric to the endpoint
    """
    if endpoint is None:
        logger.log_and_echo(messages.Endpoint_DOES_NOT_EXIST, error=True)

    endpoint.log_metric(name=name, y=y, x=x)
