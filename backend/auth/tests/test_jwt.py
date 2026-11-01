from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest

from app.core.exceptions import InvalidTokenException, TokenExpiredException
from app.core.security.jwt import JWTValidator


KEY = "test-signing-key-with-at-least-32-bytes"


def token(**claims):
    payload = {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
    payload.update(claims)
    return jwt.encode(payload, KEY, algorithm="HS256")


@pytest.fixture
def validator():
    return JWTValidator(SimpleNamespace(jwt_secret=KEY, jwt_algorithm="HS256"))


def test_valid_token(validator):
    assert validator.decode_token(token(role="admin"))["role"] == "admin"


def test_expired_token(validator):
    with pytest.raises(TokenExpiredException):
        validator.decode_token(token(exp=datetime.now(timezone.utc) - timedelta(minutes=1)))


@pytest.mark.parametrize("subject", ["0", "-1", "abc", "١", 1, ""])
def test_invalid_subject(validator, subject):
    with pytest.raises(InvalidTokenException):
        validator.decode_token(token(sub=subject))


@pytest.mark.parametrize("claims", [{"role": 1}, {"session_token": ""}, {"session_token": 1}])
def test_invalid_claims(validator, claims):
    with pytest.raises(InvalidTokenException):
        validator.decode_token(token(**claims))


def test_wrong_signing_key(validator):
    forged = jwt.encode({"sub": "1", "exp": 4102444800}, "other-key-with-at-least-32-bytes!!", algorithm="HS256")
    with pytest.raises(InvalidTokenException):
        validator.decode_token(forged)


@pytest.mark.parametrize("claims", [{"sub": "1"}, {"exp": 4102444800}])
def test_required_claims(validator, claims):
    with pytest.raises(InvalidTokenException):
        validator.decode_token(jwt.encode(claims, KEY, algorithm="HS256"))
