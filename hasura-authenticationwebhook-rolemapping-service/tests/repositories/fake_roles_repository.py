from src.models import (
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Role,
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
    ):
        self.role = role
        self.user_role = user_role
        self.group_role = group_role
        self.root_field_name_role = root_field_name_role

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
