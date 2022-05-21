from typing import List

from common.repository import Repository
from core.card import Card
from core.deck import Deck


class DummyRepository(Repository):

    def __init__(self):
        pass

    def clear_all(self):
        pass

    def save(self, obj):
        pass

    def clear_all(self):
        pass

    def get_cards_by_id(self, id: str):
        return []

    def get_registers_by_id(self, id: str) -> (List[Card], List[bool]):
        return [], []

    def get_deck_by_id(self, id: str) -> Deck:
        return None

    def delete_by_id(self, id: str):
        pass

    def delete(self, o: object):
        pass

