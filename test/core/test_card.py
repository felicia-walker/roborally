import pytest
from assertpy import assert_that

from common.enums import CardType
from core.card import Card


def set_number(c, v):
    c.number = v


def set_filename(c, v):
    c.filename = v


def set_type(c, v):
    c.type = v


# -------------------
def test_empty():
    card: Card = Card.empty()

    assert_that(card.number).is_equal_to(Card.NUMBER_EMPTY)
    assert_that(card.filename).is_empty()


def test_constructor_valid():
    card: Card = Card(123, "somefile/image.png", CardType.POWER)

    assert_that(card.number).is_equal_to(123)
    assert_that(card.filename).is_equal_to("somefile/image.png")


@pytest.mark.parametrize("check, value", [(set_number, 3),
    (set_filename, "bogus"), (set_type, CardType.POWER)])
def test_cannot_set_values(check, value):
    card: Card = Card(123, "somefile/image.png", CardType.PROGRAM)

    with pytest.raises(AttributeError):
        check(card, value)


@pytest.mark.parametrize("other, expected", [(None, False),
    (Card(12, "somefile/image.png", CardType.POWER), False),
    (Card(123, "image.png", CardType.PROGRAM), False),
    (Card(123, "somefile/image.png", CardType.PROGRAM), False),
    (Card(123, "somefile/image.png", CardType.POWER), True)])
def test_equals_core(other: Card, expected: bool):
    card: Card = Card(123, "somefile/image.png", CardType.POWER)

    result: bool = card == other

    assert_that(result).is_equal_to(expected)
