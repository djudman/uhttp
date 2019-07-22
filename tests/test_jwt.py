import unittest

from uhttp.auth.jwt import (
    create_token, verify_token, JwtInvalidSignature
)


class TestJwt(unittest.TestCase):
    def test_token(self):
        payload = {
            "sid": "xxx",
        }
        token = create_token(payload, "secret")
        jwt_token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzaWQiOiAieHh4In0.BtGutwEv6/M95b90AhHs+vOZodaF8yBOb0ezyneQqig"
        self.assertEqual(token, jwt_token)
        header, payload = verify_token(token, "secret")
        self.assertEqual(header, {"alg": "HS256", "typ": "JWT"})
        self.assertEqual(payload, {"sid": "xxx"})
        with self.assertRaises(JwtInvalidSignature) as ctx:
            verify_token(token, "xxx")
        self.assertEqual(str(ctx.exception), jwt_token)
