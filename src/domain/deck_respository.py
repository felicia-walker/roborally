from __future__ import annotations

from typing import List

from sqlalchemy.orm import Query, Session

from common.enums import DeckType
from common.repository import Repository
from core.base_deck import BaseDeck
from core.deck import Deck
from domain.models.deck_model import DeckModel


class DeckRepository(Repository[BaseDeck]):
    def __init__(self, database: str = None):
        super().__init__(database)

    def delete(self, deck: Deck):
        self.delete_by_id(deck.id)

    def delete_by_id(self, id: str):
        with self.get_session_begin() as session:
            session.query(DeckModel).filter_by(id=id).delete()

    def save(self, deck: Deck, session: Session = None):
        if session is None:
            session = self.get_session_begin()

        with session as s:
            result: Query = s.query(DeckModel).filter_by(parent_id=deck.id)
            deck_models: List[DeckModel] = DeckModel.from_deck(deck)

            if result.count() > 0:
                result.delete()

            s.add_all(deck_models)

    def get_by_id_and_type(self, id: str, type: DeckType) -> Deck:
        with self.get_session_begin() as session:
            result: List[DeckModel] = session.query(DeckModel).filter_by(parent_id=id).order_by(
                DeckModel.card_order).all()

            return DeckModel.to_deck(result, type, id)
