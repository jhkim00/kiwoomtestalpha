import sqlite3
import logging

logger = logging.getLogger()

class DbHelper:
    instance = None

    def __init__(self):
        self._conn = sqlite3.connect('kiwoomtestalpha.db')
        self._cursor = self._conn.cursor()

        self._createTableFavorite()

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = DbHelper()
        return cls.instance

    def _createTableFavorite(self):
        query = "CREATE TABLE IF NOT EXISTS Favorite (Name TEXT, Code TEXT PRIMARY_KEY UNIQUE)"
        self._cursor.execute(query)

    def insertStockToTableFavorite(self, name: str, code: str):
        query = "INSERT OR IGNORE INTO Favorite VALUES(?, ?)"
        self._cursor.execute(query, (name, code))
        self._conn.commit()

    def deleteStockFromTableFavorite(self, code: str):
        query = f"DELETE FROM Favorite WHERE Code = '{code}'"
        logger.debug(query)
        self._cursor.execute(query)
        self._conn.commit()

    def selectTableFavorite(self) -> list:
        self._cursor.execute("SELECT * FROM Favorite")
        rows = self._cursor.fetchall()
        return rows
