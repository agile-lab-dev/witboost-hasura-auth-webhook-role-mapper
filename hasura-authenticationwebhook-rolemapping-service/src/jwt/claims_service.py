from abc import ABC, abstractmethod
from typing import Any


class ClaimsService(ABC):
    @abstractmethod
    async def get_user(self, payload: dict[str, Any]) -> str:
        """Extract the user from the claims defined in the JWT token

        Args:
            payload: claims defined in JWT token

        Returns:
            The user from the claims defined in the JWT token
        """
        pass

    @abstractmethod
    async def get_groups(self, payload: dict[str, Any]) -> list[str]:
        """Returns the groups a user is a member of

        Args:
            payload: claims defined in JWT token

        Returns:
            The groups a user is a member of
        """
        pass
