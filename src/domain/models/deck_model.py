from __future__ import annotations

from typing import List

from sqlalchemy import Column, String, Integer, ForeignKey

from application import db
from common.enums import DeckType
from core.base_deck import BaseDeck
from core.card import Card
from core.deck import Deck
from core.hand import Hand


class DeckModel(db.Model):
    __tablename__ = "deck"

    parent_id = Column('parent_id', String, ForeignKey("player.id"), ForeignKey("game.id"), nullable=False,
                       primary_key=True)
    type = Column('type', String, nullable=False, primary_key=True)
    card_order = Column('card_order', Integer, nullable=False, primary_key=True)
    card_type = Column('card_type', String, nullable=False)
    card_num = Column('card_num', Integer, nullable=False)
    card_filename = Column('card_filename', String, nullable=False)

    # num_uses = Column('num_uses', Integer, nullable=False, default=0)

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_deck(deck: BaseDeck) -> List[DeckModel]:
        models: List[DeckModel] = []
        for i in range(0, deck.size):
            model: DeckModel = DeckModel(parent_id=deck.id,
                                         type=deck.deck_type,
                                         card_order=i,
                                         card_num=deck.cards[i].number,
                                         card_filename=deck.cards[i].filename,
                                         card_type=deck.cards[i].type)
            models.append(model)

        return models

    @staticmethod
    def to_deck(result: List[DeckModel], type: DeckType, parent_id: str) -> Deck:
        if len(result) == 0:
            return Deck(type, parent_id)

        cards: List[Card] = []
        for row in result:
            id: str = row.parent_id
            type: str = row.type
            card: Card = Card(row.card_num, row.card_filename, row.card_type)
            cards.append(card)

        deck: Deck = Deck(type, id)
        deck.fill(cards)

        return deck

    @staticmethod
    def to_hand(result: List[DeckModel], type: DeckType, parent_id: str,
                max_size: int = Deck.ABSOLUTE_MAX_DECK_SIZE) -> Hand:
        if len(result) == 0:
            return Hand(type, id=parent_id)

        cards: List[Card] = []
        for row in result:
            id: str = row.parent_id
            type: str = row.type
            card: Card = Card(row.card_num, row.card_filename, row.card_type)
            cards.append(card)

        hand: Hand = Hand(type, max_size, id)
        hand.fill(cards)

        return hand
