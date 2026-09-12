# Player Leaderboard - Sprint 2 (API)

Sprint 1 was een consoleprogramma (`main.py`) waarmee je spelers en scores
kon beheren via een menu in de terminal. In Sprint 2 ontsluiten we diezelfde
data via een **web-API** met FastAPI, zodat andere programma's (of een
frontend) de spelersdata kunnen opvragen via HTTP.

## Onderzoek: wat is FastAPI?

FastAPI is een modern Python-framework voor het bouwen van web-API's.
Een paar kernpunten:

- Je definieert endpoints (URL's) als gewone Python-functies met een
  decorator zoals `@app.get("/players")`.
- FastAPI genereert automatisch **interactieve documentatie** (Swagger UI
  op `/docs`), waarmee je endpoints direct in de browser kunt uittesten.
- Het valideert automatisch inputs op basis van type hints (bijvoorbeeld
  `player_id: int` zorgt dat FastAPI een fout teruggeeft als iemand geen
  geldig getal meegeeft).
- Het is snel, omdat het gebruikmaakt van `async`/`await` en de Starlette-
  en Pydantic-bibliotheken onder de motorkap.

Je gebruikt FastAPI wanneer je data of functionaliteit uit een Python-
programma beschikbaar wilt maken via internet of een netwerk - bijvoorbeeld
zodat een website, mobiele app of ander programma jouw spelersdata kan
opvragen zonder dat het zelf toegang hoeft te hebben tot `players.json`.

## Onderzoek: HTTP requests, responses en statuscodes

- Een **request** is het verzoek dat een client (bijv. je browser) naar de
  server stuurt. Bij een GET-request vraag je data op, zonder dat er iets
  wijzigt op de server.
- Een **response** is het antwoord dat de server terugstuurt: meestal data
  (hier in JSON-formaat) plus een statuscode.
- Een **statuscode** vertelt of het verzoek gelukt is en zo niet, waarom
  niet. Belangrijke codes in dit project:
  - `200 OK` - het verzoek is gelukt, de gevraagde data komt terug.
  - `404 Not Found` - de gevraagde resource (bijv. een speler-ID) bestaat
    niet.
  - `422 Unprocessable Entity` - FastAPI geeft dit automatisch terug als
    de input niet aan het verwachte type voldoet (bijv. tekst in plaats
    van een getal bij `/players/{id}`).

## Project structuur

```
.
├── main.py           # Sprint 1: consoleprogramma + databeheer-functies
├── api.py            # Sprint 2: FastAPI-app met de endpoints
├── run.py            # Eén-commando starter (installeert + start de server)
├── players.json       # Databron (gedeeld door main.py en api.py)
├── requirements.txt  # Python-dependencies
└── README.md
```

`api.py` hergebruikt de `load_players()`-functie uit `main.py`, zodat er
geen dubbele logica ontstaat en beide programma's dezelfde `players.json`
als bron gebruiken.

## Snel starten (één commando)

Open een terminal in deze map en voer uit:

```bash
python run.py
```

Dit installeert automatisch `fastapi` en `uvicorn` (als ze nog niet
aanwezig zijn) en start daarna de server. De API is bereikbaar via
`http://127.0.0.1:8000` en Swagger UI via `http://127.0.0.1:8000/docs`.

Op sommige systemen gebruik je `python3 run.py` in plaats van `python run.py`.

### Handmatig (alternatief)

Wil je het liever los doen:

```bash
pip install -r requirements.txt
uvicorn api:app --reload
```

- `api` = bestandsnaam (`api.py`)
- `app` = de naam van de FastAPI-instantie in dat bestand
- `--reload` = herstart de server automatisch bij codewijzigingen (handig
  tijdens ontwikkelen)

## Endpoints

| Methode | Endpoint         | Beschrijving                                      |
|---------|------------------|----------------------------------------------------|
| GET     | `/`              | Test-endpoint, controleert of de API draait        |
| GET     | `/players`       | Geeft alle spelers terug als JSON                   |
| GET     | `/players/{id}`  | Geeft één specifieke speler terug (404 als die niet bestaat) |
| GET     | `/leaderboard`   | Geeft spelers terug gesorteerd van hoogste naar laagste score |

## Testen via Swagger UI

FastAPI genereert automatisch een interactieve testomgeving. Start de
server en ga naar:

```
http://127.0.0.1:8000/docs
```

Daar kun je:
1. Elk endpoint openklappen.
2. Op "Try it out" klikken.
3. (Eventueel) parameters invullen, zoals een speler-ID.
4. Op "Execute" klikken om de echte response en statuscode te zien.

Test in elk geval:
- `/players` → moet een lijst met alle spelers teruggeven (200 OK).
- `/players/1` → moet één bestaande speler teruggeven (200 OK).
- `/players/9999` → moet een 404-foutmelding teruggeven, omdat deze speler
  niet bestaat.
- `/leaderboard` → moet de spelers gesorteerd op score teruggeven, hoogste
  score eerst.

## Git: wijzigingen committen en pushen

Werk in kleine, duidelijke commits, bijvoorbeeld:

```bash
git add api.py requirements.txt
git commit -m "Basis FastAPI-app met test-endpoint toegevoegd"

git add api.py
git commit -m "GET /players endpoint toegevoegd"

git add api.py
git commit -m "GET /players/{id} endpoint met 404-afhandeling toegevoegd"

git add api.py
git commit -m "GET /leaderboard endpoint toegevoegd, gesorteerd op score"

git add README.md
git commit -m "README bijgewerkt met FastAPI-uitleg en instructies"

git push
```

Zorg dat je repository al bestaat en gekoppeld is (zie eventueel de
originele Sprint 1 `git init` / `git remote add origin ...`-stappen).

## Definition of done - checklist

- [ ] API bereikbaar via de browser (`http://127.0.0.1:8000`)
- [ ] `GET /players` geeft alle spelers als JSON terug
- [ ] `GET /players/{id}` geeft één specifieke speler terug
- [ ] Niet-bestaande speler geeft een passende foutresponse (404 Not Found)
- [ ] `GET /leaderboard` sorteert spelers correct van hoogste naar laagste
      score
- [ ] Minimaal drie zinvolle GET-endpoints aanwezig (`/players`,
      `/players/{id}`, `/leaderboard`)
- [ ] Endpoints te testen via Swagger UI (`/docs`)
- [ ] Wijzigingen staan met meerdere duidelijke commits op GitHub
