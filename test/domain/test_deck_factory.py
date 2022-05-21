from typing import Tuple

import pytest
from assertpy import assert_that

from common.enums import DeckType
from core.deck import Deck
from domain.deck_factory import DeckFactory
from support.fake_card_repository import FakeCardRepository


@pytest.fixture
def deck_maker():
    def __make_deck() -> Tuple[DeckFactory, FakeCardRepository]:
        card_repository = FakeCardRepository()
        return DeckFactory(card_repository), card_repository

    return __make_deck


@pytest.mark.parametrize("type,", [
    DeckType.POWER_DECK,
    DeckType.PROGRAM_DECK,
    DeckType.PROGRAM_HAND,
    DeckType.POWER_HAND])
def test_fill(type: DeckType, deck_maker):
    factory, c_repo = deck_maker()
    if type == DeckType.PROGRAM_DECK or type == DeckType.PROGRAM_HAND:
        original_deck = c_repo.get_program_cards()
    else:
        original_deck = c_repo.get_power_cards()

    deck: Deck = factory.new_deck(type)

    assert_that(deck.cards).is_length(len(original_deck))
