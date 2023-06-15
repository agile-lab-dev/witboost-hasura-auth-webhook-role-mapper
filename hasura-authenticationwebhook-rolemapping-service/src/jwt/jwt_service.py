from abc import ABC, abstractmethod
from typing import Any


class JWTService(ABC):
    @abstractmethod
    def validate(self, token: str) -> None:
        """Validates a JWT Token

        Args:
            token: JWT token to validate

        Raises:
            PyJWTError: if the validation fails
        """
        pass

    @abstractmethod
    def get_payload(self, token: str) -> dict[str, Any]:
        """Return the claims defined in the JWT token

        Args:
            token: JWT token to validate

        Returns:
            The claims defined in the JWT token

        Raises:
            PyJWTError: if the validation fails
        """
        pass
