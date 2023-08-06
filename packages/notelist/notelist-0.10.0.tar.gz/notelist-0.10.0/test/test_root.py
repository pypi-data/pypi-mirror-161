"""Root resource unit tests."""

from os import environ
import unittest

import common

from notelist.responses import METHOD_NOT_ALLOWED, ERROR_METHOD_NOT_ALLOWED


class RootTestCase(common.BaseTestCase):
    """Root resource unit tests."""

    def test_get_ok(self):
        """Test the Get method of the Root view.

        This test tries to call the Get method having the "NL_ROOT_DOC"
        environment variable set to "1", which should work.
        """
        v = "NL_ROOT_DOC"
        environ[v] = "1"
        r = self.client.get("/")

        # Check status code
        self.assertEqual(r.status_code, 200)

        environ.pop(v)

    def test_get_not_found(self):
        """Test the Get method of the Root view.

        This test tries to call the Get method without having the "NL_ROOT_DOC"
        environment variable set to "1", which should not work.
        """
        r = self.client.get("/")

        # Check status code
        self.assertEqual(r.status_code, 404)

    def test_post_error(self):
        """Test the Post method of the Root view.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_put_error(self):
        """Test the Put method of the Root view.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)

    def test_delete_error(self):
        """Test the Delete method of the Root view.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/")

        # Check status code
        self.assertEqual(r.status_code, 405)

        # Check message
        keys = ("message", "message_type")

        for i in keys:
            self.assertIn(i, r.json)

        self.assertEqual(r.json[keys[0]], METHOD_NOT_ALLOWED)
        self.assertEqual(r.json[keys[1]], ERROR_METHOD_NOT_ALLOWED)


if __name__ == "__main__":
    unittest.main()
