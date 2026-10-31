import jwt


class JWTValidator:
    def __init__(self, settings):
        self.settings = settings

    def decode_token(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.settings.jwt_secret,
            algorithms=[self.settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
