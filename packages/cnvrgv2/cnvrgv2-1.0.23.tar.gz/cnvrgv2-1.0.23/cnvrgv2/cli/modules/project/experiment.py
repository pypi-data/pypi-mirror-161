import click

from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command
from time import sleep
from cnvrgv2.modules.workflows.experiment.experiment import Experiment


@click.group(name='experiment')
def experiment_group():
    pass


@experiment_group.command()
@click.option('-t', '--title', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@click.option('-tm', '--templates', default=None, help=messages.EXPERIMENT_HELP_TEMPLATES)
@click.option('-l/-nl', '--local/--no-local', default=False, help=messages.EXPERIMENT_HELP_LOCAL)
@click.option('-c', '--command', prompt=messages.EXPERIMENT_PROMPT_COMMAND, help=messages.EXPERIMENT_HELP_COMMAND)
@click.option('-d', '--datasets', default=None, help=messages.EXPERIMENT_HELP_DATASETS)
@click.option('-v', '--volume', default=None, help=messages.EXPERIMENT_HELP_VOLUME)
@click.option('-sb/-nsb', '--sync-before/--no-sync-before', default=True, help=messages.EXPERIMENT_HELP_SYNC_BEFORE)
@click.option('-sa/-nsa', '--sync-after/--no-sync-after', default=True, help=messages.EXPERIMENT_HELP_SYNC_AFTER)
@click.option('-i', '--image', default=None, help=messages.EXPERIMENT_HELP_IMAGE)
@click.option('-gb', '--git-branch', default=None, help=messages.EXPERIMENT_HELP_GIT_BRANCH)
@click.option('-gc', '--git-commit', default=None, help=messages.EXPERIMENT_HELP_GIT_COMMIT)
@prepare_command()
def run(
    cnvrg,
    logger,
    project,
    title,
    templates,
    local,
    command,
    datasets,
    volume,
    sync_before,
    sync_after,
    image,
    git_branch,
    git_commit
):
    """
      run an experiment
    """
    dataset_objects = None
    volume_object = None
    kwargs = {}
    templates_list = templates.split(",") if templates else None

    if datasets:
        dataset_names = datasets.split(",")
        dataset_objects = [cnvrg.datasets.get(ds_name) for ds_name in dataset_names]

    if volume:
        volume_object = project.volumes.get(volume)

    if image:
        image_name, image_tag = image.split(":")
        kwargs["image"] = cnvrg.images.get(name=image_name, tag=image_tag)

    if git_branch:
        kwargs["git_branch"] = git_branch

    if git_commit:
        kwargs["git_commit"] = git_commit

    experiment = project.experiments.create(
        title=title,
        templates=templates_list,
        local=local,
        command=command,
        datasets=dataset_objects,
        volume=volume_object,
        sync_before=sync_before,
        sync_after=sync_after,
        **kwargs
    )
    success_message = messages.EXPERIMENT_CREATE_SUCCESS.format(experiment.title, experiment.full_href)
    logger.log_and_echo(success_message)


@experiment_group.command()
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@click.option('-c', '--commit', prompt=messages.EXPERIMENT_PROMPT_COMMIT, default='latest', required=False,
              help=messages.EXPERIMENT_HELP_COMMIT)
@prepare_command()
def merge_to_master(logger, project, experiment, slug, commit):
    # TODO: slug is not necessary as a parameter (it is as an option, since prepare command uses it).
    #  Change prepare command to send only required arguments

    if project.git:
        logger.log_and_echo(messages.EXPERIMENT_GIT_ERROR_MESSAGE, error=True)
        return
    commit_param = None if commit == 'latest' else commit
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    sha1 = experiment.merge_to_master(commit_param)
    logger.log_and_echo(messages.EXPERIMENT_MERGE_SUCCESS)
    logger.log_and_echo(messages.COMMIT_SHA1_MESSAGE.format(sha1))


@experiment_group.command()
@click.option('-k', '--key', help='')
@click.option('-v', '--value', help='')
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@prepare_command()
def log_param(experiment, logger, slug, key, value):
    """
      logging a parameter of an experiment
    """
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    experiment.log_param(key=key, value=value)
    logger.log_and_echo('{0}: {1} was logged'.format(key, value))

@experiment_group.command()
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@click.option('-f', '--files', prompt=messages.DATASET_PUT_PROMPT_FILES, help=messages.DATASET_PUT_HELP_FILES)
@click.option('-g', '--git-diff', is_flag=True, default=None, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@click.option('-d', '--work-dir', required=False,
              help=messages.EXPERIMENT_HELP_COMMIT)
@prepare_command()
def log_artifacts(cnvrg, logger, project, experiment, slug, files, git_diff, work_dir):
    file_paths = files.split(",")
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    experiment.log_artifacts(paths=file_paths, git_diff=git_diff, work_dir=work_dir)
    logger.log_and_echo(messages.EXPERIMENT_LOG_ARTIFACTS_SUCCESS)

@experiment_group.command()
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@click.option('-f', '--files', prompt=messages.DATASET_PUT_PROMPT_FILES, help=messages.DATASET_PUT_HELP_FILES)
@prepare_command()
def log_images(cnvrg, logger, project, experiment, slug, files):
    file_paths = files.split(",")
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    experiment.log_images(file_paths=file_paths)
    logger.log_and_echo(messages.EXPERIMENT_LOG_IMAGES_SUCCESS)
    
@experiment_group.command()
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@prepare_command()
def start_tensorboard(experiment, logger, slug):
    """
      start a tensorboard associated  with the current experiment
    """
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    experiment.start_tensorboard()
    logger.log_and_echo('tensorboard started!')


@experiment_group.command()
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@prepare_command()
def stop_tensorboard(experiment, logger, slug):
    """
      stops a tensorboard associated  with the current experiment
    """
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    experiment.stop_tensorboard()
    logger.log_and_echo('tensorboard session stopped')


@experiment_group.command()
@click.option('-s', '--slug', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@click.option('-c', '--commit', prompt=messages.EXPERIMENT_ARTIFACTS_PROMPT_COMMIT, default='latest', required=False,
              help=messages.EXPERIMENT_ARTIFACTS_HELP_COMMIT)
@prepare_command()
def pull_artifacts(experiment, logger, slug, commit):
    """
      pull artifacts
      default is experiment's last commit
    """
    if experiment is None:
        logger.log_and_echo(messages.EXPERIMENT_DOES_NOT_EXIST, error=True)
    commit_param = None if commit == 'latest' else commit
    experiment.pull_artifacts(commit_sha1=commit_param)
    logger.log_and_echo(messages.EXPERIMENT_PULL_ARTIFACTS_SUCCESS)


