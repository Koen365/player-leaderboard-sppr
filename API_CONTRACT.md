# API-contract

Contractversie **3.1.0**. Standaardadres: `http://127.0.0.1:8000`.
Het poortnummer kan met `python run.py --port 8001` worden veranderd.
Deze API beheert spelers en voorbeeldscores; er is geen spel aangesloten.

- Interactief testen: `/docs` (Swagger).
- Leesbare API-reference: `/redoc`.
- Actueel machineleesbaar contract: `/openapi.json`.
- Meegelverde versie: [openapi.json](openapi.json).
- Uitgeschreven oefening: [De API gebruiken](docs/GEBRUIKEN.md).

## Verzoeken en antwoorden

Stuur JSON met `Content-Type: application/json`, behalve bij `/auth/login`:
dat endpoint verwacht `application/x-www-form-urlencoded`. Antwoorden zijn JSON,
behalve **204**, dat een lege body heeft. GET-lijsten zijn arrays, ook als ze leeg zijn.
Er zijn geen paginering of zoekfilters; lijsten bevatten alle records.

Alle pad-ids zijn gehele getallen van 1 t/m 9223372036854775807. Een ongeldig id
geeft 422; een geldig maar onbekend id 404. Bewaar bij grote ids de gehele waarde:
JavaScript-getallen zijn boven 9007199254740991 niet altijd exact.

| Methode | Pad | Invoer | Uitvoer | Succes | Toegang |
|---|---|---|---|---|---|
| GET | `/` | Geen | Status | 200 | Openbaar |
| POST | `/auth/register` | UserCreate, JSON | User | 201 | Openbaar |
| POST | `/auth/login` | username + password, formulier | Token | 200 | Openbaar |
| GET | `/auth/me` | Bearer-token | User | 200 | Ingelogd |
| POST | `/auth/logout` | Bearer-token | Leeg | 204 | Ingelogd |
| GET | `/players` | Geen | Player[] | 200 | Openbaar |
| POST | `/players` | PlayerCreate | Player | 201 | Ingelogd |
| GET | `/players/{player_id}` | player_id | Player | 200 | Openbaar |
| PUT | `/players/{player_id}` | player_id + PlayerReplace | Player | 200 | Eigenaar |
| PATCH | `/players/{player_id}` | player_id + PlayerPatch | Player | 200 | Eigenaar |
| DELETE | `/players/{player_id}` | player_id | Leeg | 204 | Eigenaar |
| GET | `/players/{player_id}/scores` | player_id | Score[] | 200 | Openbaar |
| POST | `/players/{player_id}/scores` | player_id + ScoreCreate | Score | 201 | Eigenaar |
| GET | `/scores` | Geen | Score[] | 200 | Openbaar |
| GET | `/scores/{score_id}` | score_id | Score | 200 | Openbaar |
| PATCH | `/scores/{score_id}` | score_id + ScoreCreate | Score | 200 | Eigenaar |
| DELETE | `/scores/{score_id}` | score_id | Leeg | 204 | Eigenaar |
| GET | `/leaderboard` | Geen | Player[] | 200 | Openbaar |

## Modellen

| Model | Velden |
|---|---|
| UserCreate | username verplicht; password verplicht, 10–128 tekens |
| User | id, username; geen password of password_hash |
| Token | access_token, token_type = bearer, expires_in = 3600 seconden |
| PlayerCreate | username verplicht; score optioneel, standaard 0 |
| PlayerReplace | username én score verplicht |
| PlayerPatch | username en/of score; minstens één veld, geen null |
| Player | id, username, score |
| ScoreCreate | score verplicht |
| Score | id, player_id, score |
| Status | status = ok, message |

Namen worden getrimd en zijn daarna 1–50 tekens. Ze mogen geen besturingstekens
zoals NUL of een regelafbreking bevatten. Unicode-namen zoals Zoë mogen wel.
Accountnamen en spelernamen zijn ieder binnen hun eigen lijst uniek zonder
hoofdletterverschil. Een accountnaam en spelernaam mogen gelijk zijn.

Een score is een geheel JSON-getal van 0 t/m 2147483647. Tekst zoals `"100"`,
booleans, kommagetallen en null zijn ongeldig. Onbekende invoervelden zijn niet
toegestaan. `id`, `owner_id` en `player_id` zijn geen vrij invulbare bodyvelden.

Voorbeeld speler toevoegen:

```json
{"username":"Nova","score":100}
```

Voorbeeld antwoord (ids zijn voorbeelden, gebruik de werkelijk teruggegeven ids):

```json
{"id":5,"username":"Nova","score":100}
```

Voorbeeld nieuwe score en antwoord:

