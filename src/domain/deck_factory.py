from typing import List

from common.enums import DeckType, CardType
from core.card import Card
from core.deck import Deck
from domain.card_respository import CardRepository


class DeckFactory:
    def __init__(self, card_repository: CardRepository = None):
        if card_repository is None:
            self._card_repository: CardRepository = CardRepository()
        else:
            self._card_repository: CardRepository = card_repository

    def new_deck(self, type: DeckType, id: str = None) -> Deck:
        card_type: CardType = CardType.POWER

        if type == DeckType.PROGRAM_DECK or type == DeckType.PROGRAM_HAND:
            card_type = CardType.PROGRAM

        cards: List[Card] = self._card_repository.get_all_by_type(card_type)
        deck: Deck = Deck(type, id)
        deck.fill(cards)

        return deck
