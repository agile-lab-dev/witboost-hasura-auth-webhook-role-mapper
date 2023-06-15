from src.jwt.membership_service import MembershipService


class FakeMembershipService(MembershipService):
    def __init__(self, groups: list[str]):
        self.groups = groups

    async def get_memberships(self, user_id: str) -> list[str]:
        return self.groups
