from __future__ import annotations

from abc import ABC
from uuid import uuid4


class Entity(ABC):

    @property
    def id(self):
        return self._id

    def __init__(self, id: str = None):
        if id is None:
            self._id: str = str(uuid4())
        else:
            self._id: str = id

    def __eq__(self, other: Entity) -> bool:
        if other is None:
            return False

        if self is other:
            return True

        if id == 0 or other.id == 0:
            return False

        return self.id == other.id

    def attributes(self):
        return self.__dict__
