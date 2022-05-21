from assertpy import assert_that

from common.enums import CardType, DeckType
from core.card import Card
from core.player import Player
from support.fake_player_repository import FakePlayerRepository


def _verify_player(player: Player, id: str, repo: FakePlayerRepository):
    fake_player = repo.get_fake_player_info(id)
    assert_that(player.id).is_equal_to(fake_player['id'])
    assert_that(player.name).is_equal_to(fake_player['name'])
    assert_that(player.avatar_filename).is_equal_to(fake_player['avatar_filename'])
    assert_that(player.damage).is_equal_to(fake_player['damage'])
    assert_that(player.is_powered_down).is_equal_to(fake_player['powered_down'])

    fake_nums, fake_filenames, fake_locks = repo.get_fake_register_info(fake_player['id'])
    assert_that(player.registers.cards).extracting('number').is_equal_to(fake_nums)
    assert_that(player.registers.cards).extracting('filename').is_equal_to(fake_filenames)
    assert_that(player.registers.locks).is_equal_to(fake_locks)

    fake_nums, fake_filenames, fake_types = repo.get_fake_card_info_by_deck_id(fake_player['id'], DeckType.PROGRAM_HAND)
    assert_that(player.program_hand.cards).extracting('number').is_equal_to(fake_nums)
    assert_that(player.program_hand.cards).extracting('filename').is_equal_to(fake_filenames)
    assert_that(player.program_hand.cards).extracting('type').is_equal_to(fake_types)

    fake_nums, fake_filenames, fake_types = repo.get_fake_card_info_by_deck_id(fake_player['id'], DeckType.POWER_HAND)
    assert_that(player.power_hand.cards).extracting('number').is_equal_to(fake_nums)
    assert_that(player.power_hand.cards).extracting('filename').is_equal_to(fake_filenames)
    assert_that(player.power_hand.cards).extracting('type').is_equal_to(fake_types)


def test_load():
    repo = FakePlayerRepository()

    player: Player = repo.get_by_id("111xyz")

    _verify_player(player, "111xyz", repo)


def test_save__new():
    repo = FakePlayerRepository()
    repo.clear_all()
    player: Player = repo.create_fake_player("111xyz")

    repo.save(player)

    repo_player: Player = repo.get_by_id("111xyz")
    _verify_player(repo_player, "111xyz", repo)


def test_save_update():
    repo = FakePlayerRepository()
    player: Player = repo.get_by_id("a-34-er")
    player.dec_damage()
    player.move_card_to_register(1, 3)
    card1: Card = Card(434, "woo.jpg", CardType.POWER)
    player.power_hand.add_card(card1, 0)
    player.registers.lock_register(0)
    player.will_power_down()

    repo.save(player)

    repo_player: Player = repo.get_by_id("a-34-er")
    assert_that(player.id).is_equal_to(repo_player.id)
    assert_that(player.name).is_equal_to(repo_player.name)
    assert_that(player.avatar_filename).is_equal_to(repo_player.avatar_filename)
    assert_that(player.damage).is_equal_to(repo_player.damage)
    assert_that(player.is_powered_down).is_true()

    assert_that(player.registers.cards).extracting('number').is_equal_to([34, 9, -1, 71, 22])
    assert_that(player.registers.locks).is_equal_to([True, False, False, False, False])

    assert_that(player.program_hand.cards).extracting('number').is_equal_to([616, 17])
    assert_that(player.program_hand.cards).extracting('filename').is_equal_to(['ishiko.png', 'shinohara.png'])
    assert_that(player.program_hand.cards).extracting('type').is_equal_to(["program", "program"])

    assert_that(player.power_hand.cards).extracting('number').is_equal_to([434, 124, 19])
    assert_that(player.power_hand.cards).extracting('filename').is_equal_to(
        ['woo.jpg', 'muco.png', 'komatsu.png'])
    assert_that(player.power_hand.cards).extracting('type').is_equal_to(["power", "power", "power"])


def test_delete():
    repo = FakePlayerRepository()
    player: Player = repo.create_fake_player("111xyz")

    repo.delete(player)

    repo_player = repo.get_by_id(player.id)
    assert_that(repo_player).is_none()
    assert_that(repo.are_registers_present(player.registers.id)).is_false()
    assert_that(repo.is_deck_present(player.program_hand.id, DeckType.PROGRAM_HAND)).is_false()
    assert_that(repo.is_deck_present(player.power_hand.id, DeckType.POWER_HAND)).is_false()
