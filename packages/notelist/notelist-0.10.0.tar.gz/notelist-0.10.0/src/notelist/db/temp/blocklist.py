"""Temporary Database Block List module."""

from redis import Redis


class TempDbBlockListManager():
    """Temporary Database Block List manager (for Redis)."""

    def __init__(self, db: Redis):
        """Initialize instance.

        :param db: Redis database object.
        """
        self._db = db

    def contains(self, jti: str) -> bool:
        """Return whether a given JTI (JWT token ID) exists or not.

        If the document exists but is expired, it's deleted and `False` is
        returned.

        :param _id: Block list ID (JWD token).
        :return: Whether the block list contains the ID or not.
        """
        return self._db.get(jti) is not None

    def put(self, jti: str, exp: int):
        """Put a JTI (JWT token ID).

        :param jti: JTI.
        :param exp: 10-digit expiration timestamp in seconds.
        """
        self._db.set(jti, "", exp)
