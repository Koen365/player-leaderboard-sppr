"""Registratie, inloggen en het intrekken van sessies."""

import time

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from models import AccessSession, User
import security


class InvalidCredentials(ValueError):
    pass


class AccountExists(ValueError):
    pass


def register_user(session, data):
    user = User(
        username=data.username,
        username_key=data.username.casefold(),
        password_hash=security.hash_password(data.password.get_secret_value()),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        if "users.username_key" in str(error.orig):
            raise AccountExists("Deze accountnaam bestaat al.") from error
        raise
    session.refresh(user)
    return user


def login(session, username, password):
    if not 1 <= len(username) <= 50 or not 10 <= len(password) <= 128:
        raise InvalidCredentials("Gebruikersnaam of wachtwoord onjuist.")
    user = session.scalar(
        select(User).where(User.username_key == username.strip().casefold())
    )
    # Controleer ook bij een onbekende naam een hash om tijdsverschillen te beperken.
    stored_hash = user.password_hash if user else security.dummy_password_hash
    valid = security.verify_password(password, stored_hash)
    if not valid or user is None:
        raise InvalidCredentials("Gebruikersnaam of wachtwoord onjuist.")
    token = security.new_token()
    now = int(time.time())
    session.execute(delete(AccessSession).where(AccessSession.expires_at <= now))
    session.add(
        AccessSession(
            token_hash=security.hash_token(token),
            user_id=user.id,
            expires_at=now + security.TOKEN_LIFETIME,
        )
    )
    session.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": security.TOKEN_LIFETIME,
    }


def user_for_token(session, token):
    if len(token) != 43:
        raise InvalidCredentials(
            "Log opnieuw in: je toegangstoken is ongeldig of verlopen."
        )
    access = session.get(AccessSession, security.hash_token(token))
    if access is None or access.expires_at <= int(time.time()):
        raise InvalidCredentials(
            "Log opnieuw in: je toegangstoken is ongeldig of verlopen."
        )
    user = session.get(User, access.user_id)
    if user is None:
        raise InvalidCredentials("Log opnieuw in: je account bestaat niet meer.")
    return user


def logout(session, token):
    session.execute(
        delete(AccessSession).where(
            AccessSession.token_hash == security.hash_token(token)
        )
    )
    session.commit()
