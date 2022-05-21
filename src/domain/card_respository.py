from __future__ import annotations

from typing import List

from sqlalchemy.orm import Query

from common.enums import CardType
from common.repository import Repository, T
from core.card import Card
from domain.models.card_model import CardModel


class CardRepository(Repository[Card]):
    def __init__(self, database: str = None):
        super().__init__(database)

    def get_by_id(self, id: str) -> T:
        raise NotImplemented("Cannot look value objects up by id")

    def save(self, card: Card):
        raise NotImplemented("Value objects cannot be saved")

    def delete(self, card: Card):
        model_card: CardModel = CardModel.from_card(card)

        with self.get_session_begin() as session:
            session.delete(model_card)

    def clear_all(self):
        with self.get_session_begin() as session:
            session.query(CardModel).delete()

    def create(self, card: Card):
        model_card: CardModel = CardModel.from_card(card)

        with self.get_session_begin() as session:
            session.add(model_card)

    def get_all_by_type(self, type: CardType) -> List[Card]:
        with self.get_session_begin() as session:
            result: Query = \
                session.query(CardModel).filter(CardModel.type == type,
                                                CardModel.number != 9999).order_by(CardModel.number)

            cards: List[Card] = []
            for row in result:
                cards.append(row.to_card())

        return cards

    def get_card_back(self, type: CardType) -> Card:
        with self.get_session_begin() as session:
            db_card: CardModel = session.query(CardModel).filter(CardModel.type == type,
                                                                 CardModel.number == 9999).first()

            return db_card.to_card()
