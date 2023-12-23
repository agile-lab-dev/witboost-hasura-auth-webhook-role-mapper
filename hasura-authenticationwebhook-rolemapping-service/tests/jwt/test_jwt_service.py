import base64
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import PyJWTError

from src.jwt.concrete_jwt_service import ConcreteJWTService, JWTConfig


class TestJWTService:
    headers = {
        "typ": "JWT",
        "alg": "RS256",
        "x5t": "-KI3Q9nNR7bRofxmeZoXqbHZGew",
        "kid": "-KI3Q9nNR7bRofxmeZoXqbHZGew"
    }
    payload = {
        "aud": "https://management.core.windows.net/",
        "iss": "https://sts.windows.net/0fd0de9a-5b02-4b59-9eec-a9a4ae9b4b94/",
        "iat": 1686735964,
        "nbf": 1686735964,
        "exp": 1686740776,
        "acr": "1",
        "aio": "AYQAe/8TAAAA3hXKdzxI72E05wI1pz3E5V0WP4jbmG8iaXxSNpVsdrE69G8hEdezR5XYET3bigzbcH5cLtaGpsMta0rM5i04kPkpFHkanx6/NlqZc5b56tPPVRrNlJK0/MLkFE37tG3+D/QEeWqeT6k3OG1BRV0v4aW8TSMv+GHs8c4aK183xos=", # noqa: E501
        "altsecid": "5::10032001FFB8CC44",
        "amr": [
            "pwd",
            "rsa",
            "mfa"
        ],
        "appid": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
        "appidacr": "0",
        "email": "cristian.astorino@agilelab.it",
        "family_name": "Astorino",
        "given_name": "Cristian",
        "groups": [
            "1f3f3e5a-c7fa-4ecf-a0b3-47677f6774bb",
            "47b40f88-6f55-4163-ac5a-cd35d8b8f6ff"
        ],
        "idp": "https://sts.windows.net/eee7e750-299f-468f-a6c3-9f28923f6133/",
        "ipaddr": "123.123.123.123",
        "name": "Cristian Astorino",
        "oid": "eb33994d-ccdb-42f6-804e-56343d1fe5b2",
        "puid": "10032002B0CA4A46",
        "rh": "0.AUsAmt7QDwJbWUue7KmkrptLlEZIf3kAutdPukPawfj2MBNLALI.",
        "scp": "user_impersonation",
        "sub": "ncwBF8gMKRqFNo29aOF9G8VOpeid1Z9ywEGSJra2v-o",
        "tid": "0fd0de9a-5b02-4b59-9eec-a9a4ae9b4b94",
        "unique_name": "cristian.astorino@agilelab.it",
        "uti": "B3DpPGd0w0enwpkO73gUAA",
        "ver": "1.0",
        "wids": [
            "b79fbf4d-3ef9-4689-8143-76b194e85509"
        ],
        "xms_cc": [
            "CP1"
        ],
        "xms_tcdt": 1665591330
    }
    private_key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    n = public_key.public_numbers().n
    n_enc = base64.b64encode(n.to_bytes((n.bit_length() + 7) // 8, byteorder="big"))
    e = public_key.public_numbers().e
    e_enc = base64.b64encode(e.to_bytes((e.bit_length() + 7) // 8, byteorder="big"))
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "kid": "-KI3Q9nNR7bRofxmeZoXqbHZGew",
                "x5t": "-KI3Q9nNR7bRofxmeZoXqbHZGew",
                "n": n_enc,
                "e": e_enc,
                "x5c": [
                    "MIIC/TCCAeWgAwIBAgIIUd7j/OIahkYwDQYJKoZIhvcNAQELBQAwLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDAeFw0yMzExMDExNjAzMjdaFw0yODExMDExNjAzMjdaMC0xKzApBgNVBAMTImFjY291bnRzLmFjY2Vzc2NvbnRyb2wud2luZG93cy5uZXQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCzZMJFMHQcoR8sE+Lf/wLEJtaKvPuuW/Nxeen/SPeOuZv+Gy3SKIeJ9IHATQVXVZbv0rLDQABOQt9IsvKWXIK7OChQ6CZd3dgxqoHyZA4Eh5wVAMAeQzWzLOL9XBV0m3wfXIjSE4Zw6S26MM8eJ1UW066gOoBaUKzuQIbCVrMrhJ+7+md8kjhGZTwC+o7Rq4ZzGDbggJuk/TUbQ+Bu9by6FZJZJJNeZ90iHnrsk4eyC8WvSbUBRC/vBt5HGDKIfCfb2HqDVvBJgkHgjpMwb5wPKC9T2U1YXN5iG2obhn9wDeSFYgyZOrd1XMKyLiJTfT35zQWilZpxMei4fIxFykkVAgMBAAGjITAfMB0GA1UdDgQWBBRNcCE3HDX+HOJOu/bKfLYoSX3/0jANBgkqhkiG9w0BAQsFAAOCAQEAExns169MDr1dDNELYNK0JDjPUA6GR50jqfc+xa2KOljeXErOdihSvKgDS/vnDN6fjNNZuOMDyr6jjLvRsT0jVWzf/B6v92FrPRa/rv3urGXvW5am3BZyVPipirbiolMTuork95G7y7imftK7117uHcMq3D8f4fxscDiDXgjEEZqjkuzYDGLaVWGJqpv5xE4w+K4o2uDwmEIeIX+rI1MEVucS2vsvraOrjqjHwc3KrzuVRSsOU7YVHyUhku+7oOrB4tYrVbYYgwd6zXnkdouVPqOX9wTkc9iTmbDP+rfkhdadLxU+hmMyMuCJKgkZbWKFES7ce23jfTMbpqoHB4pgtQ=="
                ],
                "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0"
            }
        ]
    }
    token = jwt.encode(payload=payload,
                       algorithm="RS256",
                       key=private_key,
                       headers=headers)

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

    @patch('jwt.jwks_client.PyJWKClient.fetch_data')
    def test_validate_fail_on_wrong_aud(self, mock_fetch_data):
        mock_fetch_data.return_value = self.jwks
        jwt_service = ConcreteJWTService(self.jwt_config_verify_wrong_aud)

        with pytest.raises(PyJWTError):
            jwt_service.validate(self.token)

    @patch('jwt.jwks_client.PyJWKClient.fetch_data')
    def test_validate_ok(self, mock_fetch_data):
        mock_fetch_data.return_value = self.jwks
        jwt_service = ConcreteJWTService(self.jwt_config_verify_exp_disabled)

        jwt_service.validate(self.token)

    @patch('jwt.jwks_client.PyJWKClient.fetch_data')
    def test_get_payload_ok(self, mock_fetch_data):
        mock_fetch_data.return_value = self.jwks
        jwt_service = ConcreteJWTService(self.jwt_config_verify_exp_disabled)

        data = jwt_service.get_payload(self.token)

        assert len(data) > 0

