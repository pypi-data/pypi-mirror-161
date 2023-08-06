"""Main Database notes module."""

from typing import Optional

from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database


class DbNoteManager():
    """Database note manager (for MongoDB)."""

    def __init__(self, root_dm: "DbManager", db: Database, col: str):
        """Initialize instance.

        :param root_dm: Root database manager.
        :param db: MongoDB database object.
        :param col: MongoDB notes collection name.
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
        fields = [("notebook_id", ASCENDING)]
        self._col.create_index(fields, name="notebook_id_index")

    def _select_note(self, n: dict, tags: list[str], no_tags: bool) -> bool:
        """Return whether a note document is selected or not based on its tags.

        :param n: Note document.
        :param tags: Tags filter.
        :param no_tags: No Tags filter.
        :return: `True` if `n` is selected or `False` otherwise.
        """
        k = "tags"
        note_tags = n[k] if k in n else []

        return (
            (len(note_tags) == 0 and no_tags) or
            any(map(lambda t: t in note_tags, tags))
        )

    def get_by_filter(
        self, notebook_id: str, archived: Optional[bool] = None,
        tags: Optional[list[str]] = None, no_tags: bool = False,
        last_mod: bool = False, asc: bool = True
    ) -> list[dict]:
        """Return all the note documents of a given notebook by a filter.

        :param notebook_id: Notebook ID.
        :param archived: State filter (include archived notes or not archived
        notes).
        :param tags: Tags filter (include notes that has any of these tags).
        This list contains tag names.
        :param no_tags: Notes with No Tags filter (include notes with no tags).
        This filter is only applicable if a tag filter has been provided, i.e.
        `tags` is not None).
        :param last_mod: `True` if notes should be sorted by their Last
        Modified timestamp. `False` if notes should be sorted by their Created
        timestamp (default).
        :param asc: Whether the notes order should be ascending (default) or
        not.
        :return: Note documents.
        """
        # Filter
        f = {"notebook_id": notebook_id}

        if archived in (True, False):
            f["archived"] = archived

        # Order
        k = "last_modified" if last_mod else "created"
        d = ASCENDING if asc else DESCENDING

        # Get notes
        notes = self._col.find(f, sort=[(k, d)])

        # Tags and Not Tags filters
        if tags is not None:
            notes = filter(
                lambda n: self._select_note(n, tags, no_tags), notes
            )

        return list(map(self._root_dm.switch_id, notes))

    def get_by_id(self, _id: str) -> Optional[dict]:
        """Return a note document given its ID.

        :param _id: Note ID.
        :return: Note document.
        """
        note = self._col.find_one({"_id": _id})
        return self._root_dm.switch_id(note)

    def put(self, note: dict):
        """Put a note document.

        If an existing document has the same ID as `note`, the existing
        document is replaced with `note`.

        :param note: Note document.
        """
        note = self._root_dm.switch_id(note)
        f = {"_id": note["_id"]}
        self._col.replace_one(f, note, upsert=True)

    def delete(self, _id: str):
        """Delete a note document given its ID.

        :param _id: Note ID.
        """
        self._col.delete_one({"_id": _id})
