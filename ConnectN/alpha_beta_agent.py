import math
import agent
import random
import os
import sys

random.seed(1)

###########################
# Alpha-Beta Search Agent #
###########################

class AlphaBetaAgent(agent.Agent):
    """Agent that uses alpha-beta search"""

    # Class constructor.
    #
    # PARAM [string] name:      the name of this player
    # PARAM [int]    max_depth: the maximum search depth
    def __init__(self, name, max_depth):
        super().__init__(name)
        self.zb_table = None

        self.trans_table = {}
        # Max search depth
        self.max_depth = max_depth

    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        if self.zb_table == None or (len(self.zb_table)<brd.h) or (len(self.zb_table[0])<brd.w):
            self.zobrist_init(brd)
            #print(self.zb_table)
        """Search for the best move (choice of column for the token)"""
        successors = self.get_successors(brd)
        #print(successors)
        best = -math.inf
        best_index = -1
        alpha = -math.inf
        beta = math.inf
        for i,succ in enumerate(successors):
            result = self.solve(succ[0],alpha,beta)
            if result>best:
                best_index = i
                best = result

        return successors[best_index][1]#returns column number
        #brd.print_it()

    #solve for the best possible next move
    def solve(self, brd, alpha, beta):
        #brd.print_it()
        #print(f"\n{alpha}, {beta}")
        successors = self.get_successors(brd)
        
        #if there is a draw
        if len(successors) == 0:
            return 0
        
        #If current player can win in the next move
        for s in successors:
            if s[0].get_outcome() != 0:
                return ((s[0].h * s[0].w) + 1 - self.num_moves(s[0]))
        
        #the lower bound of the best possible score
        #best = -s[0].h*s[0].w
        
        #upper bound of score - cannot win right away
        max = (s[0].h*s[0].w) - self.num_moves(s[0])
        
        if beta > max:
            #beta does not need to be greater than max
            beta = max
            #prune the alpha,beta window
            if alpha >= beta:
                return beta
        
        #find score of all possible next moves and keep the best one
        for s in successors:
            score = 0
            hash = self.zb_hash(s[0])
            if hash in self.trans_table:
                score = self.trans_table[hash]
            else:
                score = -self.solve(s[0], -beta,-alpha)
                self.trans_table[hash] = score

            #prune if we found a better move than before
            if score >= beta:
                return score
            #reduce the alpha,beta window for search
            if score > alpha:
                alpha = score

        #return best
        return alpha

    def num_moves(self, brd):
        n = 0
        for y in range(brd.h):
            for x in range(brd.w):
                if brd.board[y][x] != 0:
                    n+=1
        return n
    
    def zobrist_init(self,brd):
        self.zb_table = [[(os.urandom(8),os.urandom(8))] * brd.w for i in range(brd.h)]
        self.trans_table = {}
                

    def zb_hash(self,brd):
        h = 0
        for y in range(0,brd.h):
            for x in range(0,brd.w):
                piece = brd.board[y][x]
                if piece != 0:
                    h = h ^ int.from_bytes(self.zb_table[y][x][piece-1],"little")
        return h


    # Get the successors of the given board.
    #
    # PARAM [board.Board] brd: the board state
    # RETURN [list of (board.Board, int)]: a list of the successor boards,
    #                                      along with the column where the last
    #                                      token was added in it
    def get_successors(self, brd):
        """Returns the reachable boards from the given board brd. The return value is a tuple (new board state, column number where last token was added)."""
        # Get possible actions
        freecols = brd.free_cols()
        # Are there legal actions left?
        if not freecols:
            return []
        # Make a list of the new boards along with the corresponding actions
        random.shuffle(freecols)
        succ = []
        for col in freecols:
            # Clone the original board
            nb = brd.copy()
            # Add a token to the new board
            # (This internally changes nb.player, check the method definition!)
            nb.add_token(col)
            # Add board to list of successors
            succ.append((nb,col))
        return succ

THE_AGENT = AlphaBetaAgent("Group21", 4)
