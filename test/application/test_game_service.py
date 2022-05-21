import os

import pytest
from assertpy import assert_that

from application.card_uploader import CardUploader
from application.game_service import GameService
from domain.deck_factory import DeckFactory
from support.fake_card_repository import FakeCardRepository
from support.fake_deck_repository import FakeDeckRepository
from support.fake_player_repository import FakePlayerRepository


@pytest.mark.skip
def test_add_player():
    plaery_repo = FakePlayerRepository()
    player_factory = DeckFactory(FakeCardRepository())
    uploader = CardUploader(os.getcwd() + "/support/images", FakeCardRepository())
    card_repository = FakeCardRepository()
    deck_repository = FakeDeckRepository()
    game_repository = FakeGameRepository()
    game_factory = FakeGameFactory()

    service = GameService(player_repository=repo, deck_factory=factory, card_uploader=uploader)

    player = service.add_player("Cloud Strife", "player.gif")

    assert_that(player.name).is_equal_to("Cloud Strife")
    assert_that(player.avatar_filename).is_equal_to("player.gif")
