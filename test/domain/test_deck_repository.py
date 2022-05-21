from typing import Tuple

import pytest
from assertpy import assert_that

from common.enums import DeckType, CardType
from core.card import Card
from core.deck import Deck
from core.hand import Hand
from support.fake_card_repository import FakeCardRepository
from support.fake_deck_repository import FakeDeckRepository


@pytest.fixture
def deck_with_cards():
    def __make_deck(deck_type: DeckType, id: str) -> Tuple[Deck, FakeCardRepository]:
        card_repository = FakeCardRepository()
        card_type = card_repository.get_card_type_from_deck_type(deck_type)
        cards = card_repository.get_all_by_type(card_type)

        deck = Deck(deck_type, id)
        deck.fill(cards)

        return deck, card_repository

    return __make_deck


@pytest.fixture
def hand_factory():
    def __make_hand(max_size: int) -> Tuple[Hand, FakeDeckRepository]:
        repository = FakeDeckRepository()
        return Hand(DeckType.PROGRAM_HAND, max_size), repository

    return __make_hand


# ------------------

def test_load_deck():
    repo = FakeDeckRepository()

    deck: Deck = repo.get_by_id_and_type("xyz-5-6", DeckType.POWER_DECK)

    assert_that(deck.id).is_equal_to("xyz-5-6")
    assert_that(deck.cards).extracting('number').is_equal_to([34, 9, 175])
    assert_that(deck.cards).extracting('type').is_equal_to(["power", "power", "power"])
    assert_that(deck.cards).extracting('filename').is_equal_to(["ware_ware.png", "soro_soro.png", "waka_waka.png"])


def test_save_deck_new(deck_with_cards):
    deck, c_repo = deck_with_cards(DeckType.PROGRAM_HAND, "314-woo")
    repo = FakeDeckRepository()
    repo.clear_all()

    repo.save(deck)

    repo_nums = repo.get_card_nums_by_parent(deck.id, deck.deck_type)
    assert_that(repo_nums).is_equal_to([0, 12, 15, 344, 954])
    repo_files = repo.get_card_filenames_by_parent(deck.id, deck.deck_type)
    assert_that(repo_files).is_equal_to(
        ["zero.png", "twelve.png", "fifteen.png", "three_forty_four.png", "nine_fifty_four.png"])
    repo_types = repo.get_card_types_by_parent(deck.id, deck.deck_type)
    assert_that(repo_types).is_equal_to(
        ["program_hand", "program_hand", "program_hand", "program_hand", "program_hand"])


def test_save_deck_update(deck_with_cards):
    repo: FakeDeckRepository = FakeDeckRepository()
    deck: Deck = repo.get_by_id_and_type("abc123", DeckType.PROGRAM_DECK)
    deck.shuffle(1)
    discard: Deck = Deck(DeckType.PROGRAM_HAND)
    deck.deal_card(discard)

    repo.save(deck)

    repo_nums = repo.get_card_nums_by_parent(deck.id, deck.deck_type)
    assert_that(repo_nums).is_equal_to([6, 6789, 204, 346])
    repo_files = repo.get_card_filenames_by_parent(deck.id, deck.deck_type)
    assert_that(repo_files).is_equal_to(
        ['mofu_mofu.png', 'fuwa_fuwa.png', 'pika_pika.png', 'kira_kira.png'])
    repo_types = repo.get_card_types_by_parent(deck.id, deck.deck_type)
    assert_that(repo_types).is_equal_to(["program_deck", "program_deck", "program_deck", "program_deck"])


def test_load_hand():
    repo = FakeDeckRepository()

    hand = repo.get_by_id_and_type("abc123", DeckType.PROGRAM_HAND)

    assert_that(hand.id).is_equal_to("abc123")
    assert_that(hand.size).is_equal_to(5)
    assert_that(hand.cards).extracting('number').is_equal_to([346, 6, 1111, 6789, 204])
    assert_that(hand.cards).extracting('type').is_equal_to(["program", "program", "program", "program", "program"])
    assert_that(hand.cards).extracting('filename').is_equal_to(
        ["kira_kira.png", "mofu_mofu.png", "kari_kari.png", "fuwa_fuwa.png", "pika_pika.png"])


def test_save_hand_new(hand_factory):
    hand, repo = hand_factory(5)
    repo.clear_all()
    hand.add_card(Card(434, "woo.jpg", CardType.PROGRAM))
    hand.add_card(Card(8, "boop.jpg", CardType.POWER))
    hand.add_card(Card(111, "snooz.png", CardType.PROGRAM))

    repo.save(hand)

    repo_cards = repo.get_card_nums_by_parent(hand.id, hand.deck_type)
    assert_that(repo_cards).is_length(len(hand.cards))
    assert_that(repo_cards).is_equal_to([434, 8, 111])
