from __future__ import annotations

from typing import List

from common.repository import Repository
from core.player import Player
from domain.models.player_model import PlayerModel


class PlayerRepository(Repository['Player']):
    def __init__(self, database: str = None):
        super().__init__(database)

    def delete(self, player: Player):
        self.delete_by_id(player.id)

    def delete_by_id(self, id: str):
        with self.get_session_begin() as session:
            result = session.query(PlayerModel).filter_by(id=id).one()
            session.delete(result)

    def save(self, player: Player):
        with self.get_session_begin() as session:
            result: PlayerModel = session.query(PlayerModel).filter_by(id=player.id).first()
            player_model: PlayerModel = PlayerModel.from_player(player)

            if result is not None:
                session.delete(result)

            session.add(player_model)

    def get_by_id(self, id: str) -> Player:
        with self.get_session_begin() as session:
            result: PlayerModel = session.query(PlayerModel).filter_by(id=id).first()

            if result is None:
                return None

            return result.to_player()

    def get_all(self) -> List[Player]:
        players: List[Player] = []

        with self.get_session_begin() as session:
            result: List[PlayerModel] = session.query(PlayerModel).all()

            if result is not None:
                for player in result:
                    players.append(player.to_player())

        return players
