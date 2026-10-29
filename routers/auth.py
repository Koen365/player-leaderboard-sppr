from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

import auth_service
from responses import error_responses
from dependencies import BearerToken, CurrentUser, DatabaseSession
from schemas import TokenRead, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Account"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="Account registreren",
    responses=error_responses(409),
)
def register(data: UserCreate, session: DatabaseSession):
    """Maak een account met een wachtwoord van 10 tot 128 tekens."""
    return auth_service.register_user(session, data)


@router.post(
    "/login",
    response_model=TokenRead,
    summary="Inloggen",
    responses=error_responses(400, 401),
)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DatabaseSession,
    response: Response,
):
    """Log in met formuliergegevens of gebruik de Authorize-knop bovenaan."""
    result = auth_service.login(session, form.username, form.password)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return result


@router.get(
    "/me",
    response_model=UserRead,
    summary="Mijn account bekijken",
    responses=error_responses(401),
)
def me(user: CurrentUser):
    return user


@router.post(
    "/logout", status_code=204, summary="Uitloggen", responses=error_responses(401)
)
def logout(user: CurrentUser, token: BearerToken, session: DatabaseSession):
    """Trek het gebruikte token direct in; andere sessies blijven geldig."""
    auth_service.logout(session, token)
    return Response(status_code=204)
