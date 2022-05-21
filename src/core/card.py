from __future__ import annotations

from common.enums import CardType
from common.value_object import ValueObject


class Card(ValueObject['Card']):
    NUMBER_EMPTY: int = -9999
    NUMBER_POWER_DOWN: int = -1002

    @property
    def number(self) -> int:
        return self._number

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def type(self) -> CardType:
        return self._type

    def __init__(self, number: int, filename: str, type: CardType):
        super().__init__()

        values = [item.value for item in CardType]
        if type not in values:
            raise AttributeError("Invalid card type: " + str(type))

        self._number: int = number
        self._filename: str = filename
        self._type: CardType = type

    def equals_core(self, value_object: Card) -> bool:
        result: bool = self._filename == value_object.filename
        result = result and self._number == value_object.number
        result = result and self._type == value_object.type

        return result

    @staticmethod
    def empty() -> Card:
        return Card(Card.NUMBER_EMPTY, "", CardType.POWER)