```json
{"score":300}
```

```json
{"id":9,"player_id":5,"score":300}
```

POST voor een speler of score geeft bovendien een **Location**-header met het
relatieve pad naar dat record. Registratie geeft geen Location-header.

## Inloggen en rechten

Registreer met JSON bij `/auth/register`. Log in via de Authorize-knop in Swagger
of stuur de formuliervelden `username` en `password` naar `/auth/login`.
client_id en client_secret zijn niet nodig. Een loginresponse bevat een opaque
toegangstoken (geen JWT). Gebruik het in volgende verzoeken:

```http
Authorization: Bearer <jouw-access_token>
```

Het token is één uur geldig. Loginresponses hebben `Cache-Control: no-store`
en `Pragma: no-cache`. Logout trekt alleen het gebruikte token in. Andere sessies
blijven geldig. De Authorize-knop kan een token lokaal vergeten; alleen
POST /auth/logout trekt het ook op de server in.

De API koppelt nieuwe spelers aan de ingelogde gebruiker. Voor een wijziging
wordt eerst de login gecontroleerd en daarna de eigenaar van de speler. Een
score hoort bij dezelfde eigenaar als zijn speler. Oude spelers zonder eigenaar
blijven leesbaar, maar kunnen via de API pas na lokaal koppelen worden gewijzigd.
Zie de README voor `assign_owner.py`. Het consolemenu is vertrouwd lokaal beheer.

## Betekenis van scores en updates

De laatst toegevoegde score (hoogste score-id) is actueel, niet de hoogste waarde.
Zonder scores is de actuele score 0. Het leaderboard sorteert aflopend op actuele
score en bij gelijkstand oplopend op speler-id. Overige lijsten zijn op id gesorteerd.

PUT geeft naam en score samen op; PATCH wijzigt alleen aanwezige velden. Een
gewijzigde score maakt een registratie. Een herhaling met dezelfde actuele score
maakt geen extra registratie. Als alle scores verwijderd zijn, maakt het instellen
van 0 wel een nieuwe registratie; daarna is dezelfde PUT opnieuw zonder extra effect.
POST /players/{player_id}/scores maakt altijd een nieuwe registratie, ook als
de waarde gelijk is. PATCH /scores/{score_id} corrigeert één bestaande registratie.
Na verwijderen van de actuele score wordt de vorige registratie actueel.
Een speler verwijderen verwijdert diens hele scoregeschiedenis.

## Fouten

| Code | Betekenis en vervolgactie |
|---|---|
| 400 | Bijvoorbeeld een lege PATCH; stuur een wijziging mee |
| 401 | Login ontbreekt, is verkeerd of verlopen; opnieuw inloggen |
| 403 | Je bent geen eigenaar; controleer het account en speler-id |
| 404 | Route, speler of score bestaat niet; controleer het pad en id |
| 405 | Verkeerde HTTP-methode; de Allow-header noemt toegestane methoden |
| 409 | Account- of spelernaam bestaat al; kies een andere naam |
| 422 | Ongeldige invoer of ongeldige JSON; herstel het aangegeven veld |
| 500 | Onverwachte interne fout; meld de gebruikte actie aan de beheerder |
| 503 | Database tijdelijk niet beschikbaar; Retry-After: 1, probeer later opnieuw |

Een fout bevat normaal één tekst:

```json
{"detail":"Je mag alleen je eigen spelers en scores wijzigen."}
```

Validatiefouten hebben een lijst, bijvoorbeeld bij een negatieve score:

```json
{"detail":[{"loc":["body","score"],"msg":"Input should be greater than or equal to 0","type":"greater_than_equal"}]}
```

`loc` beschrijft waar het fout gaat, `msg` geeft uitleg en `type` benoemt het soort
validatiefout. De API stuurt geen ruwe invoer of wachtwoorden terug in deze fout.
Clients moeten de statuscode en velden gebruiken, niet een exacte foutzin vergelijken.
Een 401 heeft `WWW-Authenticate: Bearer`. Interne fouten geven geen SQL, paden of
stacktrace terug. Bij een onzeker netwerkresultaat eerst GET gebruiken om te
controleren of een POST is uitgevoerd; POST is niet gegarandeerd idempotent.

## Contract bijwerken

Na een bewuste wijziging aan routes of schemas:

```powershell
python export_openapi.py
python export_openapi.py --check
.\.venv\Scripts\python.exe -m pytest -q
```

Commit code en contract samen. De contracttest vergelijkt de meegeleverde export
met de API en valideert echte antwoorden tegen het schema. Een contractwijziging
is pas klaar wanneer voorbeelden, handleiding en tests daarbij passen.
