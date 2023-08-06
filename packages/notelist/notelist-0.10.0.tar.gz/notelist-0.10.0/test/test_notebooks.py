"""Notebook resources unit tests."""

import unittest
from unittest.mock import patch

import envvars
import mocks
import common

from notelist.tools import get_uuid

from notelist.responses import (
    METHOD_NOT_ALLOWED, MISSING_TOKEN, INVALID_TOKEN, NOT_FRESH_TOKEN,
    USER_UNAUTHORIZED, OK, ERROR_METHOD_NOT_ALLOWED, ERROR_MISSING_TOKEN,
    ERROR_INVALID_TOKEN, ERROR_NOT_FRESH_TOKEN, ERROR_UNAUTHORIZED_USER,
    ERROR_VALIDATION, ERROR_ITEM_EXISTS
)

from notelist.views.notebooks import (
    RETRIEVED_1, RETRIEVED, CREATED, UPDATED, DELETED, EXISTS
)


class NotebookListTestCase(common.BaseTestCase):
    """Notebook List resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get(self):
        """Test the Get method of the Notebook List view.

        This test logs in as some user, creates some notebooks and then tries
        to get the user's notebook list, which should work.
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
        r = self.client.get("/notebooks/notebooks", headers=headers)
        res_data = r.json

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", res_data)
        notebooks = res_data["result"]
        self.assertEqual(type(notebooks), list)

        # Check list
        self.assertEqual(len(notebooks), 0)

        # Create notebook
        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        res_data = r.json
        notebook_id = res_data["result"]["id"]

        # Get list
        r = self.client.get("/notebooks/notebooks", headers=headers)
        res_data = r.json

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], RETRIEVED_1)
        self.assertEqual(res_data[keys[1]], OK)

        # Check result
        self.assertIn("result", res_data)
        notebooks = res_data["result"]
        self.assertEqual(type(notebooks), list)

        # Check list
        self.assertEqual(len(notebooks), 1)
        notebook = notebooks[0]

        for i in ("id", "name", "tag_colors"):
            self.assertIn(i, notebook)

        self.assertEqual(notebook["id"], notebook_id)
        self.assertEqual(notebook["name"], n["name"])
        self.assertEqual(notebook["tag_colors"], n["tag_colors"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Notebook List view.

        This test tries to get the notebook list of the request user without
        providing the access token, which shouldn't work.
        """
        # Get list without providing the access token
        r = self.client.get("/notebooks/notebooks")
        res_data = r.json

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook List view.

        This test tries to get the user's notebook list providing an invalid
        access token, which shouldn't work.
        """
        # Get list providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/notebooks/notebooks", headers=headers)
        res_data = r.json

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    def test_post(self):
        """Test the Post method of the Notebook List view.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/notebooks/notebooks")

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
        """Test the Put method of the Notebook List view.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/notebooks/notebooks")

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
        """Test the Delete method of the Notebook List view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/notebooks/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(res_data[keys[1]], ERROR_METHOD_NOT_ALLOWED)


class NotebookTestCase(common.BaseTestCase):
    """Notebook resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get(self):
        """Test the Get method of the Notebook view.

        This test logs in as some user, creates a notebook and then tries to
        get this notebook, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Get the data of the notebook
        url = f"/notebooks/notebook/{notebook_id}"
        r = self.client.get(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], RETRIEVED)
        self.assertEqual(res_data[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        notebook = r.json["result"]
        self.assertEqual(type(notebook), dict)

        # Check notebook
        self.assertEqual(len(notebook), 5)

        for i in ("id", "name", "tag_colors", "created", "last_modified"):
            self.assertIn(i, notebook)

        self.assertEqual(notebook["id"], notebook_id)

        for i in ("name", "tag_colors"):
            self.assertEqual(notebook[i], n[i])

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_missing_access_token(self):
        """Test the Get method of the Notebook view.

        This test tries to get a notebook without providing the access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Get notebook without providing the access token
        r = self.client.get(f"/notebooks/notebook/{notebook_id}")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook view.

        This test tries to get a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Get notebook providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        url = f"/notebooks/notebook/{notebook_id}"
        r = self.client.get(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_unauthorized_user(self):
        """Test the Get method of the Notebook view.

        This test tries to get a notebook of some user as another user, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"/notebooks/notebook/{notebook_id}"
        r = self.client.get(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(res_data[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get_notebook_not_found(self):
        """Test the Get method of the Notebook view.

        This test tries to get a notebook that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        _id = get_uuid()
        r = self.client.get(f"/notebooks/notebook/{_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(res_data[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post(self):
        """Test the Post method of the Notebook view.

        This test tries to create a notebook, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], CREATED)
        self.assertEqual(res_data[keys[1]], OK)

        # Check result
        self.assertIn("result", r.json)
        result = res_data["result"]
        self.assertIn("id", result)
        notebook_id = result["id"]
        self.assertEqual(type(notebook_id), str)

    def test_post_missing_access_token(self):
        """Test the Post method of the Notebook view.

        This test tries to create a notebook without providing the access
        token, which shouldn't work.
        """
        # Create notebook
        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Notebook view.

        This test tries to create a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Create notebook providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_missing_fields(self):
        """Test the Post method of the Notebook view.

        This test tries to create a notebook with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook (without data)
        headers = {"Authorization": f"Bearer {access_token}"}
        r1 = self.client.post("/notebooks/notebook", headers=headers)

        # Create notebook (with empty data)
        r2 = self.client.post(
            "/notebooks/notebook", headers=headers, json=dict()
        )

        # Check status codes and messages
        for r in (r1, r2):
            self.assertEqual(r.status_code, 400)
            r_data = r.json
            self.assertIn("message", r_data)
            self.assertIn("message_type", r_data)
            self.assertEqual(r_data["message_type"], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_user(self):
        """Test the Post method of the Notebook view.

        This test tries to create a new notebook specifying its user, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "user_id": self.reg1["id"],
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post(url, headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_invalid_fields(self):
        """Test the Post method of the Notebook view.

        This test tries to create a notebook providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook", "invalid_field": "1234"}
        r = self.client.post("/notebooks/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_notebook_exists(self):
        """Test the Post method of the Notebook view.

        This test tries to create a notebook with the same name of an existing
        notebook of the request user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create same notebook again
        r = self.client.post("/notebooks/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], EXISTS)
        self.assertEqual(res_data[keys[1]], ERROR_ITEM_EXISTS)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new(self):
        """Test the Put method of the Notebook view.

        This test tries to create a notebook, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put("/notebooks/notebook", headers=headers, json=n)
        res_data = r.json

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertIn("id", result)
        notebook_id = result["id"]
        self.assertEqual(type(notebook_id), str)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], CREATED)
        self.assertEqual(res_data[keys[1]], OK)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit(self):
        """Test the Put method of the Notebook view.

        This test tries to edit one of the request user's notebooks, which
        should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Edit notebook
        new_notebook = {
            "name": "Test Notebook 2",
            "tag_colors": {"tag3": "#ff0000"}
        }

        url = f"/notebooks/notebook/{notebook_id}"
        r = self.client.put(url, headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], UPDATED)
        self.assertEqual(res_data[keys[1]], OK)

        # Get notebook
        url = f"/notebooks/notebook/{notebook_id}"
        r = self.client.get(url, headers=headers)
        notebook = r.json["result"]

        # Check data
        self.assertEqual(len(notebook), 5)

        for i in ("id", "name", "tag_colors", "created", "last_modified"):
            self.assertIn(i, notebook)

        self.assertEqual(notebook["id"], notebook_id)

        for i in ("name", "tag_colors"):
            self.assertEqual(notebook[i], new_notebook[i])

        # Edit notebook without setting the tag colors
        new_notebook = {"name": "Test Notebook 3"}
        self.client.put(url, headers=headers, json=new_notebook)

        # Get notebook
        r = self.client.get(url, headers=headers)
        notebook = r.json["result"]

        # Check data
        self.assertEqual(len(notebook), 4)

        for i in ("id", "name", "created", "last_modified"):
            self.assertIn(i, notebook)

        self.assertNotIn("tag_colors", notebook)
        self.assertEqual(notebook["name"], new_notebook["name"])

    def test_put_new_missing_access_token(self):
        """Test the Put method of the Notebook view.

        This test tries to create a new notebook without providing the access
        token, which shouldn't work.
        """
        # Create notebook without providing the access token
        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put("/notebooks/notebook", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_edit_new_missing_access_token(self):
        """Test the Put method of the Notebook view.

        This test tries to edit a notebook without providing the access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Edit notebook without providing the access token
        n = {"name": "Test Notebook"}
        r = self.client.put(f"/notebooks/notebook/{notebook_id}", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], MISSING_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_MISSING_TOKEN)

    def test_put_new_invalid_access_token(self):
        """Test the Put method of the Notebook view.

        This test tries to create a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Create notebook providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put("/notebooks/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the Notebook view.

        This test tries to edit a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Edit notebook providing an invalid access token ("1234")
        url = f"/notebooks/notebook/{notebook_id}"
        headers = {"Authorization": "Bearer 1234"}
        n = {"name": "Test Notebook"}
        r = self.client.put(url, headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], INVALID_TOKEN)
        self.assertEqual(res_data[keys[1]], ERROR_INVALID_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_unauthorized_user(self):
        """Test the Get method of the Notebook view.

        This test creates a notebook of some user, and then tries to edit the
        notebook as another user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebooks/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the notebook as the administrator user
        url = f"/notebooks/notebook/{notebook_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        new_notebook = {"name": "Test Notebook 2"}
        r = self.client.put(url, headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(res_data[keys[1]], ERROR_UNAUTHORIZED_USER)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_missing_fields(self):
        """Test the Put method of the Notebook view.

        This test tries to create a notebook with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook (without data)
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}
        r1 = self.client.put(url, headers=headers)

        # Create notebook (with empty data)
        r2 = self.client.put(url, headers=headers, json=dict())

        # Check status codes and messages
        for r in (r1, r2):
            self.assertEqual(r.status_code, 400)
            r_data = r.json
            self.assertIn("message", r_data)
            self.assertIn("message_type", r_data)
            self.assertEqual(r_data["message_type"], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_user(self):
        """Test the Put method of the Notebook view.

        This test tries to create a notebook specifying its user, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "user_id": self.reg1["id"],
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put(url, headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_invalid_fields(self):
        """Test the Put method of the Notebook view.

        This test tries to create a notebook providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook providing an invalid field
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook", "invalid_field": "1234"}
        r = self.client.put(url, headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_user(self):
        """Test the Put method of the Notebook view.

        This test tries to change the user of some notebook, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Change notebook user
        url = f"/notebooks/notebook/{notebook_id}"
        new_notebook = {"user_id": self.reg2["id"]}
        r = self.client.put(url, headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[1]], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit_invalid_fields(self):
        """Test the Put method of the Notebook view.

        This test tries to edit a notebook providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Edit the notebook providing an invalid field
        url = f"/notebooks/notebook/{notebook_id}"
        n = {"name": "Test Notebook", "invalid_field": "1234"}
        r = self.client.put(url, headers=headers, json=n)

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
    def test_put_new_notebook_exists(self):
        """Test the Put method of the Notebook view.

        This test tries to create a notebook with the same name of an existing
        notebook of the request user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        url = "/notebooks/notebook"

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put(url, headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create another notebook with the same name
        n = {"name": "Test Notebook"}
        r = self.client.put(url, headers=headers, json=n)

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
    def test_put_edit_notebook_not_found(self):
        """Test the Put method of the Notebook view.

        This test tries to edit a notebook that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit notebook that doesn't exist
        url = f"/notebooks/notebook/{get_uuid()}"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put(url, headers=headers, json=n)

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
    def test_delete(self):
        """Test the Delete method of the Notebook view.

        This test creates a notebook and then tries to delete it, which should
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.put(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Get user notebook list
        r = self.client.get("/notebooks/notebooks", headers=headers)
        notebooks = r.json["result"]

        # Check list
        self.assertEqual(len(notebooks), 1)
        self.assertEqual(notebooks[0]["name"], n["name"])

        # Delete notebook
        url = f"/notebooks/notebook/{notebook_id}"
        r = self.client.delete(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], DELETED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get user notebook list
        r = self.client.get("/notebooks/notebooks", headers=headers)
        notebooks = r.json["result"]

        # Check list
        self.assertEqual(len(notebooks), 0)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete_missing_access_token(self):
        """Test the Delete method of the Notebook view.

        This test tries to delete an existing notebook without providing the
        access token, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Delete notebook without providing the access token
        r = self.client.delete(f"/notebooks/notebook/{notebook_id}")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete_invalid_access_token(self):
        """Test the Delete method of the Notebook view.

        This test tries to delete a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Delete notebook providing an invalid access token ("1234")
        url = f"/notebooks/notebook/{notebook_id}"
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
        """Test the Delete method of the Notebook view.

        This test tries to delete some notebook providing a not fresh access
        token, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        result = self.client.post("/auth/login", json=data).json["result"]
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Get a new, not fresh, access token
        url = "/auth/refresh"
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.get(url, headers=headers)
        access_token = r.json["result"]["access_token"]

        # Delete notebook
        url = f"/notebooks/notebook/{notebook_id}"
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
        """Test the Delete method of the Notebook view.

        This test tries to delete a notebook of a user different than the
        request user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        url = "/notebooks/notebook"
        headers = {"Authorization": f"Bearer {access_token}"}

        n = {
            "name": "Test Notebook",
            "tag_colors": {"tag1": "#00ff00", "tag2": "#0000ff"}
        }

        r = self.client.post(url, headers=headers, json=n)
        notebook_id = r.json["result"]["id"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete notebook
        url = f"/notebooks/notebook/{notebook_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(url, headers=headers)

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
    def test_delete_notebook_not_found(self):
        """Test the Delete method of the Notebook view.

        This test tries to delete a notebook that doesn't exist, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]
        }

        r = self.client.post("/auth/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete notebook that doesn't exist
        url = f"/notebooks/notebook/{get_uuid()}"
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(url, headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], USER_UNAUTHORIZED)
        self.assertEqual(r.json[keys[1]], ERROR_UNAUTHORIZED_USER)


if __name__ == "__main__":
    unittest.main()
