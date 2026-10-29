"""Gedeelde CRUD-logica voor de API en het consolemenu."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import Player, Score


class NotFound(ValueError):
    pass


class DuplicateUsername(ValueError):
    pass


class Forbidden(ValueError):
    pass


def get_player(session, player_id):
    player = session.get(Player, player_id)
    if player is None:
        raise NotFound(f"Speler met ID {player_id} niet gevonden.")
    return player


def list_players(session, leaderboard=False):
    players = list(session.scalars(select(Player).order_by(Player.id)))
    return sorted(players, key=lambda player: (-player.score, player.id)) if leaderboard else players


def commit_player(session):
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        # Alleen de unieke naambeperking vertalen naar een gebruikersfout.
        if "players.username_key" in str(error.orig):
            raise DuplicateUsername("Deze username bestaat al.") from error
        raise


def create_player(session, data, owner_id=None):
    player = Player(username=data.username, username_key=data.username.casefold(), owner_id=owner_id)
    player.scores.append(Score(score=data.score))
    session.add(player)
    commit_player(session)
    session.refresh(player)
    return player


def update_player(session, player_id, data):
    player = get_player(session, player_id)
    changes = data.model_dump(exclude_unset=True)
    if "username" in changes:
        player.username = changes["username"]
        player.username_key = player.username.casefold()
    # Een herhaalde PUT met dezelfde score mag geen extra registratie maken.
    if "score" in changes and (not player.scores or changes["score"] != player.score):
        player.scores.append(Score(score=changes["score"]))
    commit_player(session)
    session.refresh(player)
    return player


def delete_player(session, player_id):
    session.delete(get_player(session, player_id))
    session.commit()


def list_scores(session, player_id=None):
    statement = select(Score).order_by(Score.id)
    if player_id is not None:
        get_player(session, player_id)
        statement = statement.where(Score.player_id == player_id)
    return list(session.scalars(statement))


def get_score(session, score_id):
    score = session.get(Score, score_id)
    if score is None:
        raise NotFound(f"Score met ID {score_id} niet gevonden.")
    return score


def create_score(session, player_id, data):
    get_player(session, player_id)
    score = Score(player_id=player_id, score=data.score)
    session.add(score)
    session.commit()
    session.refresh(score)
    return score


def update_score(session, score_id, data):
    score = get_score(session, score_id)
    score.score = data.score
    session.commit()
    session.refresh(score)
    return score


def delete_score(session, score_id):
    session.delete(get_score(session, score_id))
    session.commit()


def require_player_owner(session, player_id, user_id):
    player = get_player(session, player_id)
    if player.owner_id != user_id:
        raise Forbidden("Je mag alleen je eigen spelers en scores wijzigen.")
    return player


def require_score_owner(session, score_id, user_id):
    score = get_score(session, score_id)
    require_player_owner(session, score.player_id, user_id)
    return score
