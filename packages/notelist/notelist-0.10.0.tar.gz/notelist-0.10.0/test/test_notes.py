"""Note resources unit tests."""

import time
import unittest
from unittest.mock import patch
from typing import Optional

import envvars
import mocks
import common

from notelist.tools import get_uuid

from notelist.responses import (
    URL_NOT_FOUND, METHOD_NOT_ALLOWED, MISSING_TOKEN, INVALID_TOKEN,
    USER_UNAUTHORIZED, OK, ERROR_URL_NOT_FOUND, ERROR_METHOD_NOT_ALLOWED,
    ERROR_MISSING_TOKEN, ERROR_INVALID_TOKEN, ERROR_UNAUTHORIZED_USER,
    ERROR_VALIDATION
)

from notelist.views.notes import (
    RETRIEVED_1, RETRIEVED_N, RETRIEVED, CREATED, UPDATED, DELETED
)


def _get_tags() -> list[str]:
    """Return test tags.

    :return: Tag list.
    """
    return ["Test Tag 1", "Test Tag 2"]


def _get_notes(notebook_id: str, tags: list[str]) -> list[dict]:
    """Return test notes.

    :param notebook_id: Notebook ID.
    :param tags: Tags.
    :return: List containing note dictionaries.
    """
    return [{
        "notebook_id": notebook_id,
        "archived": False,
        "title": "Test Note 1",
        "body": "This is a test note",
        "tags": tags
    }, {
        "notebook_id": notebook_id,
        "archived": False,
        "title": "Test Note 2",
        "body": "This is another test note",
        "tags": [tags[0]]
    }, {
        "notebook_id": notebook_id,
        "archived": True,
        "title": "Test Note 3",
        "body": "Another note",
        "tags": [tags[1]]
    }, {
        "notebook_id": notebook_id,
        "archived": True,
        "title": "Test Note 4",
        "body": "Another note",
        "tags": []
    }]


