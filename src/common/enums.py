from enum import Enum


class CardType(str, Enum):
    PROGRAM = "program"
    POWER = "power"


class DeckType(str, Enum):
    PROGRAM_DECK = "program_deck"
    POWER_DECK = "power_deck"
    PROGRAM_HAND = "program_hand"
    POWER_HAND = "power_hand"
