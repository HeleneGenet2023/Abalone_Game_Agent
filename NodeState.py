from game_state_abalone import GameStateAbalone
from seahorse.game.game_state import GameState
from seahorse.game.action import Action
from copy import copy
def manhattanDist(A, B):
    dist = abs(B[0] - A[0]) + abs(B[1] - A[1])
    return dist

# Classe pour représenter l'état d'un nœud dans l'arbre de recherche
class NodeState:
    """
    Classe NodeState pour représenter l'état d'un nœud dans l'arbre de recherche.
    """
    def __init__(self, game: GameState, maxPlayerID: int, maxPlayerName: str, maxPlayerPieceType: str):
        """
        Initialise un nouvel objet NodeState.
        
        Args:
            game (GameState): L'état actuel du jeu.
            currentPlayerID (int): L'ID du joueur courant.
            currentPlayerName (str): Le nom du joueur courant.
            currentPlayerPieceType (str): Le type de pièce du joueur courant (noir ou blanc).
        """
        # Informations sur le noeud parent et l'action pour arriver au noeud actuel
        self.parent = None
        self.action_from_parent = None
        # Type de pièce pour chaque joueur : noir et blanc
        self.maxPlayerPieceType = maxPlayerPieceType
        self.minPlayerPieceType = self.getMinPlayerPieceType()
        self.gameState = game
        
        # Définition des joueurs
        self.maxPlayerID = maxPlayerID
        self.maxPlayerName = maxPlayerName
        self.minPlayerID = self.getMinPlayerID()
        self.minPlayerName = self.getMinPlayerName()
        # Informations sur le joueur MIN
        self.minPlayerScore = self.gameState.scores[self.maxPlayerID] * -1
        # Informations sur le joueur MAX    
        self.maxPlayerScore = self.gameState.scores[self.minPlayerID] * -1 # Si l'agent MAX pousse une bille ennemie, le score augmente de 1
        # Distances de Manhattan
        self.maxPlayerDistance, self.minPlayerDistance = self.distanceFromCenter()

    def getMinPlayerPieceType(self) -> str:
        """
        Détermine le type de pièce du joueur suivant en fonction du type de pièce du joueur courant.
        
        Returns:
            str: Le type de pièce du joueur suivant ("B" pour noir, "W" pour blanc).
        """
        if self.maxPlayerPieceType == "B":
            return "W"
        return "B"

    def isTerminal(self) -> bool:
        """
        Vérifie si l'état du jeu est terminal (fini).
        
        Returns:
            bool: True si le jeu est terminé, sinon False.
        """
        return self.gameState.is_done()

    def getActions(self) -> list:
        """
        Génère la liste des actions possibles à partir de l'état actuel du jeu.
        
        Returns:
            list: Liste des actions possibles.
        """
        return list(self.gameState.generate_possible_actions())

    def applyAction(self, action : Action):
        """
        Applique une action à l'état actuel du jeu pour obtenir un nouvel état.
        
        Args:
            action: L'action à appliquer.
        
        Returns:
            NodeState: Le nouvel état du jeu après l'application de l'action.
        """
        nextGameState = action.get_next_game_state()
        child_node = NodeState(nextGameState, self.maxPlayerID, self.maxPlayerName, self.maxPlayerPieceType)
        return child_node


    def getChildren(self, playerType = "max")  -> list:
        """
        Obtient la liste des états enfants en appliquant toutes les actions possibles à l'état actuel.
        
        Returns:
            list: Liste des états enfants.
        """
        actions = self.getActions()
        children = list()
        for action in actions :
            action, child = action, self.applyAction(action)
            if playerType == "max" : 
                currentMinScore = self.minPlayerScore
                nextMinScore = child.minPlayerScore
                if nextMinScore <= currentMinScore :  # On ne retourne pas les mouvements qui impliquent de pousser ses propres billes
                    children.append((action, child))
                    children.append((action, child))
            if playerType == "min" : 
                currentMaxScore = self.maxPlayerScore
                nextMaxScore = child.maxPlayerScore
                if nextMaxScore <= currentMaxScore : # On ne retourne pas les mouvements qui impliquent de pousser ses propres billes
                    children.append((action, child))
        return children

    def getMinPlayerID(self) -> int:
        """
        Trouve l'ID du joueur suivant.
        
        Returns:
            int: L'ID du joueur suivant.
        """
        for player_id in self.gameState.scores.keys():
            if player_id != self.maxPlayerID:
                return player_id
        return None

    def getMinPlayerName(self) -> str:
        """
        Trouve le nom du joueur suivant.
        
        Returns:
            str: Le nom du joueur suivant.
        """
        for player in self.gameState.players:
            if player.name != self.maxPlayerName:
                return player.name
        return None

    def get_player_scores(self) -> dict:
        """
        Obtient les scores des joueurs.
        
        Returns:
            dict: Dictionnaire contenant les scores des joueurs.
        """
        return self.gameState.scores

    def distanceFromCenter(self) -> tuple:
        """
        Calcule la distance de Manhattan depuis le centre pour chaque joueur.
        
        Returns:
            tuple: Distance de Manhattan pour le joueur courant et le joueur suivant.
        """
        final_rep = self.gameState.get_rep()
        env = final_rep.get_env()
        dim = final_rep.get_dimensions()
        dist = dict.fromkeys([self.maxPlayerID, self.minPlayerID], 0)
        center = (dim[0] // 2, dim[1] // 2)
        for i, j in list(env.keys()):
            p = env.get((i, j), None)
            if p.get_owner_id():
                dist[p.get_owner_id()] += manhattanDist(center, (i, j))

        return dist[self.maxPlayerID], dist[self.minPlayerID]

    def isWin(self) -> bool:
        """
        Détermine si l'état actuel est un état gagnant.
        
        Returns:
            bool: True si l'état est gagnant, False sinon, si egalite renvoie None.
        """
        if self.maxPlayerScore != self.minPlayerScore:
            return self.maxPlayerScore > self.minPlayerScore
        
        elif self.maxPlayerDistance != self.minPlayerDistance:
            return self.maxPlayerDistance > self.minPlayerDistance
        
        return None
    
    def isCapturingMove(self,action, playerType = "max") -> bool:
        
        nextNode = self.applyAction(action)
        if playerType == "max" :
            score_diff = nextNode.minPlayerScore - self.minPlayerScore
            return score_diff > 0
        
        elif playerType == "min" : 
            score_diff = nextNode.maxPlayerScore - self.maxPlayerScore
            return score_diff > 0
        
    def isQuiescent(self, actions, playerType="max") -> bool:
        if self.isTerminal():
            return True

        # Si les mouvements ultérieurs conduisent à une capture possible par un ennemi, l'état n'est pas quiescent
        captureMove = any(self.isCapturingMove(action, playerType) for action in actions)
        return captureMove == False
    
    def calculateCohesion(self, playerType = "max") -> float:
        """Somme des distances de manhattan entre chaque pair de billes"""
        board = self.gameState.get_rep()
        player_marbles = []  # Liste des coord. des marbres

        for i in range(board.dimensions[0]):
            for j in range(board.dimensions[1]):
                
                if playerType == "max" :
                    if board.env.get((i, j)) and board.env[(i, j)].get_owner_id() == self.maxPlayerPieceType:
                        player_marbles.append((i, j))

                elif playerType == "min" : 
                    if board.env.get((i, j)) and board.env[(i, j)].get_owner_id() == self.minPlayerPieceType:
                        player_marbles.append((i, j))

        if len(player_marbles) == 0:
            return 0.0  # Pas de marbre pour pour le calcul cohesion

        total_distance = 0
        for marble1 in player_marbles:
            for marble2 in player_marbles:
                total_distance += manhattanDist(marble1, marble2)

        average_distance = total_distance / (len(player_marbles) * (len(player_marbles) - 1))

        return 1.0 / (1.0 + average_distance)

    
    def getPlayerPieces(self, playerType = "max"):

        PlayerPieces = []
        board = self.gameState.get_rep()

        if playerType == "max":
            playerID = self.maxPlayerID
        else : playerID = self.minPlayerID
    
        for i in range(board.dimensions[0]):
            for j in range(board.dimensions[1]):
                if board.env.get((i, j)) and board.env[(i, j)].get_owner_id() == playerID:
                    PlayerPieces.append((i, j))
                    
        return PlayerPieces

    

    


