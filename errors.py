"""Duidelijke JSON-fouten zonder wachtwoorden, SQL of stacktraces in responses."""

import logging

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

import auth_service
import service

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    status_codes = {
        service.NotFound: 404,
        service.DuplicateUsername: 409,
        service.Forbidden: 403,
        auth_service.InvalidCredentials: 401,
        auth_service.AccountExists: 409,
    }

    async def domain_error(_request, error):
        status_code = status_codes[type(error)]
        headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
        return JSONResponse(
            status_code=status_code, content={"detail": str(error)}, headers=headers
        )

    for exception_type in status_codes:
        app.add_exception_handler(exception_type, domain_error)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(_request, error):
        details = []
        for item in error.errors():
            # Ook een onbekende veldnaam met ongeldige Unicode moet een 422 geven.
            location = [
                (
                    part.encode("utf-8", errors="replace").decode("utf-8")
                    if isinstance(part, str)
                    else part
                )
                for part in item["loc"]
            ]
            details.append({"loc": location, "msg": item["msg"], "type": item["type"]})
        return JSONResponse(status_code=422, content={"detail": details})

    @app.exception_handler(OperationalError)
    async def unavailable_database(_request, error):
        logger.error("Database tijdelijk niet beschikbaar (%s).", type(error).__name__)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database tijdelijk niet beschikbaar. Probeer later opnieuw."
            },
            headers={"Retry-After": "1"},
        )

    @app.exception_handler(SQLAlchemyError)
    @app.exception_handler(Exception)
    async def unexpected_error(_request, error):
        logger.error("Onverwachte serverfout (%s).", type(error).__name__)
        return JSONResponse(
            status_code=500, content={"detail": "Er ging iets mis op de server."}
        )
