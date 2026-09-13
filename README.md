# Game Score Manager — SPPR SD24

Python-consoleapp en FastAPI REST API voor spelers, scores en een leaderboard.
Uitgewerkt volgens sprint 1 t/m 4 van het [Trello-bord](https://trello.com/b/IEi2Nb14/sppr-fd-sd24).
De API en het consolemenu delen een SQLite-database via SQLAlchemy.

## Starten

Vereist: Python 3.10 of nieuwer; getest op Windows met Python 3.14.
Open een terminal in deze projectmap en voer uit:

```powershell
python run.py
```

De starter gebruikt een eigen `.venv`, installeert ontbrekende pakketten en start op:

- API: http://127.0.0.1:8000
- Interactieve Swagger-documentatie: http://127.0.0.1:8000/docs
- Leaderboard als JSON: http://127.0.0.1:8000/leaderboard

Afsluiten met Ctrl+C. Voor automatisch herladen: `python run.py --reload`.
Is poort 8000 bezet, gebruik dan `python run.py --port 8001`.
Je kunt ook dubbelklikken op `Start-API.cmd`.

Voor het consolemenu, na installatie van de dependencies:

```powershell
.\.venv\Scripts\python.exe main.py
```

Handmatige installatie, bijvoorbeeld na het klonen van GitHub:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Op Linux/macOS is de interpreter `.venv/bin/python`.

## Wat kun je ermee?

- Spelers toevoegen, bekijken, op id opvragen, hernoemen en verwijderen.
- In het consolemenu ook zoeken op username.
- Scores toevoegen, bekijken, corrigeren en verwijderen.
- Een leaderboard bekijken, van hoogste naar laagste actuele score.
- Gegevens behouden na afsluiten en opnieuw starten.

De **laatst toegevoegde score** is de actuele score van een speler. Een nieuwe
score vervangt de actuele waarde, maar bewaart de eerdere registraties.
Een score van 100 gevolgd door 40 geeft dus 40 op het leaderboard. Dit behoudt
het gedrag van 'score aanpassen' uit sprint 1. Zonder registraties is de score 0.
Bij gelijke scores sorteert het leaderboard op speler-id.

## Endpoints

| Methode | Endpoint | Actie | Succes |
|---|---|---|---|
| GET | `/` | Status van de API | 200 |
| GET | `/players` | Alle spelers | 200 |
| POST | `/players` | Nieuwe speler | 201 |
| GET | `/players/{player_id}` | Eén speler | 200 |
| PUT | `/players/{player_id}` | Naam én actuele score vervangen | 200 |
| PATCH | `/players/{player_id}` | Meegegeven velden wijzigen | 200 |
| DELETE | `/players/{player_id}` | Speler inclusief scores verwijderen | 204 |
| GET | `/leaderboard` | Gesorteerde spelers | 200 |
| GET | `/players/{player_id}/scores` | Scoregeschiedenis van een speler | 200 |
| POST | `/players/{player_id}/scores` | Nieuwe scoreregistratie | 201 |
| GET | `/scores` | Alle scoreregistraties | 200 |
| GET | `/scores/{score_id}` | Eén scoreregistratie | 200 |
| PATCH | `/scores/{score_id}` | Scoreregistratie corrigeren | 200 |
| DELETE | `/scores/{score_id}` | Scoreregistratie verwijderen | 204 |

Een Player-response bevat `id`, `username`, `score`. Een Score-response bevat
`id`, `player_id`, `score`. De score-id en speler-id zijn verschillende sleutels.
POST geeft een `Location`-header met het pad naar het aangemaakte record.

Validatie: namen worden getrimd, zijn 1–50 tekens en zijn uniek zonder
hoofdletterverschil. Scores zijn gehele getallen van 0 t/m 2147483647;
booleans, strings, kommagetallen, null en onbekende velden worden geweigerd.
PATCH laat ontbrekende velden met rust; PUT verwacht zowel username als score.

| Foutcode | Betekenis |
|---|---|
| 400 | Lege PATCH: geen velden om te wijzigen |
| 404 | Speler of score bestaat niet |
| 409 | Username bestaat al |
| 422 | Ongeldige invoer, ontbrekend verplicht veld of ongeldig id |

## Proberen met Swagger

Open `/docs`, klap een endpoint open, klik **Try it out**, vul de gegevens in en
klik **Execute**. Onder **Server response** staat de echte statuscode en JSON.

1. POST `/players` met `{"username":"MijnSpeler","score":100}`. Onthoud het teruggegeven id.
2. GET `/players` en GET `/players/{player_id}` met dat id.
3. PATCH de speler met `{"score":150}`. De username blijft gelijk.
4. PUT de speler met `{"username":"NieuweNaam","score":200}`.
5. POST `/players/{player_id}/scores` met `{"score":300}`. Onthoud de score-id.
6. GET de scoregeschiedenis, `/scores`, één score en `/leaderboard`.
7. PATCH `/scores/{score_id}` met `{"score":250}` om een registratie te corrigeren.
8. Stop en herstart de API. Vraag dezelfde speler opnieuw op: die staat er nog.
9. DELETE de testscore, daarna de testspeler. Beide antwoorden met 204 zonder body.
10. GET de verwijderde speler: 404. Probeer een negatieve score: 422. Probeer een
    bestaande naam met andere hoofdletters: 409.

Gebruik hiervoor een eigen testspeler. De wijzigingsendpoints passen de database echt aan.

## Bestanden en database

| Bestand | Verantwoordelijkheid |
|---|---|
| `main.py` | Consolemenu, invoer en foutmeldingen |
| `api.py` | HTTP-endpoints, statuscodes, Swagger en sessie per request |
| `schemas.py` | Pydantic-modellen voor invoer en uitvoer |
| `models.py` | SQLAlchemy-classes Player en Score met hun relatie |
| `service.py` | CRUD-logica die console en API delen |
| `database.py` | SQLite-verbinding, tabellen en JSON-import |
| `players.json` | Bestaande spelers als eenmalige importbron |
| `players.db` | Actuele gegevens; lokaal en genegeerd door Git |
| `ONTWERP.md` | Endpointkeuzes en databaseontwerp |
| `tests/test_api.py` | Automatische functionele tests |
| `TESTVERSLAG.md` | Uitgevoerde controles en koppeling aan de sprints |

Bij de eerste start worden de vier bestaande spelers geïmporteerd, inclusief
hun ids en scores. Het JSON-bestand blijft ongewijzigd. Daarna wordt uitsluitend
de database gebruikt; latere JSON-wijzigingen worden niet opnieuw geïmporteerd.
Ook na het verwijderen van alle spelers vindt geen herimport plaats.
Een ongeldig importbestand stopt de import zonder gedeeltelijke records op te slaan.

De standaarddatabase staat altijd naast de code, onafhankelijk van de werkmap.
Voor een aparte oefendatabase kun je vóór het starten instellen:

```powershell
$env:PLAYER_DATABASE = "$env:TEMP\player-oefenen.db"
python run.py --port 8001
```

Voor een back-up: stop console en API en kopieer `players.db` naar een veilige map.

## Uitleg voor de sprints

Een **client** (Swagger, een game of een andere applicatie) stuurt een HTTP-request
naar de **server** (FastAPI). De server antwoordt met een statuscode en meestal JSON.
REST organiseert endpoints rond resources: hier players en scores. CRUD staat voor
Create (POST), Read (GET), Update (PUT/PATCH) en Delete (DELETE).

Een request body is de JSON die je meestuurt. **Pydantic** zet deze om naar een
Python-object en controleert de velden. **SQLAlchemy** is de ORM: die koppelt
Python-objecten aan relationele tabellen en voert de bijbehorende SQL uit.
Een Pydantic-model controleert de API-invoer; een SQLAlchemy-model beschrijft de opslag.

Bij POST `/players` gebeurt achtereenvolgens:

1. FastAPI ontvangt de HTTP-request.
2. Pydantic valideert username en score.
3. `service.create_player` maakt een Player en een bijbehorende Score.
4. SQLAlchemy maakt met INSERT de records aan.
5. `session.commit()` slaat de transactie definitief op in SQLite.
6. De API antwoordt met status 201 en een PlayerRead als JSON.

Een **primary key** is de unieke id van een record. De **foreign key**
`scores.player_id` verwijst naar `players.id`: één speler kan meerdere scores hebben.
Een SQLite-bestand blijft op schijf bestaan na het stoppen van Python; een gewone
Python-list in het geheugen niet. SELECT leest, INSERT voegt toe, UPDATE wijzigt,
DELETE verwijdert. SQLAlchemy maakt deze statements voor de CRUD-functies.

Lees de code en oefen deze uitleg zelf voor de beoordeling; werkende software
bewijst niet automatisch dat je de leerdoelen kunt uitleggen.

Bronnen: [FastAPI body updates](https://fastapi.tiangolo.com/tutorial/body-updates/),
[SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/quickstart.html),
[SQLite-koppeling](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html).

## Tests en Git

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Tests gebruiken tijdelijke databases en veranderen je eigen spelers niet.
Zie `TESTVERSLAG.md` voor de resultaten.

```powershell
git status
git log --oneline
git add .
git commit -m "Beschrijf je wijziging"
git push
```

De oorspronkelijke code staat in de eerste commit. De uitwerking, het ontwerp en
de verificatie staan in afzonderlijke commits. `.venv`, databases en caches
worden niet naar GitHub gestuurd.
