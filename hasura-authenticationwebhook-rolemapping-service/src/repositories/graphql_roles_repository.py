import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from pydantic import BaseSettings

from src.models import (
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Role,
    RoleGraphqlRootFieldName,
    UserRoleMappings,
)
from src.repositories.queries_mutations import (
    mutation_delete_group_role,
    mutation_delete_root_field_name_role,
    mutation_delete_user_role,
    mutation_upsert_group_role,
    mutation_upsert_role,
    mutation_upsert_root_field_name_role,
    mutation_upsert_user_role,
    query_get_role_by_component_id,
    query_get_role_by_role_id,
    query_get_role_graphql_root_field_names,
    query_get_roles_by_user_and_groups,
)
from src.repositories.roles_repository import RoleRepository


class GraphqlConfig(BaseSettings):
    graphql_url: str
    graphql_role: str
    graphql_admin_secret: str
    rolemapping_table_schema: str


class RoleNotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class RoleUpsertNotAllowedException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class GraphqlRoleRepository(RoleRepository):
    def __init__(self, config: GraphqlConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def _get_transport(self) -> AIOHTTPTransport:
        return AIOHTTPTransport(
            url=self.config.graphql_url,
            headers={
                "X-Hasura-Role": self.config.graphql_role,
                "X-Hasura-Admin-Secret": self.config.graphql_admin_secret,
            },
        )

    def get_schema_name(self) -> str:
        match self.config.rolemapping_table_schema:
            case "public":
                return ""
            case other:
                return f"{other}_"

    async def get_role_by_role_id(self, role_id: str) -> Role:
        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                query_get_role_by_role_id.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            params = {"role_id": role_id}
            result = await session.execute(query, variable_values=params)
            if len(result[f"{self.get_schema_name()}roles"]) > 0:
                return Role.parse_obj(result[f"{self.get_schema_name()}roles"][0])
            raise RoleNotFoundException(f"Role not found for role_id {role_id}")

    async def get_role_by_component_id(self, component_id: str) -> Role:
        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                query_get_role_by_component_id.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            params = {"component_id": component_id}
            result = await session.execute(query, variable_values=params)
            if len(result[f"{self.get_schema_name()}roles"]) > 0:
                return Role.parse_obj(result[f"{self.get_schema_name()}roles"][0])
            raise RoleNotFoundException(
                f"Role not found for component_id {component_id}"
            )

    async def upsert_role(
        self, role: GraphqlRootFieldNameRoleMappings
    ) -> GraphqlRootFieldNameRoleMappings:
        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            # upsert on table roles
            gql_mutation_upsert_role = gql(
                mutation_upsert_role.replace("{{schema_name}}", self.get_schema_name())
            )
            params = {
                "component_id": role.component_id,
                "role_id": role.role_id,
            }
            result = await session.execute(
                gql_mutation_upsert_role, variable_values=params
            )
            if result[f"insert_{self.get_schema_name()}roles_one"] is None:
                raise RoleUpsertNotAllowedException(
                    f"Cannot upsert role with role_id {role.role_id}"
                )

            # upsert on table role_graphql_root_field_names
            root_field_names: list[str] = []
            gql_mutation_upsert_root_field_name_role = gql(
                mutation_upsert_root_field_name_role.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            for root_field_name in role.graphql_root_field_names:
                upsert_params = {
                    "graphql_root_field_name": root_field_name,
                    "role_id": role.role_id,
                }
                upsert_result = await session.execute(
                    gql_mutation_upsert_root_field_name_role,
                    variable_values=upsert_params,
                )
                root_field_names.append(
                    upsert_result[
                        f"insert_{self.get_schema_name()}role_graphql_root_field_names"
                    ]["returning"][0]["graphql_root_field_name"]
                )

            # delete from table role_graphql_root_field_names
            gql_mutation_delete_root_field_name_role = gql(
                mutation_delete_root_field_name_role.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            delete_params = {
                "graphql_root_field_names": role.graphql_root_field_names,
                "role_id": role.role_id,
            }
            await session.execute(
                gql_mutation_delete_root_field_name_role, variable_values=delete_params
            )

            return GraphqlRootFieldNameRoleMappings(
                role_id=result[f"insert_{self.get_schema_name()}roles_one"]["role_id"],
                component_id=result[f"insert_{self.get_schema_name()}roles_one"][
                    "component_id"
                ],
                graphql_root_field_names=root_field_names,
            )

    async def upsert_user_roles(self, role: UserRoleMappings) -> UserRoleMappings:
        # ensuring role exists
        await self.get_role_by_role_id(role.role_id)

        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            upsert_mutation = gql(
                mutation_upsert_user_role.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            users: list[str] = []
            for user in role.users:
                upsert_params = {
                    "user": user,
                    "role_id": role.role_id,
                }
                result = await session.execute(
                    upsert_mutation, variable_values=upsert_params
                )
                users.append(
                    result[f"insert_{self.get_schema_name()}user_roles"]["returning"][
                        0
                    ]["user"]
                )

            delete_mutation = gql(
                mutation_delete_user_role.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            delete_params = {
                "users": role.users,
                "role_id": role.role_id,
            }
            await session.execute(delete_mutation, variable_values=delete_params)

            return UserRoleMappings(role_id=role.role_id, users=users)

    async def upsert_group_roles(self, role: GroupRoleMappings) -> GroupRoleMappings:
        # ensuring role exists
        await self.get_role_by_role_id(role.role_id)

        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            upsert_mutation = gql(
                mutation_upsert_group_role.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            groups: list[str] = []
            for group in role.groups:
                upsert_params = {
                    "group": group,
                    "role_id": role.role_id,
                }
                result = await session.execute(
                    upsert_mutation, variable_values=upsert_params
                )
                groups.append(
                    result[f"insert_{self.get_schema_name()}group_roles"]["returning"][
                        0
                    ]["group"]
                )

            delete_mutation = gql(
                mutation_delete_group_role.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            delete_params = {
                "groups": role.groups,
                "role_id": role.role_id,
            }
            await session.execute(delete_mutation, variable_values=delete_params)

            return GroupRoleMappings(role_id=role.role_id, groups=groups)

    async def get_roles_by_user_and_groups(
        self, user: str, groups: list[str]
    ) -> list[str]:
        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                query_get_roles_by_user_and_groups.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            params = {"user": user, "groups": groups}
            result = await session.execute(query, variable_values=params)
            roles: list[str] = []
            if len(result[f"{self.get_schema_name()}user_roles"]) > 0:
                roles.extend(
                    [
                        r["role_id"]
                        for r in result[f"{self.get_schema_name()}user_roles"]
                    ]
                )
            if len(result[f"{self.get_schema_name()}group_roles"]) > 0:
                roles.extend(
                    [
                        r["role_id"]
                        for r in result[f"{self.get_schema_name()}group_roles"]
                    ]
                )
            return list(dict.fromkeys(roles))

    async def get_role_graphql_root_field_names(
        self, graphql_root_field_names: list[str]
    ) -> list[RoleGraphqlRootFieldName]:
        async with Client(
            transport=self._get_transport(),
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                query_get_role_graphql_root_field_names.replace(
                    "{{schema_name}}", self.get_schema_name()
                )
            )
            params = {
                "graphql_root_field_names": graphql_root_field_names,
            }
            result = await session.execute(query, variable_values=params)
            roles: list[RoleGraphqlRootFieldName] = []
            if (
                len(result[f"{self.get_schema_name()}role_graphql_root_field_names"])
                > 0
            ):
                roles.extend(
                    [
                        RoleGraphqlRootFieldName.parse_obj(r)
                        for r in result[
                            f"{self.get_schema_name()}role_graphql_root_field_names"
                        ]
                    ]
                )
            return roles
