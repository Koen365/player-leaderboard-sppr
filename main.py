import json
from pathlib import Path

DATA_FILE = Path("players.json")


def load_players():
    """Laad spelers uit het JSON-bestand."""
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Kon spelersbestand niet laden. Er wordt met een lege lijst gestart.")
        return []


def save_players(players):
    """Sla alle spelers op in het JSON-bestand."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(players, file, indent=4)
    except OSError:
        print("Er ging iets mis bij het opslaan.")


def get_next_id(players):
    """Geef de eerstvolgende vrije ID."""
    if not players:
        return 1
    return max(player["id"] for player in players) + 1


def add_player(players):
    """Voeg een nieuwe speler toe."""
    username = input("Username: ").strip()

    if not username:
        print("Username mag niet leeg zijn.")
        return

    if any(player["username"].lower() == username.lower() for player in players):
        print("Deze username bestaat al.")
        return

    player = {
        "id": get_next_id(players),
        "username": username,
        "score": 0
    }

    players.append(player)
    save_players(players)
    print(f"Speler '{username}' is toegevoegd met ID {player['id']}.")


def show_players(players):
    """Toon alle spelers."""
    if not players:
        print("Er zijn nog geen spelers.")
        return

    print("\n--- Alle spelers ---")
    for player in players:
        print(
            f"ID: {player['id']} | "
            f"Username: {player['username']} | "
            f"Score: {player['score']}"
        )


def find_player(players):
    """Zoek een speler op ID of username."""
    if not players:
        print("Er zijn nog geen spelers.")
        return None

    search = input("Zoek op ID of username: ").strip()

    for player in players:
        if str(player["id"]) == search or player["username"].lower() == search.lower():
            return player

    print("Speler niet gevonden.")
    return None


def search_player(players):
    """Zoek en toon een speler."""
    player = find_player(players)

    if player:
        print(
            f"ID: {player['id']} | "
            f"Username: {player['username']} | "
            f"Score: {player['score']}"
        )


def change_score(players):
    """Wijzig de score van een speler."""
    player = find_player(players)

    if not player:
        return

    while True:
        try:
            score = int(input(f"Nieuwe score voor {player['username']}: "))
            if score < 0:
                print("Score mag niet negatief zijn.")
                continue
            break
        except ValueError:
            print("Voer een geldig getal in.")

    player["score"] = score
    save_players(players)
    print(f"Score aangepast naar {score}.")


def leaderboard(players):
    """Toon spelers gesorteerd van hoogste naar laagste score."""
    if not players:
        print("Er zijn nog geen spelers.")
        return

    sorted_players = sorted(players, key=lambda player: player["score"], reverse=True)

    print("\n========== LEADERBOARD ==========")
    for position, player in enumerate(sorted_players, start=1):
        print(f"{position}. {player['username']} - {player['score']} punten")
    print("=================================")


def show_menu():
    """Toon het hoofdmenu."""
    print("\n==============================")
    print("       PLAYER LEADERBOARD")
    print("==============================")
    print("1. Speler toevoegen")
    print("2. Alle spelers bekijken")
    print("3. Speler zoeken")
    print("4. Score aanpassen")
    print("5. Leaderboard")
    print("6. Afsluiten")
    print("==============================")


def main():
    players = load_players()

    while True:
        show_menu()
        choice = input("Maak een keuze (1-6): ").strip()

        if choice == "1":
            add_player(players)
        elif choice == "2":
            show_players(players)
        elif choice == "3":
            search_player(players)
        elif choice == "4":
            change_score(players)
        elif choice == "5":
            leaderboard(players)
        elif choice == "6":
            save_players(players)
            print("Programma afgesloten. Tot de volgende keer!")
            break
        else:
            print("Ongeldige keuze. Kies een getal van 1 t/m 6.")


if __name__ == "__main__":
    main()
