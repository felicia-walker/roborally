from __future__ import annotations

from datetime import date
from typing import List

from common.entity import Entity
from common.enums import DeckType
from core.deck import Deck


class Game(Entity):

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def start_date(self) -> str:
        return self._start_date

    @property
    def program_deck(self) -> Deck:
        return self._program_deck

    @program_deck.setter
    def program_deck(self, value: Deck):
        if value.deck_type != DeckType.PROGRAM_DECK:
            raise ValueError("This is not a program deck")

        self._program_deck = value

    @property
    def power_deck(self) -> Deck:
        return self._power_deck

    @property
    def board_state_filenames(self) -> List[str]:
        return self._board_state_filenames

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, notes: str):
        self._notes = notes

    def __init__(self, props: GameProps):
        super().__init__()

        self._program_deck = props.program_deck
        self._power_deck = props.power_deck
        self._turn: int = props.turn
        self._start_date: str = props.start_date
        self._board_state_filenames: List[str] = props.board_state_filenames
        self._notes: str = props.notes

        if len(props.id) > 0:
            self._id = props.id

    def inc_turn(self):
        self._turn = self._turn + 1

    def add_board_state(self, filename: str):
        self._board_state_filenames.append(filename)

    def clear_board_states(self):
        self._board_state_filenames = []


class GameProps:
    def __init__(self):
        self.id: str = ""
        self.turn: int = 1
        self.start_date: str = date.today().strftime("%m/%d/%Y")
        self.program_deck: Deck = None
        self.power_deck: Deck = None
        self.board_state_filenames = []
        self.notes = ""
