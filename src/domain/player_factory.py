from common.enums import DeckType
from core.hand import Hand
from core.player import PlayerProps, Player
from core.registers import Registers


class PlayerFactory:

    @staticmethod
    def new_player(props: PlayerProps) -> Player:
        props.program_hand = Hand(DeckType.PROGRAM_HAND)
        props.power_hand = Hand(DeckType.POWER_HAND)
        props.registers = Registers()

        player: Player = Player(props)
        return player
