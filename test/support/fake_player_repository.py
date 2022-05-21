from __future__ import annotations

from typing import Dict, List

from sqlalchemy.orm import Query

from common.enums import DeckType, CardType
from core.card import Card
from core.deck import Deck
from core.player import PlayerProps, Player
from core.registers import Registers
from domain.models.deck_model import DeckModel
from domain.models.player_model import PlayerModel
from domain.models.registers_model import RegistersModel
from domain.player_respository import PlayerRepository
from support.fake_deck_repository import FakeDeckRepository


class FakePlayerRepository(PlayerRepository):

    @property
    def player_data(self):
        return self._player_data

    @property
    def register_data(self):
        return self._register_data

    def __init__(self):
        super().__init__("/test/support/test.db")

        self._player_data = [
            {'id': "111xyz", 'name': "Lance Uppercut", 'damage': 3, 'life': 2,
                'powered_down': True, 'avatar_filename': 'one.jpg'},
            {'id': "a-34-er", 'name': "Tralfaz Abzot", 'damage': 10, 'life': 0, 'powered_down': False,
                'avatar_filename': 'two.png'},
            {'id': "45tub", 'name': "Foxy Donuts", 'damage': 0, 'life': 4, 'powered_down': False,
                'avatar_filename': 'three.jpg'}
        ]

        self._register_data = [
            {'parent_id': "111xyz", 'register_num': 0, 'card_number': 346, 'card_filename': 'kira_kira.png',
                'locked': 0},
            {'parent_id': "111xyz", 'register_num': 1, 'card_number': 6, 'card_filename': 'mofu_mofu.png', 'locked': 0},
            {'parent_id': "111xyz", 'register_num': 2, 'card_number': 1111, 'card_filename': 'kari_kari.png',
                'locked': 0},
            {'parent_id': "111xyz", 'register_num': 3, 'card_number': 6789, 'card_filename': 'fuwa_fuwa.png',
                'locked': 1},
            {'parent_id': "111xyz", 'register_num': 4, 'card_number': 204, 'card_filename': 'pika_pika.png',
                'locked': 1},
            {'parent_id': "a-34-er", 'register_num': 0, 'card_number': 34, 'card_filename': 'ware_ware.png',
                'locked': 0},
            {'parent_id': "a-34-er", 'register_num': 1, 'card_number': 9, 'card_filename': 'soro_soro.png',
                'locked': 0},
            {'parent_id': "a-34-er", 'register_num': 2, 'card_number': -1, 'card_filename': '', 'locked': 0},
            {'parent_id': "a-34-er", 'register_num': 3, 'card_number': -1, 'card_filename': '', 'locked': 0},
            {'parent_id': "a-34-er", 'register_num': 4, 'card_number': 22, 'card_filename': 'tsuya_tsuya.png',
                'locked': 0}]

        self._deck_repo = FakeDeckRepository()
        self.reset()

    def reset(self):
        self.clear_all()
        self._deck_repo.reset()

        with self.get_session_begin() as session:
            for item in self._player_data:
                model_player: PlayerModel = PlayerModel(id=item['id'],
                                                        name=item['name'],
                                                        damage=item['damage'],
                                                        powered_down=item['powered_down'],
                                                        avatar_filename=item['avatar_filename'])
                session.add(model_player)

            for item in self._register_data:
                model_registers: RegistersModel = RegistersModel(parent_id=item['parent_id'],
                                                                 register_num=item['register_num'],
                                                                 card_num=item['card_number'],
                                                                 card_filename=item['card_filename'],
                                                                 locked=item['locked'])
                session.add(model_registers)

    def clear_all(self):
        self._deck_repo.clear_all()

        with self.get_session_begin() as session:
            session.query(RegistersModel).delete()
            session.query(PlayerModel).delete()

    def are_registers_present(self, id: str) -> List[Registers]:
        with self.get_session_begin() as session:
            result: Query = session.query(RegistersModel).filter_by(parent_id=id)

            return result.count() > 0

    def is_deck_present(self, id: str, deck_type: DeckType) -> List[Registers]:
        with self.get_session_begin() as session:
            result: Query = session.query(DeckModel).filter(DeckModel.parent_id == id, DeckModel.type == deck_type)

            return result.count() > 0

    # -------

    def get_fake_player_info(self, id: str) -> Dict:
        dict: Dict = {}
        for player in self._player_data:
            if player['id'] == id:
                dict = player
                break

        return dict

    def get_fake_register_info(self, id: str) -> (List[str], List[str], List[bool]):
        nums = [item['card_number'] for item in self._register_data if item['parent_id'] == id]
        filenames = [item['card_filename'] for item in self._register_data if item['parent_id'] == id]
        locks = [bool(item['locked']) for item in self._register_data if item['parent_id'] == id]

        return nums, filenames, locks

    def get_fake_card_info_by_deck_id(self, id: str, type: DeckType) -> (List[int], List[str], List[str]):
        return self._deck_repo.get_fake_card_info(id, type)

    def create_fake_player(self, id: str) -> Player:
        info: Dict = self.get_fake_player_info(id)
        props: PlayerProps = PlayerProps()
        props.id = info['id']
        props.name = info['name']
        props.damage = info['damage']
        props.powered_down = info['powered_down']
        props.avatar_filename = info['avatar_filename']

        props.program_hand = Deck(DeckType.PROGRAM_HAND)
        props.program_hand.fill(self._get_fake_cards(info['id'], DeckType.PROGRAM_HAND))
        props.power_hand = Deck(DeckType.POWER_HAND)
        props.power_hand.fill(self._get_fake_cards(info['id'], DeckType.POWER_HAND))

        nums, filenames, locks = self.get_fake_register_info(info['id'])
        cards: List[Card] = []

        for i in range(0, len(nums)):
            cards.append(Card(nums[i], filenames[i], CardType.PROGRAM))
        props.registers = Registers(info['id'], cards, locks)

        return Player(props)

    def _get_fake_cards(self, id: str, type: DeckType) -> List[Card]:
        card_info = self._deck_repo.get_fake_card_info(id, type)
        fake_cards = tuple(zip(card_info[0], card_info[1], card_info[2]))
        cards: List[Card] = []

        for card in fake_cards:
            cards.append(Card(card[0], card[1], card[2]))

        return cards
