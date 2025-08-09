
from passlib.context import CryptContext


class Password:

    pwd_context = CryptContext(
        schemes=["bcrypt", "sha256_crypt"],
        deprecated="auto"
    )

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(
        self, password: str
    ) -> str:
        return self.pwd_context.hash(password)


class Token:

    _token = None

    @property
    def token(self):
        if self._token:
            token_type = self._token.get("token_type", None)
            access_token = self._token.get("access_token", None)
            return f'{token_type} {access_token}'


password = Password()
token = Token()
