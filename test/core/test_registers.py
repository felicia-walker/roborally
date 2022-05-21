from typing import Tuple

import pytest
from assertpy import assert_that

from common.enums import CardType, DeckType
from core.card import Card
from core.hand import Hand
from core.registers import Registers
from support.fake_deck_repository import FakeDeckRepository
from support.fake_player_repository import FakePlayerRepository


@pytest.fixture
def registers_factory():
    def __make_reg() -> Tuple[Registers, FakePlayerRepository]:
        repository = FakePlayerRepository()
        return Registers(), repository

    return __make_reg


@pytest.fixture
def hand_factory():
    def __make_hand(max_size: int) -> Tuple[Hand, FakeDeckRepository]:
        repository = FakeDeckRepository()
        return Hand(DeckType.PROGRAM_DECK, max_size), repository

    return __make_hand


# -----------------------

def test_constructor_valid(registers_factory):
    registers, repo = registers_factory()

    assert_that(registers.max_size).is_equal_to(Registers.REGISTER_SIZE)
    assert_that(registers.cards).is_length(5)
    assert_that(registers.cards).extracting('number').is_equal_to([-1, -1, -1, -1, -1])
    assert_that(registers.locks).is_length(5)
    assert_that(registers.locks).contains_sequence(False, False, False, False, False)


def test_add_card_no_card(registers_factory):
    registers, repo = registers_factory()

    registers.add_card(None, 2)

    assert_that(registers.cards).is_length(5)
    assert_that(registers.cards).extracting('number').is_equal_to([-1, -1, -1, -1, -1])


@pytest.mark.parametrize("index,", [None, -1, Registers.REGISTER_SIZE])
def test_add_card_invalid_indexes(registers_factory, index):
    registers, repo = registers_factory()
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)

    with pytest.raises(IndexError):
        registers.add_card(card, index)


@pytest.mark.parametrize("index,", [0, 1, 2, 3, 4])
def test_transfer_card_invalid_source_index(registers_factory, index):
    registers, repo = registers_factory()
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)

    registers.add_card(card, index)

    assert_that(registers.cards).is_length(5)
    for i in range(0, registers.REGISTER_SIZE):
        if i == index:
            assert_that(registers.cards[i]).is_equal_to(card)
        else:
            assert_that(registers.cards[i]).is_equal_to(Card.empty())


@pytest.mark.parametrize("index,", [0, 1, 2, 3, 4])
def test_add_card_when_register_locked(registers_factory, index):
    registers, repo = registers_factory()
    registers.lock_register(index)
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)

    with pytest.raises(LookupError):
        registers.add_card(card, index)

    assert_that(registers.cards).is_length(5)
    assert_that(registers.cards).extracting('number').is_equal_to([-1, -1, -1, -1, -1])


def test_transfer_card_no_deck(registers_factory):
    registers, repo = registers_factory()
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    registers.add_card(card, 1)

    with pytest.raises(ValueError):
        registers.transfer_card(1, None)

    assert_that(registers.cards).is_length(5)
    assert_that(registers.cards).extracting('number').is_equal_to([-1, 434, -1, -1, -1])


@pytest.mark.parametrize("index,", [-1, Registers.REGISTER_SIZE])
def test_transfer_card_valid_indexes(registers_factory, hand_factory, index):
    registers, repo = registers_factory()
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    registers.add_card(card, 1)
    target, target_repo = hand_factory(3)

    with pytest.raises(IndexError):
        registers.transfer_card(index, target)

    assert_that(registers.cards).is_length(5)
    assert_that(registers.cards).extracting('number').is_equal_to([-1, 434, -1, -1, -1])


@pytest.mark.parametrize("index,", [0, 1, 2, 3, 4])
def test_transfer_card_when_register_locked(registers_factory, hand_factory, index):
    registers, repo = registers_factory()
    card: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    registers.add_card(card, index)
    registers.lock_register(index)
    target, target_repo = hand_factory(3)

    with pytest.raises(LookupError):
        registers.transfer_card(index, target)

    assert_that(registers.cards).is_length(5)
    for i in range(0, registers.REGISTER_SIZE):
        if i == index:
            assert_that(registers.cards[i]).is_equal_to(card)
        else:
            assert_that(registers.cards[i]).is_equal_to(Card.empty())


def test_transfer_card_empty(registers_factory, hand_factory):
    registers, repo = registers_factory()
    target, target_repo = hand_factory(3)

    with pytest.raises(ValueError):
        registers.transfer_card(1, target, 0)

    assert_that(registers.cards).is_length(5)
    assert_that(registers.cards).extracting('number').is_equal_to([-1, -1, -1, -1, -1])


def test_transfer_card_valid(registers_factory, hand_factory):
    source, repo = registers_factory()
    target, target_repo = hand_factory(3)
    card1: Card = Card(434, "woo.jpg", CardType.PROGRAM)
    card2: Card = Card(67, "xyzzy.jpg", CardType.PROGRAM)
    card3: Card = Card(9, "plugh.png", CardType.PROGRAM)
    source.add_card(card1, 1)
    source.add_card(card2, 4)
    target.add_card(card3)

    # Add to the end of target
    source.transfer_card(1, target, 5)

    assert_that(source.cards).is_length(5)
    assert_that(source.cards).extracting('number').is_equal_to([-1, -1, -1, -1, 67])
    assert_that(target.cards).is_length(2)
    assert_that(target.cards).contains_sequence(card3, card1)

    source.transfer_card(4, target, 0)

    assert_that(source.cards).is_length(5)
    assert_that(source.cards).extracting('number').is_equal_to([-1, -1, -1, -1, -1])
    assert_that(target.cards).is_length(3)
    assert_that(target.cards).contains_sequence(card2, card3, card1)


@pytest.mark.parametrize("index,", [0, 1, 2, 3, 4])
def test_lock_register_by_index(registers_factory, index):
    registers, repo = registers_factory()

    registers.lock_register(index)

    for i in range(0, registers.REGISTER_SIZE):
        if i == index:
            assert_that(registers.locks[i]).is_true()
        else:
            assert_that(registers.locks[i]).is_false()


@pytest.mark.parametrize("times,", [1, 2, 3, 4, 5, 6])
def test_lock_register(registers_factory, times):
    registers, repo = registers_factory()

    for i in range(0, times):
        registers.lock_register()

    for i in range(0, registers.REGISTER_SIZE):
        if i >= registers.REGISTER_SIZE - times:
            assert_that(registers.locks[i]).is_true()
        else:
            assert_that(registers.locks[i]).is_false()


@pytest.mark.parametrize("index,", [0, 1, 2, 3, 4])
def test_unlock_register_by_index(registers_factory, index):
    registers, repo = registers_factory()
    for i in range(0, registers.REGISTER_SIZE):
        registers.locks[i] = True

    registers.unlock_register(index)

    for i in range(0, registers.REGISTER_SIZE):
        if i == index:
            assert_that(registers.locks[i]).is_false()
        else:
            assert_that(registers.locks[i]).is_true()


@pytest.mark.parametrize("times,", [1, 2, 3, 4, 5, 6])
def test_unlock_register(registers_factory, times):
    registers, repo = registers_factory()
    for i in range(0, registers.REGISTER_SIZE):
        registers.locks[i] = True

    for i in range(0, times):
        registers.unlock_register()

    for i in range(0, registers.REGISTER_SIZE):
        if i >= times:
            assert_that(registers.locks[i]).is_true()
        else:
            assert_that(registers.locks[i]).is_false()
