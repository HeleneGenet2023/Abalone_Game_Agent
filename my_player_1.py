from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from NodeState import NodeState
#from AlphaBeta import AlphaBeta
from game_state_abalone import GameStateAbalone
from seahorse.game.game_layout.board import Piece
from seahorse.game.action import Action
import json
from AlphaBetaZobrist import AlphaBetaZobrist
from TranspositionTable import ZobristTable

class MyPlayer(PlayerAbalone):
    """
    Classe de joueur pour le jeu Abalone.

    Attributs:
        piece_type (str): type de pièce du joueur
    """


    def __init__(self, piece_type: str, name: str = "Alpha Beta", time_limit: float=60*15,*args) -> None:
        """
        Initialise l'instance PlayerAbalone.

        Args:
            piece_type (str): Type de la pièce de jeu du joueur
            name (str, facultatif): Nom du joueur (par défaut "bob")
            time_limit (float, facultatif): limite de temps en (s)
        """
        super().__init__(piece_type,name,time_limit,*args)
        self.myStep = 0        
        self.strategy = AlphaBetaZobrist(depth =1 , playerID=self.id)
        self.hit_rate= 0
        self.zobrist_table = ZobristTable()
        self.node_visits=0
    
    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Fonction pour implémenter la logique du joueur.

        Args:
            current_state (GameState): Représentation de l'état de jeu actuel
            **kwargs: Arguments supplémentaires par mot-clé

        Returns:
            Action: action réalisable sélectionnée
        """
        self.strategy.pruned_nodes_max = 0
        self.strategy.pruned_nodes_min = 0
        node = NodeState(current_state,self.id,self.name,self.piece_type)
        print(f"{self.piece_type} Player turn.")
        print(f"Max player color : {node.maxPlayerPieceType} score : {node.maxPlayerScore}")
        print(f"Min player color : {node.minPlayerPieceType} score : {node.minPlayerScore}")

        _,action = self.strategy.search(node)
            
        self.myStep += 1
        return action

