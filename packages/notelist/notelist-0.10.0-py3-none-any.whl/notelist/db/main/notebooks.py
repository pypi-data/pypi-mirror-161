"""Main Database notebooks module."""

from typing import Optional

from pymongo import IndexModel, ASCENDING
from pymongo.database import Database


class DbNotebookManager():
    """Database notebook manager (for MongoDB)."""

    def __init__(self, root_dm: "DbManager", db: Database, col: str):
        """Initialize instance.

        :param root_dm: Root database manager.
        :param db: MongoDB database object.
        :param col: MongoDB notebooks collection name.
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
        i1 = IndexModel([("user_id", ASCENDING)], name="user_id_index")

        fields = [("user_id", ASCENDING), ("name", ASCENDING)]
        i2 = IndexModel(fields, unique=True, name="user_id_name_index")

        self._col.create_indexes([i1, i2])

    def get_by_user(self, user_id: str) -> list[dict]:
        """Return all the notebook documents of a given user.

        :param user_id: User ID.
        :return: Notebook documents.
        """
        f = {"user_id": user_id}
        s = [("name", ASCENDING)]
        notebooks = self._col.find(f, sort=s)

        return list(map(self._root_dm.switch_id, notebooks))

    def get_by_id(self, _id: str) -> Optional[dict]:
        """Return a notebook document given its ID.

        :param _id: Notebook ID.
        :return: Notebook document if it exists or None otherwise.
        """
        notebook = self._col.find_one({"_id": _id})
        return self._root_dm.switch_id(notebook)

    def get_by_name(self, user_id: str, name: str) -> Optional[dict]:
        """Return a notebook document given its user and name.

        :param user_id: Notebook user ID.
        :param name: Notebook name.
        :return: Notebook document if it exists or None otherwise.
        """
        f = {"user_id": user_id, "name": name}
        notebook = self._col.find_one(f)

        return self._root_dm.switch_id(notebook)

    def put(self, notebook: dict):
        """Put a notebook document.

        If an existing document has the same ID as `notebook`, the existing
        document is replaced with `notebook`.

        :param notebook: Notebook document.
        """
        notebook = self._root_dm.switch_id(notebook)
        f = {"_id": notebook["_id"]}
        self._col.replace_one(f, notebook, upsert=True)

    def delete(self, _id: str):
        """Delete a notebook document given its ID.

        :param _id: Notebook ID.
        """
        self._col.delete_one({"_id": _id})
