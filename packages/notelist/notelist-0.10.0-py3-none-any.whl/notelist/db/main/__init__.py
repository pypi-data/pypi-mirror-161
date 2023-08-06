"""Main Database package."""

from pymongo import MongoClient

from notelist.db.main.users import DbUserManager
from notelist.db.main.notebooks import DbNotebookManager
from notelist.db.main.notes import DbNoteManager


class MainDbManager():
    """Main Database manager (for MongoDB)."""

    def __init__(
        self, uri: str, db: str, us_col: str, nb_col: str, no_col: str
    ):
        """Initialize instance.

        This method creates the collection indexes if they don't exist.

        :param uri: MongoDB URI ("mongodb://user:password@localhost:27017").
        :param db: MongoDB database name. E.g. "notelist".
        :param us_col: MongoDB users collection name. E.g. "users".
        :param nb_col: MongoDB notebooks collection name. E.g. "notebooks".
        :param no_col: MongoDB notes collection name. E.g. "notes".
        """
        # Client
        self._client = MongoClient(uri)

        # Database object
        self._db = self._client[db]

        # Managers
        self._users = DbUserManager(self, self._db, us_col)
        self._notebooks = DbNotebookManager(self, self._db, nb_col)
        self._notes = DbNoteManager(self, self._db, no_col)

    def create_db(self):
        """Create the database.

        The database is automatically created when creating the collections and
        the collections are automatically created when creating their indexes
        or when accessing to them for the first time.
        """
        self._users.create_collection()
        self._notebooks.create_collection()
        self._notes.create_collection()

    def delete_db(self):
        """Delete the database."""
        self._client.drop_database(self._db)

    def switch_id(self, doc: dict) -> dict:
        """Rename the "id" key by "_id" in a document or viceversa.

        If the document has the "id" key, the key is renamed to "_id". If the
        document has the "_id" key, the key is renamed to "id".

        :param doc: Original document.
        :return: Result document.
        """
        k1 = "id"
        k2 = "_id"

        if doc is None or (k1 not in doc and k2 not in doc):
            return doc

        old_key = k1 if k1 in doc else k2
        new_key = k2 if old_key == k1 else k1

        doc = doc.copy()
        val = doc.pop(old_key)

        return {new_key: val} | doc

    @property
    def users(self) -> DbUserManager:
        """Return the user data manager.

        :return: `DbUserManager` instance.
        """
        return self._users

    @property
    def notebooks(self) -> DbNotebookManager:
        """Return the notebook data manager.

        :return: `DbNotebookManager` instance.
        """
        return self._notebooks

    @property
    def notes(self) -> DbNoteManager:
        """Return the note data manager.

        :return: `DbNoteManager` instance.
        """
        return self._notes
