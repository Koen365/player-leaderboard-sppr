"""Koppel bestaande spelers lokaal aan een geregistreerd account."""

if __name__ == "__main__":
    from run import ensure_dependencies
    ensure_dependencies(__file__)

import argparse

from sqlalchemy import select

from database import initialize_database, make_engine, make_session_factory
from models import Player, User


def assign_players(session, username, player_id=None, all_unowned=False):
    user = session.scalar(select(User).where(User.username_key == username.strip().casefold()))
    if user is None:
        raise ValueError("Registreer dit account eerst via /auth/register.")
    if all_unowned:
        players = list(session.scalars(select(Player).where(Player.owner_id.is_(None))))
    else:
        player = session.get(Player, player_id)
        if player is None:
            raise ValueError("Speler niet gevonden.")
        if player.owner_id is not None and player.owner_id != user.id:
            raise ValueError("Deze speler heeft al een andere eigenaar.")
        players = [player]
    for player in players:
        player.owner_id = user.id
    session.commit()
    return len(players)


def main():
    parser = argparse.ArgumentParser(description="Koppel bestaande spelers aan een account")
    parser.add_argument("--user", required=True, help="Accountnaam, niet de spelernaam")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--player-id", type=int)
    group.add_argument("--all-unowned", action="store_true")
    args = parser.parse_args()
    engine = make_engine()
    try:
        initialize_database(engine)
        with make_session_factory(engine)() as session:
            count = assign_players(session, args.user, args.player_id, args.all_unowned)
        print(f"{count} speler(s) gekoppeld aan {args.user}.")
    except ValueError as error:
        parser.exit(1, f"{error}\n")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
