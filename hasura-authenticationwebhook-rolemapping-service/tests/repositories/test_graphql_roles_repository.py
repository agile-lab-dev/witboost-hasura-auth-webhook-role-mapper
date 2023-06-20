import pytest
from gql.client import Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import ExecutionResult

from src.models import (
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Role,
    UserRoleMappings,
)
from src.repositories.graphql_roles_repository import (
    GraphqlConfig,
    GraphqlRoleRepository,
    RoleNotFoundException,
    RoleUpsertNotAllowedException,
)


@pytest.fixture
def monkeypatch_base(monkeypatch):
    monkeypatch.setattr(AIOHTTPTransport, "connect", mock_connect)
    monkeypatch.setattr(Client, "_build_schema_from_introspection", mock_build_schema)


async def mock_connect(*args, **kwargs):
    pass


def mock_build_schema(*args, **kwargs):
    return None


async def role_mock_execute_no_data(*args, **kwargs):
    return ExecutionResult(
        data={
            "roles": [],
        }
    )


async def role_mock_execute_with_data(*args, **kwargs):
    return ExecutionResult(
        data={
            "roles": [
                {
                    "role_id": "role_id",
                    "component_id": "component_id",
                }
            ],
        }
    )


async def upsert_role_mock_execute_no_data(*args, **kwargs):
    return ExecutionResult(
        data={
            "insert_roles_one": None,
        }
    )


async def upsert_role_mock_execute_data(*args, **kwargs):
    return ExecutionResult(
        data={
            "insert_roles_one": {
                "role_id": "role_id",
                "component_id": "component_id",
                "graphql_root_field_name": "graphql_root_field_name",
            },
            "insert_role_graphql_root_field_names": {
                "returning": [{"graphql_root_field_name": "graphql_root_field_name1"}]
            },
        }
    )


async def upsert_user_role_mock_execute_data(*args, **kwargs):
    return ExecutionResult(
        data={
            "insert_user_roles": {"returning": [{"user": "user:user1"}]},
            "roles": [
                {
                    "role_id": "role_id",
                    "component_id": "component_id",
                    "graphql_root_field_name": "graphql_root_field_name",
                }
            ],
        }
    )


async def upsert_group_role_mock_execute_data(*args, **kwargs):
    return ExecutionResult(
        data={
            "insert_group_roles": {"returning": [{"group": "group:group1"}]},
            "roles": [
                {
                    "role_id": "role_id",
                    "component_id": "component_id",
                    "graphql_root_field_name": "graphql_root_field_name",
                }
            ],
        }
    )


async def roles_by_user_and_groups_mock_execute(*args, **kwargs):
    return ExecutionResult(
        data={
            "user_roles": [
                {
                    "role_id": "role_id",
                }
            ],
            "group_roles": [
                {
                    "role_id": "role_id",
                }
            ],
        }
    )


async def role_graphql_root_field_names_mock_execute(*args, **kwargs):
    return ExecutionResult(
        data={
            "role_graphql_root_field_names": [
                {
                    "role_id": "role_id",
                    "graphql_root_field_name": "graphql_root_field_name",
                }
            ]
        }
    )


class TestGraphqlRolesRepository:
    config = GraphqlConfig(
        graphql_url="http://unused",
        graphql_role="fake",
        graphql_admin_secret="fake",
    )
    repo = GraphqlRoleRepository(config)

    @pytest.mark.asyncio
    async def test_get_role_by_role_id_not_found(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(AIOHTTPTransport, "execute", role_mock_execute_no_data)

        with pytest.raises(RoleNotFoundException):
            await self.repo.get_role_by_role_id("not_existant_role_id")

    @pytest.mark.asyncio
    async def test_get_role_by_role_id_found(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(AIOHTTPTransport, "execute", role_mock_execute_with_data)

        role = await self.repo.get_role_by_role_id("role_id")

        assert role.role_id == "role_id"
        assert role.component_id == "component_id"

    @pytest.mark.asyncio
    async def test_get_role_by_component_id_not_found(
        self, monkeypatch, monkeypatch_base
    ):
        monkeypatch.setattr(AIOHTTPTransport, "execute", role_mock_execute_no_data)

        with pytest.raises(RoleNotFoundException):
            await self.repo.get_role_by_component_id("not_existant_component_id")

    @pytest.mark.asyncio
    async def test_get_role_by_component_id_found(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(AIOHTTPTransport, "execute", role_mock_execute_with_data)

        role = await self.repo.get_role_by_component_id("component_id")

        assert role.role_id == "role_id"
        assert role.component_id == "component_id"

    @pytest.mark.asyncio
    async def test_upsert_role_not_allowed(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(
            AIOHTTPTransport, "execute", upsert_role_mock_execute_no_data
        )

        with pytest.raises(RoleUpsertNotAllowedException):
            await self.repo.upsert_role(
                Role(
                    role_id="role_id",
                    component_id="component_id",
                    graphql_root_field_name="graphql_root_field_name",
                )
            )

    @pytest.mark.asyncio
    async def test_upsert_role_ok(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(AIOHTTPTransport, "execute", upsert_role_mock_execute_data)

        role = await self.repo.upsert_role(
            GraphqlRootFieldNameRoleMappings(
                role_id="role_id",
                component_id="component_id",
                graphql_root_field_names=["graphql_root_field_name1"],
            )
        )

        assert role.role_id == "role_id"
        assert role.component_id == "component_id"
        assert role.graphql_root_field_names == [
            "graphql_root_field_name1",
        ]

    @pytest.mark.asyncio
    async def test_upsert_user_role_ok(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(
            AIOHTTPTransport, "execute", upsert_user_role_mock_execute_data
        )

        user_role = await self.repo.upsert_user_roles(
            UserRoleMappings(role_id="role_id", users=["user:user1"])
        )

        assert user_role.role_id == "role_id"
        assert user_role.users == ["user:user1"]

    @pytest.mark.asyncio
    async def test_upsert_group_role_ok(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(
            AIOHTTPTransport, "execute", upsert_group_role_mock_execute_data
        )

        group_role = await self.repo.upsert_group_roles(
            GroupRoleMappings(role_id="role_id", groups=["group:group1"])
        )

        assert group_role.role_id == "role_id"
        assert group_role.groups == ["group:group1"]

    @pytest.mark.asyncio
    async def test_get_roles_by_user_and_groups_ok(self, monkeypatch, monkeypatch_base):
        monkeypatch.setattr(
            AIOHTTPTransport, "execute", roles_by_user_and_groups_mock_execute
        )

        result = await self.repo.get_roles_by_user_and_groups("user1", ["group1"])

        assert len(result) == 1
        assert result[0] == "role_id"

    @pytest.mark.asyncio
    async def test_get_role_graphql_root_field_names_ok(
        self, monkeypatch, monkeypatch_base
    ):
        monkeypatch.setattr(
            AIOHTTPTransport, "execute", role_graphql_root_field_names_mock_execute
        )

        result = await self.repo.get_role_graphql_root_field_names(
            ["graphql_root_field_name"]
        )

        assert len(result) == 1
        assert result[0].role_id == "role_id"
        assert result[0].graphql_root_field_name == "graphql_root_field_name"
