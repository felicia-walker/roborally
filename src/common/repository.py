from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

basedir: str = os.path.abspath(os.path.dirname(__file__))
db_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + "/database"

T = TypeVar("T")


class Repository(ABC, Generic[T]):

    @property
    def database(self):
        return self._database

    def __init__(self, database: str = None):
        if database is None:
            database = os.path.join(db_dir,"roborally.db")

        engine = create_engine("sqlite+pysqlite:///{}".format(database),
                               connect_args={"check_same_thread": False})

        self._factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self._database = database

    def get_session(self) -> Session:
        return self._factory()

    def get_session_begin(self) -> Session:
        return self._factory.begin()

    @abstractmethod
    def save(self, obj: T):
        pass

    @abstractmethod
    def delete(self, obj: T):
        pass
