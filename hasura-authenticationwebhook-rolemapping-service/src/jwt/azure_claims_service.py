import logging
from typing import Any

from src.jwt.membership_service import MembershipService

from .claims_service import ClaimsService


class AzureClaimsService(ClaimsService):
    def __init__(self, membership_service: MembershipService):
        self.membership_service = membership_service
        self.logger = logging.getLogger(__name__)

    async def get_user(self, payload: dict[str, Any]) -> str:
        return payload["unique_name"]

    async def get_groups(self, payload: dict[str, Any]) -> list[str]:
        groups = await self.membership_service.get_memberships(payload["oid"])
        return groups
