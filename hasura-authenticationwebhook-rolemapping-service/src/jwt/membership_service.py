from abc import ABC, abstractmethod


class MembershipService(ABC):
    @abstractmethod
    async def get_memberships(self, user_id: str) -> list[str]:
        """Return the groups the user is member of

        Args:
            user_id: User identifier

        Returns:
            The groups the user is member of
        """
        pass
