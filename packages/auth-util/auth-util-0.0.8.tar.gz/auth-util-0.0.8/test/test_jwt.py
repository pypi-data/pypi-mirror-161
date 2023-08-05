from unittest import TestCase

from auth_util import JwtManager


class TestJwt(TestCase):

    def test_password_gen(self):
        jwt = JwtManager()

        username, user_id = '李雷', 3
        t = jwt.gen_jwt(username=username, user_id=user_id)
        res = jwt.decode_jwt(t)
        self.assertEqual(res['username'], username)
        self.assertEqual(res['user_id'], user_id)

    def test_rs256(self):
        with open('yingde.pub', mode='r') as r:
            pub_key = r.read()
        with open('yingde.priv', mode='r') as r:
            priv_key = r.read()
        jwt = JwtManager(
            JWT_ALGORITHM='RS256', JWT_PUBLIC_KEY=pub_key,
            JWT_PRIVATE_KEY=priv_key
        )
        username, user_id = '李雷', 3
        t = jwt.gen_jwt(username=username, user_id=user_id)
        res = jwt.decode_jwt(t)
        self.assertEqual(res['username'], username)
        self.assertEqual(res['user_id'], user_id)
