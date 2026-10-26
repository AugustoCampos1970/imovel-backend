"""Hash de senhas e tokens de acesso assinados usando apenas a stdlib."""

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Optional

from app.config import JWT_EXPIRE_SECONDS, JWT_SECRET_KEY

_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), _ITERATIONS
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), _ITERATIONS
        ).hex()
    except (ValueError, TypeError):
        return False
    return secrets.compare_digest(candidate, digest)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(user_id: int) -> str:
    """Cria um JWT HS256 com validade configurável."""
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + JWT_EXPIRE_SECONDS,
    }
    header_part = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode()
    )
    payload_part = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    )
    signing_input = f"{header_part}.{payload_part}".encode()
    signature = hmac.new(
        JWT_SECRET_KEY.encode(), signing_input, hashlib.sha256
    ).digest()
    return f"{header_part}.{payload_part}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Valida assinatura e expiração; retorna o payload ou None."""
    try:
        header_part, payload_part, signature_part = token.split(".")
        signing_input = f"{header_part}.{payload_part}".encode()
        expected = hmac.new(
            JWT_SECRET_KEY.encode(), signing_input, hashlib.sha256
        ).digest()
        received = _b64url_decode(signature_part)
        if not hmac.compare_digest(expected, received):
            return None

        header = json.loads(_b64url_decode(header_part))
        payload = json.loads(_b64url_decode(payload_part))
        if header.get("alg") != "HS256" or not payload.get("sub"):
            return None
        if int(payload.get("exp", 0)) <= int(time.time()):
            return None
        return payload
    except (
        ValueError,
        TypeError,
        json.JSONDecodeError,
        binascii.Error,
        UnicodeDecodeError,
        AttributeError,
    ):
        return None
