import logging
import os
import sqlite3

from .config import Config
from .helpers import try_or_error


class Database:
    def __init__(self, name: str = None, path: str = None):
        self.name = name or 'hatter.db'
        self.path = os.path.join(path or os.getcwd(), self.name)

        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        logging.info("Connection open")
        self.request = []
        self.commit_script(' '.join([Config.PRAGMA_SCRIPT[key] for key in Config.PRAGMA_SCRIPT]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def close(self):
        logging.info("Connection close")
        return self.connection.close()

    @try_or_error
    def commit(self):
        for request in self.request:
            logging.info(request)
            self.cursor.execute(*request if not isinstance(request, str) else [request])
        self.request = None
        self.connection.commit()
        return self.cursor.fetchall()

    @try_or_error
    def commit_script(self, request: str):
        logging.info(request)
        self.cursor.executescript(self.request or request)
        self.request = None
        self.connection.commit()
        return self.cursor.fetchall()

    def rollback(self):
        pass

    def add(self, request):
        row = request if isinstance(request, str) else request()
        if self.request:
            self.request.append(row)
        else:
            self.request = [row, ]

    def create_all(self, models: list):
        self.commit_script(' '.join([model.create_table() for model in models]))

    def drop(self, table: object):
        self.add('DROP TABLE {}; '.format(table.__tablename__))
        self.commit()

    def drop_all(self):
        self.add("SELECT name FROM sqlite_master WHERE type='table' and name <> 'sqlite_sequence'")
        tables = self.commit()
        for table in tables:
            self.add('DROP TABLE IF EXISTS {}'.format(table[0]))
        self.commit()
