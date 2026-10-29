"""Foutmodellen en voorbeelden voor het OpenAPI-contract."""

from schemas import ErrorResponse, ValidationErrorResponse

DESCRIPTIONS = {
    400: "Lege PATCH of onleesbaar verzoek.",
    401: "Log in met Authorize; het token ontbreekt, is ongeldig of is verlopen.",
    403: "Je mag alleen je eigen spelers en scores wijzigen.",
    404: "De speler of score bestaat niet.",
    409: "Deze naam bestaat al (namen zijn niet hoofdlettergevoelig).",
    500: "Er ging iets mis op de server.",
    503: "Database tijdelijk niet beschikbaar. Probeer later opnieuw.",
}


def error_responses(*codes):
    responses = {}
    for code in codes:
        responses[code] = {
            "model": ErrorResponse,
            "description": DESCRIPTIONS[code],
            "content": {"application/json": {"example": {"detail": DESCRIPTIONS[code]}}},
        }
        if code == 401:
            responses[code]["headers"] = {"WWW-Authenticate": {"schema": {"type": "string"}, "example": "Bearer"}}
        if code == 503:
            responses[code]["headers"] = {"Retry-After": {"schema": {"type": "string"}, "example": "1"}}
    return responses


VALIDATION_RESPONSE = {
    "model": ValidationErrorResponse,
    "description": "Ongeldige invoer. loc wijst het veld aan; msg en type leggen de fout uit.",
    "content": {"application/json": {"example": {"detail": [
        {"loc": ["body", "score"], "msg": "Input should be greater than or equal to 0", "type": "greater_than_equal"}
    ]}}},
}

CREATED_LOCATION = {"Location": {"description": "Relatief pad naar het nieuwe record.",
                                  "schema": {"type": "string"}}}
