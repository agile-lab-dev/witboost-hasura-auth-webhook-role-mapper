from typing import Any

from src.jwt.jwt_service import JWTService


class FakeJWTService(JWTService):
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def validate(self, token: str) -> None:
        pass

    def get_payload(self, token: str) -> dict[str, Any]:
        return self.data
