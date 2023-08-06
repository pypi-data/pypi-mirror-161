"""User resources unit tests."""

import unittest
from unittest.mock import patch

import envvars
import mocks
import common


from notelist.responses import (
    METHOD_NOT_ALLOWED, MISSING_TOKEN, INVALID_TOKEN, OK,
    ERROR_METHOD_NOT_ALLOWED, ERROR_INVALID_CREDENTIALS, ERROR_MISSING_TOKEN,
    ERROR_INVALID_TOKEN, ERROR_VALIDATION
)

from notelist.views.authentication import (
    USER_LOGGED_IN, TOKEN_REFRESHED, USER_LOGGED_OUT, INVALID_CREDENTIALS
)


class LoginTestCase(common.BaseTestCase):
    """Login resource unit tests."""

    def test_get(self):
        """Test the Get method of the Login view.

        This test tries to call the Get method, which shouldn't work.
        """
        r = self.client.get("/auth/login")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post(self):
        """Test the Get method of the Login view.

        This test tries to log in as some user with valid credentials, which
        should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], USER_LOGGED_IN)
        self.assertEqual(res_data[keys[1]], OK)

        # Check result
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(type(result), dict)

        for i in (
            "user_id", "access_token", "access_token_expiration",
            "refresh_token", "refresh_token_expiration"
        ):
            self.assertIn(i, result)
            v = result[i]
            self.assertEqual(type(v), str)
            self.assertNotEqual(v, "")

    def test_post_missing_fields(self):
        """Test the Get method of the Login view.

        This test tries to log in as some user with some mandatory field
        missing, which shouldn't work.
        """
        # Log in (without data)
        r1 = self.client.post("/auth/login")

        # Log in (without username)
        data = {"password": self.reg1["password"]}
        r2 = self.client.post("/auth/login", json=data)

        # Log in (without password)
        data = {"username": self.reg1["username"]}
        r3 = self.client.post("/auth/login", json=data)

        # Check status codes and messages
        for r in (r1, r2, r3):
            self.assertEqual(r.status_code, 400)
            r_data = r.json
            self.assertIn("message", r_data)
            self.assertIn("message_type", r_data)
            self.assertEqual(r_data["message_type"], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_disabled_user(self):
        """Test the Get method of the Login view.

        This test tries to log in as some disabled user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg2["username"],
            "password": self.reg2["password"]
        }

        r = self.client.post("/auth/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_CREDENTIALS)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_CREDENTIALS)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_user_not_found(self):
        """Test the Get method of the Login view.

        This test tries to log in as a user that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {"username": "test", "password": "test_password"}
        r = self.client.post("/auth/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_CREDENTIALS)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_CREDENTIALS)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_invalid_password(self):
        """Test the Get method of the Login view.

        This test tries to log in as some user providing an invalid password,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"] + "_"
        }

        r = self.client.post("/auth/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_CREDENTIALS)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_CREDENTIALS)

    def test_put(self):
        """Test the Put method of the Login view.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/auth/login")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """Test the Delete method of the Login view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/auth/login")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)


class TokenRefreshTestCase(common.BaseTestCase):
    """Token Refresh resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get(self):
        """Test the Get method of the Token Refresh view.

        This test tries to get a new, not fresh, access token providing the
        user refresh token, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        refresh_token = r.json["result"]["refresh_token"]

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.get("/auth/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], TOKEN_REFRESHED)
        self.assertEqual(res_data[keys[1]], OK)

        # Check result
        self.assertIn("result", res_data)
        result = r.json["result"]
        self.assertEqual(type(result), dict)

        # Check new access token
        self.assertIn("access_token", result)
        access_token = result["access_token"]
        self.assertEqual(type(access_token), str)
        self.assertNotEqual(access_token, "")

    def test_get_missing_refresh_token(self):
        """Test the Get method of the Token Refresh view.

        This test tries to get a new, not fresh, access token without providing
        a refresh token, which shouldn't work.
        """
        # Get access token
        r = self.client.get("/auth/refresh")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    def test_get_invalid_refresh_token(self):
        """Test the Get method of the Token Refresh view.

        This test tries to get a new, not fresh, access token given an invalid
        refresh token, which shouldn't work.
        """
        # Get a new, not fresh, access token providing an invalid access token
        # ("1234").
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/auth/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    def test_post(self):
        """Test the Post method of the Token Refresh view.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/auth/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_put(self):
        """Test the Put method of the Token Refresh view.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/auth/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """Test the Delete method of the Token Refresh view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/auth/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)


class LogoutTestCase(common.BaseTestCase):
    """Logout resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get(self):
        """Test the Get method of the Logout view.

        This test logs in as some user with valid credentials and then tries to
        log out, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Log out
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/auth/logout", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], USER_LOGGED_OUT)
        self.assertEqual(res_data[keys[1]], OK)

    def test_get_missing_access_token(self):
        """Test the Get method of the Logout view.

        This test tries to log out without providing an access token, which
        shouldn't work.
        """
        # Log out without providing the access token
        r = self.client.get("/auth/logout")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Logout view.

        This test tries to log out providing an invalid access token, which
        shouldn't work.
        """
        # Log out providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/auth/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    def test_post(self):
        """Test the Post method of the Logout view.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/auth/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_put(self):
        """Test the Put method of the Logout view.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/auth/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """Test the Delete method of the Logout view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/auth/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)


if __name__ == "__main__":
    unittest.main()
