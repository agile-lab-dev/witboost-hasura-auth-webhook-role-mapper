from src.models import (
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Role,
    RoleGraphqlRootFieldName,
    UserRoleMappings,
)
from src.repositories.graphql_roles_repository import (
    RoleNotFoundException,
    RoleUpsertNotAllowedException,
)
from src.repositories.roles_repository import RoleRepository


class FakeRoleRoleRepository(RoleRepository):
    def __init__(
        self,
        role: Role,
        user_role: UserRoleMappings,
        group_role: GroupRoleMappings,
        root_field_name_role: GraphqlRootFieldNameRoleMappings,
        roles_by_user_and_groups: list[str],
        role_graphql_root_field_names: list[RoleGraphqlRootFieldName],
    ):
        self.role = role
        self.user_role = user_role
        self.group_role = group_role
        self.root_field_name_role = root_field_name_role
        self.roles_by_user_and_groups = roles_by_user_and_groups
        self.role_graphql_root_field_names = role_graphql_root_field_names

    async def get_role_by_role_id(self, role_id: str) -> Role:
        return self.role

    async def get_role_by_component_id(self, component_id: str) -> Role:
        return self.role

    async def upsert_role(
        self, role: GraphqlRootFieldNameRoleMappings
    ) -> GraphqlRootFieldNameRoleMappings:
        return self.root_field_name_role

    async def upsert_user_roles(self, role: UserRoleMappings) -> UserRoleMappings:
        return self.user_role

    async def upsert_group_roles(self, role: GroupRoleMappings) -> GroupRoleMappings:
        return self.group_role

    async def get_roles_by_user_and_groups(
        self, user: str, groups: list[str]
    ) -> list[str]:
        return self.roles_by_user_and_groups

    async def get_role_graphql_root_field_names(
        self, graphql_root_field_names: list[str]
    ) -> list[RoleGraphqlRootFieldName]:
        return self.role_graphql_root_field_names


class FakeRoleRoleRepositoryRaisingHandledError(RoleRepository):
    async def get_role_by_role_id(self, role_id: str) -> Role:
        raise RoleNotFoundException("error")

    async def get_role_by_component_id(self, component_id: str) -> Role:
        raise RoleNotFoundException("error")

    async def upsert_role(
        self, role: GraphqlRootFieldNameRoleMappings
    ) -> GraphqlRootFieldNameRoleMappings:
        raise RoleUpsertNotAllowedException("error")

    async def upsert_user_roles(self, role: UserRoleMappings) -> UserRoleMappings:
        raise RoleNotFoundException("error")

    async def upsert_group_roles(self, role: GroupRoleMappings) -> GroupRoleMappings:
        raise RoleNotFoundException("error")

    async def get_roles_by_user_and_groups(
        self, user: str, groups: list[str]
    ) -> list[str]:
        return []

    async def get_role_graphql_root_field_names(
        self, graphql_root_field_names: list[str]
    ) -> list[RoleGraphqlRootFieldName]:
        return []


class FakeRoleRoleRepositoryRaisingGenericError(RoleRepository):
    async def get_role_by_role_id(self, role_id: str) -> Role:
        raise Exception("error")

    async def get_role_by_component_id(self, component_id: str) -> Role:
        raise Exception("error")

    async def upsert_role(
        self, role: GraphqlRootFieldNameRoleMappings
    ) -> GraphqlRootFieldNameRoleMappings:
        raise Exception("error")

    async def upsert_user_roles(self, role: UserRoleMappings) -> UserRoleMappings:
        raise Exception("error")

    async def upsert_group_roles(self, role: GroupRoleMappings) -> GroupRoleMappings:
        raise Exception("error")

    async def get_roles_by_user_and_groups(
        self, user: str, groups: list[str]
    ) -> list[str]:
        raise Exception("error")

    async def get_role_graphql_root_field_names(
        self, graphql_root_field_names: list[str]
    ) -> list[RoleGraphqlRootFieldName]:
        raise Exception("error")
