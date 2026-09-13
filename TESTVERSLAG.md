# Testverslag — 13 september 2026

## Resultaat

**45 automatische tests geslaagd** op Windows met Python 3.14.
Uitgevoerd met `.venv\Scripts\python.exe -m pytest -q`.
Twee deprecation-waarschuwingen komen uit de testdependencies Starlette/AnyIO;
er zijn geen falende tests.

## Automatische controles

- Spelers aanmaken, lezen, volledig vervangen, gedeeltelijk wijzigen en verwijderen.
- GET-responses behouden de velden id, username en score uit sprint 2.
- Leaderboard sorteert aflopend; gelijke scores worden op speler-id gesorteerd.
- Scores toevoegen, geschiedenis lezen, registraties corrigeren en verwijderen.
- Verlaging van de actuele score en terugvallen op de vorige score na verwijderen.
- Verwijderen van een speler verwijdert alle gekoppelde scores.
- Ontbrekende resources geven 404; lege PATCH geeft 400; dubbele namen geven 409.
- Lege/lange namen, null, onbekende velden, negatieve/niet-gehele scores en
  ongeldige/grote ids geven 422.
- Een mislukte naamswijziging met scorewijziging laat geen gedeeltelijke update achter.
- SQLite bewaakt foreign keys, scorebeperkingen en cascadeverwijdering.
- JSON wordt eenmaal geïmporteerd; verwijderen en herstarten maakt geen spelers opnieuw aan.
- Een ongeldige import wordt volledig teruggedraaid en kan na correctie opnieuw worden gestart.
- Consolemenu getest vanuit een andere werkmap, inclusief ongeldige invoer en opslag.
- OpenAPI-schema en Swagger-pagina zijn beschikbaar.

## Uitgevoerd via Swagger in de browser

Alle **14 API-operaties** uitgevoerd tegen een aparte oefendatabase op poort 8765:

| Operatie | Uitkomst |
|---|---|
| GET / | 200, status ok |
| GET /players | 200, JSON-lijst |
| POST /players | 201, testspeler en Location-header |
| GET /players/{player_id} | 200, juiste testspeler |
| PUT /players/{player_id} | 200, naam en score vervangen |
| PATCH /players/{player_id} | 200, score gewijzigd, naam behouden |
| DELETE /players/{player_id} | 204, lege body |
| GET /leaderboard | 200, aflopend gesorteerd |
| GET /players/{player_id}/scores | 200, scoregeschiedenis |
| POST /players/{player_id}/scores | 201, score aan juiste speler gekoppeld |
| GET /scores | 200, alle registraties |
| GET /scores/{score_id} | 200, juiste registratie |
| PATCH /scores/{score_id} | 200, score gecorrigeerd |
| DELETE /scores/{score_id} | 204, lege body |

De eigen spelersdata is bij deze tests niet veranderd.

## Volledige serverherstart

Naast de automatische test met nieuwe app-instanties is het serverproces echt
opgestart, gestopt en opnieuw gestart op poort 8766 met een tijdelijke database.
Er is gecontroleerd dat de poort gesloten was voordat de tweede server startte.
Een nieuwe speler met score 321 kreeg een tweede score van 654. Na de herstart
waren de speler, actuele score 654 en beide scoreregistraties nog aanwezig.
Ook starten vanuit een andere werkmap werkt.

## Koppeling aan Trello

| Sprint | Opgeleverde functionaliteit |
|---|---|
| 1 — Basis Python | Consolemenu, spelersbeheer, zoeken, score aanpassen, leaderboard, foutafhandeling, eigen Player/Score-classes |
| 2 — FastAPI + HTTP | GET-endpoints, JSON, path parameters, 404, Swagger |
| 3 — REST API & CRUD | GET/POST/PUT/PATCH/DELETE, Pydantic, scores, validatie, HTTP-statuscodes |
| 4 — Database | SQLite, SQLAlchemy-modellen, één-op-veelrelatie, permanente CRUD en herstartcontrole |

Ontwerp en uitleg staan in ONTWERP.md en README.md. De Git-geschiedenis bewaart de
beginsituatie en de afzonderlijke wijzigingen. De Trello-kaarten zijn niet aangepast;
de openbare bordweergave geeft alleen leestoegang. De leerdoelen over het zelfstandig
kunnen uitleggen van de code moeten door de student zelf worden doorgenomen.
