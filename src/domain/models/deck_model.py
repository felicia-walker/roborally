from __future__ import annotations

from typing import List

from sqlalchemy import Column, String, Integer, ForeignKey

from application import db
from common.enums import DeckType
from core.base_deck import BaseDeck
from core.card import Card
from core.deck_card import DeckCard
from core.deck import Deck
from core.hand import Hand
from core.base_card import BaseCard


class DeckModel(db.Model):
    __tablename__ = "deck"

    parent_id = Column('parent_id', String, ForeignKey("player.id"), ForeignKey("game.id"), nullable=False,
                       primary_key=True)
    type = Column('type', String, nullable=False, primary_key=True)
    card_order = Column('card_order', Integer, nullable=False, primary_key=True)
    card_type = Column('card_type', String, nullable=False)
    card_num = Column('card_num', Integer, nullable=False)
    card_filename = Column('card_filename', String, nullable=False)
    card_orb = Column('card_orb', Integer, nullable=False, default=0)
    card_num_uses = Column('card_num_uses', Integer, nullable=False, default=0)

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_deck(deck: BaseDeck) -> List[DeckModel]:
        models: List[DeckModel] = []
        for i in range(0, deck.size):
            cur_card: BaseCard = deck.cards[i]

            if type(cur_card ) is DeckCard:
                model: DeckModel = DeckModel(parent_id=deck.id,
                                            type=deck.deck_type,
                                            card_order=i,
                                            card_num=deck.cards[i].number,
                                            card_filename=deck.cards[i].filename,
                                            card_type=deck.cards[i].type,
                                            card_orb=deck.cards[i].orb,
                                            card_num_uses=deck.cards[i].num_uses)
            else:
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

        cards: List[DeckCard] = []
        for row in result:
            id: str = row.parent_id
            t: str = row.type
            card: Card = Card(row.card_num, row.card_filename, row.card_type)
            deck_card: DeckCard = DeckCard(card, row.card_orb, row.card_num_uses)
            cards.append(deck_card)

        deck: Deck = Deck(t, id)
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
            deck_card: DeckCard = DeckCard(card, orb=row.card_orb, num_uses=row.card_num_uses)
            cards.append(deck_card)

        hand: Hand = Hand(type, max_size, id)
        hand.fill(cards)

        return hand
