from core.card import Card
from core.hand import Hand


class MockHand(Hand):

    def __init__(self):
        pass

    def add_card(self, card: Card, index: int = None):
        raise IndexError("Cannot add any more cards to this hand.")
