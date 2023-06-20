from abc import ABC, abstractmethod

from src.models import (
    GraphqlRootFieldNameRoleMappings,
    GroupRoleMappings,
    Role,
    UserRoleMappings,
)


class RoleRepository(ABC):
    @abstractmethod
    async def get_role_by_role_id(self, role_id: str) -> Role:
        """Return the role identified by role_id

        Args:
            role_id: The role ID

        Returns:
            The role identified by role_id

        Raises:
            RoleNotFoundException: if the role doesn't exist
        """
        pass

    @abstractmethod
    async def get_role_by_component_id(self, component_id: str) -> Role:
        """Return the role identified by component_id

        Args:
            component_id: The component ID

        Returns:
            The role identified by component_id

        Raises:
            RoleNotFoundException: if the role doesn't exist
        """
        pass

    @abstractmethod
    async def upsert_role(
        self, role: GraphqlRootFieldNameRoleMappings
    ) -> GraphqlRootFieldNameRoleMappings:
        """Upsert a role

        Args:
            role: The role to upsert

        Returns:
            The upserted role

        Raises:
            RoleUpsertNotAllowedException: if the role_id already exists but
                component_id is different
        """
        pass

    @abstractmethod
    async def upsert_user_roles(self, role: UserRoleMappings) -> UserRoleMappings:
        """Upsert a user role

        Args:
            role: The user role to upsert

        Returns:
            The uperted user role

        Raises:
            RoleNotFoundException: if the corresponding role doesn't exist
        """
        pass

    @abstractmethod
    async def upsert_group_roles(self, role: GroupRoleMappings) -> GroupRoleMappings:
        """Upsert a group role

        Args:
            role: The group role to upsert

        Returns:
            The uperted group role

        Raises:
            RoleNotFoundException: if the corresponding role doesn't exist
        """
        pass
