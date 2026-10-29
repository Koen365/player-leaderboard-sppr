# Player Leaderboard

Python-app voor spelers, scores en een ranglijst. Er is geen spel gekoppeld:
je voert de scores zelf in. De console en FastAPI gebruiken dezelfde SQLite-database.

De technische onderdelen van sprint 1 t/m 8 zijn uitgewerkt volgens het
[Trello-bord](https://trello.com/b/IEi2Nb14/sppr-fd-sd24). De controles door een
klasgenoot en het zelf kunnen uitleggen van de code blijven nog door jou te doen.

## Starten

Open deze projectmap in VS Code en voer in de terminal uit:

```powershell
python run.py
```

Python 3.10 of nieuwer is nodig; getest met Python 3.14. De starter maakt zo nodig
een eigen `.venv` en installeert pakketten. De eerste keer is internet nodig.

- [Swagger](http://127.0.0.1:8000/docs): API proberen.
- [ReDoc](http://127.0.0.1:8000/redoc): API-reference lezen.
- [Status](http://127.0.0.1:8000/): controleren of de server draait.

Stop met Ctrl+C. Is 8000 bezet, open de al draaiende app of gebruik
`python run.py --port 8001` en bezoek dan poort 8001.
Voor automatisch herladen tijdens programmeren: `python run.py --reload`.
Dubbelklikken op `Start-API.cmd` kan ook.

Het lokale consolemenu start je met `python main.py` of `Start-Console.cmd`.

## Eerste keer gebruiken

1. Maak in Swagger via **POST /auth/register** een account met een eigen
   wachtwoord van 10 tot 128 tekens.
2. Klik op **Authorize**, vul die accountnaam en dat wachtwoord in, laat
   client_id en client_secret leeg en sluit het venster.
3. Controleer **GET /auth/me**. Maak daarna een eigen speler via **POST /players**.

Lezen is openbaar. Voor toevoegen moet je inloggen; wijzigen en verwijderen
mag alleen bij je eigen spelers en hun scores. Het token verloopt na één uur.
Een account kan meerdere spelers beheren. Scores zijn gehele getallen vanaf 0.

De volledige oefening staat in **[De API gebruiken](docs/GEBRUIKEN.md)**.
Daarin staan ook voorbeelden, verwachte antwoorden en uitleg van foutmeldingen.

## Oude spelers en gegevens

`players.db` naast de code bevat de actuele gegevens. `players.json` is alleen
een eenmalige importbron; verwijderde spelers komen niet bij elke start terug.
De laatst toegevoegde score is actueel; de geschiedenis blijft bewaard.
Identieke PUT-verzoeken maken geen dubbele scoregeschiedenis.

Oude spelers hebben nog geen eigenaar. Registreer eerst een eigen account en
koppel ze lokaal (vervang MijnAccount door je accountnaam):

```powershell
python assign_owner.py --user MijnAccount --all-unowned
```

Voor één speler: `python assign_owner.py --user MijnAccount --player-id 1`.
Dit neemt geen speler van een ander account over. Het consolemenu is lokaal
beheer en maakt spelers zonder eigenaar aan; die kun je op dezelfde manier koppelen.

De database staat los van Git. Voor een back-up stop je console en API en kopieer
je het databasebestand. De oefenhandleiding gebruikt een aparte database via
`PLAYER_DATABASE`, zodat je zelf kunt testen met eigen oefengegevens.

## Tests uitvoeren

Installeer de testpakketten eenmaal en voer daarna alle tests achter elkaar uit:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Op Linux/macOS gebruik je `.venv/bin/python`. De tests maken tijdelijke databases
en veranderen de eigen spelers niet. Resultaten, gevonden fouten en de keuze
van tests staan in **[TESTVERSLAG.md](TESTVERSLAG.md)**.

## Documentatie en bestanden

Voor een code-review kun je deze volgorde aanhouden:

1. `api.py`: start de API en koppelt de routes.
2. `routers/players.py`: ontvangt een verzoek en controleert wie iets mag wijzigen.
3. `schemas.py`: bepaalt welke invoer en antwoorden zijn toegestaan.
4. `service.py`: voert de acties op spelers en scores uit.
5. `models.py` en `database.py`: beschrijven de tabellen en regelen de opslag.
6. `routers/auth.py`, `auth_service.py` en `security.py`: regelen inloggen en tokens.
7. `tests/`: laat zien welk gedrag automatisch wordt gecontroleerd.

Een voorbeeld om te volgen is **POST /players**: FastAPI controleert de invoer
met `PlayerCreate` en haalt via `CurrentUser` de ingelogde gebruiker op.
De route roept `service.create_player` aan, die de speler met een eigenaar
opslaat. `PlayerRead` bepaalt welke velden in het antwoord terugkomen.

Beide reviewers vullen afzonderlijk [het reviewformulier](docs/KLASGENOOT.md)
in. Bekijk naast de code ook het gedrag in Swagger.

| Bestand | Waarvoor? |
|---|---|
| [docs/GEBRUIKEN.md](docs/GEBRUIKEN.md) | Zelfstandig registreren, inloggen en CRUD proberen |
| [API_CONTRACT.md](API_CONTRACT.md) | Endpoints, velden, rechten, statuscodes en voorbeelden |
| [openapi.json](openapi.json) | Machineleesbaar contract, ook te importeren in API-tools |
| [docs/KLASGENOOT.md](docs/KLASGENOOT.md) | Echte gebruiks- en foutcontrole laten vastleggen |
| [ONTWERP.md](ONTWERP.md) | Keuzes voor structuur, database en beveiliging |
| `api.py`, `routers/` | App en HTTP-routes |
| `service.py`, `auth_service.py` | Spelers-, score- en accountlogica |
| `models.py`, `database.py` | Tabellen, relaties, opslag en migratie |
| `schemas.py`, `responses.py` | Invoercontrole en API-contract |
| `errors.py` | JSON-foutafhandeling |
| `security.py`, `dependencies.py` | Hashes, toegangstokens en huidige gebruiker |
| `main.py` | Consolemenu |

Na een wijziging aan de API kun je `python export_openapi.py` uitvoeren.
Met `python export_openapi.py --check` controleer je of de export nog klopt.
De automatische contracttest controleert dat ook.
