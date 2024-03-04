from __future__ import annotations

import copy
import json
from typing import TYPE_CHECKING

from board_abalone import BoardAbalone
from seahorse.game.action import Action
from seahorse.game.game_layout.board import Piece
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable

if TYPE_CHECKING:
    from game_state_abalone import GameStateAbalone


class PlayerAbalone(Player):
    """
    Une classe de joueur pour le jeu Abalone.

    Attributs:
        piece_type (str): type de pièce du joueur
    """

    def __init__(self, piece_type: str, name: str = "bob", *args, **kwargs) -> None:
        """
        Initialise une nouvelle instance de la classe JoueurAbalone.

        Args:
            piece_type (str): Type de la pièce de jeu du joueur.
            name (str, facultatif): Le nom du joueur. Par défaut, "bob".
        """
        super().__init__(name,*args,**kwargs)
        self.piece_type = piece_type

    def get_piece_type(self) -> str:
        """
        Obtient le type de pièce de jeu du joueur.

        Returns:
            str: Le type de pièce de jeu du joueur.
        """
        return self.piece_type

    def to_json(self) -> str:
        return {i:j for i,j in self.__dict__.items() if i!="timer"}

    @classmethod
    def from_json(cls, data) -> Serializable:
        return PlayerAbalone(**json.loads(data))
