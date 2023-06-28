import logging

from gql import gql
from graphql import (
    ExecutableDefinitionNode,
    FieldNode,
    GraphQLError,
    OperationDefinitionNode,
    OperationType,
)

from src.jwt.claims_service import ClaimsService
from src.jwt.jwt_service import JWTService
from src.models import (
    AuthenticationRequest,
    AuthenticationResponse,
    RoleGraphqlRootFieldName,
)
from src.repositories.roles_repository import RoleRepository


class WebhookHandlerUnauthorizedException(Exception):
    pass


class WebhookHandlerInvalidQueryException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class WebhookHandler:
    def __init__(
        self,
        claims_service: ClaimsService,
        jwt_service: JWTService,
        role_repository: RoleRepository,
    ):
        self.claims_service = claims_service
        self.jwt_service = jwt_service
        self.role_repository = role_repository
        self.PREFIX = "Bearer"
        self.logger = logging.getLogger(__name__)

    def get_token(self, authorization_header: str) -> str:
        """Extracts the JWT token from Authorization Header string

        Args:
            authorization_header: Authorization Header containing bearer token

        Returns:
            The JWT token

        Raises:
            ValueError: if the Authorization Header is not valid
        """
        bearer, _, token = authorization_header.partition(" ")
        if bearer != self.PREFIX:
            self.logger.error(f"Invalid Authorization Header: {authorization_header}")
            raise ValueError("Invalid Authorization Header")
        return token

    async def authenticate_request(
        self, authentication_request: AuthenticationRequest
    ) -> AuthenticationResponse:
        """Authenticates a request

        Args:
            authentication_request: Authentication request sent by Hasura about a client

        Returns:
            Authentication response with the X-Hasura-* variables

        Raises:
            WebhookHandlerUnauthorizedException: if the user is not authorized
            WebhookHandlerInvalidQueryException: if the graphql query has syntax errors
        """
        try:
            token = self.get_token(authentication_request.headers.authorization)
            self.jwt_service.validate(token)
            payload = self.jwt_service.get_payload(token)
            jwt_user = await self.claims_service.get_user(payload)
            jwt_groups = await self.claims_service.get_groups(payload)
        except Exception:
            self.logger.exception("Exception in authenticate_request")
            raise WebhookHandlerUnauthorizedException()
        else:
            try:
                parsed_query = gql(authentication_request.request.query)
            except GraphQLError as ge:
                # query parse error
                self.logger.exception("Query parse error:")
                raise WebhookHandlerInvalidQueryException(
                    f"Graphql query has one or more errors. {ge.message}"
                )
            else:
                # if there's an operation type different from query -> 401
                for d in parsed_query.definitions:
                    if isinstance(d, OperationDefinitionNode):
                        if d.operation != OperationType.QUERY:
                            self.logger.error(
                                f"Attempted an operation different from QUERY: {d.operation}"  # noqa: E501
                            )
                            raise WebhookHandlerUnauthorizedException()

                # mapping user and groups to witboost format
                acl_user = self.map_jwt_user_to_witboost_format(jwt_user)
                acl_groups = [
                    self.map_jwt_group_to_witboost_format(jwt_group)
                    for jwt_group in jwt_groups
                ]

                role_set = await self.role_repository.get_roles_by_user_and_groups(
                    acl_user, acl_groups
                )
                if len(role_set) == 0:
                    self.logger.error(f"The role set for the user {jwt_user} is empty")
                    raise WebhookHandlerUnauthorizedException()

                # extract all root_field_names from query
                root_field_names: list[str] = []
                for d in parsed_query.definitions:
                    if isinstance(d, ExecutableDefinitionNode):
                        for s in d.selection_set.selections:
                            if isinstance(s, FieldNode):
                                root_field_names.append(s.name.value)
                # get the corresponding roles
                roles = await self.role_repository.get_role_graphql_root_field_names(
                    root_field_names
                )

                # roles with access to all the root_field_names
                valid_roles = [
                    r.role_id
                    for r in roles
                    if self.has_access_to_all_root_field_names(
                        r.role_id, roles, root_field_names
                    )
                ]

                if len(valid_roles) == 0:
                    self.logger.error(
                        f"No roles were found that satisfied the search queries for the user {jwt_user}"  # noqa: E501
                    )
                    raise WebhookHandlerUnauthorizedException()

                # if there's one or more roles in the user role set, the user has access
                for valid_role in valid_roles:
                    if valid_role in role_set:
                        return AuthenticationResponse(
                            X_Hasura_User_Id=acl_user, X_Hasura_Role=valid_role
                        )

                self.logger.error(
                    f"The intersection between the valid roles and the role set for the user {jwt_user} is empty"  # noqa: E501
                )
                raise WebhookHandlerUnauthorizedException()

    def map_jwt_user_to_witboost_format(self, jwt_user: str) -> str:
        return f"user:{jwt_user.replace('@', '_', 1)}"

    def map_jwt_group_to_witboost_format(self, jwt_group: str) -> str:
        return f"group:{jwt_group}"

    def has_access_to_all_root_field_names(
        self,
        role_id: str,
        roles: list[RoleGraphqlRootFieldName],
        root_field_names: list[str],
    ) -> bool:
        for root_field_name in root_field_names:
            found = False
            for role in roles:
                if (
                    role.graphql_root_field_name == root_field_name
                    and role.role_id == role_id
                ):
                    found = True
                    break
            if found is False:
                return False
        return True
