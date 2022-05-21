from __future__ import annotations

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from application import db
from common.enums import DeckType
from core.player import Player, PlayerProps
from domain.models.deck_model import DeckModel
from domain.models.registers_model import RegistersModel


class PlayerModel(db.Model):
    __tablename__ = "player"

    id = Column('id', String, nullable=False, primary_key=True)
    name = Column('name', String, nullable=False)
    damage = Column('damage', Integer, nullable=False)
    powered_down = Column('powered_down', Boolean, nullable=False)
    will_power_down = Column('will_power_down', Boolean, nullable=False, default=0)
    avatar_filename = Column('avatar_filename', String, nullable=False)
    instructions = Column('instructions', String)
    active = Column('active', Boolean, nullable=False, default=1)

    program_hand = relationship("DeckModel",
                                primaryjoin="and_(PlayerModel.id == DeckModel.parent_id, DeckModel.type == 'program_hand')",
                                cascade="all, delete, delete-orphan",
                                overlaps="power_hand, power_deck, program_deck")
    power_hand = relationship("DeckModel",
                              primaryjoin="and_(PlayerModel.id == DeckModel.parent_id, DeckModel.type == 'power_hand')",
                              cascade="all, delete, delete-orphan",
                              overlaps="program_hand, power_deck, program_deck")
    registers = relationship("RegistersModel",
                             primaryjoin="PlayerModel.id == RegistersModel.parent_id",
                             cascade="all, delete, delete-orphan")

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_player(player: Player) -> PlayerModel:
        model: PlayerModel = PlayerModel(id=player.id,
                                         name=player.name,
                                         damage=player.damage,
                                         active=player.is_active,
                                         powered_down=player.is_powered_down,
                                         will_power_down=player.will_be_powered_down,
                                         avatar_filename=player.avatar_filename,
                                         instructions=player.instructions,
                                         program_hand=DeckModel.from_deck(player.program_hand),
                                         power_hand=DeckModel.from_deck(player.power_hand),
                                         registers=RegistersModel.from_registers(player.registers))

        return model

    def to_player(self) -> Player:
        props: PlayerProps = PlayerProps()

        props.id = self.id
        props.avatar_filename = self.avatar_filename
        props.instructions = self.instructions
        props.damage = self.damage
        props.powered_down = self.powered_down
        props.will_power_down = self.will_power_down
        props.name = self.name
        props.active = self.active
        props.program_hand = DeckModel.to_hand(self.program_hand, DeckType.PROGRAM_HAND, self.id,
                                               Player.MAX_PROGRAM_HAND_SIZE)
        props.power_hand = DeckModel.to_hand(self.power_hand, DeckType.POWER_HAND, self.id,
                                             Player.MAX_POWER_HAND_SIZE)
        props.registers = RegistersModel.to_registers(self.registers, self.id)

        player: Player = Player(props)
        return player
