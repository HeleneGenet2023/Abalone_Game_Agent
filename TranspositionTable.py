from NodeState import NodeState
from seahorse.game.action import Action
import random, json

def indexOf(pieceType):
    """
    Associe chaque type de pièce à un nombre.
    'W' pour les pièces blanches, 'B' pour les pièces noires, et 0 pour les cases vides.
    """
    if pieceType == 'W':
        return 1
    elif pieceType == 'B':
        return 2
    elif pieceType == "V":
        return 0

def randomInt():
    """
    Génère un nombre aléatoire de 0 à 3^(dimsRows*dimsCols).
    Utilisé pour initialiser la table de hachage Zobrist.
    """
    dimsRows = 17
    dimsCols = 9
    nbPieceTypes = 3  # Noir, blanc ou vide
    min = 0
    max = pow(nbPieceTypes, dimsRows * dimsCols)
    return random.randint(min, max)

class ZobristTable:
    def __init__(self):
        """
        Constructeur de la classe ZobristTable.
        Initialise la table de hachage.
        """
        self.initialTable = self.initTable()
        self.hits=0
        self.misses=0
        self.total_lookups=0

    def initTable(self):
        """
        Initialise la table de hachage Zobrist.
        Retourne un tableau tridimensionnel.
        """
        nbPieceTypes = 3  # Noir, blanc ou vide
        dimsRows = 17
        dimsCols = 9
        return [[[randomInt() for _ in range(nbPieceTypes)] for _ in range(dimsCols)] for _ in range(dimsRows)]

    def boardHash(self, node: NodeState):
        """
        Calcule le hachage Zobrist du plateau de jeu.
        """
        hashRep = 0
        dimsRows = 17
        dimsCols = 9
        final_rep = node.gameState.get_rep()
        env = final_rep.get_env()
        populatedSquares = list(env.keys())
        # Gestion des cases occupées
        for i, j in list(env.keys()):
            p = env.get((i, j), None)
            pieceType = p.get_type()
            pieceIndex = indexOf(pieceType)
            hashRep ^= self.initialTable[i][j][pieceIndex]
        # Gestion des cases vides
        for row in range(dimsRows):
            for col in range(dimsCols) :
                if (row,col) not in populatedSquares : 
                    pieceType = "V"
                    pieceIndex = indexOf(pieceType)
                    hashRep ^= self.initialTable[row][col][pieceIndex]                    
        return hashRep

    def updateBoard(self, tableHash, oldNode: NodeState, newNode: NodeState):
        """
        Met à jour le hachage Zobrist en fonction des mouvements effectués.
        """
        toErase = self.getDelta(oldNode, newNode)
        toMove = self.getDelta(newNode, oldNode)

        for loc in toErase:
            pieceIndex = indexOf(loc[-1])
            row, col = loc[0]
            tableHash = self.eraseMoveHash(tableHash, row, col, pieceIndex)

        for loc in toMove:
            pieceIndex = indexOf(loc[-1])
            row, col = loc[0]
            tableHash = self.makeMoveHash(tableHash, row, col, pieceIndex)

        return tableHash

    def getDelta(self, oldNode: NodeState, newNode: NodeState):
        """
        Retourne les index où un changement a eu lieu.
        """
        oldRep = oldNode.gameState.get_rep()
        newRep = newNode.gameState.get_rep()
        oldEnv = oldRep.get_env()
        newEnv = newRep.get_env()

        # Les cases vides doivent être celles qui ne sont pas des clés dans le dictionnaire newEnv
        voidSquares =  list(  set([(i,j) for i,j in oldEnv.keys()]) - set([(i,j) for i,j in newEnv.keys()])   )
        deltaVoid = [(loc,"V") for loc in voidSquares]
        oldIndexes = [((i, j), oldEnv.get((i, j), None).get_type()) for i, j in list(oldEnv.keys())]
        newIndexes = [((i, j), newEnv.get((i, j), None).get_type()) for i, j in list(newEnv.keys())]
        deltaPopulated = list(set(newIndexes) - set(oldIndexes)) 
        return deltaPopulated + deltaVoid

    def makeMoveHash(self, tableHash, row: int, col: int, pieceIndex: int):
        """
        Met à jour le hachage pour un mouvement donné.
        """
        tableHash ^= self.initialTable[row][col][pieceIndex]
        return tableHash

    def eraseMoveHash(self, tableHash, row: int, col: int, pieceIndex: int):
        """
        Annule l'impact du mouvement sur le hachage.
        """
        tableHash ^= self.initialTable[row][col][pieceIndex]
        return tableHash
    
    
    def lookup(self, zobrist_hash):
        """
        Recherche une entrée dans la table de transposition et met à jour les comptes de réussite/échec.
        """
        self.total_lookups += 1
        if zobrist_hash in self.table:
            self.hit_count += 1
            self.hits += 1
            return self.table[zobrist_hash]
        else:
            self.misses += 1
            return None

    def calculate_hit_rate(self):
        """
        Calcule et retourne le taux de réussite.
        """
        if self.total_lookups > 0:
            hit_rate = self.hits / self.total_lookups
            return f"Hit Rate: {hit_rate:.2%} (Hits: {self.hits}, Misses: {self.misses})"
        else:
            return "Hit Rate: N/A (No lookups performed)"

    @classmethod
    def to_json(cls):
        """
        Convertit la table de hachage en une chaîne JSON.
        """
        return json.dumps(None)
