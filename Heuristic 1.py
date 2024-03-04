from NodeState import NodeState
from collections import deque
import numpy as np

# Utiliser des ensembles pour des vérifications de membres plus rapides
topLeftEdge = {(6,0),(8,0),(10,0)}
downLeftEdge = {(13,1),(14,2),(15,3)}
topRightEdge = {(1,5),(2,6),(3,7)}
downRightEdge = {(6,8),(8,8),(10,8)}

topLeftCorner = (4,0)
downLeftCorner = (16,4)
topRightCorner = (0,4)
downRightCorner = (12,8)
leftCorner = (12,0)
rightCorner = (4,8)

nordWest = (-1,-1)
nordEast = (-2,0)
southWest = (2,0)
southEast = (1,1)
west = (1,-1)
east = (-1,1)

# Cartographie de positions spécifiques à leurs directions
DIRECTIONS_MAP = {
    topLeftCorner: [east, southEast, southWest],
    downLeftCorner: [east, nordEast, nordWest],
    topRightCorner: [west, southEast, southWest],
    downRightCorner: [west, nordWest, nordEast],
    leftCorner: [east, nordEast, southEast],
    rightCorner: [west, nordWest, southWest],
    **{pos: [east, nordEast, southEast, southWest] for pos in topLeftEdge},
    **{pos: [east, nordEast, nordWest, southEast] for pos in downLeftEdge},
    **{pos: [west, nordWest, southEast, southWest] for pos in topRightEdge},
    **{pos: [west, nordEast, nordWest, southWest] for pos in downRightEdge}
}
#cartographie des axes
AXE_MAP = {
    nordWest : "westDiagonal",
    nordEast : "eastDiagonal",
    southWest : "westDiagonal",
    southEast : "eastDiagonal",
    west : "horizontal",
    east : "horizontal"
}
def getNeighbors(position):
    """
    Obtient les voisins d'une position donnée.

    Args:
    - position (tuple): position (x, y) sur le plateau.

    Retourne:
    - list: liste des positions voisines.
    """
    x, y = position
    directions = DIRECTIONS_MAP.get(position)
    
    if not directions:
        total = x + y 
        if total == 20:  # Bordure inférieure du plateau
            directions = [east, west, nordEast, nordWest]
        elif total == 4:  # Bordure supérieure du plateau
            directions = [east, west, southEast, southWest]
        else:  # Au milieu du plateau, toutes les six directions possibles
            directions = [east, west, nordEast, nordWest, southWest, southEast]
    
    neighbors = [(x + dx, y + dy) for dx, dy in directions]
    return neighbors
# Fonction pour calculer la distance de Manhattan entre deux positions
def manhattanDistance(A, B):
    mask1 = [(0,2),(1,3),(2,4)]
    mask2 = [(0,4)]
    diff = (abs(B[0] - A[0]),abs(B[1] - A[1]))
    dist = (abs(B[0] - A[0]) + abs(B[1] - A[1]))/2
    if diff in mask1:
        dist += 1
    if diff in mask2:
        dist += 2
    return dist

# Fonction pour obtenir la direction de pos1 à pos2
def getDirection(pos1,pos2):
    return (pos1[0] - pos2[0], pos1[1] - pos2[1]) 

# Fonction pour vérifier si une position est valide sur le plateau
def isValid(pos, boardDict, visited ,color, checked):
    if checked == True :
        return True
    return pos not in visited and pos in boardDict.keys() and boardDict[pos].get_type() == color

# Fonction pour initialiser les données relatives au cluster
def initialize_cluster_data(initialPosition, boardDict):

    color = boardDict[initialPosition].get_type()
    strengthDict = {initialPosition: {"total":1,"horizontal": 1, "eastDiagonal": 1, "westDiagonal": 1}}
    axeDict = dict()  # Associe chaque billes à ses axes où elle a un voisin
    cluster = set()
    return color, strengthDict, axeDict, cluster

# Fonction pour mettre à jour les données relatives au cluster
def update_cluster_data(current, neighbor, strengthDict, axeDict):

    direction = getDirection(neighbor, current)
    axeDict.setdefault(current, set()).add(direction)
    
    # Mettre à jour la force agrégée
    try :
        strengthDict[current]["total"] += 1
    except KeyError :
        print(strengthDict[current])
    # Mettre à jour la force axiale
    axe = AXE_MAP[direction]
    strengthDict[current][axe] += 1
    
    # Initialiser ou mettre à jour la force du voisin
    try:
        strengthDict[neighbor]["total"] += 1
        strengthDict[neighbor][axe] += 1
    except KeyError: #Initialisation a deux, car il est deja voisin
        strengthDict[neighbor] = {"total":2,"horizontal": 1, "eastDiagonal": 1, "westDiagonal": 1}
        strengthDict[neighbor][axe] = 2

