from fastapi import APIRouter, HTTPException, Response

import service
from dependencies import DatabaseSession, ResourceId
from schemas import PlayerCreate, PlayerPatch, PlayerRead, PlayerReplace


router = APIRouter()


@router.get("/players", response_model=list[PlayerRead], tags=["Players"])
def get_players(session: DatabaseSession):
    return service.list_players(session)


@router.post("/players", response_model=PlayerRead, status_code=201, tags=["Players"],
                  responses={409: {"description": "Username bestaat al"}})
def add_player(data: PlayerCreate, session: DatabaseSession, response: Response):
    player = service.create_player(session, data)
    response.headers["Location"] = f"/players/{player.id}"
    return player


@router.get("/players/{player_id}", response_model=PlayerRead, tags=["Players"],
                 responses={404: {"description": "Speler niet gevonden"}})
def get_player(player_id: ResourceId, session: DatabaseSession):
    return service.get_player(session, player_id)


@router.put("/players/{player_id}", response_model=PlayerRead, tags=["Players"])
def replace_player(player_id: ResourceId, data: PlayerReplace, session: DatabaseSession):
    """Vervang naam en actuele score; eerdere scores blijven in de geschiedenis."""
    return service.update_player(session, player_id, data)


@router.patch("/players/{player_id}", response_model=PlayerRead, tags=["Players"])
def patch_player(player_id: ResourceId, data: PlayerPatch, session: DatabaseSession):
    """Wijzig alleen meegegeven velden. Een scorewijziging voegt een registratie toe."""
    if not data.model_fields_set:
        raise HTTPException(status_code=400, detail="Geef minstens één veld op.")
    return service.update_player(session, player_id, data)


@router.delete("/players/{player_id}", status_code=204, tags=["Players"])
def remove_player(player_id: ResourceId, session: DatabaseSession):
    """Verwijder de speler en alle bijbehorende scores."""
    service.delete_player(session, player_id)
    return Response(status_code=204)
