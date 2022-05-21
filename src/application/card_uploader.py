import os

from common.enums import CardType
from core.card import Card
from domain.card_respository import CardRepository


class CardUploader:
    IMAGE_DIRECTORY: str = "/static/images"

    def __init__(self, base_dir: str = "", card_repository: CardRepository = None):
        if card_repository is None:
            self._card_repository: CardRepository = CardRepository()
        else:
            self._card_repository: CardRepository = card_repository

        if len(base_dir) == 0:
            self._base_dir = os.getcwd() + self.IMAGE_DIRECTORY
        else:
            self._base_dir = base_dir

    def refresh_all_cards(self):
        self._card_repository.clear_all()

        errs: str = self._refresh_power_cards()
        errs2: str = self._refresh_program_cards()

        errors: str = ""
        if len(errs) > 0:
            errors = "Could not add power cards: " + errs + "\n"
        if len(errs2) > 0:
            errors = errors + "Could not add program cards: " + errs2

        if len(errors) > 0:
            raise Exception(errors)

    def _refresh_power_cards(self) -> str:
        cards = os.scandir(self._base_dir + "/power_cards")
        errors: str = ""

        for card in cards:
            if card.is_file():
                parts = card.name.split("_")

                if len(parts) != 2 and card.name:
                    errors = errors + card.name + ", "
                else:
                    number: int = int(parts[0])
                    self._card_repository.create(Card(number, card.name, CardType.POWER))

        return errors

    def _refresh_program_cards(self) -> str:
        cards = os.scandir(self._base_dir + "/program_cards")
        errors: str = ""

        for card in cards:
            if card.is_file():
                parts = card.name.split("_")

                if len(parts) != 3 and card.name:
                    errors = errors + card.name + ", "
                else:
                    number: int = int(parts[2][:-4])  # String out file suffix
                    self._card_repository.create(Card(number, card.name, CardType.PROGRAM))

        return errors
