from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.config import routes, error_messages
from cnvrgv2.utils.validators import validate_email, validate_user_role
from cnvrgv2 import cnvrg
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config.error_messages import FAULTY_VALUE


class MembersClient:
    def __init__(self, organization):
        if type(organization) is not cnvrg.Cnvrg:
            raise CnvrgArgumentsError(error_messages.ARGUMENT_BAD_TYPE.format(cnvrg.Cnvrg, type(organization)))
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.ORGANIZATION_MEMBERS.format(scope["organization"])

    def add(self, email, role):
        """
        Add a new member to the organization
        @param email: User email
        @param role: Role to add
        """

        if not validate_user_role(role):
            raise CnvrgArgumentsError(FAULTY_VALUE.format(role))

        if not validate_email(email):
            raise CnvrgArgumentsError(FAULTY_VALUE.format(email))

        self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="users", attributes={"email": email, "role": role})
        )

    def revoke(self, email):
        """
        Revoke user access to organization
        @param email: User's email
        """
        if not validate_email(email):
            raise CnvrgArgumentsError(FAULTY_VALUE.format(email))

        self._proxy.call_api(
            route=self._route,
            http_method=HTTP.DELETE,
            payload=JAF.serialize(type="users", attributes={"email": email})
        )
