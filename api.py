"""
Sprint 2 - Player Leaderboard API
==================================

Deze FastAPI-app bouwt voort op het Sprint 1 consoleproject (main.py).
We hergebruiken de bestaande load_players()-functie zodat we dezelfde
players.json als databron gebruiken - er is dus geen dubbele logica.

Starten:
    uvicorn api:app --reload

Swagger UI (interactieve documentatie/testomgeving):
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException

from main import load_players

app = FastAPI(
    title="Player Leaderboard API",
    description="Een eenvoudige API om spelers en hun scores op te vragen.",
    version="1.0.0",
)


@app.get("/")
def root():
    """Test-endpoint om te controleren of de API draait."""
    return {"status": "ok", "message": "De Player Leaderboard API draait!"}


@app.get("/players")
def get_players():
    """Geef alle spelers terug als JSON."""
    players = load_players()
    return players


@app.get("/players/{player_id}")
def get_player(player_id: int):
    """Geef één specifieke speler terug op basis van ID.

    Bestaat de speler niet, dan geven we een 404 met een duidelijke
    foutmelding terug (via FastAPI's HTTPException).
    """
    players = load_players()

    for player in players:
        if player["id"] == player_id:
            return player

    raise HTTPException(
        status_code=404,
        detail=f"Speler met ID {player_id} niet gevonden."
    )


@app.get("/leaderboard")
def get_leaderboard():
    """Geef alle spelers terug, gesorteerd van hoogste naar laagste score."""
    players = load_players()
    sorted_players = sorted(players, key=lambda player: player["score"], reverse=True)
    return sorted_players
