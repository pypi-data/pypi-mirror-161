"""Database package."""

from notelist.config import SettingsManager
from notelist.db.main import MainDbManager
from notelist.db.temp import TempDbManager


def get_main_db() -> MainDbManager:
    """Return an instance of `MainDbManager` given the setting values.

    :return: `MainDbManager` instance.
    """
    sm = SettingsManager()

    uri = sm.get("NL_MONGODB_URI")
    db = sm.get("NL_MONGODB_DB")
    us_col = sm.get("NL_MONGODB_US_COL")
    nb_col = sm.get("NL_MONGODB_NB_COL")
    no_col = sm.get("NL_MONGODB_NO_COL")

    return MainDbManager(uri, db, us_col, nb_col, no_col)


def get_temp_db() -> TempDbManager:
    """Return an instance of `TempDbManager` given the setting values.

    :return: `TempDbManager` instance.
    """
    sm = SettingsManager()

    host = sm.get("NL_REDIS_HOST")
    port = sm.get("NL_REDIS_PORT")
    bl_db = sm.get("NL_REDIS_BL_DB")
    password = sm.get("NL_REDIS_PASSWORD")

    return TempDbManager(host, port, bl_db, password)
