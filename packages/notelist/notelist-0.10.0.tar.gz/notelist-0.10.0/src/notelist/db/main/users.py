"""Main Database users module."""

from typing import Optional

from pymongo import ASCENDING
from pymongo.database import Database


class DbUserManager():
    """Database user manager (for MongoDB)."""

    def __init__(self, root_dm: "DbManager", db: Database, col: str):
        """Initialize instance.

        :param root_dm: Root database manager.
        :param db: MongoDB database object.
        :param col: MongoDB users collection name.
        """
        self._root_dm = root_dm
        self._col_name = col
        self._col = db[col]

    def create_collection(self):
        """Create the collection.

        The database is automatically created when creating the collections and
        the collections are automatically created when creating their indexes
        or when accessing to them for the first time.
        """
        fields = [("username", ASCENDING)]
        self._col.create_index(fields, unique=True, name="username_index")

    def get_all(self) -> list[dict]:
        """Return all the user documents.

        :return: User documents.
        """
        users = self._col.find(sort=[("username", ASCENDING)])
        return list(map(self._root_dm.switch_id, users))

    def get_by_id(self, _id: str) -> Optional[dict]:
        """Return a user document given its ID.

        :param _id: User ID.
        :return: User document if it exists or None otherwise.
        """
        user = self._col.find_one({"_id": _id})
        return self._root_dm.switch_id(user)

    def get_by_username(self, username: str) -> Optional[dict]:
        """Return a user document given its username.

        :param username: Username.
        :return: User document if it exists or None otherwise.
        """
        user = self._col.find_one({"username": username})
        return self._root_dm.switch_id(user)

    def put(self, user: dict):
        """Put a user document.

        If an existing document has the same ID as `user`, the existing
        document is replaced with `user`.

        :param user: User document.
        """
        user = self._root_dm.switch_id(user)
        f = {"_id": user["_id"]}
        self._col.replace_one(f, user, upsert=True)

    def delete(self, _id: str):
        """Delete a user document given its ID.

        :param _id: User ID.
        """
        self._col.delete_one({"_id": _id})
