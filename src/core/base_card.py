from __future__ import annotations

from typing import List

from common.entity import Entity
from core.card import Card
from common.enums import CardType


# This exists solely to embed the Card value type into an object that adds other attributes
# We don't want to extend Card since it is a value type and we need an entity
class BaseCard(Entity):

    @property
    def number(self) -> int:
        return self._card.number

    @property
    def filename(self) -> str:
        return self._card.filename

    @property
    def type(self) -> CardType:
        return self._card.type

    def __init__(self, card: Card, id: str = None):
        super().__init__(id)

        self._card = card
