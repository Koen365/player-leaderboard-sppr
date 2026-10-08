"""Eigen classes die SQLAlchemy aan SQLite-tabellen koppelt."""

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    username_key: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class AccessSession(Base):
    __tablename__ = "access_sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[int]


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        CheckConstraint("length(trim(username)) BETWEEN 1 AND 50", name="valid_username"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    username_key: Mapped[str] = mapped_column(String(100), unique=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    scores: Mapped[list["Score"]] = relationship(
        back_populates="player", cascade="all, delete-orphan",
        passive_deletes=True, order_by="Score.id", lazy="selectin",
    )

    @property
    def score(self) -> int:
        """Behoud het score-veld uit sprint 1/2 zonder dubbele opslag."""
        return self.scores[-1].score if self.scores else 0


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        CheckConstraint("typeof(score) = 'integer' AND score BETWEEN 0 AND 2147483647", name="valid_score"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    score: Mapped[int]
    player: Mapped[Player] = relationship(back_populates="scores")


class Metadata(Base):
    __tablename__ = "app_metadata"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]
