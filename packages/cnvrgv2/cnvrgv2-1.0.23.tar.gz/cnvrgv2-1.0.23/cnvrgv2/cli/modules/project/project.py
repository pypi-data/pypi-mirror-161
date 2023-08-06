import os

import click
from prettytable import PrettyTable

from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command
from cnvrgv2.config import CONFIG_FOLDER_NAME, Config
from cnvrgv2.config import error_messages
from cnvrgv2.utils.storage_utils import cnvrgignore_exists, create_cnvrgignore


@click.group(name='project')
def project_group():
    pass


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_CREATE, help=messages.PROJECT_HELP_CREATE)
@prepare_command()
def create(cnvrg, logger, name):
    """
    Creates a new project, and associates the current folder with the created project.
    It is recommended to create a new project in an empty folder.
    To create a project from a folder that contains content please refer to project link command.
    """
    if os.listdir():
        click.confirm(messages.PROJECT_CREATE_FOLDER_NOT_EMPTY, default=False, abort=True)

    logger.log_and_echo(messages.PROJECT_CREATING_PROJECT.format(name))
    new_project = cnvrg.projects.create(name)

    new_project.local_commit = new_project.commit

    logger.log_and_echo(messages.PROJECT_CONFIGURING_FOLDER)
    new_project.save_config()

    logger.log_and_echo(messages.PROJECT_CREATE_SUCCESS.format(new_project.title))


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_CLONE, help=messages.PROJECT_PROMPT_CLONE)
@click.option('-o', '--override', is_flag=True, default=False, help=messages.PROJECT_HELP_CLONE_OVERRIDE)
@click.option('-c', '--commit', prompt=messages.DATA_PROMPT_COMMIT, default="latest",
              help=messages.PROJECT_HELP_CLONE_COMMIT)
@prepare_command()
def clone(cnvrg, logger, name, override, commit):
    """
    Clones the given project to local folder
    """
    project = cnvrg.projects.get(name)
    logger.info(messages.LOG_CLONING_PROJECT.format(name))
    if os.path.exists(project.slug + '/' + CONFIG_FOLDER_NAME) and not override:
        logger.log_and_echo(messages.PROJECT_CLONE_SKIP.format(name))
        return
    project.clone(progress_bar_enabled=True, override=override, commit=commit)
    success_message = messages.PROJECT_CLONE_SUCCESS.format(name)
    logger.log_and_echo(success_message)


@project_group.command(name='list')
@prepare_command()
def list_command(cnvrg, logger):
    """
    list projects title
    """
    projects = cnvrg.projects.list()
    domain = cnvrg._context.domain
    organization = cnvrg._context.organization
    table = PrettyTable()
    table.field_names = ["Project Title", "Project Link", "Public"]
    table.align["Project Title"] = "l"
    table.align["Project Link"] = "l"
    table.align["Public"] = "l"
    for project in projects:
        url = "{0}/{1}/projects/{2}".format(domain, organization, project.slug)
        table.add_row([project.title, url, project.public])
    click.echo(table)


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_DELETE, help=messages.PROJECT_HELP_DELETE)
@prepare_command()
def delete(cnvrg, logger, name):
    """
    Deletes the current project
    """
    click.confirm(messages.PROJECT_DELETE_CONFIRM.format(name), default=False, abort=True)
    cnvrg.projects.delete([name])
    success_message = messages.PROJECT_DELETE_SUCCESS.format(name)
    logger.log_and_echo(success_message)


