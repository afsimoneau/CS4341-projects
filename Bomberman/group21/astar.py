from world import World
import sys
import heapq
sys.path.insert(0, '../bomberman')


class Node:
    EMPTY = 0
    EXIT = 1
    WALL = 2
    BOMB = 3
    EXPLOSION = 4
    MONSTER = 5
    CHARACTER = 6

    def __init__(self, type, parent, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.parent = parent
        if parent:
            self.path = parent.path[:]
        else:
            self.path = []
        self.h = 0
        self.g = 0

    def __eq__(self, other):
        return self.type == other.type and self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.f() < other.f()

    def __gt__(self, other):
        return self.f() > other.f()

    def __repr__(self):
        return f"({self.type}, {self.x}, {self.y})"

    def f(self):
        return self.h + self.g


class Solver:
    NW = (-1, -1)
    N = (0, -1)
    NE = (1, -1)
    W = (-1, 0)
    E = (1, 0)
    SW = (-1, 1)
    S = (0, 1)
    SE = (1, 1)

    directions = [NW, N, NE, W, E, SW, S, SE]

    def backtrack(finish: Node):
        path = []
        node = finish
        while node is not None:
            path.append(node)
            node = node.parent
        path.reverse()
        return path

    def what_is(wrld, x, y) -> int:
        if wrld.empty_at(x, y):
            return Node.EMPTY
        elif wrld.exit_at(x, y):
            return Node.EXIT
        elif wrld.wall_at(x, y):
            return Node.WALL
        elif wrld.bomb_at(x, y):
            return Node.BOMB
        elif wrld.explosion_at(x, y):
            return Node.EXPLOSION
        elif wrld.monsters_at(x, y):
            return Node.MONSTER
        elif wrld.characters_at(x, y):
            return Node.CHARACTER

    def valid_action(wrld, coords, wallClip, noMonsters):
        #print(f"valid action start {coords[0]} {coords[1]}")
        if coords[0] > wrld.width()-1 or coords[0] < 0 or coords[1] > wrld.height()-1 or coords[1] < 0:
            return False  # out of bounds
        #print("valid action not out of bounds")
        type = Solver.what_is(wrld,coords[0], coords[1])
        if type == Node.WALL and not wallClip:
            return False  # can't go through a wall
        #print("valid action not wall")
        if type == Node.MONSTER and noMonsters:
            return False  # avoiding monsters
        #print("valid action monster")
        #aprint(f"({coords[0]}, {coords[1]}) valid")
        return True

    def solve_path(wrld,start,end, wallClip=False, noMonsters=True):
        '''
        1 2 3
        4 x 5
        6 7 8
        '''
        # list of tuples in dx,dy form

        open = []
        heapq.heapify(open)
        closed = []
        heapq.heapify(closed)

        heapq.heappush(open, start)
        while open:
            current: Node = heapq.heappop(open)

            closed.append(current)

            # target is found, get path
            if current.type == end.type:
                #print("found path")
                return Solver.backtrack(current)

            # add all valid neighbors
            neighbors = []
            for dx, dy in Solver.directions:
                x_val = current.x+dx
                y_val = current.y+dy

                if not Solver.valid_action(wrld,(x_val, y_val), wallClip, noMonsters):
                    continue # skip invalid actions
    
                n = Node(Solver.what_is(wrld,x_val,y_val), current, x_val, y_val)
                neighbors.append(n)

            #print(f"Node: {current} | Neighbors: {neighbors}")
            for next in neighbors:
                if next in closed:
                    continue  # neighbor in closed list
                next.g = current.g+1
                next.h = 0 
                if next.type==Node.WALL:
                    next.h +=100
                # the heuristic below is bad
                #next.h = (next.x-end.x)**2 + (next.y-end.y)**2
                if next in open:
                    continue  # neighbor in open list
                heapq.heappush(open, next)
        return None  # no path found
