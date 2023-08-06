import click
from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command
from cnvrgv2.modules.workflows.workspace.workspace import Workspace


@click.group(name='workspace')
def workspace_group():
    pass


@workspace_group.command()
@click.option('-s', '--slug', default=None, help=messages.WORKSPACE_SLUG)
@prepare_command()
def start_tensorboard(workspace, logger, slug):
    """
      starts tensorboard associated with the current workspace
    """
    if workspace is None:
        logger.log_and_echo(messages.WORKSPACE_DOES_NOT_EXIST, error=True)

    workspace.start_tensorboard()
    logger.log_and_echo('tensorboard started!')


@workspace_group.command()
@click.option('-s', '--slug', default=None, help=messages.WORKSPACE_SLUG)
@prepare_command()
def stop_tensorboard(workspace, logger, slug):
    """
      stops tensorboard associated with the current workspace
    """
    if workspace is None:
        logger.log_and_echo(messages.WORKSPACE_DOES_NOT_EXIST, error=True)

    workspace.stop_tensorboard()
    logger.log_and_echo('tensorboard session stopped')
