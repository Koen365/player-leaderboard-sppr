from fastapi import APIRouter, Response

import service
from responses import CREATED_LOCATION, error_responses
from dependencies import CurrentUser, DatabaseSession, ResourceId
from schemas import ScoreCreate, ScoreRead


router = APIRouter()


@router.get("/players/{player_id}/scores", response_model=list[ScoreRead], tags=["Scores"],
            summary="Scoregeschiedenis bekijken", responses=error_responses(404))
def player_scores(player_id: ResourceId, session: DatabaseSession):
    return service.list_scores(session, player_id)


@router.post("/players/{player_id}/scores", response_model=ScoreRead, status_code=201, tags=["Scores"],
             summary="Nieuwe score registreren", responses={**error_responses(401, 403, 404), 201: {"headers": CREATED_LOCATION}})
def add_score(player_id: ResourceId, data: ScoreCreate, session: DatabaseSession, response: Response,
              user: CurrentUser):
    service.require_player_owner(session, player_id, user.id)
    score = service.create_score(session, player_id, data)
    response.headers["Location"] = f"/scores/{score.id}"
    return score


@router.get("/scores", response_model=list[ScoreRead], tags=["Scores"], summary="Alle scores bekijken")
def all_scores(session: DatabaseSession):
    return service.list_scores(session)


@router.get("/scores/{score_id}", response_model=ScoreRead, tags=["Scores"],
            summary="Score opvragen", responses=error_responses(404))
def get_score(score_id: ResourceId, session: DatabaseSession):
    return service.get_score(session, score_id)


@router.patch("/scores/{score_id}", response_model=ScoreRead, tags=["Scores"],
              summary="Bestaande score corrigeren", responses=error_responses(401, 403, 404))
def patch_score(score_id: ResourceId, data: ScoreCreate, session: DatabaseSession, user: CurrentUser):
    """Corrigeer een bestaande scoreregistratie."""
    service.require_score_owner(session, score_id, user.id)
    return service.update_score(session, score_id, data)


@router.delete("/scores/{score_id}", status_code=204, tags=["Scores"],
               summary="Score verwijderen", responses=error_responses(401, 403, 404))
def remove_score(score_id: ResourceId, session: DatabaseSession, user: CurrentUser):
    service.require_score_owner(session, score_id, user.id)
    service.delete_score(session, score_id)
    return Response(status_code=204)
