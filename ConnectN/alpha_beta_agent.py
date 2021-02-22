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
        if self.zb_table == None or (len(self.zb_table) < brd.h) or (len(self.zb_table[0]) < brd.w):
            self.zobrist_init(brd)
            # print(self.zb_table)
        """Search for the best move (choice of column for the token)"""
        successors = self.get_successors(brd)
        # print(successors)
        best = -math.inf
        best_index = -1
        alpha = -math.inf
        beta = math.inf
        for i, succ in enumerate(successors):
            result = self.solve(succ[0], alpha, beta, self.max_depth)
            if result > best:
                best_index = i
                best = result

        return successors[best_index][1]  # returns column number
        # brd.print_it()

    # solve for the best possible next move
    def solve(self, brd, alpha, beta, depth):
        if depth == 0:
            return self.evaluate(brd)

        #brd.print_it()

        #print(f"\n{alpha}, {beta}")
        successors = self.get_successors(brd)

        # if there is a draw
        if len(successors) == 0:
            return 0

        # If current player can win in the next move
        for s in successors:
            if s[0].get_outcome() != 0:
                # 10^n is the winning ticket!! (do -num moves to find quicker wins)
                return (int(math.pow(10, brd.n)) + 1 - self.num_moves(s[0]))

        # upper bound of score - cannot win right away
        max = (int(math.pow(10, brd.n)) - self.num_moves(s[0]))
        curHash = self.zb_hash(brd)
        if curHash in self.trans_table:
            max = self.trans_table[curHash] + beta - 1

        if beta > max:
            # beta does not need to be greater than max
            beta = max
            # prune the alpha,beta window
            if alpha >= beta:
                return beta

        # find score of all possible next moves and keep the best one
        for s in successors:
            score = -self.solve(s[0], -beta, -alpha, depth-1)

            # prune if we found a better move than before
            if score >= beta:
                return score
            # reduce the alpha,beta window for search
            if score > alpha:
                alpha = score

        # return best
        self.trans_table[self.zb_hash(brd)] = alpha
        return alpha

    def num_moves(self, brd):
        n = 0
        for y in range(brd.h):
            for x in range(brd.w):
                if brd.board[y][x] != 0:
                    n += 1
        return n

    def zobrist_init(self, brd):
        self.zb_table = [[(os.urandom(8), os.urandom(8))]
                         * brd.w for i in range(brd.h)]
        self.trans_table = {}

    def zb_hash(self, brd):
        h = 0
        for y in range(0, brd.h):
            for x in range(0, brd.w):
                piece = brd.board[y][x]
                if piece != 0:
                    h = h ^ int.from_bytes(
                        self.zb_table[y][x][piece-1], "little")
        return h

    def find_line(self, brd, x, y, dx, dy):
        if ((x + (brd.n-1) * dx >= brd.w) or
                (y + (brd.n-1) * dy < 0) or (y + (brd.n-1) * dy >= brd.h)):
            return (0, [])
        # Get token at (x,y)
        player_token = brd.board[y][x]
        # Go through elements
        coords = [(x, y)]
        for i in range(1, brd.n):
            if brd.board[y + i*dy][x + i*dx] != player_token:
                break
            coords.append((x + i*dx, y + i*dy))
        return (player_token, coords)

    def evaluate(self, brd):
        all_lines = []
        for x in range(brd.w):
            for y in range(brd.h):
                checked = False
                for coords in all_lines:
                    if (x, y) in coords[1]:
                        # if we've evaluated this x,y before, ignore it. part of line(s) already calculated
                        checked = True
                if not checked:
                    #check directions
                    #ignore anything out of bounds
                    line = self.find_line(brd, x, y, 1, 0)  # Horizontal
                    if line[0] != 0 and len(line[1]) != 1:
                        all_lines.append(line)
                    line = self.find_line(brd, x, y, 0, 1)  # Vertical
                    if line[0] != 0 and len(line[1]) != 1:
                        all_lines.append(line)
                    line = self.find_line(brd, x, y, 1, 1)  # Diag up
                    if line[0] != 0 and len(line[1]) != 1:
                        all_lines.append(line)
                    line = self.find_line(brd, x, y, 1, -1)  # Diag down
                    if line[0] != 0 and len(line[1]) != 1:
                        all_lines.append(line)
        p1_val = 0
        p2_val = 0
        for line in all_lines:
            # powers of 10^n-1 length of the line (line length 2 -> 10)
            n = int(math.pow(10, len(line[1])-1))
            if line[0] == 1:
                p1_val += n
            else:
                p2_val += n
        ret = (p1_val-p2_val)  # what we will return
        if self.max_depth % 2 == 0:
            ret *= -1 #if max depth is even, we invert result. p2 should be at a positive value when p2 is winning
        return ret

    '''
\    
 \   
  \  
   \
    \
     \
                
5 odd 
1 5 %2 1
2 4 %2 0
1 3 %2 1
2 2 %2 0
1 1 %2 1
2 0 %2 0 && 1

4 even
1 4 %2 0
2 3 %2 1
1 2 %2 0
2 1 %2 1
1 0 %2 0 && 0
'''

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
            succ.append((nb, col))
        return succ


THE_AGENT = AlphaBetaAgent("Group21", 10)
