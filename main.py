

# Gebruik eerst de projectomgeving met de benodigde pakketten.
if __name__ == "__main__":
    from run import ensure_dependencies
    ensure_dependencies(__file__)

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

import service
from database import initialize_database, make_engine, make_session_factory
from schemas import PlayerCreate, PlayerPatch


def show_players(players):
    if not players:
        print("Er zijn nog geen spelers.")
    for player in players:
        print(f"ID: {player.id} | Username: {player.username} | Score: {player.score}")


def find_player(session):
    search = input("Zoek op ID of username: ").strip()
    for player in service.list_players(session):
        if str(player.id) == search or player.username.casefold() == search.casefold():
            return player
    raise service.NotFound("Speler niet gevonden.")


def add_player(session):
    data = PlayerCreate(username=input("Username: ").strip())
    player = service.create_player(session, data)
    print(f"Speler '{player.username}' is toegevoegd met ID {player.id}.")


def change_score(session):
    player = find_player(session)
    while True:
        try:
            score = int(input(f"Nieuwe score voor {player.username}: "))
            # Controleer of de score binnen het toegestane bereik valt.
            data = PlayerPatch(score=score)
            break
        except ValueError:
            print("Voer een geheel getal van 0 t/m 2147483647 in.")
    service.update_player(session, player.id, data)
    print(f"Score aangepast naar {score}.")


def leaderboard(session):
    print("\n========== LEADERBOARD ==========")
    players = service.list_players(session, leaderboard=True)
    if not players:
        print("Er zijn nog geen spelers.")
    for position, player in enumerate(players, start=1):
        print(f"{position}. {player.username} - {player.score} punten")
    print("=================================")


def show_menu():
    print("\n======== PLAYER LEADERBOARD ========")
    print("1. Speler toevoegen")
    print("2. Alle spelers bekijken")
    print("3. Speler zoeken")
    print("4. Score aanpassen")
    print("5. Leaderboard")
    print("6. Afsluiten")


def main():
    engine = make_engine()
    try:
        initialize_database(engine)
        session_factory = make_session_factory(engine)
        while True:
            show_menu()
            choice = input("Maak een keuze (1-6): ").strip()
            if choice == "6":
                print("Programma afgesloten. Alle wijzigingen zijn opgeslagen.")
                break
            # Een nieuwe sessie per menuactie ziet ook wijzigingen via de API.
            with session_factory() as session:
                try:
                    if choice == "1":
                        add_player(session)
                    elif choice == "2":
                        show_players(service.list_players(session))
                    elif choice == "3":
                        show_players([find_player(session)])
                    elif choice == "4":
                        change_score(session)
                    elif choice == "5":
                        leaderboard(session)
                    else:
                        print("Ongeldige keuze. Kies een getal van 1 t/m 6.")
                except ValidationError as error:
                    print(f"Ongeldige invoer: {error.errors()[0]['msg']}")
                except (service.NotFound, service.DuplicateUsername) as error:
                    print(error)
                except SQLAlchemyError:
                    print("Databasebewerking mislukt. Controleer of het bestand schrijfbaar is.")
    except (EOFError, KeyboardInterrupt):
        print("\nProgramma afgesloten. Eerdere wijzigingen zijn opgeslagen.")
    except (ValueError, SQLAlchemyError) as error:
        print(f"Database kon niet worden geopend: {error}")
    finally:
        # Sluit de databaseverbindingen ook af als er een fout optreedt.
        engine.dispose()


if __name__ == "__main__":
    main()
