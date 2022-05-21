from __future__ import annotations

from typing import List

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean

from application import db
from common.enums import CardType
from core.card import Card
from core.registers import Registers


class RegistersModel(db.Model):
    __tablename__ = "registers"

    parent_id = Column('parent_id', ForeignKey("player.id"), primary_key=True)
    register_num = Column('register_num', Integer, nullable=False, primary_key=True)
    card_num = Column('card_num', Integer, nullable=False)
    card_filename = Column('card_filename', String, nullable=False)
    locked = Column('locked', Boolean, nullable=False)
    throw = Column('throw', Boolean, nullable=False, default=0)

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_registers(registers: Registers) -> List[RegistersModel]:
        models: List[RegistersModel] = []
        for i in range(0, registers.size):
            model: RegistersModel = RegistersModel(parent_id=registers.id,
                                                   register_num=i,
                                                   card_num=registers.cards[i].number,
                                                   card_filename=registers.cards[i].filename,
                                                   locked=registers.locks[i],
                                                   throw=registers.throws[i])
            models.append(model)

        return models

    @staticmethod
    def to_registers(result: List[RegistersModel], parent_id: str) -> Registers:
        if len(result) == 0:
            return Registers(parent_id)

        cards: List[Card] = []
        locks: List[Boolean] = []
        throws: List[Boolean] = []
        for row in result:
            id: str = row.parent_id
            card: Card = Card(row.card_num, row.card_filename, CardType.PROGRAM)
            cards.append(card)
            locks.append(row.locked)
            throws.append(row.throw)

        registers: Registers = Registers(id, cards, locks, throws)
        return registers
