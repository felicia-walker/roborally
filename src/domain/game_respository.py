from __future__ import annotations

import sqlalchemy.exc

from common.repository import Repository
from core.game import Game
from domain.models.game_model import GameModel


class GameRepository(Repository['Game']):

    def __init__(self, database: str = None):
        super().__init__(database)

    def clear_all(self):
        with self.get_session_begin() as session:
            try:
                results = session.query(GameModel)

                for result in results:
                    session.delete(result)
            except sqlalchemy.exc.NoResultFound:
                pass

    def delete(self, game: Game):
        self.delete_by_id(game.id)

    def delete_by_id(self, id: str):
        with self.get_session_begin() as session:
            result = session.query(GameModel).filter_by(id=id).first()

            if result is not None:
                session.delete(result)

    def save(self, game: Game):
        with self.get_session_begin() as session:
            result: GameModel = session.query(GameModel).filter_by(id=game.id).first()
            game_model: GameModel = GameModel.from_game(game)

            if result is not None:
                session.delete(result)

            session.add(game_model)

    def get_game(self) -> Game:
        with self.get_session_begin() as session:
            result: GameModel = session.query(GameModel).first()

            if result is None:
                return None

            return result.to_game()

    def get_by_id(self, id: str) -> Game:
        return self.get_game()
