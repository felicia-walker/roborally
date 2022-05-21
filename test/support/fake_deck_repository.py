from __future__ import annotations

from typing import List

from common.enums import DeckType
from domain.deck_respository import DeckRepository
from domain.models.deck_model import DeckModel


class FakeDeckRepository(DeckRepository):
    @property
    def data(self):
        return self._data

    def __init__(self):
        super().__init__("/test/support/test.db")

        self._data = [
            {'parent_id': "abc123", 'type': "program_deck", 'card_type': "program", 'card_order': 0, 'card_number': 346,
                'card_filename': 'kira_kira.png'},
            {'parent_id': "abc123", 'type': "program_deck", 'card_type': "program", 'card_order': 1, 'card_number': 6,
                'card_filename': 'mofu_mofu.png'},
            {'parent_id': "abc123", 'type': "program_deck", 'card_type': "program", 'card_order': 2,
                'card_number': 1111, 'card_filename': 'kari_kari.png'},
            {'parent_id': "abc123", 'type': "program_deck", 'card_type': "program", 'card_order': 3,
                'card_number': 6789, 'card_filename': 'fuwa_fuwa.png'},
            {'parent_id': "abc123", 'type': "program_deck", 'card_type': "program", 'card_order': 4, 'card_number': 204,
                'card_filename': 'pika_pika.png'},
            {'parent_id': "xyz-5-6", 'type': "power_deck", 'card_type': "power", 'card_order': 0, 'card_number': 34,
                'card_filename': 'ware_ware.png'},
            {'parent_id': "xyz-5-6", 'type': "power_deck", 'card_type': "power", 'card_order': 1, 'card_number': 9,
                'card_filename': 'soro_soro.png'},
            {'parent_id': "xyz-5-6", 'type': "power_deck", 'card_type': "power", 'card_order': 2, 'card_number': 175,
                'card_filename': 'waka_waka.png'},
            {'parent_id': "111xyz", 'type': "power_hand", 'card_type': "power", 'card_order': 0, 'card_number': 224,
                'card_filename': 'tsuya_tsuya.png'},
            {'parent_id': "111xyz", 'type': "power_hand", 'card_type': "power", 'card_order': 1, 'card_number': 69,
                'card_filename': 'doki_doki.png'},
            {'parent_id': "111xyz", 'type': "program_hand", 'card_type': "program", 'card_order': 0, 'card_number': 656,
                'card_filename': 'go_go_go.png'},
            {'parent_id': "111xyz", 'type': "program_hand", 'card_type': "program", 'card_order': 1, 'card_number': 77,
                'card_filename': 'ban.png'},
            {'parent_id': "111xyz", 'type': "program_hand", 'card_type': "program", 'card_order': 2, 'card_number': 27,
                'card_filename': 'jii.png'},
            {'parent_id': "111xyz", 'type': "power_hand", 'card_type': "power", 'card_order': 0, 'card_number': 98,
                'card_filename': 'zu_sha.png'},
            {'parent_id': "a-34-er", 'type': "power_hand", 'card_type': "power", 'card_order': 0, 'card_number': 124,
                'card_filename': 'muco.png'},
            {'parent_id': "a-34-er", 'type': "power_hand", 'card_type': "power", 'card_order': 1, 'card_number': 19,
                'card_filename': 'komatsu.png'},
            {'parent_id': "a-34-er", 'type': "program_hand", 'card_type': "program", 'card_order': 0,
                'card_number': 616,
                'card_filename': 'ishiko.png'},
            {'parent_id': "a-34-er", 'type': "program_hand", 'card_type': "program", 'card_order': 1, 'card_number': 71,
                'card_filename': 'rena.png'},
            {'parent_id': "a-34-er", 'type': "program_hand", 'card_type': "program", 'card_order': 2, 'card_number': 17,
                'card_filename': 'shinohara.png'},
            {'parent_id': "a-34-er", 'type': "power_hand", 'card_type': "power", 'card_order': 0, 'card_number': 91,
                'card_filename': 'bouda.png'}
        ]

        self.reset()

    def reset(self):
        self.clear_all()

        with self.get_session_begin() as session:
            for item in self._data:
                model_deck: DeckModel = DeckModel(parent_id=item['parent_id'],
                                                  type=item['type'],
                                                  card_order=item['card_order'],
                                                  card_num=item['card_number'],
                                                  card_filename=item['card_filename'],
                                                  card_type=item['card_type'])
                session.add(model_deck)

    def get_card_nums_by_parent(self, id: str, deck_type: DeckType) -> List[int]:
        with self.get_session_begin() as session:
            result = session.query(DeckModel.card_num).filter(
                DeckModel.parent_id == id, DeckModel.type == deck_type).order_by(
                DeckModel.card_order)
            nums: List[int] = [value for value, in result]

            return nums

    def get_card_filenames_by_parent(self, id: str, deck_type: DeckType) -> List[str]:
        with self.get_session_begin() as session:
            result = session.query(DeckModel.card_filename).filter(
                DeckModel.parent_id == id, DeckModel.type == deck_type).order_by(DeckModel.card_order)
            filenames: List[int] = [value for value, in result]

            return filenames

    def get_card_types_by_parent(self, id: str, deck_type: DeckType) -> List[str]:
        with self.get_session_begin() as session:
            result = session.query(DeckModel.type).filter(
                DeckModel.parent_id == id, DeckModel.type == deck_type).order_by(DeckModel.card_order)
            types: List[int] = [value for value, in result]

            return types

    def clear_all(self):
        with self.get_session_begin() as session:
            session.query(DeckModel).delete()

    # -------------

    def get_fake_card_info(self, id: str, type: DeckType) -> (List[int], List[str], List[str]):
        nums = [item['card_number'] for item in self._data if item['parent_id'] == id and item['type'] == type]
        filenames = [item['card_filename'] for item in self._data if item['parent_id'] == id and item['type'] == type]
        types = [item['card_type'] for item in self._data if item['parent_id'] == id and item['type'] == type]

        return nums, filenames, types
