import abc
import json
import os
import re
import shutil
import time
from datetime import datetime
from itertools import chain

from cnvrgv2.cli.utils.progress_bar_utils import init_progress_bar_for_cli
from cnvrgv2.config import Config
from cnvrgv2.config import CONFIG_FOLDER_NAME
from cnvrgv2.config import error_messages
from cnvrgv2.config.routes import COMMIT_REMOVE_FILES
from cnvrgv2.data import ArtifactsDownloader
from cnvrgv2.data import FileCompare, LocalFileDeleter
from cnvrgv2.data import FileDownloader
from cnvrgv2.data import FileUploader
from cnvrgv2.data import RemoteFileDeleter
from cnvrgv2.errors import CnvrgArgumentsError, CnvrgError, CnvrgFileError
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.modules.file import File
from cnvrgv2.modules.folder import Folder
from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.converters import convert_bytes
from cnvrgv2.utils.filter_utils import Operators, list_to_multiple_conditions
from cnvrgv2.utils.storage_utils import (
    cnvrgignore_exists, create_cnvrgignore, create_dir_if_not_exists, filter_by_mimetypes, get_files_and_dirs_recursive
)
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.validators import validate_directory_name


class DataOwner(DynamicAttributes):
    TMP_FOLDER_NAME = ".tmp"

    def __init__(self):
        # Data attributes
        self._config = Config()
        self._working_dir = None
        self._storage_meta = None
        self._storage_meta_update_time = None
        self._local_commit = None
        self.query = None

    @property
    def storage_meta(self):
        """
        Retrieve the storage meta of the data owner
        @return: storage meta in a dict
        """
        # Calculate minutes diff from last update. If over 5 minutes - update storage meta.
        minutes_diff = 0
        if self._storage_meta_update_time is not None:
            minutes_diff = (datetime.now() - self._storage_meta_update_time).total_seconds() / 60
        if self._storage_meta is None or minutes_diff > 5:
            response = self._proxy.call_api(
                route=urljoin(self._route, "storage_client"),
                http_method=HTTP.GET
            )
            storage_meta = response.meta["storage"]
            self._storage_meta = storage_meta
            self._storage_meta_update_time = datetime.now()

        return self._storage_meta

    @abc.abstractmethod
    def _validate_config_ownership(self):
        """
        Returns if local config file is matched with current object
        """
        pass

    @property
    def local_commit(self):
        """
        Returns the current commit for the data owner
        @return: string denoting current/active commit
        """
        config_commit = None

        if self._validate_config_ownership():
            config_commit = self._config.commit_sha1

        return self._local_commit or config_commit

    @local_commit.setter
    def local_commit(self, commit_sha1):
        self._local_commit = commit_sha1

    @property
    def working_dir(self):
        """
        Returns the local working dir for the data owner
        @return: string denoting the path to the working dir
        """
        if self._working_dir:
            return self._working_dir
        else:
            return os.curdir

    @working_dir.setter
    def working_dir(self, working_dir):
        """
        Sets the working directory
        @param working_dir: string denoting the path to the working dir
        @return: None
        """
        self._working_dir = working_dir

    def _start_commit(self, message="", source="sdk", parent_sha1=None, blank=False, force=False, job_slug=None):
        """
        Starts a new commit
        @param message: Commit message string (Optional)
        @param source: Source of the commit string (Optional)
        @param parent_sha1: Commit sha1 of the parent of the new commit
        @param blank: Start from a blank state or from a previous commit
        @param force: Start from a blank state or from a previous commit
        @param job_slug: Job that this commit related to
        @return: Dict containing commit data
        """
        data = {
            "force": force,
            "blank": blank,
            "job_slug": job_slug,
            "parent_sha1": parent_sha1,
            "source": source,
            "message": message
        }
        response = self._proxy.call_api(
            route=urljoin(self._route, "commits"),
            http_method=HTTP.POST,
            payload=data
        )

        return response.attributes["sha1"]

    def _end_commit(self, commit_sha1, tag_images=False, with_commit_compare=False):
        """
        End the commit after uploading/deleting files from the dataset.
        @commit_sha1: the commit sha1 to end
        @param tag_images: Will cause images in this commit to be tagged so they can be
            displayed in specific places on front
        @param with_commit_compare: the server will delete the commit if it is identical to the previous
            one (in the case nothing has actually been updated to the server): send last_commit to the server to compare
             with the current commit. (we don't want to create empty commits)
        @return: Dict containing commit data
        """
        data = {'tag_images': tag_images, 'workflow_slug': self.slug}
        if with_commit_compare:
            data["base_commit_sha1"] = self.last_commit
        response = self._proxy.call_api(
            route=urljoin(self._route, "commits", commit_sha1, "end_commit"),
            http_method=HTTP.PUT,
            payload=data
        )
        # Response will be empty if the commit has been deleted
        # (in the case nothing has actually been updated to the server).
        return response.attributes["sha1"] if (response and response.attributes) else None

    def reload(self):
        """
        Performs hard reload for the module attributes and config
        @return: None
        """
        super().reload()
        self._config = Config()
        self._local_commit = None
        # check ownership of local config, unless remove the config
        if not self._validate_config_ownership():
            self._config.local_config = {}

    def put_files(
        self,
        paths,
        pattern="*",
        message="",
        job_slug=None,
        blank=False,
        override=False,
        force=False,
        upload=False,
        tag_images=False,
        progress_bar_enabled=False,
        git_diff=False
    ):
        """
        Uploads the files and folders given.
        If a folder is given all the relevant files in that folder (that confirms to the regex) will be uploaded.
        @param paths: List of file/folder paths
        @param pattern: String defining the filename pattern
        @param message: String defining the commit message
        @param job_slug: Slug of a job to upload the files to
        @param blank: Start from a blank state or from a previous commit
        @param override: Boolean stating whether or not we should re-upload even if the file already exists
        @param force: Boolean stating whether or not we the new commit should copy files from parent
        @param upload: Boolean gives info if the put files comes from upload or not
        @param tag_images: Boolean indicating if we want to allow only images to be uploaded. used by exp.log_image
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param git_diff: upload files from git diff output in addition to the given paths
        @return: string - The Commit sha1 that was created
        """

        filters = []
        if tag_images:
            filters = ['image']

        paths_to_upload = paths

        if git_diff:
            paths_to_upload += self._handle_git_files()

        full_paths = self._get_full_paths(paths_to_upload, filters, pattern)
        unique_full_paths = list(set(full_paths) - {"./", ".", "/", "//"})

        if not unique_full_paths and not upload:
            return

        last_commit = self.local_commit
        if job_slug is not None:
            # Ugly patch, decided on 12/07/2022 by Elad
            # For experiments, parent commit should be last commit and not start commit
            if type(self).__name__ == 'Experiment':
                last_commit = self.last_commit
            elif last_commit is None and self.start_commit is not None:
                last_commit = self.start_commit["sha1"]

        unique_full_paths = self._filter_deleted_files(unique_full_paths)
        validate_directory_name(unique_full_paths)

        if not unique_full_paths:
            return

        return self._upload_files(message, blank, last_commit, job_slug, force, unique_full_paths, override,
                                  progress_bar_enabled, tag_images, upload)

    def _filter_deleted_files(self, unique_full_paths):
        result = []
        tmp_folder = "{}/{}".format(self.working_dir, DataOwner.TMP_FOLDER_NAME)

        # This function should run only if tmp folder exist (sync/download)
        if not os.path.exists(tmp_folder):
            return unique_full_paths

        for up in unique_full_paths:
            deleted_file = "{}/{}.deleted".format(tmp_folder, up)
            if not os.path.exists(deleted_file):
                result.append(up)

        # Make sure to filter out all paths that are under deleted folders
        deleted_folders = get_files_and_dirs_recursive(root_dir=tmp_folder, regex=".*deleted/", force=True)
        for deleted_folder in deleted_folders:
            # Prepare a regex that matches all paths in the regular dir, that are under a dir marked to be deleted
            # in the tmp folder
            matching_path = deleted_folder.replace(".tmp/", "").replace(".deleted", "")
            regex = re.compile("^(?!{})".format(matching_path))
            result = [path for path in result if regex.match(path)]

        return result

    def _handle_git_files(self):
        return list(filter(None, self.get_git_diff()))  # Clean from falsy values

    def get_git_diff(self):
        """
        collects file names from git diff output
        @return: list of file names from git diff command
        """
        command = "git diff --name-only"
        return os.popen(command).read().strip().split("\n")

    def _upload_files(
            self, message, blank, last_commit, job_slug, force, paths, override, progress_bar_enabled,
            tag_images, upload
            ):
        commit_sha1 = self._start_commit(
            message=message,
            blank=blank,
            parent_sha1=last_commit,
            job_slug=job_slug,
            force=force
        )

        uploader = self._get_file_uploader(paths, commit_sha1, override, progress_bar_enabled)

        while uploader.in_progress:
            time.sleep(0.1)

        # TODO: Decide on error behaviour later
        if uploader.errors:
            raise uploader.errors[0]

        if upload:
            self.reload()
            deleter = self._get_remote_file_deleter(commit_sha1)
            while deleter.in_progress:
                time.sleep(0.1)

        # Pass with_commit_compare to end_commit: the server will delete the commit if it is identical to the previous
        # One (in the case where nothing has actually been updated to the server)
        with_commit_compare = not override
        commit = self._end_commit(commit_sha1=commit_sha1, tag_images=tag_images,
                                  with_commit_compare=with_commit_compare)
        # Commit will be null if the commit has been deleted
        # In the case nothing has actually been updated to the server, return last_commit
        return commit if commit else self.last_commit

    def _get_file_uploader(self, paths, commit_sha1, override, progress_bar_enabled):
        # this is required for mocking. please don't delete the wrapping function
        return FileUploader(
            self,
            paths,
            commit=commit_sha1,
            override=override,
            progress_bar_enabled=progress_bar_enabled
        )

    def _get_remote_file_deleter(self, commit_sha1):
        # this is required for mocking. please don't delete the wrapping function
        return RemoteFileDeleter(self, commit=commit_sha1)

    def _get_full_paths(self, paths_to_upload, filters, pattern):
        result = []
        for path in paths_to_upload:
            is_dir = os.path.isdir(path)
            is_file = os.path.isfile(path)

            if is_dir:
                result += get_files_and_dirs_recursive(
                    root_dir=path,
                    regex=pattern,
                    project_root=self._config.root,
                    filters=filters)
                continue

            if is_file and filter_by_mimetypes(filters, path):
                result.append(path)
                continue

            # path sent might be a regex
            files_by_regex = get_files_and_dirs_recursive(
                root_dir=".",
                regex=path,
                filters=filters)

            if files_by_regex:
                result += files_by_regex
                continue

            print("{} does not exists skipping it".format(path))
        return result

    def remove_files(self, paths, message="", progress_bar_enabled=False):
        """
        Removes the given files remotely
        @param paths: List of file paths to remove (regex and wildcards allowed)
        @param message: Commit message
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @return: Number of files removed
        """
        progress_bar = None
        commit_sha1 = self._start_commit(message=message)

        data = {
            "filter": json.dumps({
                "operator": 'OR',
                "conditions": list_to_multiple_conditions("fullpath", Operators.LIKE, paths),
            })
        }

        meta = self._remove_api_call(commit_sha1=commit_sha1, data=data)

        total_files_count = meta["total"]
        total_files_size = float(meta["total_size"])
        removed_files_count = meta["removed_files_count"]

        if progress_bar_enabled and total_files_size > 0:
            progress_bar = init_progress_bar_for_cli("Removing", total_files_size) if progress_bar_enabled else None

        while True:
            if progress_bar:
                converted_bytes, unit = convert_bytes(float(meta["removed_files_size"]), progress_bar.unit)
                progress_bar.throttled_next(converted_bytes)

            if removed_files_count >= total_files_count:
                break

            meta = self._remove_api_call(commit_sha1=commit_sha1, data=data)
            removed_files_count += meta["removed_files_count"]

        self._end_commit(commit_sha1=commit_sha1)
        return removed_files_count

    def _remove_api_call(self, commit_sha1, data):
        """
        Performs API call to the server with the data to remove
        @param data: Hash containing the paths to remove
        @return: Hash with metadata regarding the remove action
        """
        route = urljoin(self._route, COMMIT_REMOVE_FILES.format(commit_sha1))
        return self._proxy.call_api(
            route=route,
            http_method=HTTP.POST,
            payload=data
        ).meta

    def clone(self, progress_bar_enabled=False, override=False, commit=None, use_cached=False, threads=40,
              query_slug=None):
        """
        Clones the remote project / dataset
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param override: Boolean stating whether we should re-clone even if the project / dataset already cloned
        @param commit: [String] sha1 of the commit to clone
        @param use_cached: Boolean stating whether to use nfs cache link or not
        @param threads: number of threads that will be used in order to clone the project
        @return: None
        """
        self.reload()

        if not os.path.exists(self.slug):
            os.makedirs(self.slug)
        elif os.path.exists(self.slug + '/' + CONFIG_FOLDER_NAME):
            if not override:
                # If already cloned and override set to false - won't clone again
                return
            else:
                # If already cloned and override set to true - remove config file so that verify will fail until the
                # data owner is cloned again
                shutil.rmtree(self.slug + '/' + CONFIG_FOLDER_NAME)

        if commit and commit.lower() != 'latest':
            # self.last_commit should be a value returned from the server,
            # and no value should be manually assigned to it.
            # this is a workaround for cloning a specific commit:
            # because FileDownloader uses self.last_commit instead of receiving commit as an arg
            # todo : pass commit to FileDownloader

            self.last_commit = commit

        old_working_dir = self.working_dir
        self.working_dir = "{}/{}".format(old_working_dir, self.slug)

        # Will download files from self.last_commit.
        # In the case of cloning a specific commit, last_commit is actually that specific commit assigned previously

        downloader = FileDownloader(self, progress_bar_enabled=progress_bar_enabled, use_cached=use_cached,
                                    num_workers=threads, query_slug=query_slug)

        while downloader.in_progress:
            time.sleep(1)

        if downloader.errors:
            if os.path.exists(self.slug) and not override:
                os.rmdir(self.slug)
            raise CnvrgError(downloader.errors.args)

        # In the case of cloning a specific commit, last_commit is that specific commit
        # and not the actual data_owner last_commit
        self.local_commit = self.last_commit
        self.save_config(local_config_path=self.working_dir + '/' + CONFIG_FOLDER_NAME)

        # Reload will reset self.last_commit to the actual data_owner last_commit in case it has been changed previously
        self.reload()
        self.working_dir = old_working_dir

        if not cnvrgignore_exists(self.slug):
            create_cnvrgignore(self.slug)

    def upload(self, sync=False, job_slug=None, progress_bar_enabled=False, git_diff=False, message="",
               output_dir=None):
        """
        Uploads files to remote project / dataset
        @param sync: Boolean gives info if the put files comes from sync or not
        @param job_slug: Slug of a job to upload the files to
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param git_diff: upload only files from git diff output
        @param message: String defining the commit message
        @param output_dir: String will only upload the files in the output_dir specified
        @return: None
        """

        # We want to make sure we are in a project/dataset folder in order to continue with the action
        self.reload()
        if not self._validate_config_ownership():
            raise CnvrgFileError(error_messages.CONFIG_YAML_NOT_FOUND)

        working_dir = "{0}/{1}".format(self._config.root, output_dir) if output_dir else self._config.root
        old_working_dir = os.getcwd()
        os.chdir(self._config.root)

        new_commit_sha1 = self.put_files(
            [working_dir],
            upload=True,
            job_slug=job_slug,
            progress_bar_enabled=progress_bar_enabled,
            git_diff=git_diff,
            message=message
        )

        if sync:
            self.move_files_from_tmp()

        self.local_commit = new_commit_sha1
        self.save_config()
        os.chdir(old_working_dir)

    def download(self, sync=False, progress_bar_enabled=False, commit_sha1=None):
        """
        Download files from remote project / dataset
        @param sync: Boolean gives info if the put files comes from sync or not
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param commit_sha1: Sha1 of a specific commit to download
        @return: None
        """
        # We want to make sure we are in a project/dataset folder in order to continue with the action
        self.reload()
        if not self._validate_config_ownership():
            raise CnvrgFileError(error_messages.CONFIG_YAML_NOT_FOUND)

        context_working_dir = os.getcwd()
        os.chdir(self._config.root)

        """
        download files from last commit on the server and put them in .tmp folder
        will be fetched at the end out of .tmp
        """
        # create .tmp dir
        if not os.path.exists(DataOwner.TMP_FOLDER_NAME):
            os.makedirs(DataOwner.TMP_FOLDER_NAME)

        old_working_dir = self.working_dir
        self.working_dir = "{}/{}".format(self.working_dir, DataOwner.TMP_FOLDER_NAME)
        downloader = ArtifactsDownloader(
            self,
            base_commit_sha1=self.local_commit,
            commit_sha1=commit_sha1 or self.last_commit,
            progress_bar_enabled=progress_bar_enabled
        )
        while downloader.in_progress:
            time.sleep(1)

        if downloader.errors:
            raise CnvrgError(downloader.errors.args)

        self.working_dir = old_working_dir

        # put all files that need to be deleted at .tmp with .deleted extension
        file_deleter = LocalFileDeleter(self)
        while file_deleter.in_progress:
            time.sleep(1)

        # remove all folders needed that should be deleted
        folder_deleter = LocalFileDeleter(self, mode="folders")
        while folder_deleter.in_progress:
            time.sleep(1)

        if not sync:
            self.move_files_from_tmp()
            self.local_commit = commit_sha1 or self.last_commit
            self.save_config()

        os.chdir(context_working_dir)

    def sync(self, job_slug=None, git_diff=False, progress_bar_enabled=False, message='', output_dir=None):
        """
        Sync local project / dataset to remote
        @param job_slug: Slug of a job to upload the files to
        @param git_diff: upload only files from git diff output
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param message: String defining the commit message
        @param output_dir: String will only sync the files in the output_dir specified
        @return: None
        """
        try:
            self.download(sync=True, progress_bar_enabled=progress_bar_enabled)
            self.upload(sync=True, progress_bar_enabled=progress_bar_enabled, job_slug=job_slug, git_diff=git_diff,
                        message=message, output_dir=output_dir)
        finally:
            # make sure the tmp folder used by download and upload will be deleted
            if os.path.exists(DataOwner.TMP_FOLDER_NAME):
                shutil.rmtree(DataOwner.TMP_FOLDER_NAME)

    def list_files(self, commit_sha1=None, query=None, query_raw=None, sort="-id"):
        """
        List all files in a specific query
        @param commit_sha1: Sha1 of the commit to list
        @param query: Query slug to list files from
        @param query_raw: Raw query to list files (e.g. {color: yellow})
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields file objects
        """
        return self._list("files", commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)

    def list_folders(self, commit_sha1=None, query=None, query_raw=None, sort="-id"):
        """
        List all folders in a specific query
        @param commit_sha1: Sha1 of the commit to list
        @param query: Query slug to list folders from
        @param query_raw: Raw query to list folders (e.g. {color: yellow})
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields folder objects
        """
        return self._list("folders", commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)

    def list(self, commit_sha1=None, query=None, query_raw=None, sort="-id"):
        """
        List all files and folders in a specific query
        @param commit_sha1: Sha1 of the commit to list
        @param query: Query slug to list files and folders from
        @param query_raw: Raw query to list files and folders (e.g. {color: yellow})
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields files and folders objects
        """
        list_folders = self.list_folders(commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)
        list_files = self.list_files(commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)
        return chain(list_folders, list_files)

    def move_files_from_tmp(self):
        """
        Takes files from .tmp folder and complete the sync/download/upload operation
        @return: None
        """
        tmp_folder = "{}/{}".format(self.working_dir, DataOwner.TMP_FOLDER_NAME)
        try:
            fullpaths = get_files_and_dirs_recursive(root_dir='.')
            unique_fullpaths = list(set(fullpaths) - {"./", ".", "/", "//"})

            if unique_fullpaths:
                compare = FileCompare(self, unique_fullpaths)
                while compare.in_progress:
                    time.sleep(1)

            downloaded_files = get_files_and_dirs_recursive(root_dir=tmp_folder, force=True)
            for df in downloaded_files:
                if df == ".tmp/" or df == ".tmp/.cnvrgignore":
                    continue

                if df.endswith('.deleted') or df.endswith('.deleted/'):
                    original_file = re.sub(DataOwner.TMP_FOLDER_NAME, self.working_dir, df)
                    original_file = re.sub(".deleted", "", original_file)
                    if(os.path.isfile(original_file)):
                        os.remove(original_file)
                    elif(os.path.isdir(original_file)):
                        shutil.rmtree(original_file)
                    continue

                new_path = re.sub(DataOwner.TMP_FOLDER_NAME, self.working_dir, df)
                create_dir_if_not_exists(new_path)

                # Prevents moving folders with content. Generally, creation of folders is done when dealing with files
                # inside the folders, except for empty folders. This makes sure that only empty folders will be copied
                if os.path.isdir(df) and (len(os.listdir(df)) != 0 or len(os.listdir(new_path)) != 0):
                    continue

                os.rename(df, new_path)
        finally:
            if os.path.exists(tmp_folder):
                shutil.rmtree(tmp_folder)

    def _get_git_diff_files(self):
        return list(filter(None, self.get_git_diff()))   # Clean from falsy values

    def _list(self, mode, commit_sha1=None, query=None, query_raw=None, sort="-id"):

        if query and query_raw:
            raise CnvrgArgumentsError(error_messages.QUERY_LIST_FAULTY_PARAMS.format("query and query_raw"))

        if query and commit_sha1:
            raise CnvrgArgumentsError(error_messages.QUERY_LIST_FAULTY_PARAMS.format("query and commit_sha1"))

        if not commit_sha1:
            self.reload()
            commit_sha1 = self.local_commit or self.last_commit

        list_object = Folder if mode == "folders" else File

        return api_list_generator(
            context=self._context,
            route=urljoin(self._route, "commits", commit_sha1, "files?mode={}".format(mode)),
            object=list_object,
            sort=sort,
            identifier="fullpath",
            pagination_type="offset",
            data={
                "query": query,
                "query_raw": query_raw
            }
        )
