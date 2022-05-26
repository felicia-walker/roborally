from __future__ import annotations

from random import *

from common.enums import DeckType
from core.base_deck import BaseDeck
from core.deck_card import DeckCard


class Deck(BaseDeck):
    MIN_SHUFFLES = 10
    MAX_SHUFFLES = 50

    def __init__(self, type: DeckType, id: str = None):
        super().__init__(type, id)

    def deal_card(self, target: BaseDeck) -> DeckCard:
        if target is None:
            raise ValueError("No target deck specified.")

        if len(self._cards) == 0:
            raise IndexError("The deck is empty")

        DeckCard: DeckCard = None
        try:
            DeckCard = self._cards.pop()
            target.add_card(DeckCard)
        except IndexError as err:
            if DeckCard is not None:
                self._cards.append(DeckCard)

            raise err

        return DeckCard

    def shuffle(self, times=0):
        deck = self._cards

        if times == 0:
            times = randint(self.MIN_SHUFFLES, self.MAX_SHUFFLES)

        for times in range(0, times):
            deck, second_deck = self._cut_deck(deck)

            for index, item in enumerate(second_deck):
                insert_index = index * 2 + 1
                deck.insert(insert_index, item)

        deck, second_deck = self._cut_deck(deck)
        self._cards = second_deck + deck

    def _cut_deck(self, deck):
        # TODO - Check deck size to avoid index error
        cut_index = randint(10, len(deck) - 10)
        deck, second_deck = deck[:cut_index], deck[cut_index:]

        return deck, second_deck
