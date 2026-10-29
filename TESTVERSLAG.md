# Testverslag — 29 oktober 2026

## Sprint 7 en 8: resultaat

**89 automatische tests geslaagd** op Windows met Python 3.14.
Uitgevoerd met `.venv\Scripts\python.exe -m pytest -q`.
De eerdere 71 tests bleven slagen. Er zijn 16 fout- en regressiecontroles en
2 contractcontroles toegevoegd. De contractflow controleert meerdere aanvragen.
De twee bestaande deprecation-waarschuwingen uit Starlette/AnyIO blijven zichtbaar;
ze zijn niet onderdrukt en veroorzaken geen testfout.

## Gevonden problemen en regressietests

De drie onderstaande tests zijn eerst op de oude code uitgevoerd: alle drie
faalden. Na de reparatie slaagden ze. Dit waren eigen technische controles,
geen controle door een klasgenoot.

| Probleem | Voor reparatie | Na reparatie | Test in tests/test_errors.py |
|---|---|---|---|
| Naam met NUL-teken | Onverwerkte databasefout, 500 | 422, niets opgeslagen; volgende aanvraag werkt | test_null_character_in_name_returns_422 |
| Wachtwoord met ongeldig Unicode-teken | Hashfunctie gaf een serverfout, 500 | 422, wachtwoord niet teruggestuurd | test_invalid_unicode_password_returns_422 |
| Twee identieke PUTs | Scorehistorie werd 10,20,20 | Historie blijft 10,20; expliciete POST mag wel herhalen | test_repeated_put_does_not_duplicate_score_history |

De naamcontrole weigert besturingstekens. Gewone Unicode-namen blijven toegestaan.
Wachtwoorden worden op geldige UTF-8 controleerbaarheid getest voordat ze gehasht
worden. De service voegt bij PUT/PATCH alleen een score toe als die verandert of
als er nog geen score is.

## Wat is getest en waarom?

- **CRUD, opslag en scoregeschiedenis:** de kern van de app moet blijven werken.
- **Authentication en eigenaarschap:** een verkeerde gebruiker mag geen data wijzigen.
- **Verkeerde bodies en JSON:** een API-client kan andere invoer sturen dan Swagger.
- **404 en 405:** verkeerde ids, routes en methoden moeten duidelijke fouten geven.
- **Databasefout:** een nagebootste mislukte commit geeft 503 met Retry-After; de
  sessie wordt gesloten zonder halve speler op te slaan. De volgende aanvraag werkt.
- **Onverwachte fout:** een nagebootste interne fout geeft generieke JSON met 500;
  de response bevat geen stacktrace, SQL, pad of wachtwoord. Daarna werkt de API weer.
- **Unicode en SQL-achtige tekst:** geldige namen blijven data en worden niet als SQL uitgevoerd.
- **Idempotente PUT:** opnieuw versturen mag geen onbedoelde scoreregistratie maken.
- **OpenAPI-contract:** alle 18 operaties, successtatuscodes en loginplichten kloppen.
- **Gedocumenteerde voorbeelden:** registratie, login, CRUD, rechten, foutgevallen en
  logout zijn uitgevoerd; echte responses zijn met jsonschema tegen OpenAPI gevalideerd.
- **Contractexport:** openapi.json komt exact overeen met de huidige API.

De databasefout en onverwachte fout zijn doelbewust nagebootst met pytest monkeypatch.
Dat test de foutafhandeling; het bewijst niet dat elk mogelijk schijf- of netwerkprobleem
is nagebootst. Alle schrijftests gebruiken tijdelijke databases, niet players.db.

## Zelf uitvoeren

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
python export_openapi.py --check
```

Eén regressietest bekijken:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_errors.py -k repeated_put -v
```

## Controle door een andere student

Nog niet uitgevoerd. Laat een klasgenoot zonder mondelinge hulp de handleiding
in docs/GEBRUIKEN.md doorlopen en proberen de API met foutieve requests te breken.
Laat echte bevindingen invullen in docs/KLASGENOOT.md. Los relevante nieuw gevonden
problemen op en voeg daar een regressietest voor toe. Dit onderdeel en het zelf
kunnen uitleggen van het werk zijn nog nodig voor de volledige Trello-afronding.

## Bronnen en hulpmiddelen