def _login(client, username: str, password: str) -> dict[str, str]:
    """Log in.

    :param client: Test API client.
    :param username: Username.
    :param password: Password.
    :return: Headers with the access token.
    """
    data = {"username": username, "password": password}
    r = client.post("/auth/login", json=data)
    access_token = r.json["result"]["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


def _create_notebook(client, headers: dict[str, str]) -> str:
    """Create a notebook.

    :param client: Test API client.
    :param headers: Headers with the access token.
    :return: Notebook ID.
    """
    n = {"name": "Test Notebook"}
    r = client.post("/notebooks/notebook", headers=headers, json=n)

    return r.json["result"]["id"]


def _create_notes(
    client, headers: dict[str, str], notes: list[dict],
    delay: Optional[int] = None
) -> list[str]:
    """Create notes.

    :param client: Test API client.
    :param headers: Headers with the access token.
    :param notes: Notes.
    :param delay: Delay in seconds between note creations, in order to make the
    notes timestamps different.
    :return: Note IDs.
    """
    note_ids = []

    for n in notes:
        r = client.post("/notes/note", headers=headers, json=n)
        note_ids.append(r.json["result"]["id"])

        if delay:
            time.sleep(delay)

    return note_ids


class NoteListTestCase(common.BaseTestCase):
    """Note List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Note List view.

        This test tries to call the Get method, which shouldn't work.
        """
        r1 = self.client.get("/notes/notes")
        r2 = self.client.get(f"/notes/notes/{get_uuid()}")

        # Check status codes
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

        # Check messages
        keys = ("message", "message_type")

        for r in (r1, r2):
            for i in keys:
                self.assertIn(i, r.json)

        self.assertEqual(r1.json[keys[0]], URL_NOT_FOUND)
        self.assertEqual(r1.json[keys[1]], ERROR_URL_NOT_FOUND)

        self.assertEqual(r2.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r2.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get the all the notes of the notebook, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all notes
        r = self.client.post(f"/notes/notes/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(
            res_data[keys[0]], RETRIEVED_N.format(4)
        )

        self.assertEqual(res_data[keys[1]], OK)

        # Check list
        res_notes = res_data["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), len(notes))

        for n in res_notes:
            self.assertEqual(type(n), dict)
            self.assertEqual(len(n), 6)

            for j in (
                "id", "archived", "title", "tags", "created", "last_modified"
            ):
                self.assertIn(j, n)

            for j in ("notebook_id", "body"):
                self.assertNotIn(j, n)

            self.assertEqual(type(n["tags"]), list)
            self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_active(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the active notes of the notebook, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all active notes
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": False}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(
            res_data[keys[0]], RETRIEVED_N.format(2)
        )

        self.assertEqual(res_data[keys[1]], OK)

        # Check list
        res_notes = res_data["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 2)

        for n in res_notes:
            self.assertEqual(type(n), dict)
            self.assertEqual(len(n), 6)

            for j in (
                "id", "archived", "title", "tags", "created", "last_modified"
            ):
                self.assertIn(j, n)

            for j in ("notebook_id", "body"):
                self.assertNotIn(j, n)

            self.assertFalse(n["archived"])
            self.assertEqual(type(n["tags"]), list)
            self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_active_tags(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the active notes of the notebook that have any tag of a given
        list of tags, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all active notes with the second tag
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": False, "tags": [tags[1]]}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], RETRIEVED_1)
        self.assertEqual(res_data[keys[1]], OK)

        # Check list
        res_notes = res_data["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 1)

        n = res_notes[0]

        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 6)

        for i in (
            "id", "archived", "title", "tags", "created", "last_modified"
        ):
            self.assertIn(i, n)

        for i in ("notebook_id", "body"):
            self.assertNotIn(i, n)

        self.assertFalse(n["archived"])
        self.assertEqual(type(n["tags"]), list)
        self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_active_tags_no_tags(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the active notes of the notebook that have any tag of a given
        list of tags and all the active notes of the notebook that don't have
        any tag, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all active notes with the second tag
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": False, "tags": [tags[1]], "no_tags": True}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(res_data[keys[0]], RETRIEVED_1)
        self.assertEqual(res_data[keys[1]], OK)

        # Check list
        res_notes = res_data["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 1)

        n = res_notes[0]
        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 6)

        for i in (
            "id", "archived", "title", "tags", "created", "last_modified"
        ):
            self.assertIn(i, n)

        for i in ("notebook_id", "body"):
            self.assertNotIn(i, n)

        self.assertFalse(n["archived"])
        self.assertEqual(type(n["tags"]), list)
        self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_inactive(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the inactive notes of the notebook, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all archived notes
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": True}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(
            res_data[keys[0]], RETRIEVED_N.format(2)
        )

        self.assertEqual(res_data[keys[1]], OK)

        # Check list
        res_notes = res_data["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 2)

        for n in res_notes:
            self.assertEqual(type(n), dict)
            self.assertEqual(len(n), 6)

            for k in (
                "id", "archived", "title", "tags", "created", "last_modified"
            ):
                self.assertIn(k, n)

            for k in ("notebook_id", "body"):
                self.assertNotIn(k, n)

            self.assertTrue(n["archived"])
            self.assertEqual(type(n["tags"]), list)
            self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_inactive_tags(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the inactive notes of the notebook that have any tag of a given
        list of tags, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all archived notes with the second tag
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": True, "tags": [tags[1]]}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_1)
        self.assertEqual(r.json[keys[1]], OK)

        # Check list
        res_notes = r.json["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 1)

        n = res_notes[0]

        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 6)

        for i in (
            "id", "archived", "title", "tags", "created", "last_modified"
        ):
            self.assertIn(i, n)

        for i in ("notebook_id", "body"):
            self.assertNotIn(i, n)

        self.assertTrue(n["archived"])
        self.assertEqual(type(n["tags"]), list)
        self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_inactive_tags_no_tags(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the inactive notes of the notebook that have any tag of a given
        list of tags and all the inactive notes of the notebook that don't have
        any tag, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all archived notes with the second tag
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": True, "tags": [tags[1]], "no_tags": True}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_N.format(2))
        self.assertEqual(r.json[keys[1]], OK)

        # Check list
        res_notes = r.json["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 2)

        for n in res_notes:
            self.assertEqual(type(n), dict)
            self.assertEqual(len(n), 6)

            for k in (
                "id", "archived", "title", "tags", "created", "last_modified"
            ):
                self.assertIn(k, n)

            for k in ("notebook_id", "body"):
                self.assertNotIn(k, n)

            self.assertTrue(n["archived"])
            self.assertEqual(type(n["tags"]), list)
            self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_tags(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook that have any tag of a given list of
        tags, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all notes with the second tag
        url = f"/notes/notes/{notebook_id}"
        f = {"tags": [tags[1]]}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_N.format(2))
        self.assertEqual(r.json[keys[1]], OK)

        # Check list
        res_notes = r.json["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 2)

        for n in res_notes:
            self.assertEqual(type(n), dict)
            self.assertEqual(len(n), 6)

            for k in (
                "id", "archived", "title", "tags", "created", "last_modified"
            ):
                self.assertIn(k, n)

            for k in ("notebook_id", "body"):
                self.assertNotIn(k, n)

            self.assertEqual(type(n["tags"]), list)
            self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_tags_no_tags(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook that have any tag of a given list of
        tags and all the notes of the notebook that don't have any tag, which
        should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all notes with the second tag
        url = f"/notes/notes/{notebook_id}"
        f = {"tags": [tags[1]], "no_tags": True}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        res_data = r.json
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, res_data)

        self.assertEqual(
            res_data[keys[0]], RETRIEVED_N.format(3)
        )

        self.assertEqual(res_data[keys[1]], OK)

        # Check list
        res_notes = res_data["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 3)

        for n in res_notes:
            self.assertEqual(type(n), dict)
            self.assertEqual(len(n), 6)

            for k in (
                "id", "archived", "title", "tags", "created", "last_modified"
            ):
                self.assertIn(k, n)

            for k in ("notebook_id", "body"):
                self.assertNotIn(k, n)

            self.assertEqual(type(n["tags"]), list)
            self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_no_tags_1(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook that don't have any tag, which should
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all notes without tags
        url = f"/notes/notes/{notebook_id}"
        f = {"tags": [], "no_tags": True}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_1)
        self.assertEqual(r.json[keys[1]], OK)

        # Check list
        res_notes = r.json["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 1)

        n = res_notes[0]

        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 6)

        for i in (
            "id", "archived", "title", "tags", "created", "last_modified"
        ):
            self.assertIn(i, n)

        for i in ("notebook_id", "body"):
            self.assertNotIn(i, n)

        self.assertEqual(type(n["tags"]), list)
        self.assertTrue(all(map(lambda t: type(t) == str, n["tags"])))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_no_tags_2(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook filtering by tags with an empty tag
        list and without selecting the notes that have no tags (which should be
        no notes), which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get all notes without tags
        url = f"/notes/notes/{notebook_id}"
        f = {"tags": []}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_N.format(0))
        self.assertEqual(r.json[keys[1]], OK)

        # Check list
        res_notes = r.json["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 0)

        # Get all notes without tags
        url = f"/notes/notes/{notebook_id}"
        f = {"tags": [], "no_tags": False}
        r = self.client.post(url, headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 0)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_last_mod(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook sorted by their Last Modified
        timestamp, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes, 1)

        # Edit the second note
        url = f"/notes/note/{note_ids[1]}"
        n = {"notebook_id": notebook_id, "title": "New title"}
        r = self.client.put(url, headers=headers, json=n)

        # Get notes sorted by Last Modified timetamp (ascending)
        url = f"/notes/notes/{notebook_id}"
        f = {"last_mod": True}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], RETRIEVED_N.format(4))
        self.assertEqual(r.json[keys[1]], OK)

        # Check list
        res_notes = r.json["result"]
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), len(notes))

        # Get notes sorted by Last Modified timetamp (descending)
        url = f"/notes/notes/{notebook_id}"
        f = {"last_mod": True, "asc": False}
        r = self.client.post(url, headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), len(notes))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_missing_access_token(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and some notes and then
        tries to get all the notes of the notebook without providing the access
        token, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get notes
        r = self.client.post(f"/notes/notes/{notebook_id}")

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
    def test_post_invalid_access_token(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get notes providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.post(f"/notes/notes/{notebook_id}", headers=headers)

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
    def test_post_invalid_invalid_field(self):
        """Test the Post method of the Note List view.

        This test creates a notebook with some tags and some notes and then
        tries to get all the notes of the notebook providing an invalid field,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create notes
        tags = _get_tags()
        notes = _get_notes(notebook_id, tags)
        _create_notes(self.client, headers, notes)

        # Get notes providing an invalid field
        url = f"/notes/notes/{notebook_id}"
        f = {"archived": False, "invalid_field": 1}
        r = self.client.post(url, headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[1]], ERROR_VALIDATION)

    def test_put(self):
        """Test the Put method of the Note List view.

        This test tries to call the Put method, which shouldn't work.
        """
        r1 = self.client.put("/notes/notes")
        r2 = self.client.put(f"/notes/notes/{get_uuid()}")

        # Check status codes
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

        # Check messages
        keys = ("message", "message_type")

        for r in (r1, r2):
            for i in keys:
                self.assertIn(i, r.json)

        self.assertEqual(r1.json[keys[0]], URL_NOT_FOUND)
        self.assertEqual(r1.json[keys[1]], ERROR_URL_NOT_FOUND)

        self.assertEqual(r2.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r2.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """Test the Delete method of the Note List view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r1 = self.client.delete("/notes/notes")
        r2 = self.client.delete(f"/notes/notes/{get_uuid()}")

        # Check status codes
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

        # Check messages
        keys = ("message", "message_type")

        for r in (r1, r2):
            for i in keys:
                self.assertIn(i, r.json)

        self.assertEqual(r1.json[keys[0]], URL_NOT_FOUND)
        self.assertEqual(r1.json[keys[1]], ERROR_URL_NOT_FOUND)

        self.assertEqual(r2.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r2.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)


class NoteTestCase(common.BaseTestCase):
    """Note resource unit tests."""

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_get(self):
        """Test the Get method of the Note view.

        This test creates a notebook with a note and then tries to get the
        note, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        tags = _get_tags()
        n = _get_notes(notebook_id, tags)[0]
        note_id = _create_notes(self.client, headers, [n])[0]

        # Get note
        r = self.client.get(f"/notes/note/{note_id}", headers=headers)

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
        note = r.json["result"]
        self.assertEqual(type(note), dict)
        self.assertEqual(len(note), 8)

        for i in (
            "id", "notebook_id", "archived", "title", "body", "tags",
            "created", "last_modified"
        ):
            self.assertIn(i, note)

        self.assertEqual(note["id"], note_id)

        for i in ("archived", "title", "body", "tags"):
            self.assertEqual(note[i], n[i])

    def test_get_missing_access_token(self):
        """Test the Get method of the Note view.

        This test tries to get the data of some note without providing the
        access token, which shouldn't work.
        """
        # Get note (that doesn't exist) without providing the access token
        r = self.client.get(f"/notes/note/{get_uuid()}")

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], MISSING_TOKEN)
        self.assertEqual(r.json[keys[1]], ERROR_MISSING_TOKEN)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Note view.

        This test tries to get the data of some note providing an invalid
        access token, which shouldn't work.
        """
        # Get note (that doesn't exist) providing an invalid access token
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get(f"/notes/note/{get_uuid()}", headers=headers)

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
        """Test the Get method of the Note view.

        This test tries to get a note of a user from another user, which
        shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        tags = _get_tags()
        n = _get_notes(notebook_id, tags)[0]
        note_id = _create_notes(self.client, headers, [n])[0]

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Get note
        r = self.client.get(f"/notes/note/{note_id}", headers=headers)

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
    def test_get_note_not_found(self):
        """Test the Get method of the Note view.

        This test tries to get a note that doesn't exist, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Get note that doesn't exist
        _id = get_uuid()
        r = self.client.get(f"/notes/note/{_id}", headers=headers)

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
    def test_post(self):
        """Test the Post method of the Note view.

        This test tries to create a note, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.post("/notes/note", headers=headers, json=n)

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
        note_id = result["id"]
        self.assertEqual(type(note_id), str)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_missing_access_token(self):
        """Test the Post method of the Note view.

        This test tries to create a note without providing the access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.post("/notes/note", json=n)

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
    def test_post_invalid_access_token(self):
        """Test the Post method of the Note view.

        This test tries to create a note providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create a note providing an invalid access token ("1234")
        url = "/notes/note"
        headers = {"Authorization": "Bearer 1234"}

        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.post(url, headers=headers, json=n)

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
    def test_post_missing_fields(self):
        """Test the Post method of the Note view.

        This test tries to create a note with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        _create_notebook(self.client, headers)

        # Create note (without data)
        r1 = self.client.post("/notes/note", headers=headers)

        # Create note (without the notebook ID)
        r2 = self.client.post("/notes/note", headers=headers, json=dict())

        # Check status codes and messages
        for r in (r1, r2):
            self.assertEqual(r1.status_code, 400)
            r_data = r.json
            self.assertIn("message", r_data)
            self.assertIn("message_type", r_data)
            self.assertEqual(r_data["message_type"], ERROR_VALIDATION)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_post_invalid_fields(self):
        """Test the Post method of the Note view.

        This test tries to create a note providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create a note with an invalid field ("invalid_field")
        n = {"notebook_id": notebook_id, "invalid_field": 1}
        r = self.client.post("/notes/note", headers=headers, json=n)

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
    def test_post_notebook_user_unauthorized(self):
        """Test the Post method of the Note view.

        This test tries to create a note for a notebook that doesn't belong to
        the request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create note
        n = {"notebook_id": notebook_id}
        r = self.client.post("/notes/note", headers=headers, json=n)

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
    def test_post_notebook_not_found(self):
        """Test the Post method of the Note view.

        This test tries to create a note for a notebook that doesn't exist,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create note for a notebook that doesn't exist
        n = {"notebook_id": get_uuid()}
        r = self.client.post("/notes/note", headers=headers, json=n)

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
    def test_put_new(self):
        """Test the Put method of the Note view.

        This test tries to create a note, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)

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
        note_id = result["id"]
        self.assertEqual(type(note_id), str)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_edit(self):
        """Test the Put method of the Note view.

        This test tries to edit one of the notes of one of the request user's
        notebooks, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Edit note
        url = f"/notes/note/{note_id}"

        new_note = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]
        }

        r = self.client.put(url, headers=headers, json=new_note)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], UPDATED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get note
        r = self.client.get(f"/notes/note/{note_id}", headers=headers)
        note = r.json["result"]

        self.assertEqual(len(note), 8)

        # Check note
        for i in (
            "id", "notebook_id", "archived", "title", "body", "tags",
            "created", "last_modified"
        ):
            self.assertIn(i, note)

        self.assertEqual(note["id"], note_id)

        for i in ("archived", "title", "body", "tags"):
            self.assertEqual(note[i], new_note[i])

        self.assertEqual(type(note["tags"]), list)
        self.assertEqual(len(note["tags"]), len(new_note["tags"]))

        # Check that all the tags of the retrieved note are the ones expected
        m = map(lambda x: x in new_note["tags"], note["tags"])
        self.assertTrue(all(m))

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_put_new_missing_access_token(self):
        """Test the Put method of the Note view.

        This test tries to create a note without providing the access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", json=n)

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
    def test_put_edit_missing_access_token(self):
        """Test the Put method of the Note view.

        This test tries to edit one of the notes of one of the request user's
        notebooks without providing the access token, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Edit note
        new_note = {
            "archived": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]
        }

        r = self.client.put(f"/notes/note/{note_id}", json=new_note)

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
    def test_put_new_invalid_access_token(self):
        """Test the Put method of the Note view.

        This test tries to create a note providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}

        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)

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
    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the Note view.

        This test tries to edit a note providing an invalid access token, which
        shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Edit note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}

        new_note = {
            "archived": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]
        }

        r = self.client.put(
            f"/notes/note/{note_id}", headers=headers, json=new_note
        )

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
    def test_put_new_missing_fields(self):
        """Test the Put method of the Note view.

        This test tries to create a note with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        _create_notebook(self.client, headers)

        # Create note without data
        r = self.client.put("/notes/note", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create note without the notebook ID
        n = {
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)

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
    def test_put_new_invalid_fields(self):
        """Test the Put method of the Note view.

        This test tries to create a note providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note with an invalid field ("invalid_field")
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"],
            "invalid_field": 1
        }

        r = self.client.put("/notes/note", headers=headers, json=n)

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
        """Test the Put method of the Note view.

        This test tries to edit a note providing some invalid/unexpected field,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Edit note with an invalid field ("invalid_field")
        url = f"/notes/note/{note_id}"

        new_note = {
            "archived": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"],
            "invalid_field": 1
        }

        r = self.client.put(url, headers=headers, json=new_note)

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
    def test_put_new_notebook_user_unauthorized(self):
        """Test the Put method of the Note view.

        This test tries to create a note for a notebook that doesn't belong to
        the request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)

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
    def test_put_edit_notebook_user_unauthorized(self):
        """Test the Put method of the Note view.

        This test tries to edit a note by changing its notebook to one that
        doesn't belong to the request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create notebook
        notebook_id_1 = _create_notebook(self.client, headers)

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id_2 = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id_2,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Edit note
        n = {
            "notebook_id": notebook_id_1,
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put(f"/notes/note/{note_id}", headers=headers, json=n)

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
    def test_put_new_notebook_not_found(self):
        """Test the Put method of the Note view.

        This test tries to create a note for a notebook that doesn't exist,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create note for a notebook that doesn't exist
        n = {
            "notebook_id": get_uuid(),
            "archived": False,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]
        }

        r = self.client.put("/notes/note", headers=headers, json=n)

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
    def test_put_edit_user_unauthorized(self):
        """Test the Put method of the Note view.

        This test tries to edit a note of a notebook that doesn't belong to the
        request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note 1"
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Edit note
        url = f"/notes/note/{note_id}"
        new_note = {"notebook_id": notebook_id, "title": "Test Note 2"}
        r = self.client.put(url, headers=headers, json=new_note)

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
        """Test the Delete method of the Note view.

        This test creates a note and then tries to delete it, which should
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note"
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Get notebook note list
        r = self.client.post(f"/notes/notes/{notebook_id}", headers=headers)
        notes = r.json["result"]

        # Check list
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["id"], note_id)
        self.assertEqual(notes[0]["archived"], n["archived"])
        self.assertEqual(notes[0]["title"], n["title"])

        # Delete note
        r = self.client.delete(f"/notes/note/{note_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], DELETED)
        self.assertEqual(r.json[keys[1]], OK)

        # Get notebook note list
        r = self.client.post(f"/notes/notes/{notebook_id}", headers=headers)
        notes = r.json["result"]

        # Check list
        self.assertEqual(len(notes), 0)

    @patch.dict("os.environ", envvars.env)
    @patch("pymongo.MongoClient", mocks.mongo_client)
    @patch("redis.Redis", mocks.redis)
    def test_delete_missing_access_token(self):
        """Test the Delete method of the Note view.

        This test tries to delete an existing note without providing the access
        token, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note"
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Delete note
        r = self.client.delete(f"/notes/note/{note_id}")

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
        """Test the Delete method of the Note view.

        This test tries to delete a note providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note"
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Delete note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.delete(f"/notes/note/{note_id}", headers=headers)

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
    def test_delete_unauthorized_user(self):
        """Test the Delete method of the Note view.

        This test tries to delete a note of a user different than the request
        user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"]
        )

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "archived": False,
            "title": "Test Note"
        }

        r = self.client.put("/notes/note", headers=headers, json=n)
        note_id = r.json["result"]["id"]

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Delete note
        r = self.client.delete(f"/notes/note/{note_id}", headers=headers)

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
    def test_delete_note_not_found(self):
        """Test the Delete method of the Note view.

        This test tries to delete a note that doesn't exist, which shouldn't
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"]
        )

        # Delete note that doesn't exist
        r = self.client.delete(f"/notes/note/{get_uuid()}", headers=headers)

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
