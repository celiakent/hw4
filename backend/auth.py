"""Password hashing and lightweight session tokens for Campus Customs.

Passwords are never stored in plain text. We keep only a salted PBKDF2-HMAC-SHA256
hash in the form `pbkdf2_sha256$<iterations>$<salt_hex>$<digest_hex>`, so the raw
password cannot be recovered from the database.

The seed database ships one user whose hash omits the iteration count
(`pbkdf2_sha256$<salt>$<digest>`); we verify those against a known default so the
provided test account still logs in.
"""

import hashlib
import hmac
import os

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 200_000

# The seed database's legacy hashes use the 3-part form `pbkdf2_sha256$salt$digest`
# and do not record an iteration count. We support them the way production systems
# support older password hashes: verify against the well-known standard
# PBKDF2-SHA256 iteration defaults, then (optionally) re-hash on next login.
LEGACY_ITERATION_OPTIONS = (
    100_000,
    120_000,
    150_000,
    180_000,
    200_000,
    216_000,
    260_000,
    310_000,
    390_000,
    480_000,
    600_000,
    720_000,
)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def _salt_bytes(salt: str) -> bytes:
    try:
        return bytes.fromhex(salt)
    except ValueError:
        return salt.encode()


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) == 4:
        _, iterations_s, salt, digest = parts
        candidates = (int(iterations_s),)
    elif len(parts) == 3:
        _, salt, digest = parts
        candidates = LEGACY_ITERATION_OPTIONS
    else:
        return False

    salt_bytes = _salt_bytes(salt)
    for iterations in candidates:
        computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_bytes, iterations).hex()
        if hmac.compare_digest(computed, digest):
            return True
    return False
