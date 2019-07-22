import hmac
import json
import base64


class JwtInvalidSignature(Exception):
    pass


def create_token(payload: dict, secret: str):
    def b64_encode(data):
        if isinstance(data, str):
            data = data.encode()
        encoded = base64.b64encode(data).decode()
        return encoded.rstrip("=")

    header = json.dumps({
        "alg": "HS256",
        "typ": "JWT",
    })
    payload = json.dumps(payload)
    token = "{b64_header}.{b64_payload}".format(
        b64_header=b64_encode(header),
        b64_payload=b64_encode(payload),
    )
    signature = hmac.new(secret.encode(), token.encode(), "sha256").digest()
    return "{token}.{b64_signature}".format(token=token,
        b64_signature=b64_encode(signature))


def verify_token(token: str, secret: str):
    def b64_decode(data: str):
        padding = 4 - len(data) % 4
        data = "".join((data, padding * "="))
        return base64.b64decode(data)

    _token, signature = token.rsplit(".", 1)
    signature = b64_decode(signature)
    expected_signature = hmac.new(secret.encode(), _token.encode(), "sha256").digest()
    if signature != expected_signature:
        raise JwtInvalidSignature(token)
    header, payload = _token.split(".")
    header = json.loads(b64_decode(header))
    payload = json.loads(b64_decode(payload))
    return header, payload

