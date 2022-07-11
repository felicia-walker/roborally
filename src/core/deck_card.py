from __future__ import annotations

from typing import List

from common.entity import Entity
from core.card import Card
from core.base_card import BaseCard


class DeckCard(BaseCard):
    MAX_NUM_USES: int = 7

    @property
    def orb(self) -> int:
        return self._orb

    @orb.setter
    def orb(self, value: int):
        if value < 0 or value > 3:
            raise AttributeError("Orb value must be between 0 and 3, inclusive")

        self._orb = value

    @property
    def num_uses(self) -> int:
        return self._num_uses

    @num_uses.setter
    def num_uses(self, value: int):
        if value < 0 or value > DeckCard.MAX_NUM_USES:
            raise AttributeError("Num_uses must be betwen 0 and 7, inclusive")

        self._num_uses = value

    def __init__(self, card: Card, id: str = None, orb: int = 0, num_uses: int = 0):
        super().__init__(card, id)

        self._orb: int = orb
        self._num_uses:int = num_uses

    # Need to flatten out the card attributes
    def attributes(self):
        return {"filename": self.filename,
                "number": self.number,
                "type": self.type,
                "orb": self.orb,
                "num_uses": self.num_uses}

    def clear(self):
        self._orb = 0
        self._num_uses = 0