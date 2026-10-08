"""Game Score REST API. Start met python run.py en bezoek /docs."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import service
from database import PROJECT_DIR, initialize_database, make_engine, make_session_factory
from routers import leaderboard, players, scores

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
        title="Player Leaderboard API", version="2.0.0", lifespan=lifespan,
        description=(
            "Game Score Manager — sprint 1 t/m 4. Spelers en scoregeschiedenis "
            "blijven bewaard in SQLite. De laatst toegevoegde score is de actuele "
            "score op het leaderboard. Gebruik Try it out om een endpoint te testen."
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


    application.include_router(players.router)
    application.include_router(scores.router)
    application.include_router(leaderboard.router)
    return application


app = create_app()
