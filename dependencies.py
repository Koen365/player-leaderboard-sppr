"""Gedeelde FastAPI-dependencies voor database en padparameters."""

from typing import Annotated

from fastapi import Depends, Path, Request
from sqlalchemy.orm import Session

ResourceId = Annotated[int, Path(ge=1, le=9_223_372_036_854_775_807)]


def get_session(request: Request):
    with request.app.state.session_factory() as session:
        yield session


DatabaseSession = Annotated[Session, Depends(get_session)]
