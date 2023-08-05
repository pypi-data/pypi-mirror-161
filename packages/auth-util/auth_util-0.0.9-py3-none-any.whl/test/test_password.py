from unittest import TestCase

from auth_util import PasswordManager


class TestPasswordManager(TestCase):
    p = PasswordManager(key='ccc', scheme='bcrypt')

    def test_password_gen(self):
        raw = 'abc'
        p = self.p.generate_password(raw)
        res = self.p.verify_password(raw, p)
        self.assertTrue(res)
