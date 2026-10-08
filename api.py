"""Game Score REST API. Start met python run.py en bezoek /docs."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import service
import auth_service
from database import PROJECT_DIR, initialize_database, make_engine, make_session_factory
from routers import auth, leaderboard, players, scores


def create_app(database_path=None, seed_file=PROJECT_DIR / "players.json"):
    @asynccontextmanager
    async def lifespan(application):
        engine = make_engine(database_path)
        try:
            initialize_database(engine, seed_file)
            application.state.session_factory = make_session_factory(engine)
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="Player Leaderboard API", version="3.0.0", lifespan=lifespan,
        description=(
            "Spelers en scoregeschiedenis blijven bewaard in SQLite. Lezen is openbaar. "
            "Registreer een account via /auth/register en log in met Authorize. "
            "Je kunt daarna spelers toevoegen en alleen je eigen spelers en scores wijzigen."
        ),
    )

    @application.exception_handler(service.NotFound)
    async def not_found(_request, error):
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @application.exception_handler(service.DuplicateUsername)
    async def duplicate_username(_request, error):
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @application.get("/", tags=["Status"])
    def root():
        return {"status": "ok", "message": "De Player Leaderboard API draait!"}

    @application.exception_handler(auth_service.InvalidCredentials)
    async def unauthorized(_request, error):
        return JSONResponse(status_code=401, content={"detail": str(error)},
                            headers={"WWW-Authenticate": "Bearer"})

    @application.exception_handler(auth_service.AccountExists)
    async def account_exists(_request, error):
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @application.exception_handler(service.Forbidden)
    async def forbidden(_request, error):
        return JSONResponse(status_code=403, content={"detail": str(error)})

    @application.exception_handler(RequestValidationError)
    async def invalid_input(_request, error):
        # Stuur invoer zoals wachtwoorden nooit terug in een foutmelding.
        details = [{"loc": item["loc"], "msg": item["msg"], "type": item["type"]}
                   for item in error.errors()]
        return JSONResponse(status_code=422, content={"detail": details})

    application.include_router(auth.router)
    application.include_router(players.router)
    application.include_router(scores.router)
    application.include_router(leaderboard.router)
    return application


app = create_app()
