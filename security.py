"""Wachtwoordhashes en willekeurige toegangstokens."""

import hashlib
import secrets

from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
dummy_password_hash = password_hasher.hash(secrets.token_urlsafe(32))
TOKEN_LIFETIME = 3600


def hash_password(password):
    return password_hasher.hash(password)


def verify_password(password, password_hash):
    return password_hasher.verify(password, password_hash)


def new_token():
    return secrets.token_urlsafe(32)


def hash_token(token):
    # Tokens hebben al veel willekeur; alleen hun hash wordt opgeslagen.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
