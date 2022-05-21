from __future__ import annotations

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import validates

from application import db
from common.enums import CardType
from core.card import Card


class CardModel(db.Model):
    __tablename__ = "card"

    number = Column(Integer, nullable=False)
    filename = Column(String, nullable=False, primary_key=True)
    type = Column(String, nullable=False, primary_key=True)

    @validates('number')
    def validate_number_not_empty(self, key, value):
        if value is None:
            raise ValueError(f"{key.capitalize()} is required.")

        return value

    @validates('filename')
    def validate_filename_not_empty(self, key, value):
        if not value:
            raise ValueError(f"{key.capitalize()} is required.")

        return value

    @validates('type')
    def validate_type_not_invalid(self, key, value):
        if not value:
            raise ValueError(f"{key.capitalize()} is required.")

        if value != CardType.POWER and value != CardType.PROGRAM:
            raise ValueError(f"{key.capitalize()} must be a valid card type.")

        return value

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_card(card: Card) -> CardModel:
        if card is None:
            return None

        return CardModel(number=card.number,
                         filename=card.filename,
                         type=card.type)

    def to_card(self) -> Card:
        return Card(number=self.number,
                    filename=self.filename,
                    type=self.type)
