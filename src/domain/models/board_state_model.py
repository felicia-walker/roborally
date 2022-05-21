from __future__ import annotations

from typing import List

from sqlalchemy import Column, String, ForeignKey

from application import db


class BoardStateModel(db.Model):
    __tablename__ = "board_state"

    parent_id = Column('parent_id', String, ForeignKey("game.id"), nullable=False)
    filename = Column('filename', String, nullable=False, primary_key=True)

    def __repr__(self):
        return self.filename

    @staticmethod
    def from_board_state_filenames(filenames: List[str], parent_id: str) -> List[BoardStateModel]:
        models: List[BoardStateModel] = []
        for filename in filenames:
            model: BoardStateModel = BoardStateModel(parent_id=parent_id,
                                                     filename=filename)
            models.append(model)

        return models

    @staticmethod
    def to_board_state_filenames(result: List[BoardStateModel]) -> List[str]:
        filenames: List[str] = []
        for row in result:
            filenames.append(row.filename)

        return filenames