- [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html):
  fouten gecontroleerd nabootsen en de wijziging na de test herstellen.
- [FastAPI-foutafhandeling](https://fastapi.tiangolo.com/tutorial/handling-errors/):
  validatiefouten en eigen foutresponses afhandelen.
- [FastAPI response-documentatie](https://fastapi.tiangolo.com/advanced/additional-responses/):
  modellen en statuscodes in OpenAPI beschrijven.
- pytest en FastAPI TestClient voeren aanvragen uit zonder een echte serverpoort.
- jsonschema controleert responses aan de hand van het publieke schema.
- AI is gebruikt bij analyse, implementatie, testgevallen en documentatie. De maker
  moet de werking en gemaakte keuzes zelf kunnen toelichten.

---

## Eerdere controles tot en met sprint 6

### Controle van 8 oktober 2026

## Resultaat

**71 automatische tests geslaagd** op Windows met Python 3.14.
Uitgevoerd met `.venv\Scripts\python.exe -m pytest -q`.
Twee deprecation-waarschuwingen komen uit de testdependencies Starlette/AnyIO;
er zijn geen falende tests.

## Sprint 5 en 6

De oorspronkelijke 45 tests slaagden vóór én na het verplaatsen van de endpoints
naar APIRouters. Vervolgens zijn de wijzigingstests met een ingelogde eigenaar
uitgevoerd en is de suite uitgebreid met controles op accounts en rechten.

- Registratie, login via formulier, huidig account en logout.
- Argon2id-hashes in de database; wachtwoorden en hashes ontbreken in accountresponses.
- Invoerfouten sturen de ingevoerde wachtwoorden niet terug.
- Dubbele accountnamen worden zonder hoofdletterverschil geweigerd (409).
- Verkeerde login, ontbrekende/ongeldige/verlopen tokens en verwijderde accounts: 401.
- Alle zeven wijzigingsroutes weigeren een niet-ingelogde gebruiker (401).
- Alle zes wijzigingen aan bestaande spelers/scores weigeren een andere eigenaar (403).
- Geweigerde wijzigingen laten spelers en scoregeschiedenis ongemoeid.
- Een client kan geen owner_id invullen of wijzigen.
- In de database staat alleen een hash van het toegangstoken.
- Sessies verlopen na één uur; logout trekt alleen het gebruikte token in.
- Sessies en ingetrokken tokens worden ook na een nieuwe appstart juist behandeld.
- Een database uit sprint 4 krijgt owner_id zonder verlies van spelers of scores.
- Herhaalde upgrade is veilig; de eerste registrant krijgt geen oude spelers cadeau.
- Het lokale koppelcommando werkt vanuit een andere werkmap en weigert overname
  van een speler met een andere eigenaar.
- De bestaande console, CRUD, scoregeschiedenis, cascades en JSON-import blijven werken.

`pip check` meldt geen conflicterende afhankelijkheden.

### Controle in de browser

Uitgevoerd in Swagger tegen een aparte oefendatabase op poort 8768:

1. POST /auth/register gaf 201 met alleen het account-id en de naam.
2. Authorize accepteerde de gekozen testlogin en toonde **Authorized**.
3. GET /auth/me gaf 200 met het juiste account; Swagger stuurde de autorisatie mee.

De browsercontrole en tests gebruiken aparte databases, niet de eigen spelers.
Vóór de upgrade is een back-up van de bestaande code en database gemaakt.

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

## Eerdere Swagger-controle (13 september 2026)

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
| 5 — Structuur | APIRouters, gedeelde dependencies, service layer, analyse en uitleg van de indeling |
| 6 — Authentication & Authorization | Accounts, Argon2id, sessies, beschermde endpoints, eigenaarschap en 401/403 |

Ontwerp en uitleg staan in ONTWERP.md en README.md. De Git-geschiedenis bewaart de
beginsituatie en de afzonderlijke wijzigingen. De Trello-kaarten zijn niet aangepast;
de openbare bordweergave geeft alleen leestoegang. De leerdoelen over het zelfstandig
kunnen uitleggen van de code moeten door de student zelf worden doorgenomen.
Voor sprint 5 moet daarnaast nog echte feedback met een klasgenoot worden
uitgewisseld. Dat onderdeel is niet als voltooid aangemerkt.
