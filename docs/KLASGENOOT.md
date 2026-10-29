# Peer review

Status: **nog niet uitgevoerd door een andere student**. Automatische tests
vervangen deze controle niet. Vul alleen echte bevindingen in.

| Gegeven | Invullen |
|---|---|
| Naam tester | |
| Reviewer | 1 / 2 |
| Datum | |
| Geteste Git-commit | |
| Python-versie | |

Gebruik een eigen projectkopie en oefendatabase volgens [GEBRUIKEN.md](GEBRUIKEN.md).
Probeer de stappen zonder mondelinge hulp van de maker uit te voeren.
Beide klasgenoten gebruiken een eigen kopie van dit formulier en beoordelen
dezelfde Git-commit. Vul de feedback eerst afzonderlijk in en bespreek die daarna.

## Code lezen

De leesvolgorde staat in [README.md](../README.md#documentatie-en-bestanden).
Volg bijvoorbeeld het toevoegen van een speler vanaf de route tot aan de database.

- [ ] Namen van bestanden, functies en variabelen zijn begrijpelijk.
- [ ] Functies hebben een duidelijke taak en zijn goed te volgen.
- [ ] Routes, invoercontrole en databaselogica zijn logisch verdeeld.
- [ ] Opmerkingen helpen bij lastige stukken zonder elke regel te herhalen.
- [ ] Ongeldige invoer en ontbrekende rechten worden afgehandeld.
- [ ] De tests controleren zowel geslaagde acties als fouten.

Noteer concrete voorbeelden, ook als iets goed is opgelost.

| Bestand en functie | Wat valt op? | Waarom? | Voorstel |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

Wat is duidelijk of goed opgelost?

Welk verbeterpunt heeft volgens jou de meeste prioriteit?

Welke vraag wil je aan de maker stellen?

## Zelfstandig gebruiken (sprint 8)

- [ ] Ik begrijp wat de API doet en het verschil tussen account en speler.
- [ ] Ik kan de API starten en Swagger openen.
- [ ] Ik kan registreren en inloggen.
- [ ] Ik kan mijn account en openbare gegevens opvragen.
- [ ] Ik kan een eigen speler en score toevoegen.
- [ ] Ik kan de speler en score wijzigen.
- [ ] Ik kan uitzoeken welke functies login of eigenaarschap vereisen.
- [ ] Ik kan bewust een verkeerd verzoek sturen en de fout begrijpen.
- [ ] Ik kan uitloggen en mijn eigen testgegevens opruimen.

Waar was de uitleg onduidelijk of was hulp nodig?

## Probeer de API kapot te krijgen (sprint 7)

Gebruik alleen zelfgemaakte oefengegevens. Probeer bijvoorbeeld ontbrekende
velden, lege namen, negatieve scores, verkeerde types, onbekende ids, een
herhaald verzoek en een wijziging met een ander account. Vraag na elke fout
opnieuw gegevens op: de API moet blijven antwoorden en geen halve wijziging opslaan.

| Request (geen wachtwoord of token noteren) | Verwacht | Werkelijk | Probleem? |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

Gevonden probleem en stappen om het te herhalen:

Oplossing door de maker:

Naam van de toegevoegde automatische regressietest:

Opnieuw gecontroleerd door / datum / resultaat:

Als je niets nieuws vindt, noteer dan eerlijk welke proeven je hebt uitgevoerd.
Drie eerder gevonden fouten en hun regressietests staan in TESTVERSLAG.md.
