from fastapi import APIRouter, HTTPException, Response

import service
from responses import CREATED_LOCATION, error_responses
from dependencies import CurrentUser, DatabaseSession, ResourceId
from schemas import PlayerCreate, PlayerPatch, PlayerRead, PlayerReplace


router = APIRouter()


@router.get("/players", response_model=list[PlayerRead], tags=["Players"], summary="Alle spelers bekijken")
def get_players(session: DatabaseSession):
    return service.list_players(session)


@router.post("/players", response_model=PlayerRead, status_code=201, tags=["Players"],
                  summary="Speler toevoegen", responses={**error_responses(401, 409), 201: {"headers": CREATED_LOCATION}})
def add_player(data: PlayerCreate, session: DatabaseSession, response: Response, user: CurrentUser):
    player = service.create_player(session, data, owner_id=user.id)
    response.headers["Location"] = f"/players/{player.id}"
    return player


@router.get("/players/{player_id}", response_model=PlayerRead, tags=["Players"],
                 summary="Speler opvragen", responses=error_responses(404))
def get_player(player_id: ResourceId, session: DatabaseSession):
    return service.get_player(session, player_id)


@router.put("/players/{player_id}", response_model=PlayerRead, tags=["Players"],
            summary="Naam en score vervangen", responses=error_responses(401, 403, 404, 409))
def replace_player(player_id: ResourceId, data: PlayerReplace, session: DatabaseSession, user: CurrentUser):
    """Vervang naam en actuele score; eerdere scores blijven in de geschiedenis."""
    service.require_player_owner(session, player_id, user.id)
    return service.update_player(session, player_id, data)


@router.patch("/players/{player_id}", response_model=PlayerRead, tags=["Players"],
              summary="Speler gedeeltelijk wijzigen", responses=error_responses(400, 401, 403, 404, 409))
def patch_player(player_id: ResourceId, data: PlayerPatch, session: DatabaseSession, user: CurrentUser):
    """Wijzig alleen meegegeven velden. Een scorewijziging voegt een registratie toe."""
    service.require_player_owner(session, player_id, user.id)
    if not data.model_fields_set:
        raise HTTPException(status_code=400, detail="Geef minstens één veld op.")
    return service.update_player(session, player_id, data)


@router.delete("/players/{player_id}", status_code=204, tags=["Players"],
               summary="Speler en scores verwijderen", responses=error_responses(401, 403, 404))
def remove_player(player_id: ResourceId, session: DatabaseSession, user: CurrentUser):
    """Verwijder de speler en alle bijbehorende scores."""
    service.require_player_owner(session, player_id, user.id)
    service.delete_player(session, player_id)
    return Response(status_code=204)
