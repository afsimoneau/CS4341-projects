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

        alpha = -sys.maxsize
        beta = sys.maxsize
        result = self.solve(brd, alpha, beta, self.max_depth)
        return result  # returns column number
        # brd.print_it()

    # Solves for the best possible move
    #
    # PARAM [board.Board] brd: current board state
    # PARAM [int] alpha: alpha value for this node
    # PARAM [int] beta: beta value for this node
    # PARAM [int] depth: depth of this node
    #
    # RETURN [int]: column index if depth = max_depth OR value for sub-tree evaluations
    def solve(self, brd, alpha, beta, depth):
        # We've reached max depth and found no winning moves
        # Determine the value of this board position
        if depth == 0:
            return self.evaluate(brd)

        # Store this for later use
        successors = self.get_successors(brd)

        # Check if the successors are empty
        # This would be a draw, return 0 since it's not a desired outcome
        if len(successors) == 0:
            return 0

        # The score limit for this current position is 10^n - num moves
        # We will check the transposition table to skip further evaluation
        max = (int(math.pow(10, brd.n)) - self.num_moves(brd))
        curHash = self.zb_hash(brd)
        if curHash in self.trans_table:
            max = self.trans_table[curHash] + beta - 1

        # Check if beta and max differ
        # When they do, we need to also check if alpha >= beta for pruning
        if beta > max:
            beta = max
            if alpha >= beta:
                return beta  # Pruned the position from previous execution data

        # If we can find a winning move from a successor, return the appropriate value
        # Subtract by number of moves to allow a/b pruning to find quicker wins
        for s in successors:
            outcome = s[0].get_outcome()
            if outcome != 0:
                # This will be a win for us since it's current player's move
                if self.max_depth == depth:
                    # We're the root node!
                    # Return column index instead of a utility value
                    return s[1]
                else:
                    #
                    return (int(math.pow(10, brd.n)) - (self.num_moves(s[0])))

        # Main recursive body ----------------------
        # Find score of all possible next moves and keep the best one
        best_col = -1
        for s in successors:
            # Implementation of a negamax search
            # We flip flop the score and a/b to change "perspective" of a player
            score = -self.solve(s[0], -beta, -alpha,
                                depth-1)

            # Prune if we've found a better move now
            if score >= beta:
                if self.max_depth == depth:
                    # Return column index if we're at root node
                    return s[1]
                else:
                    return score

            # Reduce the a/b window
            if score > alpha:
                alpha = score
                best_col = s[1]

        # Return alpha or column index of best move if root
        # Store the alpha before we exit
        self.trans_table[self.zb_hash(brd)] = alpha
        if self.max_depth == depth:
            return best_col
        else:
            return alpha

    # Counts the number of moves for a given board
    #
    # PARAM [board.Board] brd: current board state
    #
    # RETURN [int]: number of moves played on the current board
    def num_moves(self, brd):
        n = 0
        for y in range(brd.h):
            for x in range(brd.w):
                if brd.board[y][x] != 0:
                    n += 1
        return n

    # Find a line starting at x,y and going in direction dx,dy
    #
    # PARAM [int] x:  the x coordinate of the starting cell
    # PARAM [int] y:  the y coordinate of the starting cell
    # PARAM [int] dx: the step in the x direction
    # PARAM [int] dy: the step in the y direction
    #
    # RETURN [(player_token, list of tuple coordinates (x,y))]:
    #       Returns the player the line belongs to and the coordinates of the line
    def find_line(self, brd, x, y, dx, dy):
        # Check board boundaries
        if ((x + (brd.n-1) * dx >= brd.w) or
                (y + (brd.n-1) * dy < 0) or (y + (brd.n-1) * dy >= brd.h)):
            return (0, [])
        # Get token at (x,y)
        player_token = brd.board[y][x]
        # Go through elements
        coords = [(x, y)]
        for i in range(1, brd.n):
            if brd.board[y + i*dy][x + i*dx] != player_token:
                break  # Exit on a different token
            coords.append((x + i*dx, y + i*dy))  # Add coordinate to list
        return (player_token, coords)

    def evaluate(self, brd):
        all_lines = []
        dx_list = [1, 0, 1, 1]
        dy_list = [0, 1, 1, -1]
        for x in range(brd.w):
            for y in range(brd.h):
                if brd.board[y][x] != 0:
                    # Check every direction for every player coordinate
                    # Also, I really like zip() :)
                    for dx, dy in zip(dx_list, dy_list):
                        line = self.find_line(brd, x, y, dx, dy)
                        if len(line[1]) > 1:
                            all_lines.append(line)
        p1_score, p2_score = 0
        for line in all_lines:
            # We assign powers of 10 to the length-1 of a line
            '''
            length,n value
            1, not in list of lines
            2, 10
            3, 100
            etc.
            '''
            n = int(math.pow(10, len(line[1])-1))
            if line[0] == 1:
                p1_score += n
            elif line[0] == 2:
                p2_score += n
        ret = (p1_score-p2_score)  # what we will return
        # If max depth is even, we invert result
        # p2 should be at a positive value when p2 is winning
        # See design doc for more information
        if self.max_depth % 2 == 1:
            ret *= -1
        return ret

    # Initialize the Zobrist bytestring table
    #
    # PARAM [board.Board] brd: the board (used for dimensions)
    #
    # See design doc for more information
    def zobrist_init(self, brd):
        self.zb_table = [[(os.urandom(8), os.urandom(8))]
                         * brd.w for i in range(brd.h)]
        self.trans_table = {}

    # Get the hash of a given board
    #
    # PARAM [board.Board] brd: the board state
    # RETURN [int]: a Zobrist Hash of the given board state
    def zb_hash(self, brd):
        h = 0
        for y in range(0, brd.h):
            for x in range(0, brd.w):
                piece = brd.board[y][x]
                if piece != 0:
                    h = h ^ int.from_bytes(
                        self.zb_table[y][x][piece-1], "little")
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
            succ.append((nb, col))
        return succ


THE_AGENT = AlphaBetaAgent("Group21", 4)
