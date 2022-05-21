from __future__ import annotations

from core.base_deck import BaseDeck


class Hand(BaseDeck):
    def __init__(self, type, max_size=BaseDeck.ABSOLUTE_MAX_DECK_SIZE, id=None):
        super().__init__(type, id, max_size)

    def transfer_card_by_number(self, number: int, target: BaseDeck, target_index: int = None):
        for i in range(0, len(self._cards)):
            if self._cards[i].number == number:
                self.transfer_card(i, target, target_index)

                return

        raise ValueError("Card with number {} not found".format(number))

    def transfer_card(self, index: int, target: BaseDeck, target_index: int = None):
        if target is None:
            raise ValueError("No target deck specified.")

        if index < 0 or index >= len(self._cards):
            raise IndexError("Source index is out of range")

        try:
            card = self._cards.pop(index)
            target.add_card(card, target_index)
        except IndexError as err:
            if card is not None:
                self._cards.insert(index, card)

            raise err
