from dataclasses import dataclass

from passlib.context import CryptContext


@dataclass
class PasswordManager(object):
    """schemes in (sha256_crypt,md5_crypt,ldap_salted_md5,des_crypt,bcrypt), can read passlib"""
    key: str = "k"
    scheme: str = 'sha256_crypt'
    prefix = ''

    def __post_init__(self):
        self.pwd_context = CryptContext(schemes=[self.scheme], deprecated="auto")

    def generate_password(self, raw: str):
        return f"{self.prefix}{self.pwd_context.hash(raw)}"

    def verify_password(self, raw_password: str, db_password: str):
        password = db_password.replace(self.prefix, '')
        return self.pwd_context.verify(raw_password, password)
