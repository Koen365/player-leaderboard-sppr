"""Gedeelde FastAPI-dependencies voor database en padparameters."""

from typing import Annotated

from fastapi import Depends, Path, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import auth_service
from models import User

ResourceId = Annotated[int, Path(ge=1, le=9_223_372_036_854_775_807)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
BearerToken = Annotated[str, Depends(oauth2_scheme)]


def get_session(request: Request):
    # FastAPI sluit deze sessie na het verzoek, ook als er een fout optreedt.
    with request.app.state.session_factory() as session:
        yield session


DatabaseSession = Annotated[Session, Depends(get_session)]


def get_current_user(token: BearerToken, session: DatabaseSession):
    return auth_service.user_for_token(session, token)


CurrentUser = Annotated[User, Depends(get_current_user)]
