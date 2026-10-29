"""Databaseverbinding en eenmalige, transactionele JSON-import."""

import json
import os
from pathlib import Path

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import URL, create_engine, event, inspect, select, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Metadata, Player, Score
from schemas import LegacyPlayer

PROJECT_DIR = Path(__file__).resolve().parent


def make_engine(database_path=None):
    path = Path(
        database_path or os.environ.get("PLAYER_DATABASE", PROJECT_DIR / "players.db")
    )
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        URL.create("sqlite", database=str(path)),
        connect_args={"check_same_thread": False, "timeout": 15},
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        # SQLite moet relaties en gekoppelde verwijderingen expliciet afdwingen.
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def initialize_database(engine, seed_file=PROJECT_DIR / "players.json"):
    Base.metadata.create_all(engine)
    # Bestaande databases krijgen alleen een extra kolom; spelers blijven staan.
    columns = {column["name"] for column in inspect(engine).get_columns("players")}
    with engine.begin() as connection:
        if "owner_id" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE players ADD COLUMN owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL"
                )
            )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_players_owner_id ON players(owner_id)")
        )
    with Session(engine) as session, session.begin():
        if session.get(Metadata, "json_imported") is not None:
            return
        # Een al gevulde database wordt nooit met voorbeelddata overschreven.
        has_players = session.scalar(select(Player.id).limit(1)) is not None
        if not has_players and seed_file is not None and Path(seed_file).exists():
            try:
                raw = json.loads(Path(seed_file).read_text(encoding="utf-8-sig"))
                players = TypeAdapter(list[LegacyPlayer]).validate_python(raw)
                ids = [player.id for player in players]
                names = [player.username.casefold() for player in players]
                if len(set(ids)) != len(ids) or len(set(names)) != len(names):
                    raise ValueError("Dubbele speler-id of username.")
            except (OSError, ValueError, ValidationError) as error:
                raise ValueError(f"Import van {seed_file} mislukt: {error}") from error
            for item in players:
                session.add(
                    Player(
                        id=item.id,
                        username=item.username,
                        username_key=item.username.casefold(),
                        scores=[Score(score=item.score)],
                    )
                )
        session.add(Metadata(key="json_imported", value="1"))


def make_session_factory(engine):
    return sessionmaker(bind=engine)
