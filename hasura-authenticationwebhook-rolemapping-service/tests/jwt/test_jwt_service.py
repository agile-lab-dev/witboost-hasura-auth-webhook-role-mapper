import pytest
from jwt import PyJWTError

from src.jwt.concrete_jwt_service import ConcreteJWTService, JWTConfig


class TestJWTService:
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuY29yZS53aW5kb3dzLm5ldC8iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8wZmQwZGU5YS01YjAyLTRiNTktOWVlYy1hOWE0YWU5YjRiOTQvIiwiaWF0IjoxNjg2NzM1OTY0LCJuYmYiOjE2ODY3MzU5NjQsImV4cCI6MTY4Njc0MDc3NiwiYWNyIjoiMSIsImFpbyI6IkFZUUFlLzhUQUFBQTNoWEtkenhJNzJFMDV3STFwejNFNVYwV1A0amJtRzhpYVh4U05wVnNkckU2OUc4aEVkZXpSNVhZRVQzYmlnemJjSDVjTHRhR3BzTXRhMHJNNWkwNGtQa3BGSGthbng2L05scVpjNWI1NnRQUFZSck5sSkswL01Ma0ZFMzd0RzMrRC9RRWVXcWVUNmszT0cxQlJWMHY0YVc4VFNNditHSHM4YzRhSzE4M3hvcz0iLCJhbHRzZWNpZCI6IjU6OjEwMDMyMDAxRkZCOENDNDQiLCJhbXIiOlsicHdkIiwicnNhIiwibWZhIl0sImFwcGlkIjoiMDRiMDc3OTUtOGRkYi00NjFhLWJiZWUtMDJmOWUxYmY3YjQ2IiwiYXBwaWRhY3IiOiIwIiwiZW1haWwiOiJjcmlzdGlhbi5hc3Rvcmlub0BhZ2lsZWxhYi5pdCIsImZhbWlseV9uYW1lIjoiQXN0b3Jpbm8iLCJnaXZlbl9uYW1lIjoiQ3Jpc3RpYW4iLCJncm91cHMiOlsiMWYzZjNlNWEtYzdmYS00ZWNmLWEwYjMtNDc2NzdmNjc3NGJiIiwiNDdiNDBmODgtNmY1NS00MTYzLWFjNWEtY2QzNWQ4YjhmNmZmIl0sImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2VlZTdlNzUwLTI5OWYtNDY4Zi1hNmMzLTlmMjg5MjNmNjEzMy8iLCJpcGFkZHIiOiIxMzAuMjUuMTc0LjE5MCIsIm5hbWUiOiJDcmlzdGlhbiBBc3RvcmlubyIsIm9pZCI6ImViMzM5OTRkLWNjZGItNDJmNi04MDRlLTU2MzQzZDFmZTViMiIsInB1aWQiOiIxMDAzMjAwMkIwQ0E0QTQ2IiwicmgiOiIwLkFVc0FtdDdRRHdKYldVdWU3S21rcnB0TGxFWklmM2tBdXRkUHVrUGF3ZmoyTUJOTEFMSS4iLCJzY3AiOiJ1c2VyX2ltcGVyc29uYXRpb24iLCJzdWIiOiJuY3dCRjhnTUtScUZObzI5YU9GOUc4Vk9wZWlkMVo5eXdFR1NKcmEydi1vIiwidGlkIjoiMGZkMGRlOWEtNWIwMi00YjU5LTllZWMtYTlhNGFlOWI0Yjk0IiwidW5pcXVlX25hbWUiOiJjcmlzdGlhbi5hc3Rvcmlub0BhZ2lsZWxhYi5pdCIsInV0aSI6IkIzRHBQR2QwdzBlbndwa083M2dVQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfY2MiOlsiQ1AxIl0sInhtc190Y2R0IjoxNjY1NTkxMzMwfQ.g1uWH2cX0VY50jFcdAaV_3xISB3kA8czEav6h83WD79GYlDeVl5hoc1xzsD8iSTAqahXmiXGlNAKQ-VEhVLu5mAOqefx1cmVjc4c3mYANqmwhHuxHtxUYpOKwM7UCi5n1w_C32t4edp4yYlyqFVXDVYCNnJkLXfypE-PbYFVA6oQYIAAYXxPAgH1cpt4YtOI32BoGYt9vk8oL5Myic0tZ0Yt1_JCk5WNXiLjMas1B7FIuCbbAqaJ4b2BV__vVWkelRjzxBrZl5jo92LsU8-J6mhfK9BBfKhu6vIuqn1SfnbbZUUmQLG-4jZa8pWYQ6rLRny6NweIXvy_uvygoG43GA"  # noqa: E501
    jwt_config_verify_wrong_aud = JWTConfig(
        jwks_url="https://login.microsoftonline.com/common/discovery/v2.0/keys",
        jwt_audience="wrong aud",
        jwt_algorithms=["RS256", "RS512"],
        jwt_options={
            "verify_signature": True,
            "verify_exp": False,
            "require": ["exp", "iat"],
        },
    )
    jwt_config_verify_exp_disabled = JWTConfig(
        jwks_url="https://login.microsoftonline.com/common/discovery/v2.0/keys",
        jwt_audience="https://management.core.windows.net/",
        jwt_algorithms=["RS256", "RS512"],
        jwt_options={
            "verify_signature": True,
            "verify_exp": False,
            "require": ["exp", "iat"],
        },
    )

    def test_validate_fail_on_wrong_aud(self):
        jwt_service = ConcreteJWTService(self.jwt_config_verify_wrong_aud)

        with pytest.raises(PyJWTError):
            jwt_service.validate(self.token)

    def test_validate_ok(self):
        jwt_service = ConcreteJWTService(self.jwt_config_verify_exp_disabled)

        jwt_service.validate(self.token)

    def test_get_payload_ok(self):
        jwt_service = ConcreteJWTService(self.jwt_config_verify_exp_disabled)

        data = jwt_service.get_payload(self.token)

        assert len(data) > 0
