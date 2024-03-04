from NodeState import NodeState
from TranspositionTable import ZobristTable
import numpy as np
import json


class AlphaBetaZobrist:
    def __init__(self, depth, playerID):
        """Initialisation de la classe AlphaBetaZobrist.

        Args:
            depth (int): Profondeur maximale de l'arbre de recherche.
            playerID (str ou int): Identifiant du joueur.

        """
        self.depth = depth# Profondeur de recherche maximale
        self.playerID = playerID# Identifiant du joueur
        self.maxQuiescence = 1

        self.hits=0 #nombre de fois qu'une position est trouvée dans la table
        self.node_visits=0 #nombre de noeuds visités
        self.pruned_nodes_max=0 #nombre de noeuds prunés par l'agent max
        self.pruned_nodes_min=0 #nombre de noeuds prunés par l'agent min
        self.root_branches=0 #facteur de branchement du noeud racine


    def search(self,node: NodeState):
        """Recherche du meilleur coup à jouer.

        Args:
            node (NodeState): État actuel du plateau.

        Returns:
            Tuple: valeur du meilleur coup, meilleur coup

        """
        self.root_branches=len(node.getActions())
        depth = self.depth
        v, m = self.MaxValue(node,depth, alpha=float("-inf"), beta=float("inf"), current_depth=0)# Recherche du meilleur coup
        print("Pruning Efficiency:")
        print(f"    Pruned Nodes (MaxValue): {self.pruned_nodes_max}")
        print(f"    Pruned Nodes (MinValue): {self.pruned_nodes_min}")
        print(f"    Number of Branches at Root Node: {self.root_branches}")
        print(f"    Nodes Visited: {self.node_visits}")

        self.hits=0 #nombre de fois qu'une position est trouvée dans la table
        self.node_visits=0 #nombre de noeuds visités
        self.pruned_nodes_max=0 #nombre de noeuds prunés par l'agent max
        self.pruned_nodes_min=0 #nombre de noeuds prunés par l'agent min
        self.root_branches=0 #facteur de branchement du noeud racine

        return v, m
        
    
    def MaxValue(self ,node: NodeState, depth, alpha: float, beta: float, current_depth):
        """Fonction MaxValue pour l'algorithme Alpha-Beta.
        Args:
            node (NodeState): État actuel du plateau.
            nodeHash: Hash de l'état actuel.
            depth: Profondeur actuelle.
            alpha (float): Valeur alpha pour l'élagage.
            beta (float): Valeur beta pour l'élagage.
        Returns:
            Tuple: valeur maximale, action associée
        """
        self.node_visits += 1 
        v_star = float('-inf')
        m_star = None

        if node.isTerminal() or depth == 0:
            if node.isTerminal() == False :
                if current_depth > self.maxQuiescence + self.depth : 
                    MaxPlayerScore = self.Heuristic(node)
                else: 
                    sortedActions = self.sortActions(node, descending=False)
                    if node.isQuiescent(sortedActions, playerType="max") :  
                        MaxPlayerScore = self.Heuristic(node)
                    else :
                        MaxPlayerScore, _  = self.MinValue(node, 1, alpha, beta, current_depth+1)
                return MaxPlayerScore, None
            
            else : 
                if node.isWin() == True :  MaxPlayerScore = 1000
                elif node.isWin() == False : MaxPlayerScore = -1000
                else : MaxPlayerScore = 0
            return MaxPlayerScore, None
        
        sortedActions = self.sortActions(node, descending=True)

        for action in sortedActions:
            nextNode = node.applyAction(action)
            #depth -= 1
            v, m = self.MinValue(nextNode, depth-1, alpha, beta, current_depth + 1)
            if v > v_star:
                v_star = v
                m_star = action
                alpha = max(alpha, v_star)
            if v_star >= beta:
                self.pruned_nodes_max += 1
                return v_star, m_star
                    
        return v_star, m_star

    def MinValue(self,node: NodeState, depth, alpha: float, beta: float, current_depth):
        """Fonction MinValue pour l'algorithme Alpha-Beta.
        Args:
            node (NodeState): État actuel du plateau.
            nodeHash: Hash de l'état actuel.
            depth: Profondeur actuelle.
            alpha (float): Valeur alpha pour l'élagage.
            beta (float): Valeur beta pour l'élagage.

        Returns:
            Tuple: valeur minimale, action associée
        """
        self.node_visits += 1 
        v_star = float('inf')
        m_star = None

        if node.isTerminal() or depth == 0:
            if node.isTerminal() == False :
                if current_depth > self.maxQuiescence + self.depth : 
                    MaxPlayerScore = self.Heuristic(node)
                else: 
                    sortedActions = self.sortActions(node, descending=True)
                    if node.isQuiescent(sortedActions, playerType="min") :  
                        MaxPlayerScore = self.Heuristic(node)
                    else :
                        MaxPlayerScore, _  = self.MinValue(node, 1, alpha, beta, current_depth+1)
                return MaxPlayerScore, None
            else : 
                if node.isWin() == True :  MaxPlayerScore = 1000
                elif node.isWin() == False : MaxPlayerScore = -1000
                else : MaxPlayerScore = 0
            return MaxPlayerScore, None


        sortedActions = self.sortActions(node, descending=False)


        for action in sortedActions:
            nextNode = node.applyAction(action)
            #depth -= 1
            v, m  = self.MaxValue(nextNode, depth-1, alpha, beta, current_depth+1)
            if v < v_star:
                v_star = v
                m_star = action
                beta = min(beta, v_star)
            if v_star <= alpha:
                self.pruned_nodes_min+=1
                return v_star, m_star
             
        return v_star, m_star
    
    def Heuristic(self,node:NodeState) -> int :
        """Heuristique pour évaluer un état du plateau.

        Args:
            node (NodeState): État actuel du plateau.

        Returns:
            int: valeur heuristique

        """
        cohesion_score = node.calculateCohesion()
        return -5*node.maxPlayerDistance + node.minPlayerDistance + 12 * self.getScoreDiff(node) - cohesion_score 


    def sortActions(self,node : NodeState, descending = False) :
        """Trie les actions en fonction de leur évaluation.
        Args:
            node (NodeState): État actuel du plateau.
            descending (bool, optional): Ordre du tri. Par défaut False.

        Returns:
            List: Actions triées.
        """
        if descending == True : 
            actionValues = [(action, self.Heuristic(child_node)) for action,child_node in node.getChildren("max")]
        else : 
            actionValues = [(action, self.Heuristic(child_node)) for action,child_node in node.getChildren("min")]

        sortedActions = [(action, value) for action, value in sorted(actionValues, reverse= descending ,key=lambda x: x[1])]
        medianValue = np.median([value for _, value in actionValues])

        if descending == True: #Pour max player 
            return [action for action, value in sortedActions if value >= medianValue]
        else : #Pour min player 
            return [action for action, value in sortedActions if value <= medianValue]
    
    def getScoreDiff(self,node:NodeState) -> int:
        """Calcule la différence de score entre les joueurs.
        Args:
            node (NodeState): État actuel du plateau.
        Returns:
            int: différence de score
        """
        return node.maxPlayerScore - node.minPlayerScore
    

    @classmethod
    def to_json(cls) :
        """Conversion de l'objet en JSON. Non implémenté pour le moment."""
        return json.dumps(None)