# Fonction pour agréger les forces axiales
def aggregateAxisStrengths(axeDict:dict, strengthDict:dict):
    for pos in axeDict.keys():
        x,y = pos
        for direction in axeDict[pos]:
            dx, dy = direction
            #On regarde deux fois dans la meme direction car on a deja pris en compte le voisin immédiat
            #dans le fonction update_cluster_data
            neighbor = (x + 2*dx, y + 2*dy)
            axe = AXE_MAP[direction]
            try : 
                strengthDict[neighbor]["total"] += 1
                strengthDict[neighbor][axe] += 1
            except KeyError:
                continue
    return strengthDict

# Fonction pour trouver un cluster à partir d'une position initiale
def findCluster(boardDict: dict, visited: set, initialPosition: tuple):

    color, strengthDict, axeDict, cluster = initialize_cluster_data(initialPosition, boardDict)
    queue = deque([(initialPosition, False)])
    count = 0

    while queue:
        current, checked = queue.pop()
        if isValid(current, boardDict, visited, color, checked):
            cluster.add(current)
            count += 1
            visited.add(current)
            
            for neighbor in getNeighbors(current):
                if isValid(neighbor, boardDict, visited, color, False):
                    queue.append((neighbor, True))
                    update_cluster_data(current, neighbor, strengthDict, axeDict)

    strengthDict = aggregateAxisStrengths(axeDict,strengthDict)
    return list(cluster), color, visited, count, strengthDict

def getClusters(boardDict : dict) :
    """
    Obtient tous les clusters sur le plateau.

    Args:
    - boardDict (dict): dictionnaire représentant le plateau.

    Retourne:
    - tuple: clusters blancs et noirs.
    """
    visited = set()

    whiteCluster = dict()
    whiteCount = 0
    whiteClusterCount = []
    whiteClusterStrenght = dict()

    blackCluster = dict()
    blackCount = 0
    blackClusterCount = []
    blackClusterStrenght = dict()
    for pos in boardDict.keys() :
        if pos not in visited : 
            cluster, color, visited, count, strengthDict = findCluster(boardDict,visited,pos)
            if color == "W":
                #Nombre de clusters
                whiteCount += 1
                whiteCluster[whiteCount] = cluster
                whiteClusterStrenght.update(strengthDict)
                #Nombre de billes dans le cluster
                whiteClusterCount.append(count)
            else : 
                #Nombre de clusters
                blackCount += 1
                blackCluster[blackCount] = cluster
                blackClusterStrenght.update(strengthDict)
                #Nombre de billes dans le cluster
                blackClusterCount.append(count)

    return{"W" : whiteCluster, "B" : blackCluster, "WC": whiteClusterCount, "BC":blackClusterCount }, {"W": whiteCount,"B": blackCount}, {"W" : whiteClusterStrenght, "B" : blackClusterStrenght}



