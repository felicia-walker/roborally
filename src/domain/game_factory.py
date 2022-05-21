from common.enums import DeckType
from core.game import Game, GameProps
from domain.deck_factory import DeckFactory


class GameFactory:
    def __init__(self, deck_factory: DeckFactory = None):
        if deck_factory is None:
            self._deck_factory = DeckFactory()
        else:
            self._deck_factory = deck_factory

    def new_game(self, props: GameProps):
        props.program_deck = self._deck_factory.new_deck(DeckType.PROGRAM_DECK)
        props.program_deck.shuffle()
        props.power_deck = self._deck_factory.new_deck(DeckType.POWER_DECK)
        props.power_deck.shuffle()

        return Game(props)
