import pytest

from src.handlers.webhook_handler import (
    WebhookConfig,
    WebhookHandler,
    WebhookHandlerInvalidQueryException,
    WebhookHandlerUnauthorizedException,
)
from src.jwt.azure_claims_service import AzureClaimsService
from src.jwt.claims_service import ClaimsService
from src.models import (
    AuthenticationRequest,
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Request,
    Role,
    RoleGraphqlRootFieldName,
    UserRoleMappings,
)
from tests.jwt.fake_jwt_service import FakeJWTService
from tests.jwt.fake_membership_service import FakeMembershipService
from tests.repositories.fake_roles_repository import FakeRoleRoleRepository


class TestWebhookHandler:
    authorization_header = "Bearer eyJ0eXAiO"
    token = "eyJ0eXAiO"
    jwt_service = FakeJWTService(data={"unique_name": "user", "oid": "1234567890"})
    claims_service: ClaimsService = AzureClaimsService(FakeMembershipService(["dev"]))
    role = Role(
        role_id="role_id",
        component_id="component_id",
    )
    user_role = UserRoleMappings(role_id="role_id", users=["user:user1"])
    group_role = GroupRoleMappings(role_id="role_id", groups=["group:group1"])
    root_field_name_role = GraphqlRootFieldNameRoleMappings(
        role_id="role_id",
        component_id="component_id",
        graphql_root_field_names=["graphql_root_field_name1"],
    )
    role_root = RoleGraphqlRootFieldName(
        role_id="role_id", graphql_root_field_name="graphql_root_field_name1"
    )
    role_repository = FakeRoleRoleRepository(
        role=role,
        user_role=user_role,
        group_role=group_role,
        root_field_name_role=root_field_name_role,
        role_graphql_root_field_names=[role_root],
        roles_by_user_and_groups=["role_id"],
    )
    webhook_handler = WebhookHandler(
        claims_service=claims_service,
        jwt_service=jwt_service,
        role_repository=role_repository,
        webhook_config=WebhookConfig(
            authorization_header_field_names=["Authorization", "authorization"]
        ),
    )

    has_access_to_all_root_field_names_data = [
        pytest.param(
            "role_id1",
            [
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name",
                )
            ],
            ["graphql_root_field_name"],
            True,
            id="role_id1 has access to graphql_root_field_name",
        ),
        pytest.param(
            "role_id1",
            [
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_1",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_2",
                ),
            ],
            ["graphql_root_field_name_1", "graphql_root_field_name_2"],
            True,
            id="role_id1 has access to both graphql_root_field_name_1 & graphql_root_field_name_2",  # noqa: E501
        ),
        pytest.param(
            "role_id2",
            [
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_1",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id2",
                    graphql_root_field_name="graphql_root_field_name_2",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_2",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id2",
                    graphql_root_field_name="graphql_root_field_name_3",
                ),
            ],
            ["graphql_root_field_name_2", "graphql_root_field_name_3"],
            True,
            id="Results with multiple roles ids. role_id2 has access to both graphql_root_field_name_2 & graphql_root_field_name_3",  # noqa: E501
        ),
        pytest.param(
            "role_id1",
            [
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name",
                )
            ],
            ["graphql_root_field_name_error"],
            False,
            id="role_id1 has no access to graphql_root_field_name_error",
        ),
        pytest.param(
            "role_id1",
            [
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_1",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_2",
                ),
            ],
            ["graphql_root_field_name_1", "graphql_root_field_name_error"],
            False,
            id="role_id1 has access to graphql_root_field_name_1 but not to graphql_root_field_name_error",  # noqa: E501
        ),
        pytest.param(
            "role_id1",
            [
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_1",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id1",
                    graphql_root_field_name="graphql_root_field_name_2",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id2",
                    graphql_root_field_name="graphql_root_field_name_1",
                ),
                RoleGraphqlRootFieldName(
                    role_id="role_id2",
                    graphql_root_field_name="graphql_root_field_name_error",
                ),
            ],
            ["graphql_root_field_name_1", "graphql_root_field_name_error"],
            False,
            id="Results with multiple roles ids. role_id1 has access to graphql_root_field_name_1 but not to graphql_root_field_name_error, role_id2 has access to both",  # noqa: E501
        ),
    ]

    def test_get_token_fail_on_invalid_header(self):
        with pytest.raises(ValueError):
            self.webhook_handler.get_token({"authorization": "Invalid token"})

    def test_get_token_fail_on_header_not_present(self):
        with pytest.raises(ValueError):
            self.webhook_handler.get_token({})

    def test_get_token_fail_on_different_header_name(self):
        with pytest.raises(ValueError):
            self.webhook_handler.get_token({"auth": self.authorization_header})

    @pytest.mark.parametrize(
        "header_name",
        ["authorization", "Authorization"],
    )
    def test_get_token_ok(self, header_name: str):
        token = self.webhook_handler.get_token({header_name: self.authorization_header})

        assert token == self.token

    @pytest.mark.asyncio
    async def test_authenticate_request_fail_on_invalid_token(self):
        auth_request = AuthenticationRequest(
            headers={"authorization": ""}, request=Request(query="")
        )

        with pytest.raises(WebhookHandlerUnauthorizedException):
            await self.webhook_handler.authenticate_request(auth_request)

    @pytest.mark.asyncio
    async def test_authenticate_request_ok(self):
        auth_request = AuthenticationRequest(
            headers={"authorization": self.authorization_header},
            request=Request(
                query="query ProductById($id: uuid!) { graphql_root_field_name1(id: $id) { id name }}"  # noqa: E501
            ),
        )

        res = await self.webhook_handler.authenticate_request(auth_request)

        assert res.X_Hasura_User_Id == "user:user"
        assert res.X_Hasura_Role == "role_id"

    @pytest.mark.asyncio
    async def test_authenticate_request_root_field_not_authorized(self):
        auth_request = AuthenticationRequest(
            headers={"authorization": self.authorization_header},
            request=Request(
                query="query ProductById($id: uuid!) { root_field_not_authorized(id: $id) { id name }}"  # noqa: E501
            ),
        )

        with pytest.raises(WebhookHandlerUnauthorizedException):
            await self.webhook_handler.authenticate_request(auth_request)

    @pytest.mark.asyncio
    async def test_authenticate_request_invalid_query(self):
        auth_request = AuthenticationRequest(
            headers={"authorization": self.authorization_header},
            request=Request(
                query="query_invalid ProductById($id: uuid!) { root_field_not_authorized(id: $id) { id name }}"  # noqa: E501
            ),
        )

        with pytest.raises(WebhookHandlerInvalidQueryException):
            await self.webhook_handler.authenticate_request(auth_request)

    def test_map_jwt_user_to_witboost_format(self):
        user = "cristian.astorino@agilelab.it"

        mapped_user = self.webhook_handler.map_jwt_user_to_witboost_format(user)

        assert mapped_user == "user:cristian.astorino_agilelab.it"

    def test_map_jwt_group_to_witboost_format(self):
        group = "popeye"

        mapped_user = self.webhook_handler.map_jwt_group_to_witboost_format(group)

        assert mapped_user == "group:popeye"

    @pytest.mark.parametrize(
        "role_id,roles,root_field_names,expected",
        has_access_to_all_root_field_names_data,
    )
    def test_has_access_to_all_root_field_names(
        self, role_id, roles, root_field_names, expected
    ):
        assert (
            self.webhook_handler.has_access_to_all_root_field_names(
                role_id, roles, root_field_names
            )
            == expected
        )
