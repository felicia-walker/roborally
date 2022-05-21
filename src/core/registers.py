from __future__ import annotations

from typing import List

from common.enums import DeckType
from core.base_deck import BaseDeck
from core.card import Card


class Registers(BaseDeck):
    REGISTER_SIZE: int = 5

    @property
    def locks(self):
        return self._locks

    @property
    def throws(self):
        return self._throws

    @property
    def any_empty(self):
        tmp: bool = False
        for r in self._cards:
            if r.number == Card.NUMBER_EMPTY:
                tmp = True
                break

        return tmp

    def __init__(self, id: str = None, cards: List[Card] = [], locks: List[bool] = [], throws: List[bool] = []):
        super().__init__(DeckType.PROGRAM_DECK, id, self.REGISTER_SIZE)

        if len(cards) == self.REGISTER_SIZE and len(locks) == self.REGISTER_SIZE:
            self._locks: List[bool] = locks
            self._cards: List[Card] = cards
            self._throws: List[bool] = throws
        else:
            self._locks: List[bool] = []
            self._cards: List[Card] = []
            self._throws: List[bool] = []

            for i in range(0, self.REGISTER_SIZE):
                self._locks.append(False)
                self._cards.append(Card.empty())
                self._throws.append(False)

    def add_card(self, card: Card, index: int = None):
        if card is None:
            return

        if index is None or index < 0 or index >= self.REGISTER_SIZE:
            raise IndexError

        if self._locks[index]:
            raise LookupError("Cannot add a card to a locked register")
        else:
            self.cards[index] = card

    def transfer_card(self, index: int, target: BaseDeck, target_index: int = None):
        if target is None:
            raise ValueError("No target deck specified.")

        if index < 0 or index >= self.REGISTER_SIZE:
            raise IndexError("Source index is out of range")

        card: Card = self._cards[index]
        if self._locks[index]:
            raise LookupError("Cannot transfer a card from a locked register")

        if self._cards[index] == Card.empty():
            raise ValueError("Cannot transfer an empty register")

        try:
            target.add_card(card, target_index)
            self._cards[index] = Card.empty()
        except IndexError as err:
            if card is not None:
                self._cards.insert(index, card)

            raise err

    def lock_register(self, index: int = None):
        if index is not None:
            self._locks[index] = True
            return

        for i in range(len(self._locks), 0, -1):
            if not self._locks[i - 1]:
                self._locks[i - 1] = True
                break

    def unlock_register(self, index: int = None):
        if index is not None:
            self._locks[index] = False
            return

        for i in range(0, len(self._locks)):
            if self._locks[i]:
                self._locks[i] = False
                break

    def reset_locks(self):
        self._locks = []

        for i in range(0, self.REGISTER_SIZE):
            self._locks.append(False)

    def throw(self, index: int):
        self._throws[index] = not self._throws[index]

    def clear(self):
        for i in range(0, len(self._locks)):
            self._throws[i] = False

            if not self._locks[i]:
                self._cards[i] = Card.empty()
