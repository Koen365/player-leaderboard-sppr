"""Pydantic controleert JSON-invoer voordat die de database bereikt."""

from typing import Annotated, Literal
import unicodedata

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
    model_validator,
)


def readable_username(value):
    if any(unicodedata.category(character) in {"Cc", "Cs"} for character in value):
        raise ValueError(
            "Een naam mag geen besturingstekens of ongeldige Unicode bevatten."
        )
    return value


Username = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=50),
    AfterValidator(readable_username),
    Field(
        description="Naam van 1 tot 50 tekens na trimmen; geen besturingstekens. Namen zijn uniek zonder hoofdletterverschil."
    ),
]
ScoreValue = Annotated[
    int,
    Field(
        strict=True,
        ge=0,
        le=2_147_483_647,
        description="Geheel getal; geen tekst, boolean, kommagetal of null.",
    ),
]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlayerCreate(InputModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"username": "Nova", "score": 100}]}
    )
    username: Username
    score: ScoreValue = 0


class PlayerReplace(InputModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"username": "NovaNieuw", "score": 200}]}
    )
    username: Username
    score: ScoreValue


class PlayerPatch(InputModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"score": 150}]})
    username: Username | None = None
    score: ScoreValue | None = None

    @model_validator(mode="after")
    def reject_null(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} mag niet null zijn.")
        return self


class PlayerRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"id": 5, "username": "Nova", "score": 100}]},
    )
    id: int
    username: str
    score: int


class ScoreCreate(InputModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"score": 300}]})
    score: ScoreValue


class ScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    player_id: int
    score: int


class LegacyPlayer(PlayerCreate):
    id: Annotated[int, Field(strict=True, ge=1, le=9_223_372_036_854_775_807)]


class UserCreate(InputModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"username": "MijnAccount", "password": "Kies-een-eigen-wachtwoord"}
            ]
        }
    )
    username: Username
    password: SecretStr = Field(
        min_length=10,
        max_length=128,
        description="Kies een eigen wachtwoord van 10 tot 128 tekens; dit wordt nooit teruggestuurd.",
    )

    @field_validator("password")
    @classmethod
    def valid_password_encoding(cls, value):
        try:
            value.get_secret_value().encode("utf-8")
        except UnicodeEncodeError as error:
            raise ValueError("Ongeldige Unicode in het wachtwoord.") from error
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(description="Geldigheidsduur in seconden (3600 = één uur).")


class StatusRead(BaseModel):
    status: Literal["ok"]
    message: str


class ErrorResponse(BaseModel):
    detail: str


class ValidationIssue(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationIssue]
