from __future__ import annotations

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from application import db
from common.enums import DeckType
from core.game import Game, GameProps
from domain.models.board_state_model import BoardStateModel
from domain.models.deck_model import DeckModel


class GameModel(db.Model):
    __tablename__ = "game"

    id = Column('id', String, nullable=False, primary_key=True)
    round = Column('round', Integer, nullable=False)
    start_date = Column('start_date', String, nullable=False)
    notes = Column('notes', String, nullable=True)

    program_deck = relationship("DeckModel",
                                primaryjoin="and_(GameModel.id == DeckModel.parent_id,DeckModel.type == 'program_deck')",
                                cascade="all, delete, delete-orphan",
                                overlaps="power_deck, program_hand, power_hand")
    power_deck = relationship("DeckModel",
                              primaryjoin="and_(GameModel.id == DeckModel.parent_id,DeckModel.type == 'power_deck')",
                              cascade="all, delete, delete-orphan",
                              overlaps="program_deck, program_hand, power_hand")
    board_state_filenames = relationship("BoardStateModel",
                                         primaryjoin="GameModel.id == BoardStateModel.parent_id",
                                         cascade="all, delete, delete-orphan")

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_game(game: Game) -> GameModel:
        model: GameModel = GameModel(id=game.id,
                                     round=game.turn,
                                     start_date=game.start_date,
                                     program_deck=DeckModel.from_deck(game.program_deck),
                                     power_deck=DeckModel.from_deck(game.power_deck),
                                     board_state_filenames=BoardStateModel.from_board_state_filenames(
                                         game.board_state_filenames, game.id),
                                     notes=game.notes)
        return model

    def to_game(self) -> Game:
        props: GameProps = GameProps()
        props.id = self.id
        props.turn = self.round
        props.start_date = self.start_date
        props.program_deck = DeckModel.to_deck(self.program_deck, DeckType.PROGRAM_DECK, self.id)
        props.power_deck = DeckModel.to_deck(self.power_deck, DeckType.POWER_DECK, self.id)
        props.board_state_filenames = BoardStateModel.to_board_state_filenames(self.board_state_filenames)
        props.notes = self.notes

        game: Game = Game(props)
        return game
