from __future__ import annotations

from typing import List

from common.entity import Entity
from common.enums import DeckType
from core.deck_card import DeckCard
from core.card import Card


class BaseDeck(Entity):
    ABSOLUTE_MAX_DECK_SIZE: int = 999

    @property
    def max_size(self):
        return self._max_size

    @property
    def cards(self) -> List[DeckCard]:
        return self._cards

    @property
    def size(self) -> int:
        return len(self._cards)

    @property
    def deck_type(self):
        return self._deck_type

    def __init__(self, type: DeckType, id: str = None, max_size: int = ABSOLUTE_MAX_DECK_SIZE):
        super().__init__(id)

        values = [item.value for item in DeckType]
        if type not in values:
            raise AttributeError("Invalid deck type: " + str(type))

        if max_size < 1 or max_size > self.ABSOLUTE_MAX_DECK_SIZE:
            raise ValueError("Deck size must be between 0 and %d".format(self.ABSOLUTE_MAX_DECK_SIZE))
        else:
            self._max_size: int = max_size

        self._deck_type: DeckType = type
        self._cards: List[DeckCard] = []

    def add_card(self, card: DeckCard, index: int = None):
        if card is None:
            return

        if len(self._cards) + 1 > self._max_size:
            raise IndexError("Cannot add any more cards to this deck.")

        if index is None or index >= len(self._cards):
            self._cards.append(card)
        else:
            self._cards.insert(index, card)

    def fill(self, cards: List[Card]):
        self.clear()

        for cur_card in cards:
            self._cards.append(DeckCard(cur_card))

    def populate(self, cards: List[DeckCard]):
        self._cards = cards

    def clear(self):
        self._cards = []

    def getCardByFilename(self, filename) -> DeckCard:
        result = [x for x in self.cards if x.filename == filename]

        if len(result) > 1:
            raise IndexError("More than one card found with filename " + filename)
        elif len(result) == 0:
            return None
        else:
            return result[0]

