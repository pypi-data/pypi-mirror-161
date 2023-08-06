import unittest, os, requests

from . import cern_sso
from authlib.jose import jwk, jwt


class TestCernSSO(unittest.TestCase):

    AUTH_SERVER = "auth.cern.ch"
    AUTH_REALM = "cern"

    OIDC_JWKS_URL = (
        "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs"
    )

    TEST_COOKIE_URL = "https://openstack.cern.ch"
    TEST_COOKIE_URL_OLD_SSO = "https://account.cern.ch/account/Management/MyAccounts.aspx"
    TEST_COOKIE_FILE = "/tmp/cookies.txt"

    TEST_TOKEN_URL = "http://localhost:5000"
    TEST_TOKEN_CLIENT_ID = "get-sso-token-test"

    def _validate_jwt(self, token):
        def load_key(header, payload):
            jwk_set = requests.get(self.OIDC_JWKS_URL).json()
            return jwk.loads(jwk_set, header.get("kid"))

        claims = jwt.decode(token, key=load_key)
        claims.validate()
        return True

    def test_old_sso(self):
        # This test should be removed after we retire the old SSO.
        # AUTH_SERVER doesn't matter here, it is ignored if the website uses the old SSO.
        if os.path.exists(self.TEST_COOKIE_FILE):
            os.remove(self.TEST_COOKIE_FILE)
        cern_sso.save_sso_cookie(
            self.TEST_COOKIE_URL_OLD_SSO, self.TEST_COOKIE_FILE, True, self.AUTH_SERVER
        )
        assert os.path.exists(self.TEST_COOKIE_FILE)

    def test_save_sso_cookie(self):
        if os.path.exists(self.TEST_COOKIE_FILE):
            os.remove(self.TEST_COOKIE_FILE)
        cern_sso.save_sso_cookie(
            self.TEST_COOKIE_URL, self.TEST_COOKIE_FILE, True, self.AUTH_SERVER
        )
        assert os.path.exists(self.TEST_COOKIE_FILE)

    def test_get_sso_token(self):
        token = cern_sso.get_sso_token(
            self.TEST_TOKEN_URL,
            self.TEST_TOKEN_CLIENT_ID,
            True,
            self.AUTH_SERVER,
            self.AUTH_REALM,
            False
        )
        assert self._validate_jwt(token)
