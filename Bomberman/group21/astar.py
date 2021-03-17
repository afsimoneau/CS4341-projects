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

    def __init__(self, wrld: World, start: Node, end: Node):
        self.wrld = wrld
        self.start = start
        self.end = end
        self.path = None

    def backtrack(self, finish: Node):
        if self.path is None:
            self.path = []
        node = finish
        while node is not None:
            self.path.append(node)
            node = node.parent
        self.path.reverse()

    def what_is(self, x, y) -> int:
        if self.wrld.empty_at(x, y):
            return Node.EMPTY
        elif self.wrld.exit_at(x, y):
            return Node.EXIT
        elif self.wrld.wall_at(x, y):
            return Node.WALL
        elif self.wrld.bomb_at(x, y):
            return Node.BOMB
        elif self.wrld.explosion_at(x, y):
            return Node.EXPLOSION
        elif self.wrld.monsters_at(x, y):
            return Node.MONSTER
        elif self.wrld.characters_at(x, y):
            return Node.CHARACTER

    def valid_action(self, coords, wallClip, noMonsters):
        #print(f"valid action start {coords[0]} {coords[1]}")
        if coords[0] > self.wrld.width()-1 or coords[0] < 0 or coords[1] > self.wrld.height()-1 or coords[1] < 0:
            return False  # out of bounds
        #print("valid action not out of bounds")
        type = self.what_is(coords[0], coords[1])
        if type == Node.WALL and not wallClip:
            return False  # can't go through a wall
        #print("valid action not wall")
        if type == Node.MONSTER and noMonsters:
            return False  # avoiding monsters
        #print("valid action monster")
        #aprint(f"({coords[0]}, {coords[1]}) valid")
        return True

    def solve(self, wallClip=False, noMonsters=True):
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

        heapq.heappush(open, self.start)
        while open:
            current: Node = heapq.heappop(open)

            closed.append(current)

            # target is found, get path
            if current.type == self.end.type:
                #print("found path")
                return self.backtrack(current)

            # add all valid neighbors
            neighbors = []
            for dx, dy in self.directions:
                x_val = current.x+dx
                y_val = current.y+dy

                if not self.valid_action((x_val, y_val), wallClip, noMonsters):
                    continue # skip invalid actions
    
                n = Node(self.what_is(x_val,y_val), current, x_val, y_val)
                neighbors.append(n)

            #print(f"Node: {current} | Neighbors: {neighbors}")
            for next in neighbors:
                if next in closed:
                    continue  # neighbor in closed list
                next.g = current.g+1
                next.h = (next.x-self.end.x)**2 + (next.y-self.end.y)**2
                if next in open:
                    continue  # neighbor in open list
                heapq.heappush(open, next)
        return None  # no path found
