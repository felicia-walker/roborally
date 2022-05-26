from __future__ import annotations

from typing import List

from common.entity import Entity
from core.card import Card
from core.base_card import BaseCard


class DeckCard(BaseCard):

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
        if value < 0 or value > 5:
            raise AttributeError("Num_uses must be betwen 0 and 5, inclusive")

        self._num_uses = value

    def __init__(self, card: Card, id: str = None, orb: int = 0, num_uses: int = 0):
        super().__init__(card, id)

        self._orb: int = orb
        self._num_uses:int = num_uses

    # Need to flatten out the card attributes
    def attributes(self):
        card_attributes = self._card.__dict__
        attributes = {"orb": self.orb,
                      "num_uses": self.num_uses}

        return card_attributes | attributes