"""Temporary Database package."""

from redis import Redis

from notelist.db.temp.blocklist import TempDbBlockListManager


class TempDbManager():
    """Temporary Database manager (for Redis)."""

    def __init__(self, host: str, port: int, bl_db: str, password: str):
        """Initialize instance.

        :param host: Redis host.
        :param port: Redis port (usually 6379).
        :param bl_db: Redis Block List database (e.g. 0).
        :param password: Redis password (optional)
        """
        # Block List Redis database client. By setting "decode_responses" to
        # True, calls to "self._bl_client.get" will return a string instead of
        # bytes.
        self._bl_db = Redis(
            host, port, bl_db, password, decode_responses=True
        )

        # Manager
        self._blocklist = TempDbBlockListManager(self._bl_db)

    @property
    def blocklist(self) -> TempDbBlockListManager:
        """Return the Block List manager.

        :return: `TempDbBlockListManager` instance.
        """
        return self._blocklist