@project_group.command()
@click.option('-g', '--git-diff', is_flag=True, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@prepare_command()
def upload(project, logger, git_diff):
    """
    Uploads updated files from the current project folder
    """
    project.upload(progress_bar_enabled=True, git_diff=git_diff)
    logger.log_and_echo(messages.DATA_UPLOAD_SUCCESS)


@project_group.command()
@click.option('-c', '--commit', default=None, help=messages.PROJECT_DOWNLOAD_HELP_COMMIT)
@prepare_command()
def download(project, logger, commit):
    """
    Downloads updated files to the current project folder
    """
    project.download(progress_bar_enabled=True, commit_sha1=commit)
    logger.log_and_echo(messages.DATA_DOWNLOAD_SUCCESS)


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_LINK_PROMPT_NAME, help=messages.PROJECT_LINK_HELP_NAME)
@prepare_command()
def link(cnvrg, logger, name):
    """
    Links the current directory with a new project.
    This command will create a new project and upload the current folder content to the newly created project.
    """
    curr_dir_project_name = Config().data_owner_slug
    if curr_dir_project_name:
        error_message = error_messages.DIRECTORY_ALREADY_LINKED.format(curr_dir_project_name)
        logger.log_and_echo(error_message, error=True)

    logger.log_and_echo(messages.PROJECT_CREATE_NEW.format(name))
    new_project = cnvrg.projects.create(name=name)
    new_project.local_commit = new_project.commit

    logger.log_and_echo(messages.PROJECT_CONFIGURING_FOLDER)
    new_project.save_config()

    logger.log_and_echo(messages.PROJECT_UPLOAD)
    new_project.upload(progress_bar_enabled=True)

    success_message = messages.PROJECT_LINK_SUCCESS.format(new_project.title)
    logger.log_and_echo(success_message)


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_LINK_GIT_PROMPT_NAME, help=messages.PROJECT_LINK_GIT_HELP_NAME)
@click.option('-s', '--soft', is_flag=True, help=messages.SOFT_LINK_GIT_PROJECT)
@prepare_command()
def link_git(cnvrg, logger, name, soft):
    """
     Links the current directory, which is expected to be a git directory, with an existing cnvrg project
     that is configured to be a git project.
    """
    git_proj = cnvrg.projects.get(name)
    if not git_proj:
        project_not_exist_error = error_messages.PROJECT_NOT_EXIST.format(name)
        logger.log_and_echo(project_not_exist_error, error=True)

    if not git_proj.git:
        error_message = error_messages.NOT_A_GIT_PROJECT.format(git_proj.title)
        logger.log_and_echo(error_message, error=True)

    if soft and os.path.exists(CONFIG_FOLDER_NAME):
        logger.log_and_echo(messages.PROJECT_GIT_LINK_SKIP.format(git_proj.title))
        return

    logger.log_and_echo(messages.PROJECT_CONFIGURING_FOLDER)
    git_proj.local_commit = git_proj.commit
    git_proj.save_config()

    if not cnvrgignore_exists(os.getcwd()):
        create_cnvrgignore(os.getcwd())

    success_message = messages.PROJECT_LINK_SUCCESS.format(git_proj.title)
    logger.log_and_echo(success_message)


@project_group.command()
@click.option('-j', '--job-slug', default=None, help=messages.PROJECT_JOB_SLUG_HELP_NAME)
@click.option('-g', '--git-diff', is_flag=True, default=None, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@click.option('-m', '--message', default="", help=messages.DATA_COMMIT_MESSAGE)
@click.option('-o', '--output-dir', default=None, help=messages.SYNC_OUTPUT_DIR)
@prepare_command()
def sync(project, logger, message, job_slug=None, git_diff=None, output_dir=None):
    """
    Sync local project to remote
    """
    logger.log_and_echo('Syncing...')
    project.sync(job_slug=job_slug, git_diff=git_diff, progress_bar_enabled=True, message=message,
                 output_dir=output_dir)
    logger.log_and_echo(messages.PROJECT_SYNC_SUCCESS.format(project.slug))


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_NAME, help=messages.PROJECT_HELP_DELETE)
@click.option('-f', '--files', prompt=messages.DATASET_PUT_PROMPT_FILES, help=messages.DATASET_PUT_HELP_FILES)
@click.option('-g', '--git-diff', is_flag=True, help=messages.DATA_UPLOAD_HELP_GIT_DIFF)
@prepare_command()
def put(cnvrg, logger, name, files, git_diff):
    """
    Uploads the given files to the given project
    """
    file_paths = files.split(",")
    project = cnvrg.projects.get(name)
    sha1 = project.put_files(paths=file_paths, progress_bar_enabled=True, git_diff=git_diff)
    logger.log_and_echo("\n" + messages.FILES_UPLOAD_SUCCESS)
    logger.log_and_echo(messages.COMMIT_SHA1_MESSAGE.format(sha1))


@project_group.command()
@click.option('-n', '--name', prompt=messages.PROJECT_PROMPT_NAME, help=messages.PROJECT_HELP_DELETE)
@click.option('-f', '--files', prompt=messages.DATASET_REMOVE_PROMPT_FILES, help=messages.DATASET_REMOVE_HELP_FILES)
@click.option('-m', '--message', help=messages.DATA_COMMIT_MESSAGE, default="")
@prepare_command()
def rm(cnvrg, logger, name, files, message):
    """
    Removes the given files remotely
    """
    file_paths = files.split(",")
    project = cnvrg.projects.get(name)
    removed_files_count = project.remove_files(paths=file_paths, message=message, progress_bar_enabled=True)
    str_count = str(removed_files_count)
    pluralize = "File{}".format('s'[:removed_files_count ^ 1])  # Pluralizes the word (File/Files)
    logger.log_and_echo("{} {} removed.".format(str_count, pluralize))
