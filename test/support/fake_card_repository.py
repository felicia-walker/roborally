from __future__ import annotations

from typing import List

from common.enums import CardType, DeckType
from core.card import Card
from domain.card_respository import CardRepository
from domain.models.card_model import CardModel


class FakeCardRepository(CardRepository):
    @property
    def data(self):
        return self._data

    def __init__(self):
        super().__init__("/test/support/test.db")

        self._data = [{'number': 12, 'filename': "twelve.png", 'type': CardType.PROGRAM},
            {'number': 67, 'filename': "sixty_seven.png", 'type': CardType.POWER},
            {'number': 344, 'filename': "three_forty_four.png", 'type': CardType.PROGRAM},
            {'number': 1223, 'filename': "twelve_twenty_three.png", 'type': CardType.POWER},
            {'number': 15, 'filename': "fifteen.png", 'type': CardType.PROGRAM},
            {'number': 954, 'filename': "nine_fifty_four.png", 'type': CardType.PROGRAM},
            {'number': 211, 'filename': "two_eleven.png", 'type': CardType.POWER},
            {'number': 0, 'filename': "zero.png", 'type': CardType.PROGRAM},
            {'number': 1243, 'filename': "twelve_forty_three.png", 'type': CardType.POWER}]

        self.reset()

    def reset(self):
        self.clear_all()

        with self.get_session_begin() as session:
            for item in self._data:
                model_card: CardModel = CardModel(number=item['number'],
                                                  filename=item['filename'],
                                                  type=item['type'])

                session.add(model_card)

    # -----------

    def get_program_cards(self) -> List[Card]:
        return [i for i in self._data if i['type'] == CardType.PROGRAM]

    def get_power_cards(self) -> List[Card]:
        return [i for i in self._data if i['type'] == CardType.POWER]

    @staticmethod
    def get_card_type_from_deck_type(deck_type: DeckType) -> CardType:
        card_type: CardType = CardType.POWER

        if deck_type == DeckType.PROGRAM_DECK or deck_type == DeckType.PROGRAM_HAND:
            card_type = CardType.PROGRAM

        return card_type
