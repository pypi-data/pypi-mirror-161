"""Tools module."""

from uuid import uuid4
import hashlib as hl


def get_uuid() -> str:
    """Generate a random 32-character UUID.

    :return: Random UUID. E.g. "615ab2d5fe9941088786b7f59f9f1283".
    """
    return uuid4().hex


def get_hash(text: str) -> str:
    """Return the hash of a text.

    :param text: Original text.
    :return: Text hash.
    """
    s = hl.sha256()
    s.update(bytes(text, encoding="utf-8"))

    return s.hexdigest()
