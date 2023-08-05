from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional

import jwt


@dataclass
class JwtManager(object):
    """If algorithm is RS256, use public/private key, else use JWT_KEY"""
    JWT_ISSUER: str = 'company'
    JWT_ALGORITHM: str = 'HS256'
    JWT_KEY: str = 'SECRET'

    # JWT_ALGORITHM: str = 'RS256' support public/private key
    JWT_PUBLIC_KEY: Optional[str] = None
    JWT_PRIVATE_KEY: Optional[str] = None

    JWT_EXPIRE: timedelta = timedelta(hours=24)
    JWT_AUTH_HEADER_PREFIX: str = ''

    def __post_init__(self):
        if self.JWT_ALGORITHM == 'RS256':
            if not self.JWT_PUBLIC_KEY or not self.JWT_PRIVATE_KEY:
                raise ValueError('rs 256 must has public key and private key')

    def gen_jwt(self, username: str, user_id: int):
        """生成 jwt"""
        payload = {
            'username': username, 'user_id': user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.JWT_EXPIRE,
            "iss": self.JWT_ISSUER
        }

        token = jwt.encode(
            payload=payload,
            key=self.suited_key(mode='encode'),
            algorithm=self.JWT_ALGORITHM
        )

        return f"{self.JWT_AUTH_HEADER_PREFIX}{token}"

    def decode_jwt(self, token: str, algorithms: Optional[str] = ''):
        if not algorithms:
            algorithms = self.JWT_ALGORITHM
        if self.JWT_AUTH_HEADER_PREFIX:
            token = token.replace(self.JWT_AUTH_HEADER_PREFIX, '')
        return jwt.decode(token, self.suited_key(mode='decode'), algorithms)

    def suited_key(self, mode: str = ''):
        if self.JWT_ALGORITHM == 'RS256':
            return self.JWT_PRIVATE_KEY if mode == 'encode' else self.JWT_PUBLIC_KEY
        else:
            return self.JWT_KEY
