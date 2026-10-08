"""Pydantic controleert JSON-invoer voordat die de database bereikt."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints, model_validator

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
ScoreValue = Annotated[int, Field(strict=True, ge=0, le=2_147_483_647)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlayerCreate(InputModel):
    username: Username
    score: ScoreValue = 0


class PlayerReplace(InputModel):
    username: Username
    score: ScoreValue


class PlayerPatch(InputModel):
    username: Username | None = None
    score: ScoreValue | None = None

    @model_validator(mode="after")
    def reject_null(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} mag niet null zijn.")
        return self


class PlayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    score: int


class ScoreCreate(InputModel):
    score: ScoreValue


class ScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    score: int


class LegacyPlayer(PlayerCreate):
    id: Annotated[int, Field(strict=True, ge=1, le=9_223_372_036_854_775_807)]


class UserCreate(InputModel):
    username: Username
    password: SecretStr = Field(min_length=10, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
