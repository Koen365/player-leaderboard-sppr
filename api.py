"""Game Score REST API. Start met python run.py en bezoek /docs."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import PROJECT_DIR, initialize_database, make_engine, make_session_factory
from routers import auth, leaderboard, players, scores
from errors import register_error_handlers
from responses import VALIDATION_RESPONSE, error_responses
from schemas import StatusRead


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
        title="Player Leaderboard API",
        version="3.1.0",
        lifespan=lifespan,
        responses={422: VALIDATION_RESPONSE, **error_responses(500, 503)},
        openapi_tags=[
            {"name": "Status", "description": "Controleer of de API bereikbaar is."},
            {
                "name": "Account",
                "description": "Registreer eerst, gebruik dan Authorize. Een account kan meerdere spelers beheren.",
            },
            {
                "name": "Players",
                "description": "Lezen is openbaar. Toevoegen vereist login; wijzigen en verwijderen vereisen eigenaarschap.",
            },
            {
                "name": "Scores",
                "description": "Scorehistorie is openbaar. Wijzigen mag alleen voor de eigenaar van de gekoppelde speler.",
            },
            {
                "name": "Leaderboard",
                "description": "Openbare ranglijst op de laatst toegevoegde score, niet de hoogste ooit.",
            },
        ],
        description=(
            "Spelers en scoregeschiedenis blijven bewaard in SQLite. Lezen is openbaar. "
            "Registreer een account via /auth/register en log in met Authorize. "
            "Je kunt daarna spelers toevoegen en alleen je eigen spelers en scores wijzigen."
        ),
    )

    @application.get(
        "/", tags=["Status"], response_model=StatusRead, summary="Status opvragen"
    )
    def root():
        return {"status": "ok", "message": "De Player Leaderboard API draait!"}

    register_error_handlers(application)
    application.include_router(auth.router)
    application.include_router(players.router)
    application.include_router(scores.router)
    application.include_router(leaderboard.router)
    return application


app = create_app()
