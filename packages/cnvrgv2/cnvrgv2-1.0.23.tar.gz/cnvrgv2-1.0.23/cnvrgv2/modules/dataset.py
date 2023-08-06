from cnvrgv2.config import routes, error_messages
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.modules.commits.dataset_commit import DatasetCommit
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.modules.base.data_owner import DataOwner
from cnvrgv2.modules.queries.queries_client import QueriesClient
from cnvrgv2.errors import CnvrgError
from cnvrgv2.config.error_messages import LOCAL_COMMIT_DOESNT_EXIST_ERROR
import os
from cnvrgv2.config import Config


class SyncType:
    ALL = "sync_all"
    FLATTEN = "sync_flatten"


class Dataset(DataOwner):

    # TODO: add all relevant attributes.
    available_attributes = {
        "slug": str,
        "size": int,
        "title": str,
        "members": list,
        "datatype": str,
        "category": str,
        "description": str,
        "num_files": int,
        "last_commit": str,
        "is_public": bool
    }

    def __init__(self, context=None, slug=None, attributes=None):
        # Init data attributes
        super().__init__()

        self._context = Context(context=context)

        # Set current context scope to current dataset
        if slug:
            self._context.set_scope(SCOPE.DATASET, slug)

        self.scope = self._context.get_scope(SCOPE.DATASET)

        self._proxy = Proxy(context=self._context)
        self._route = routes.DATASET_BASE.format(self.scope["organization"], self.scope["dataset"])
        self._attributes = attributes or {}
        self.slug = self.scope["dataset"]
        self.use_cached = False
        self.sync_type = SyncType.ALL

        self._init_clients()

    def get_commit(self, sha_1):
        if not sha_1 or not isinstance(sha_1, str):
            raise CnvrgArgumentsError(error_messages.COMMIT_FAULTY_SHA1)

        return DatasetCommit(context=self._context, slug=sha_1)

    def list_commits(self, sort="-id"):
        """
        List all commits in a specific dataset
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields commit objects
        """
        list_commits_url = routes.DATASET_COMMITS_BASE.format(self.scope["organization"], self.scope["dataset"])

        return api_list_generator(
            context=self._context,
            route=list_commits_url,
            object=DatasetCommit,
            sort=sort,
            identifier="sha1"
        )

    def delete(self):
        """
        Deletes the current dataset
        @return: None
        """
        self._proxy.call_api(route=self._route, http_method=HTTP.DELETE)

    def _validate_config_ownership(self):
        return self.slug == self._config.dataset_slug

    def as_request_params(self):
        return {
            "slug": self.slug,
            "sync_type": self.sync_type,
            "commit": self.local_commit,
            "query_slug": "",  # TODO: add query slug
            "use_cached": self.use_cached,
        }

    def _init_clients(self):
        self.queries = QueriesClient(self._context)

    def save_config(self, local_config_path=None):
        """
        Saves the dataset configuration in the local folder
        @return: None
        """

        if not self.local_commit:
            raise CnvrgError(LOCAL_COMMIT_DOESNT_EXIST_ERROR)
        self._config.update(local_config_path=local_config_path, **{
            "dataset_slug": self.slug,
            "organization": self._context.organization,
            "commit_sha1": self.local_commit,
        })

    def verify(self):
        """
        Checks if the dataset has been created successfully (if the config file has been created)
        @return: returns True if the config file has been created
        """
        cwd = os.getcwd()
        if not os.path.isdir(self.slug):
            return False
        try:
            os.chdir(os.path.join(cwd, self.slug))
            config = Config()
            if config and config.local_config_exists:
                return True
            return False
        finally:
            os.chdir(cwd)
