# De API gebruiken

Deze app beheert spelers, scores en een ranglijst. Er is geen spel aangesloten:
je voert scores zelf in. Een account is je login; een speler is een record dat
je met die login beheert. Eén account kan meerdere spelers hebben.

## 1. Start een eigen oefenomgeving

Gebruik Python 3.10 of nieuwer en de volledige projectmap. Heb je de private
GitHub-repository niet, vraag dan toegang of gebruik een aangeleverde projectkopie.
Open de map waarin `run.py` staat in VS Code. Open **Terminal > New Terminal**.
Onderstaande opdrachten horen bij een PowerShell-prompt, niet bij Python (`>>>`).

```powershell
$env:PLAYER_DATABASE = "$env:TEMP\player-oefenen.db"
python run.py --port 8001
```

De eerste start installeert de benodigde pakketten en heeft internet nodig.
Open http://127.0.0.1:8001/docs. Houd de terminal open. Poort 8001 wordt gebruikt
zodat een al draaiende app op 8000 kan blijven draaien. Is ook 8001 bezet, kies
een vrije poort met `--port` en gebruik hetzelfde nummer in je browser.

De oefendatabase is een apart bestand. Gebruik hieronder alleen zelf aangemaakte
testspelers. Er kunnen al voorbeeldspelers in de lijst staan; die zijn niet van
jouw account. Bij herhaald oefenen blijven eerder gemaakte accounts bestaan.

Elke actie werkt hetzelfde: klap het endpoint open, klik **Try it out**, vul de
gegevens in en klik **Execute**. Kijk naar **Server response**, niet naar de
voorbeelden onder **Responses**. Die voorbeelden zijn geen uitgevoerde aanvraag.

## 2. Registreer een account

Gebruik **POST /auth/register** met bijvoorbeeld:

```json
{"username": "MijnAccount", "password": "Kies-een-eigen-wachtwoord"}
```

Vervang het voorbeeldwachtwoord door een eigen wachtwoord van 10 tot 128 tekens.
Een antwoord met **201** bevat je account-id en naam, nooit je wachtwoord.
Bij **409** bestaat die naam al: gebruik je eerdere login of kies een andere naam.

## 3. Log in

Klik bovenaan **Authorize**. Vul dezelfde accountnaam en hetzelfde wachtwoord
in; laat client_id en client_secret leeg. Klik **Authorize**, daarna **Close**.

Voer **GET /auth/me** uit. Bij **200** zie je je eigen accountnaam. Swagger
stuurt nu het Bearer-token automatisch mee. Na een uur moet je opnieuw inloggen.
De login via **POST /auth/login** gebruikt formuliervelden, geen JSON-body.

## 4. Vraag gegevens op en voeg een speler toe

Voer **GET /players** uit om de bestaande spelers te zien. Dit werkt ook zonder login.
Maak daarna je eigen testspeler met **POST /players**:

```json
{"username": "Nova", "score": 100}
```

Bij **201** krijg je bijvoorbeeld `{"id":5,"username":"Nova","score":100}`.
Jouw id kan anders zijn. Noteer het teruggegeven **speler-id**; gebruik hieronder
dat nummer bij `player_id`. Bij **409** kies je een nieuwe spelernaam.

Voer **GET /players/{player_id}** uit. De naam en score moeten overeenkomen.
De responseheader **Location** geeft het pad naar je nieuwe speler.

## 5. Wijzig je speler

Gebruik **PATCH /players/{player_id}** met:

```json
{"score": 150}
```

Bij **200** is de score 150 en is de naam behouden. PATCH verandert alleen de
meegegeven velden. Gebruik **PUT /players/{player_id}** om naam én score op te geven:

```json
{"username": "NovaNieuw", "score": 200}
```

Beide velden zijn bij PUT verplicht. Als je exact dezelfde PUT opnieuw uitvoert,
blijft de uitkomst gelijk en komt er geen dubbele score in de geschiedenis.

## 6. Bekijk de scores en ranglijst

Gebruik **POST /players/{player_id}/scores** met:

```json
{"score": 300}
```

Dit geeft **201** en een apart **score-id**. Verwar dat niet met het speler-id.
Bekijk **GET /players/{player_id}/scores** en **GET /leaderboard**. De laatst
toegevoegde score bepaalt de ranglijst, niet de hoogste score ooit.

Met **PATCH /scores/{score_id}** en `{"score":250}` corrigeer je deze registratie.
Met **GET /scores/{score_id}** lees je hem terug. POST /scores bestaat niet: een
nieuwe score hoort altijd bij een speler en gaat via /players/{player_id}/scores.

## 7. Probeer bewust een fout

Stuur `{"score":-1}` naar **PATCH /players/{player_id}**. Je krijgt **422** met
`loc`, `msg` en `type`. `loc` wijst het verkeerde veld aan. Vraag de speler opnieuw
op: de vorige score staat er nog. De API hoort na de fout gewoon verder te werken.

Andere controles:

| Proef | Verwacht |
|---|---|
| PATCH met `{}` op je eigen speler | 400: geen velden om te wijzigen |
| POST met een bestaande spelernaam | 409: naam bestaat al |
| Score als tekst, bijvoorbeeld `"100"` | 422: er moet een getal staan |
| Score als `true` of `1.5` | 422: alleen gehele getallen |
| Een onbekend extra veld meesturen | 422: veld niet toegestaan |

## 8. Controleer de toegangsrechten

De GET-routes voor spelers, scores en leaderboard zijn openbaar. Voor toevoegen
moet je ingelogd zijn. Wijzigen en verwijderen mag alleen bij je eigen speler;
dat geldt ook voor diens afzonderlijke scores.

Registreer een tweede testaccount. Klik in Authorize op **Logout**, log in met
dat tweede account en probeer de speler van je eerste account te wijzigen.
Je hoort **403** te krijgen. Log daarna weer in met je eerste account.
Voorbeeldspelers zonder eigenaar geven ook 403; gebruik voor deze oefening je
zelfgemaakte speler. Lokaal eigenaarschap koppelen staat in de README.

## 9. Controleer opslag en ruim je testspeler op

Stop de server met **Ctrl+C**. Start hem in dezelfde terminal opnieuw met
`python run.py --port 8001`. Je oefendatabase-instelling geldt daar nog steeds.
Voer GET /players/{player_id} opnieuw uit: je speler en scores zijn bewaard.
Log opnieuw in als Swagger je token niet meer heeft.

Verwijder alleen jouw eigen testspeler met **DELETE /players/{player_id}**.
**204** heeft geen responsebody. De bijbehorende scores worden mee verwijderd.
GET op hetzelfde speler-id geeft daarna **404**. Dat is de verwachte uitkomst.

Voer **POST /auth/logout** uit: dit maakt je gebruikte token direct ongeldig.
GET /auth/me geeft daarna **401**. Klik ook op **Authorize > Logout** om het
oude token uit Swagger te verwijderen.

## 10. Stoppen en terug naar de gewone app

Stop de oefenserver met Ctrl+C. In deze terminal kun je terug naar de normale database:

```powershell
Remove-Item Env:\PLAYER_DATABASE
python run.py
```

De gewone Swagger-pagina is dan http://127.0.0.1:8000/docs. Het verwijderen van
de omgevingsvariabele verwijdert je oefendatabase niet.

Bij **401** opnieuw inloggen; bij **403** je account/eigenaarschap controleren;
bij **404** het echte id via GET /players opzoeken. Het volledige overzicht staat
in [API_CONTRACT.md](../API_CONTRACT.md). Vul na je controle [KLASGENOOT.md](KLASGENOOT.md) in.
