import pytest

from src.jwt.azure_claims_service import AzureClaimsService
from tests.jwt.fake_membership_service import FakeMembershipService


class TestAzureClaimsService:
    claims_service = AzureClaimsService(FakeMembershipService(["dev"]))

    @pytest.mark.asyncio
    async def test_get_user_ok(self):
        user = await self.claims_service.get_user({"unique_name": "username"})

        assert user == "username"

    @pytest.mark.asyncio
    async def test_get_groups_ok(self):
        groups = await self.claims_service.get_groups({"oid": "unused"})

        assert len(groups) == 1
        assert groups[0] == "dev"
