from typing import Tuple

import pytest
from assertpy import assert_that

from common.enums import DeckType, CardType
from core.base_deck import BaseDeck
from core.card import Card
from core.deck import Deck
from support.fake_card_repository import FakeCardRepository
from support.mock_hand import MockHand


@pytest.fixture
def deck_with_cards():
    def __make_deck(deck_type: DeckType) -> Tuple[Deck, FakeCardRepository]:
        card_repository = FakeCardRepository()
        card_type = card_repository.get_card_type_from_deck_type(deck_type)
        cards = card_repository.get_all_by_type(card_type)

        deck = Deck(deck_type, card_repository)
        deck.fill(cards)

        return deck, card_repository

    return __make_deck


# ----------------------

# Tests for maximum size and adding to a specific index will be covered in the hand tests
# since they are more appropriate for hands

@pytest.mark.parametrize("type,", [
    DeckType.PROGRAM_DECK])
def test_constructor_valid_type(type: DeckType):
    deck = Deck(type)

    assert_that(deck.cards).is_empty()
    assert_that(deck.max_size).is_equal_to(BaseDeck.ABSOLUTE_MAX_DECK_SIZE)


def test_constructor_invalid_type():
    with pytest.raises(AttributeError):
        Deck("bogus")


def test_add_card_no_card():
    deck = Deck(DeckType.POWER_DECK)

    deck.add_card(None)

    assert_that(deck.cards).is_empty()


def test_add_card_valid():
    deck = Deck(DeckType.POWER_HAND)
    card: Card = Card(434, "woo.jpg", CardType.POWER)

    deck.add_card(card)

    assert_that(deck.cards).is_length(1)
    assert_that(deck.cards).contains(card)


def test_deal_card_no_deck(deck_with_cards):
    deck, c_repo = deck_with_cards(DeckType.POWER_DECK)
    original_deck = c_repo.get_power_cards()

    with pytest.raises(ValueError):
        deck.deal_card(None)

    assert_that(deck.cards).is_length(len(original_deck))


def test_deal_card_empty_deck():
    deck = Deck(DeckType.POWER_DECK)
    discard: Deck = Deck(DeckType.POWER_DECK)
    original_size: int = deck.size

    with pytest.raises(IndexError):
        deck.deal_card(discard)

    assert_that(deck.size).is_equal_to(original_size)


def test_deal_card(deck_with_cards):
    deck, c_repo = deck_with_cards(DeckType.POWER_DECK)
    discard: Deck = Deck(DeckType.POWER_DECK)
    original_deck = c_repo.get_power_cards()

    deck.deal_card(discard)

    assert_that(deck.cards).is_length(len(original_deck) - 1)
    assert_that(discard.cards).is_length(1)
    dealt_card = discard.cards[0]
    assert_that(deck.cards).does_not_contain(dealt_card)
    assert_that(discard.cards).contains(dealt_card)


def test_deal_card_target_problem(deck_with_cards):
    deck, c_repo = deck_with_cards(DeckType.POWER_DECK)
    discard: BaseDeck = MockHand()
    original_size: int = deck.size

    with pytest.raises(IndexError):
        deck.deal_card(discard)

    assert_that(deck.size).is_equal_to(original_size)


def test_shuffle(deck_with_cards):
    deck, c_repo = deck_with_cards(DeckType.PROGRAM_DECK)
    deck.shuffle(1)

    assert_that(deck.cards).extracting('number').is_equal_to([12, 344, 954, 0, 15])
