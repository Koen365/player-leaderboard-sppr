from fastapi import APIRouter, Response

import service
from dependencies import DatabaseSession, ResourceId
from schemas import ScoreCreate, ScoreRead


router = APIRouter()


@router.get("/players/{player_id}/scores", response_model=list[ScoreRead], tags=["Scores"])
def player_scores(player_id: ResourceId, session: DatabaseSession):
    return service.list_scores(session, player_id)


@router.post("/players/{player_id}/scores", response_model=ScoreRead, status_code=201, tags=["Scores"])
def add_score(player_id: ResourceId, data: ScoreCreate, session: DatabaseSession, response: Response):
    score = service.create_score(session, player_id, data)
    response.headers["Location"] = f"/scores/{score.id}"
    return score


@router.get("/scores", response_model=list[ScoreRead], tags=["Scores"])
def all_scores(session: DatabaseSession):
    return service.list_scores(session)


@router.get("/scores/{score_id}", response_model=ScoreRead, tags=["Scores"])
def get_score(score_id: ResourceId, session: DatabaseSession):
    return service.get_score(session, score_id)


@router.patch("/scores/{score_id}", response_model=ScoreRead, tags=["Scores"])
def patch_score(score_id: ResourceId, data: ScoreCreate, session: DatabaseSession):
    """Corrigeer een bestaande scoreregistratie."""
    return service.update_score(session, score_id, data)


@router.delete("/scores/{score_id}", status_code=204, tags=["Scores"])
def remove_score(score_id: ResourceId, session: DatabaseSession):
    service.delete_score(session, score_id)
    return Response(status_code=204)
