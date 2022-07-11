from __future__ import annotations

import os
from typing import List

from application.card_uploader import CardUploader
from common.enums import DeckType
from core.card import Card
from core.game import Game, GameProps
from core.hand import Hand
from core.player import Player, PlayerProps
from domain.card_respository import CardRepository
from domain.deck_factory import DeckFactory
from domain.deck_respository import DeckRepository
from domain.game_factory import GameFactory
from domain.game_respository import GameRepository
from domain.player_factory import PlayerFactory
from domain.player_respository import PlayerRepository


class GameService:
    NUM_POWER_CARDS_NEW_GAME: int = 3

    @property
    def game(self) -> Game:
        return self._game

    @property
    def players(self) -> List[Player]:
        players: List[Player] = self._player_repository.get_all()
        players.sort(key=lambda x: x.name)

        return players

    @property
    def active_players(self) -> List[Player]:
        return [x for x in self.players if x.is_active]

    @property
    def discard_pile(self) -> Hand:
        return self._discard_pile

    def __init__(self, base_dir: str, board_state_directory: str, card_repository: CardRepository = None,
                 deck_repository: DeckRepository = None,
                 player_repository: PlayerRepository = None, game_repository: GameRepository = None,
                 deck_factory: DeckFactory = None, game_factory: GameFactory = None,
                 card_uploader: CardUploader = None):
        if card_repository is None:
            self._card_repository: CardRepository = CardRepository()
        else:
            self._card_repository: CardRepository = card_repository

        if deck_repository is None:
            self._deck_repository = DeckRepository()
        else:
            self._deck_repository = deck_repository

        if player_repository is None:
            self._player_repository = PlayerRepository()
        else:
            self._player_repository = player_repository

        if game_repository is None:
            self._game_repository = GameRepository()
        else:
            self._game_repository = game_repository

        if deck_factory is None:
            self._deck_factory: DeckFactory = DeckFactory(self._card_repository)
        else:
            self._deck_factory: DeckFactory = deck_factory

        if game_factory is None:
            self._game_factory = GameFactory(self._deck_factory)
        else:
            self._game_factory = game_factory

        if card_uploader is None:
            self._card_uploader = CardUploader(base_dir, self._card_repository)
        else:
            self._card_uploader = card_uploader

        self._game: Game = self._game_repository.get_game()
        self._discard_pile: Hand = Hand(DeckType.POWER_HAND)  # type does not matter

        if self._game is None:
            self.start_new_game(board_state_directory)

    def start_new_game(self, board_state_directory: str):
        self._game_repository.clear_all()

        try:
            all_files = os.listdir(board_state_directory)

            for f in all_files:
                os.remove(os.path.join(board_state_directory, f))
        except Exception:
            pass

        # Refresh the cards
        self._card_uploader.refresh_all_cards()

        # Create a new game and decks
        props: GameProps = GameProps()
        self._game = self._game_factory.new_game(props)

        # Clear out old orb and number of uses on power cards
        self._game.power_deck.clear_cards()

        # Reset the players and deal new hands
        for player in self.players:
            player.reset()
            player.reset_program_hand(self._game.program_deck)

            for num_cards in range(0, self.NUM_POWER_CARDS_NEW_GAME):
                player.draw_power_card(self._game.power_deck)

            self.save_player(player)

        # Save after players since decks have been altered
        self.save_game()

    def add_board_state(self, filename: str):
        self._game.add_board_state(filename)
        self.save_game()

    def add_game_notes(self, notes: str):
        self._game.notes = notes
        self.save_game()

    def add_player(self, name: str, filename: str = "") -> Player:
        props: PlayerProps = PlayerProps()
        props.name = name
        props.avatar_filename = filename
        player: Player = PlayerFactory.new_player(props)
        player.reset_program_hand(self._game.program_deck)

        self.save_player(player)
        self.save_game()

        return player

    def delete_player(self, id: str, avatar_dir: str) -> Player:
        player: Player = None
        for p in self.players:
            if p.id == id:
                player = p

                try:
                    os.remove(os.path.join(avatar_dir, player.avatar_filename))
                except Exception:
                    pass

                self._player_repository.delete(p)
                # Don't return current cards to decks since they have been effectively played when dealt

                break

        return player

    def save_player(self, player: Player):
        self._player_repository.save(player)

    def save_game(self):
        self._game_repository.save(self._game)

    def get_player(self, id: str) -> Player:
        return self._player_repository.get_by_id(id)

    def get_cards(self, type) -> List[Card]:
        return self._card_repository.get_all_by_type(type)

    def get_game_stats(self) -> GameStats:
        return GameStats(self._game.turn, self._game.start_date, len(self.players))

    def get_register_for_turn(self, register: int):
        ret_val = [TurnRegisterInfo(p, register) for p in self.players if p.is_active]
        ret_val.sort(key=lambda x: x.card_num, reverse=True)

        return ret_val

    def get_board_state(self) -> BoardState:
        self._game: Game = self._game_repository.get_game()

        return BoardState(self._game)

    def reset_program_deck(self):
        self._game.program_deck = self._deck_factory.new_deck(DeckType.PROGRAM_DECK)
        self._game.program_deck.shuffle()

    def start_new_turn(self):
        self._game.inc_turn()
        self._game.clear_board_states()
        self.reset_program_deck()
        self.save_game()

        for player in self.players:
            if not player.is_active:
                player.program_hand.clear()
                player.registers.clear()
            elif player.will_be_powered_down:
                player.power_down()
                player.will_power_up()  # Assume players normally only want to power down for one turn
                player.reset_damage()
                player.program_hand.clear()
            else:
                player.power_up()
                player.registers.clear()
                player.reset_program_hand(self._game.program_deck)

            self.save_player(player)

        # Save after players since decks have been altered
        self.save_game()


class GameStats:
    def __init__(self, turn: int, start_date: str, num_players: int):
        self.turn = turn
        self.start_date = start_date
        self.num_players = num_players


class TurnRegisterInfo:
    def __init__(self, player: Player, register: int):
        self.name = player.name
        self.id = player.id
        self.damage = player.damage
        self.throw = player.registers.throws[register - 1]
        self.instructions = player.instructions
        self.card_num = player.registers.cards[register - 1].number
        self.card_filename = player.registers.cards[register - 1].filename
        self.is_powered_down = player.is_powered_down

        if self.is_powered_down:
            self.card_num = Card.NUMBER_POWER_DOWN


class BoardState:
    @property
    def notes(self) -> str:
        return self._notes

    @property
    def filenames(self) -> List[str]:
        return self._filenames

    def __init__(self, game: Game):
        self._notes: str = game.notes
        self._filenames: List[str] = ["{}/{}".format(os.path.join("images","board_states"), x) for x in game.board_state_filenames]
