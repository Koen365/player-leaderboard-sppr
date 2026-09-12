"""Game Score REST API. Start met python run.py en bezoek /docs."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import service
from database import PROJECT_DIR, initialize_database, make_engine, make_session_factory
from schemas import PlayerCreate, PlayerPatch, PlayerRead, PlayerReplace, ScoreCreate, ScoreRead

ResourceId = Annotated[int, Path(ge=1, le=9_223_372_036_854_775_807)]


def get_session(request: Request):
    # Iedere request heeft een eigen sessie; geen globale gedeelde transactie.
    with request.app.state.session_factory() as session:
        yield session


DatabaseSession = Annotated[Session, Depends(get_session)]


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

    @application.get("/players", response_model=list[PlayerRead], tags=["Players"])
    def get_players(session: DatabaseSession):
        return service.list_players(session)

    @application.post("/players", response_model=PlayerRead, status_code=201, tags=["Players"],
                      responses={409: {"description": "Username bestaat al"}})
    def add_player(data: PlayerCreate, session: DatabaseSession, response: Response):
        player = service.create_player(session, data)
        response.headers["Location"] = f"/players/{player.id}"
        return player

    @application.get("/players/{player_id}", response_model=PlayerRead, tags=["Players"],
                     responses={404: {"description": "Speler niet gevonden"}})
    def get_player(player_id: ResourceId, session: DatabaseSession):
        return service.get_player(session, player_id)

    @application.put("/players/{player_id}", response_model=PlayerRead, tags=["Players"])
    def replace_player(player_id: ResourceId, data: PlayerReplace, session: DatabaseSession):
        """Vervang naam en actuele score; eerdere scores blijven in de geschiedenis."""
        return service.update_player(session, player_id, data)

    @application.patch("/players/{player_id}", response_model=PlayerRead, tags=["Players"])
    def patch_player(player_id: ResourceId, data: PlayerPatch, session: DatabaseSession):
        """Wijzig alleen meegegeven velden. Een scorewijziging voegt een registratie toe."""
        if not data.model_fields_set:
            raise HTTPException(status_code=400, detail="Geef minstens één veld op.")
        return service.update_player(session, player_id, data)

    @application.delete("/players/{player_id}", status_code=204, tags=["Players"])
    def remove_player(player_id: ResourceId, session: DatabaseSession):
        """Verwijder de speler en alle bijbehorende scores."""
        service.delete_player(session, player_id)
        return Response(status_code=204)

    @application.get("/leaderboard", response_model=list[PlayerRead], tags=["Leaderboard"])
    def get_leaderboard(session: DatabaseSession):
        """Sorteer op actuele score, hoogste eerst; bij gelijkstand op speler-id."""
        return service.list_players(session, leaderboard=True)

    @application.get("/players/{player_id}/scores", response_model=list[ScoreRead], tags=["Scores"])
    def player_scores(player_id: ResourceId, session: DatabaseSession):
        return service.list_scores(session, player_id)

    @application.post("/players/{player_id}/scores", response_model=ScoreRead, status_code=201, tags=["Scores"])
    def add_score(player_id: ResourceId, data: ScoreCreate, session: DatabaseSession, response: Response):
        score = service.create_score(session, player_id, data)
        response.headers["Location"] = f"/scores/{score.id}"
        return score

    @application.get("/scores", response_model=list[ScoreRead], tags=["Scores"])
    def all_scores(session: DatabaseSession):
        return service.list_scores(session)

    @application.get("/scores/{score_id}", response_model=ScoreRead, tags=["Scores"])
    def get_score(score_id: ResourceId, session: DatabaseSession):
        return service.get_score(session, score_id)

    @application.patch("/scores/{score_id}", response_model=ScoreRead, tags=["Scores"])
    def patch_score(score_id: ResourceId, data: ScoreCreate, session: DatabaseSession):
        """Corrigeer een bestaande scoreregistratie."""
        return service.update_score(session, score_id, data)

    @application.delete("/scores/{score_id}", status_code=204, tags=["Scores"])
    def remove_score(score_id: ResourceId, session: DatabaseSession):
        service.delete_score(session, score_id)
        return Response(status_code=204)

    return application


app = create_app()
