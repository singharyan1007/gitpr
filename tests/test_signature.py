import hashlib
import hmac

from app.domain.signature import verify_signature

SECRET = "testsecret"


def _sign(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


def test_valid_signature():
    body = b'{"hello": "world"}'
    assert verify_signature(body, _sign(body), SECRET)


def test_invalid_signature():
    body = b'{"hello": "world"}'
    assert not verify_signature(body, "sha256=deadbeef", SECRET)


def test_missing_signature():
    assert not verify_signature(b"{}", None, SECRET)


# tampered signature

def test_tampered_signature():
    body = b'{"hello":"world"}'
    assert not verify_signature(body,"sha256"+"0"*64,SECRET)