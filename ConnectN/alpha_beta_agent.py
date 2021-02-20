import math
import agent

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
        # Max search depth
        self.max_depth = max_depth

    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        """Search for the best move (choice of column for the token)"""
        return self.solve(brd, 0, 0)
        #brd.print_it()

    #solve for the best possible next move
    def solve(self, brd, alpha, beta):
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
            score = self.solve(s[0], alpha, beta)
            #Checking game.py and says that game returns 1 for p1 and 2 for p2 - compare and see if player equals 2 to determine?
            if s[0].get_outcome() != 0:
                score = -(s[0].h * s[0].w) + self.num_moves(s[0])
                
            #Keep track of the best possible score so far
            #if (score > best):
                #best = score

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