class HeuristicClass : 
    def __init__(self, node : NodeState):
        # Initialisation de la classe avec un objet NodeState

        self.node = node
        self.boardDict = node.gameState.get_rep().env
        self.boardHeight = node.gameState.get_rep().get_dimensions()[0]
        self.boardWidth = node.gameState.get_rep().get_dimensions()[1]
        # Calcul des clusters
        self.clustersDict = getClusters(self.boardDict)
        # Clusters pour chaque joueur
        self.maxClusters, self.minClusters, self.maxClustersCount, self.minClustersCount = self.clusters()
        # Nombre de marbres pour chaque joueur
        self.maxMarbles, self.minMarbles = self.totalMarbles()
        # Moyenne de marbres par cluster pour chaque joueur
        self.maxMean, self.minMean = self.maxMarbles/self.maxClustersCount , self.minMarbles/self.minClustersCount
        #Cohesion des clusters en terme de quantité de marbres par cluster
        self.maxCountCohesion = self.countCohesion(self.node.maxPlayerPieceType,self.maxMarbles)
        self.minCountCohesion = self.countCohesion(self.node.minPlayerPieceType,self.minMarbles)
        # Cohésion des forces des marbres pour chaque joueur
        self.maxStrengthsDict, self.minStrengthsDict = self.marbleStrenght()
        self.maxTotalStrength = self.totalStrenght(self.maxStrengthsDict)
        self.minTotalStrength = self.totalStrenght(self.minStrengthsDict)
        self.maxMarbleStrengthCohesion = self.marbleStrengthCohesion(self.maxStrengthsDict,self.maxTotalStrength)
        self.minMarbleStrengthCohesion = self.marbleStrengthCohesion(self.minStrengthsDict,self.minTotalStrength)

    def featuresVector(self): 
        # Crée un vecteur de caractéristiques pour l'heuristique

        _, _, maxClustersCount, minClustersCount = self.clusters()
        X = {
            "maxClustersCount" : maxClustersCount,
            "minClustersCount" : minClustersCount,
            "maxMarbles" : + self.maxMarbles,
            "minMarbles" : - self.minMarbles,
            "maxMean" : + self.maxMean,
            "minMean" : - self.minMean,
            "maxCountCohesion" : + self.maxCountCohesion,
            "minCountCohesion" : - self.minCountCohesion,
            "maxTotalStrength" : + self.maxTotalStrength,
            "minTotalStrength" : - self.minTotalStrength,
            "maxMarbleStrengthCohesion" : + self.maxMarbleStrengthCohesion,
            "minMarbleStrengthCohesion" : - self.minMarbleStrengthCohesion
        }
        # Ajoute d'autres caractéristiques au vecteur
        X = self.addFacingsToFeatures(X)
        maxTotalEdge , minTotalEdge, maxEdges , minEdges = self.DistanceFromEdge()
        X["maxTotalEdge"] = + maxTotalEdge
        X["minTotalEdge"] = - minTotalEdge
        
        
        total, average_distance, inverse_average = self.totalDistancePairs(self.maxStrengthsDict)
        X["maxTotalDist"] = - total
        X["maxAverageDist"] = - average_distance
        X["maxInverseAverageDist"] = + inverse_average

        total, average_distance, inverse_average = self.totalDistancePairs(self.minStrengthsDict)
        X["minTotalDist"] = + total
        X["minAverageDist"] = + average_distance
        X["minInverseAverageDist"] = - inverse_average

        maxPlayerDistance, minPlayerDistance = self.distanceToCenter()
        X["maxPlayerDistance"] = - maxPlayerDistance
        X["minPlayerDistance"] = + minPlayerDistance



        X["minPlayerScoreIs6"] = self.node.minPlayerScore == 6
        X["maxPlayerScoreIs6"] = self.node.maxPlayerScore == 6

        X["maxPlayerHigherScore"] = self.node.maxPlayerScore > self.node.minPlayerScore
        X["minPlayerHigherScore"] = self.node.minPlayerScore > self.node.maxPlayerScore

        X["maxPlayerLessDistance"] = minPlayerDistance > maxPlayerDistance
        X["minPlayerLessDistance"] = maxPlayerDistance > minPlayerDistance
        X = list(X.values())
        X = np.array(X).reshape((1,32))
        return X
    
    def addEdges(self,X, maxEdges , minEdges):
        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                pos = (row, col)
                value = maxEdges.get(pos, -1)
                custom_key = "maxDistanceToEdge" + "_" + str(pos)
                X[custom_key] = value

        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                pos = (row, col)
                value = minEdges.get(pos, -1)
                custom_key = "minDistanceToEdge" + "_" + str(pos)
                X[custom_key] = value
        return X

    def addStrengthsToFeatures(self, X):
        maxStrengthsDict, minStrengthsDict = self.marbleStrenght()
        strengthsKeys = ["total", "horizontal", "eastDiagonal", "westDiagonal"]

        for row in range(self.boardHeight):
            for col in range(self.boardWidth):
                pos = (row, col)

                # Traiter les forces actuelles
                value = maxStrengthsDict.get(pos, 0)
                #if value != 0:
                for axis in strengthsKeys:
                    if value !=  0 :
                        strength = value.get(axis, 0)
                    else: strength = 0
                    custom_key = "max_" + str(pos) + "_" + axis
                    X[custom_key] = strength

                # Traiter les forces suivantes
                value = minStrengthsDict.get(pos, 0)
                for axis in strengthsKeys:
                    if value !=  0 :
                        strength = value.get(axis, 0)
                    else: strength = 0
                    custom_key = "min_" + str(pos) + "_" + axis
                    X[custom_key] = strength
        return X
    
    def addFacingsToFeatures(self, X):
        faceOffTotals, facings = self.faceOff()
        strengthsKeys = ["total", "horizontal", "eastDiagonal", "westDiagonal"]
        for key in strengthsKeys :
            X[key] = faceOffTotals[key]
        return X

    def clusters(self) :
        clusters, count, _ = self.clustersDict
        return clusters[self.node.maxPlayerPieceType], clusters[self.node.minPlayerPieceType],  count[self.node.maxPlayerPieceType], count[self.node.minPlayerPieceType]


    def countCohesion(self, color, totalMarbles):
        # Somme : pour tout les clusters (nombre de marbre sur le cluster/nombre total de marbre)**2
        total = 0
        clusters, _ , _ = self.clustersDict
        clusterCount = clusters[color + "C"]
        for count in clusterCount:
            total += (count/totalMarbles)**2
        return total

    def distanceToCenter(self):
        # Distance par rapport au centre : distance moyenne ou totale des billes par rapport au centre du plateau
        return self.node.maxPlayerDistance, self.node.minPlayerDistance 
    
    def totalMarbles(self):
        # nombre total de billes
        return 14 - self.node.minPlayerScore, 14 - self.node.maxPlayerScore
    
    def marbleStrenght(self):
        # Force de la bille : évalue la force d'une bille en fonction du nombre de groupes auxquels elle appartient. Une bille qui fait partie de plusieurs groupes est plus forte.
        _, _, strenghtDict = self.clustersDict
        return strenghtDict[self.node.maxPlayerPieceType], strenghtDict[self.node.minPlayerPieceType]
    
    def totalStrenght(self, strenghtDict:dict) :
        total = 0
        for pos in strenghtDict :
            total += strenghtDict[pos]["total"]
        return total
    
    def marbleStrengthCohesion(self, strengthDict, totalStrength) :
        # Somme : pour chaque marbre (puissance du marbre/somme puissance des marbres)**2
        total = 0
        for pos in strengthDict :
            total += (strengthDict[pos]["total"]/totalStrength)**2
        return total
    
    def DistanceFromEdge(self) :
        """
        Calcule la distance min aux bords des pieces de l'opposant
        Args: node (NodeState)
        retourne: score de distance aux bords du jeu pour les opposants
        """
        board = self.node.gameState.get_rep()
        minEdges = dict()
        minTotalEdge = 0
        for piece in self.minStrengthsDict:
            edgeDistance = min(piece[0], board.dimensions[0] - 1 - piece[0], piece[1], board.dimensions[1] - 1 - piece[1])
            minEdges[piece] = edgeDistance
            minTotalEdge += edgeDistance

        maxEdges = dict()
        maxTotalEdge = 0
        for piece in self.minStrengthsDict:
            edgeDistance = min(piece[0], board.dimensions[0] - 1 - piece[0], piece[1], board.dimensions[1] - 1 - piece[1])
            maxEdges[piece] = edgeDistance
            maxTotalEdge += edgeDistance

        return maxTotalEdge , minTotalEdge, maxEdges , minEdges


    def totalDistancePairs(self, strengthsDict):
        total = 0
        positions = list(strengthsDict.keys())
        totalMarbles = len(positions)
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:  # Commencez à partir de la position suivante pour éviter les paires en double
                total += manhattanDistance(pos1, pos2)
        numberOfPairs = totalMarbles * (totalMarbles - 1) / 2
        # Pour éviter une division par zéro s'il y a une ou aucune bille
        average_distance = total / numberOfPairs if numberOfPairs else 0  
        return total, average_distance, 1.0 / (1.0 + average_distance)
    
    def faceOff(self): 
        # Métrique FaceOff : comparer la force de n'importe quel cluster allié à la force du cluster ennemi le plus proche
        faceOffTotals = {"total":0,"horizontal": 0, "eastDiagonal": 0, "westDiagonal": 0}
        facings = dict()
        for pos in self.maxStrengthsDict.keys() :
            facings[pos] = {"total":0, "horizontal": 0, "eastDiagonal": 0, "westDiagonal": 0}
            neighbors = getNeighbors(pos)
            for neighbor in neighbors :
                if neighbor in self.minStrengthsDict :
                    direction = getDirection(neighbor, pos)
                    axe = AXE_MAP[direction]
                    enemyStrength = self.minStrengthsDict[neighbor][axe]
                    allyStrength  = self.maxStrengthsDict[pos][axe]
                    delta = allyStrength - enemyStrength
                    facings[pos][axe] += (allyStrength - enemyStrength)
                    facings[pos]["total"] += (allyStrength - enemyStrength)

                    faceOffTotals[axe] += delta
                    faceOffTotals["total"] += delta

        return faceOffTotals, facings


    

    