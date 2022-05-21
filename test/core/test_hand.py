from typing import Tuple

import pytest
from assertpy import assert_that

from common.enums import CardType, DeckType
from core.card import Card
from core.hand import Hand
from support.fake_deck_repository import FakeDeckRepository
from support.mock_hand import MockHand


@pytest.fixture
def hand_factory():
    def __make_hand(max_size: int) -> Tuple[Hand, FakeDeckRepository]:
        repository = FakeDeckRepository()
        return Hand(DeckType.PROGRAM_DECK, max_size), repository

    return __make_hand


# -----------


# Tests for default max size and no add index are covered under the deck tests since
# they are more appropriate for decks

@pytest.mark.parametrize("max_size,", [1, 5, 9])
def test_constructor_valid(max_size: int):
    hand = Hand(DeckType.PROGRAM_DECK, max_size)

    assert_that(hand.max_size).is_equal_to(max_size)
    assert_that(hand.cards).is_empty()


@pytest.mark.parametrize("max_size,", [-3, 0, 1000, 3425])
def test_constructor_invalid_type(max_size):
    with pytest.raises(ValueError):
        Hand(DeckType.PROGRAM_DECK, max_size)


def test_add_card_no_card(hand_factory):
    hand, repo = hand_factory(1)

    hand.add_card(None)

    assert_that(hand.cards).is_empty()


def test_add_card_valid_indexes(hand_factory):
    hand, repo = hand_factory(3)
    card1: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    card2: Card = Card(67, "xyzzy.jpg", CardType.POWER)
    card3: Card = Card(9, "plugh.png", CardType.PROGRAM)

    hand.add_card(card1)

    assert_that(hand.cards).is_length(1)
    assert_that(hand.cards).contains_sequence(card1)

    hand.add_card(card2, 0)

    assert_that(hand.cards).is_length(2)
    assert_that(hand.cards).contains_sequence(card2, card1)

    hand.add_card(card3, 1)

    assert_that(hand.cards).is_length(3)
    assert_that(hand.cards).contains_sequence(card2, card3, card1)


def test_add_card_too_many(hand_factory):
    hand, repo = hand_factory(2)
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)

    hand.add_card(card)
    hand.add_card(card)

    with pytest.raises(IndexError):
        hand.add_card(card)


def test_transfer_card_no_deck(hand_factory):
    hand, repo = hand_factory(3)
    card: Card = Card(434, "woo.jpg", CardType.POWER)
    hand.add_card(card)

    with pytest.raises(ValueError):
        hand.transfer_card(1, None)

    assert_that(hand.cards).is_length(1)


@pytest.mark.parametrize("index,", [Card.NUMBER_EMPTY, 3])
def test_transfer_card_invalid_source_index(hand_factory, index):
    source, repo = hand_factory(3)
    target, repo = hand_factory(3)
    card1: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    card2: Card = Card(67, "xyzzy.jpg", CardType.POWER)
    source.add_card(card1)
    source.add_card(card2)

    with pytest.raises(IndexError):
        source.transfer_card(index, target)

    assert_that(source.size).is_equal_to(2)


def test_transfer_card_valid(hand_factory):
    source, repo = hand_factory(3)
    target, repo = hand_factory(3)
    card1: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    card2: Card = Card(67, "xyzzy.jpg", CardType.POWER)
    card3: Card = Card(9, "plugh.png", CardType.POWER)
    source.add_card(card1)
    source.add_card(card2)
    target.add_card(card3)

    # Add to the end of target
    source.transfer_card(1, target, 5)

    assert_that(source.cards).is_length(1)
    assert_that(source.cards).contains_sequence(card1)
    assert_that(target.cards).is_length(2)
    assert_that(target.cards).contains_sequence(card3, card2)

    target.transfer_card(0, source, 0)

    assert_that(source.cards).is_length(2)
    assert_that(source.cards).contains_sequence(card3, card1)
    assert_that(target.cards).is_length(1)
    assert_that(target.cards).contains_sequence(card2)


def test_transfer_card_target_problem(hand_factory):
    source, repo = hand_factory(3)
    target = MockHand()
    card1: Card = Card(434, "woo.jpg", CardType.POWER)
    card2: Card = Card(67, "xyzzy.jpg", CardType.PROGRAM)
    source.add_card(card1)
    source.add_card(card2)

    with pytest.raises(IndexError):
        source.transfer_card(1, target)

    assert_that(source.size).is_equal_to(2)
