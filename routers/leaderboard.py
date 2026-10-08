from fastapi import APIRouter

import service
from dependencies import DatabaseSession
from schemas import PlayerRead


router = APIRouter()


@router.get("/leaderboard", response_model=list[PlayerRead], tags=["Leaderboard"])
def get_leaderboard(session: DatabaseSession):
    """Sorteer op actuele score, hoogste eerst; bij gelijkstand op speler-id."""
    return service.list_players(session, leaderboard=True)
