"""User resources unit tests."""

import unittest
from unittest.mock import patch

import envvars
import mocks
import common

from notelist.tools import get_uuid

from notelist.responses import (
    METHOD_NOT_ALLOWED, MISSING_TOKEN, INVALID_TOKEN,
    NOT_FRESH_TOKEN, USER_UNAUTHORIZED, OK, ERROR_METHOD_NOT_ALLOWED,
    ERROR_MISSING_TOKEN, ERROR_INVALID_TOKEN, ERROR_NOT_FRESH_TOKEN,
    ERROR_UNAUTHORIZED_USER, ERROR_VALIDATION, ERROR_ITEM_EXISTS,
    ERROR_ITEM_NOT_FOUND
)

from notelist.views.users import (
    RETRIEVED_N, RETRIEVED, CREATED, UPDATED, DELETED, EXISTS, NOT_FOUND
)


class UserListTestCase(common.BaseTestCase):
    """User List resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get(self):
        """Test the Get method of the User List view.

        This test logs in as an administrator user and then tries to get the
        list of users, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get list
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/users/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_N.format(3))
        self.assertEqual(r.json[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        users = r.json["result"]
        self.assertEqual(type(users), list)

        # Check list
        self.assertEqual(len(users), 3)

        for u in users:
            self.assertEqual(type(u), dict)

            for i in ("id", "username", "admin", "enabled", "name"):
                self.assertIn(i, u)

            for i in ("password", "email"):
                self.assertNotIn(i, u)

        for i, u in enumerate((self.admin, self.reg1, self.reg2)):
            self.assertEqual(users[i]["id"], u["id"])
            self.assertEqual(users[i]["username"], u["username"])

    def test_get_missing_access_token(self):
        """Test the Post method of the User List view.

        This test tries to get the list of users without providing an access
        token, which shouldn't work.
        """
        # Get list without providing the access token
        r = self.client.get("/users/users")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_get_invalid_access_token(self):
        """Test the Post method of the User List view.

        This test tries to get the list of users providing an invalid access
        token, which shouldn't work.
        """
        # Get list providing an invalid access token
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/users/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], INVALID_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_unauthorized_user(self):
        """Test the Post method of the User List view.

        This test logs in as a not administrator user and then tries to get the
        list of users, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get list
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/users/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)

    def test_put(self):
        """Test the Put method of the User List view.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/users/users")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """Test the Delete method of the User List view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/users/user")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)


class UserTestCase(common.BaseTestCase):
    """User resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_admin(self):
        """Test the Get method of the User view.

        This test logs in as an administrator user and then tries to get its
        data and the data of another existing user, which should work in both
        cases.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get user data
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f'/users/user/{self.admin["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED)
        self.assertEqual(r.json[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check user
        for i in ("id", "username", "admin", "enabled", "name"):
            self.assertIn(i, user)

        for i in ("password", "email"):
            self.assertNotIn(i, user)

        self.assertEqual(user["id"], self.admin["id"])
        self.assertEqual(user["username"], self.admin["username"])
        self.assertTrue(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], self.admin["name"])

        # Get another user's data
        r = self.client.get(f'/users/user/{self.reg1["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check user
        for i in ("id", "username", "admin", "enabled", "name"):
            self.assertIn(i, user)

        for i in ("password", "email"):
            self.assertNotIn(i, user)

        self.assertEqual(user["id"], self.reg1["id"])
        self.assertEqual(user["username"], self.reg1["username"])
        self.assertFalse(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], self.reg1["name"])

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_not_admin(self):
        """Test the Get method of the User view.

        This test logs in as a not administrator user and then tries to get its
        data, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get user data
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f'/users/user/{self.reg1["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED)
        self.assertEqual(r.json[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check user
        for i in ("id", "username", "admin", "enabled", "name"):
            self.assertIn(i, user)

        for i in ("password", "email"):
            self.assertNotIn(i, user)

        self.assertEqual(user["id"], self.reg1["id"])
        self.assertEqual(user["username"], self.reg1["username"])
        self.assertFalse(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], self.reg1["name"])

    def test_get_missing_access_token(self):
        """Test the Get method of the User view.

        This test tries to get the data of a user without providing the access
        token, which shouldn't work.
        """
        # Get the data of the user with ID 1 (which doesn't exist)
        r = self.client.get("/users/user/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_get_invalid_access_token(self):
        """Test the Get method of the User view.

        This test tries to get the data of some user providing an invalid
        access token, which shouldn't work.
        """
        # Get the user providing an invalid access token
        url = f'/users/user/{self.reg1["id"]}'
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], INVALID_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_unauthorized_user(self):
        """Test the Get method of the User view.

        This test logs in as a not administrator user and then tries to get the
        data of another user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get another user's data
        url = f'/users/user/{self.reg2["id"]}'
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_user_not_found(self):
        """Test the Get method of the User view.

        This test logs in as an administrator user and then tries to get the
        data of some user that doesn't exist, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get the data of a user with an ID that doesn't exist
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/users/user/{get_uuid()}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], NOT_FOUND)
        self.assertEqual(r.json[keys[1]], ERROR_ITEM_NOT_FOUND)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post(self):
        """Test the Post method of the User view.

        This test logs in as an administrator user and then tries to create a
        new user, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}

        u = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test"
        }

        r = self.client.post("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], CREATED)
        self.assertEqual(r.json[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertIn("id", result)
        user_id = result["id"]
        self.assertEqual(type(user_id), str)

        # Get user data
        url = f"/users/user/{user_id}"
        r = self.client.get(url, headers=headers, json=u)
        user = r.json["result"]

        # Check data
        for i in ("id", "username", "admin", "enabled", "name"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], u[i])

        for i in ("password", "email"):
            self.assertNotIn(i, user)

    def test_post_missing_access_token(self):
        """Test the Post method of the User view.

        This test tries to create a new user without providing the access
        token, which shouldn't work.
        """
        # Create a user without providing the access token
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/users/user", json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_post_invalid_access_token(self):
        """Test the Post method of the User view.

        This test tries to create a new user providing an invalid access token,
        which shouldn't work.
        """
        # Create a user providing an invalid access token
        headers = {"Authorization": "Bearer 1234"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], INVALID_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_unauthorized_user(self):
        """Test the Post method of the User view.

        This test logs in as a not administrator user and then tries to create
        a new user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_missing_fields(self):
        """Test the Post method of the User view.

        This test tries to create new users with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user without its username
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password"}
        r1 = self.client.post("/users/user", headers=headers, json=u)

        # Create a user without its password
        u = {"username": "test"}
        r2 = self.client.post("/users/user", headers=headers, json=u)

        # Check status codes and messages
        keys = ("message", "message_type")

        for r in (r1, r2):
            # Status code
            self.assertEqual(r.status_code, 400)

            # Message
            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_password_length(self):
        """Test the Post method of the User view.

        This test tries to create a new user with a password that has less than
        8 characters and another user with a password that has more than 100
        characters, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create users
        headers = {"Authorization": f"Bearer {access_token}"}
        keys = ("message", "message_type")

        for p in ("test", "test" * 100):
            u = {"username": "test", "password": p}
            r = self.client.post("/users/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

            # Check message
            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_invalid_fields(self):
        """Test the Post method of the User view.

        This test tries to create a new user providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}

        u = {
            "username": "test_user",
            "password": "test_password",
            "invalid_field": "1234"
        }

        r = self.client.post("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_user_exists(self):
        """Test the Post method of the User view.

        This test tries to create a new user with the same username of another
        user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": self.reg1["username"], "password": "test_password"}
        r = self.client.post("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], EXISTS)
        self.assertEqual(r.json[keys[1]], ERROR_ITEM_EXISTS)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new(self):
        """Test the Put method of the User view.

        This test logs in as an administrator user and then tries to create a
        new user, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}

        u = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test"
        }

        r = self.client.put("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], CREATED)
        self.assertEqual(r.json[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertIn("id", result)
        user_id = result["id"]
        self.assertEqual(type(user_id), str)

        # Get user data
        r = self.client.get(f"/users/user/{user_id}", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check data
        for i in ("id", "username", "admin", "enabled", "name"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], u[i])

        for i in ("password", "email"):
            self.assertNotIn(i, user)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_admin(self):
        """Test the Put method of the User view.

        This test logs in as an administrator user and then tries to edit
        itself and another user, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the user fields
        headers = {"Authorization": f"Bearer {access_token}"}

        new_user = {
            "username": self.admin["username"],
            "password": "test_password",
            "admin": True,
            "enabled": True,
            "name": "Admin 2"
        }

        url = f'/users/user/{self.admin["id"]}'
        r = self.client.put(url, headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], UPDATED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get user data
        r = self.client.get(f'/users/user/{self.admin["id"]}', headers=headers)
        user = r.json["result"]

        # Check data
        self.assertEqual(len(user), 7)

        for i in (
            "id", "username", "admin", "enabled", "name", "created",
            "last_modified"
        ):
            self.assertIn(i, user)

            if i not in ("id", "username", "created", "last_modified"):
                self.assertEqual(user[i], new_user[i])

        for i in ("password", "email"):
            self.assertNotIn(i, user)

        self.assertEqual(user["id"], self.admin["id"])
        self.assertEqual(user["username"], self.admin["username"])

        # Edit another user
        new_user = {
            "username": "test2",
            "password": "test_password_2",
            "admin": True,
            "enabled": True,
            "name": "Test 2"
        }

        url = f'/users/user/{self.reg1["id"]}'
        r = self.client.put(url, headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], UPDATED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get user data
        r = self.client.get(f'/users/user/{self.reg1["id"]}', headers=headers)
        user = r.json["result"]

        # Check data
        self.assertEqual(len(user), 7)

        for i in (
            "id", "username", "admin", "enabled", "name", "created",
            "last_modified"
        ):
            self.assertIn(i, user)

            if i not in ("id", "created", "last_modified"):
                self.assertEqual(user[i], new_user[i])

        for i in ("password", "email"):
            self.assertNotIn(i, user)

        self.assertEqual(user["id"], self.reg1["id"])

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_not_admin(self):
        """Test the Put method of the User view.

        This test logs in as a not administrator user and then tries to edit
        itself, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user
        headers = {"Authorization": f"Bearer {access_token}"}

        new_user = {
            "password": "test_password_2",
            "name": "Test 2"
        }

        url = f'/users/user/{self.reg1["id"]}'
        r = self.client.put(url, headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], UPDATED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get user data
        r = self.client.get(f'/users/user/{self.reg1["id"]}', headers=headers)
        user = r.json["result"]

        # Check data
        self.assertEqual(len(user), 7)

        for i in (
            "id", "username", "admin", "enabled", "name", "created",
            "last_modified"
        ):
            self.assertIn(i, user)

        for i in ("password", "email"):
            self.assertNotIn(i, user)

        self.assertEqual(user["id"], self.reg1["id"])
        self.assertEqual(user["username"], self.reg1["username"])
        self.assertFalse(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], new_user["name"])

        # Log in with the old password
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Log in with the new password
        data = {
            "username": self.reg1["username"],
            "password": new_user["password"]
        }

        r = self.client.post("/auth/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_put_new_missing_access_token(self):
        """Test the Put method of the User view.

        This test tries to create a new user without providing the access
        token, which shouldn't work.
        """
        # Create a user without providing the access token
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/users/user", json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_put_edit_missing_access_token(self):
        """Test the Put method of the User view.

        This test tries to edit a user without providing the access token,
        which shouldn't work.
        """
        # Edit user without providing the access token
        u = {"name": "Test User"}
        r = self.client.put(f'/users/user/{self.reg1["id"]}', json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_put_new_invalid_access_token(self):
        """Test the Put method of the User view.

        This test tries to create a new user providing an invalid access token,
        which shouldn't work.
        """
        # Create a user providing an invalid access token
        headers = {"Authorization": "Bearer 1234"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], INVALID_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_INVALID_TOKEN)

    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the User view.

        This test tries to edit a user providing an invalid access token, which
        shouldn't work.
        """
        # Edit user providing an invalid access token
        headers = {"Authorization": "Bearer 1234"}
        u = {"username": "test", "password": "test_password"}

        url = f'/users/user/{self.reg1["id"]}'
        r = self.client.put(url, headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], INVALID_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_unauthorized_user(self):
        """Test the Put method of the User view.

        This test logs in as a not administrator user and then tries to create
        a new user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a new, not administrator, user.
        headers = {"Authorization": f"Bearer {access_token}"}

        u = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True
        }

        r = self.client.put("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_unauthorized_user(self):
        """Test the Put method of the User view.

        This test logs in as a not administrator user, tries to edit some
        fields of itself which are not allowed to be modified and then tries to
        modify another user, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the "username", "admin" and "enabled" fields of the new user
        headers = {"Authorization": f"Bearer {access_token}"}

        user = {
            "username": "test",
            "admin": False,
            "enabled": True
        }

        for i in ("username", "admin", "enabled"):
            # Edit the field
            url = f'/users/user/{self.reg1["id"]}'
            new_user = {i: user[i]}
            r = self.client.put(url, headers=headers, json=new_user)

            # Check status code
            self.assertEqual(r.status_code, 400)

            # Check message
            keys = ("message", "message_type")

            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

        # Edit another user
        url = f'/users/user/{self.reg2["id"]}'
        new_user = {"name": "Test User"}
        r = self.client.put(url, headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_missing_fields(self):
        """Test the Put method of the User view.

        This test tries to create new users with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user without its username
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password"}
        r1 = self.client.put("/users/user", headers=headers, json=u)

        # Create a user without its password
        u = {"username": "test"}
        r2 = self.client.put("/users/user", headers=headers, json=u)

        # Check status codes and messages
        keys = ("message", "message_type")

        for r in (r1, r2):
            # Status code
            self.assertEqual(r.status_code, 400)

            # Message
            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_invalid_fields(self):
        """Test the Put method of the User view.

        This test tries to create a new user providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}

        u = {
            "username": "test_user",
            "password": "test_password",
            "invalid_field": "1234"
        }

        r = self.client.put("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_invalid_fields(self):
        """Test the Put method of the User view.

        This test tries to edit a user providing some invalid/unexpected field,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"], "password":
            self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password", "invalid_field": "1234"}

        url = f'/users/user/{self.reg1["id"]}'
        r = self.client.put(url, headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_password_length(self):
        """Test the Put method of the User view.

        This test tries to create a new user with a password that has less than
        8 characters and another user with a password that has more than 100
        characters, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create users
        headers = {"Authorization": f"Bearer {access_token}"}
        keys = ("message", "message_type")

        for i, p in enumerate(("test", "test" * 100)):
            u = {"username": f"test{i}", "password": p}
            r = self.client.put("/users/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

            # Check message
            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_password_length(self):
        """Test the Put method of the User view.

        This test logs in as some user, tries to change its password with a new
        one that has less than 8 characters and then tries to change it with
        another one that has more than 100 characters, which shouldn't work in
        either case.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            url = f'/users/user/{self.reg1["id"]}'
            u = {"password": p}
            r = self.client.put(url, headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

            # Check message
            keys = ("message", "message_type")

            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_user_exists(self):
        """Test the Put method of the User view.

        This test tries to create a new user with the same username of another
        user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": self.reg1["username"], "password": "test_password"}
        r = self.client.put("/users/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], EXISTS)
        self.assertEqual(r.json[keys[1]], ERROR_ITEM_EXISTS)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_user_not_found(self):
        """Test the Put method of the User view.

        This tries to edit some user that doesn't exist, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user that doesn't exist
        url = f"/users/user/{get_uuid()}"
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": self.admin["username"], "name": "Test"}
        r = self.client.put(url, headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 404)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], NOT_FOUND)
        self.assertEqual(r.json[keys[1]], ERROR_ITEM_NOT_FOUND)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete(self):
        """Test the Delete method of the User view.

        This test logs in as an administrator user and tries to delete a user,
        which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete user
        url = f'/users/user/{self.reg1["id"]}'
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], DELETED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get the user list
        r = self.client.get("/users/users", headers=headers)
        users = r.json["result"]

        # Check list
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["id"], self.admin["id"])
        self.assertEqual(users[1]["id"], self.reg2["id"])

    def test_delete_missing_access_token(self):
        """Test the Delete method of the User view.

        This test tries to delete some user without providing the access token,
        which shouldn't work.
        """
        # Delete user
        r = self.client.delete(f'/users/user/{self.reg1["id"]}')

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the User view.

        This test tries to delete some user providing an invalid access token,
        which shouldn't work.
        """
        # Delete user providing an invalid access token
        url = f'/users/user/{self.reg1["id"]}'
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.delete(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], INVALID_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete_access_token_not_fresh(self):
        """Test the Delete method of the User view.

        This test tries to delete some user providing a not fresh access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        refresh_token = r.json["result"]["refresh_token"]

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.get("/auth/refresh", headers=headers)
        access_token = r.json["result"]["access_token"]

        # Delete user
        url = f'/users/user/{self.reg1["id"]}'
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], NOT_FRESH_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_NOT_FRESH_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete_unauthorized_user(self):
        """Test the Delete method of the User view.

        This test logs in as a not administrator user and then tries to delete
        itself and another user, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete users
        headers = {"Authorization": f"Bearer {access_token}"}
        keys = ("message", "message_type")

        for i in (self.reg1["id"], self.reg2["id"]):
            r = self.client.delete(f"/users/user/{i}", headers=headers)

            # Check status code
            self.assertEqual(r.status_code, 403)

            # Check message
            for i in keys:
                self.assertIn(i, r.json)

            self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
            self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete_user_not_found(self):
        """Test the Delete method of the User view.

        This test tries to delete a user that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete a user with an ID that doesn't exist
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/users/user/{get_uuid()}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], NOT_FOUND)
        self.assertEqual(r.json[keys[1]], ERROR_ITEM_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
