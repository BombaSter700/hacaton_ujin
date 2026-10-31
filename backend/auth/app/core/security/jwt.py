"""JWT verification for auth; keys and algorithms come only from configuration."""

import jwt

from app.core.config import settings
from app.core.exceptions import InvalidTokenException, TokenExpiredException


class JWTValidator:
    def __init__(self, config=None):
        self.settings = config or settings

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
                options={"require": ["exp", "sub"]},
            )
            subject = payload["sub"]
            if (
                not isinstance(subject, str)
                or not subject.isascii()
                or not subject.isdecimal()
                or int(subject) < 1
            ):
                raise InvalidTokenException("Token subject must be a positive user ID")
            if not isinstance(payload.get("role", "guest"), str):
                raise InvalidTokenException()
            session_token = payload.get("session_token")
            if session_token is not None and (
                not isinstance(session_token, str) or not session_token
            ):
                raise InvalidTokenException()
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredException() from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenException() from exc
