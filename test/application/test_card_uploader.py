import os

from assertpy import assert_that

from application.card_uploader import CardUploader
from common.enums import CardType
from support.fake_card_repository import FakeCardRepository


def test_refresh_all_cards_valid():
    repo = FakeCardRepository()
    uploader = CardUploader(os.getcwd() + "/support/images", repo)

    uploader.refresh_all_cards()

    prog_cards = repo.get_all_by_type(CardType.PROGRAM)
    assert_that(prog_cards).extracting('number').is_equal_to([90, 1070])
    prog_cards = repo.get_all_by_type(CardType.POWER)
    assert_that(prog_cards).extracting('number').is_equal_to([1, 55, 107, 1004])
