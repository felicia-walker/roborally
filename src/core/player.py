from __future__ import annotations

from common.entity import Entity
from common.enums import DeckType
from core.base_deck import BaseDeck
from core.card import Card
from core.deck import Deck
from core.hand import Hand
from core.registers import Registers


class Player(Entity):
    MAX_PROGRAM_HAND_SIZE: int = 9
    MAX_POWER_HAND_SIZE: int = 999
    REGISTER_LOCK_THRESHOLD: int = 5

    @property
    def name(self) -> str:
        return self._name

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def is_powered_down(self) -> bool:
        return self._powered_down

    @property
    def will_be_powered_down(self) -> bool:
        return self._will_power_down

    @property
    def registers(self) -> Registers:
        return self._registers

    @property
    def program_hand(self) -> Hand:
        return self._program_hand

    @property
    def power_hand(self) -> Hand:
        return self._power_hand

    @property
    def is_destroyed(self) -> bool:
        return self._damage > self.MAX_PROGRAM_HAND_SIZE

    @property
    def avatar_filename(self) -> str:
        return self._avatar_filename

    @avatar_filename.setter
    def avatar_filename(self, value: str):
        self._avatar_filename = value

    @property
    def instructions(self) -> str:
        return self._instructions

    @instructions.setter
    def instructions(self, value: str):
        self._instructions = value

    @property
    def is_active(self) -> bool:
        return self._active

    @is_active.setter
    def is_active(self, value: bool):
        self._active = value

    def __init__(self, props: PlayerProps):
        super().__init__()

        self._name: str = props.name
        self._registers: Registers = props.registers
        self._program_hand: Hand = props.program_hand
        self._power_hand: Hand = props.power_hand
        self._damage: int = props.damage
        self._powered_down: bool = props.powered_down
        self._will_power_down: bool = props.will_power_down
        self._avatar_filename: str = props.avatar_filename
        self._instructions: str = props.instructions
        self._active: bool = props.active

        if len(props.id) > 0:
            self._id = props.id

    # Test only?
    def move_card_to_register(self, card: int, register: int):
        if self.is_powered_down:
            return

        self._program_hand.transfer_card(card, self._registers, register)

    # Test only?
    def move_card_to_hand(self, register: int):
        if self.is_powered_down:
            return

        self._registers.transfer_card(register, self._program_hand)

    # Test only?
    def draw_power_card(self, deck: Deck) -> Card:
        return deck.deal_card(self._power_hand)

    def reset_program_hand(self, deck: Deck):
        self._program_hand.clear()

        if self.is_powered_down or not self.is_active:
            return

        for i in range(0, self.MAX_PROGRAM_HAND_SIZE - self._damage):
            deck.deal_card(self._program_hand)

    def reset_damage(self):
        self._damage = 0
        self.registers.reset_locks()

    def inc_damage(self):
        self._damage = self._damage + 1

        if self._damage >= self.REGISTER_LOCK_THRESHOLD:
            self._registers.lock_register()

        if self._damage > self.MAX_PROGRAM_HAND_SIZE:
            self._damage = self.MAX_PROGRAM_HAND_SIZE + 1

    def dec_damage(self):
        # Need to unlock then undamage when going backwards
        if self._damage >= self.REGISTER_LOCK_THRESHOLD and self._damage <= self.MAX_PROGRAM_HAND_SIZE:
            self._registers.unlock_register()

        self._damage = self._damage - 1

        if self._damage < 0:
            self._damage = 0

    def will_power_down(self):
        self._will_power_down = True

    def will_power_up(self):
        self._will_power_down = False

    def power_down(self):
        self._powered_down = True

    def power_up(self):
        self._powered_down = False

    def reset(self):
        # Don't reset "active" since that is turn independent 
        self._instructions: str = ""
        self._damage: int = 0
        self._powered_down: bool = False
        self._will_power_down: bool = False
        self._program_hand = Hand(DeckType.PROGRAM_HAND, self.MAX_PROGRAM_HAND_SIZE)
        self._power_hand = Hand(DeckType.POWER_HAND, self.MAX_POWER_HAND_SIZE)
        self._registers = Registers()

    def get_hand_by_name(self, name: str) -> BaseDeck:
        if name.lower() == DeckType.PROGRAM_HAND.value:
            return self.program_hand

        if name.lower() == DeckType.POWER_HAND.value:
            return self.power_hand

        if name.lower() == "registers":
            return self.registers

        raise ValueError("Invalid deck type: " + name)


class PlayerProps:
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.registers: Registers = None
        self.program_hand: Hand = None
        self.power_hand: Hand = None
        self.damage: int = 0
        self.powered_down: bool = False
        self.will_power_down: bool = False
        self.avatar_filename: str = ""
        self.instructions: str = ""
        self.active: bool = True
