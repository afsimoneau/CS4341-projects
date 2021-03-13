from Bomberman.bomberman.world import World
import heapq


class Node:
    EMPTY = 0
    EXIT = 1
    WAll = 2
    BOMB = 3
    EXPLOSION = 4
    MONSTER = 5
    CHARACTER = 6

    def __init__(self, type, parent, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.parent = parent
        self.path = parent.path[:]
        self.h = 0
        self.g = 0

    def __eq__(self, other):
        return self.type == other.type and self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.f() < other.f()

    def __gt__(self, other):
        return self.f() > other.f()

    def f(self):
        return self.h + self.g


class Solver:
    def __init__(self, wrld: World, start: Node, end: Node):
        self.wrld = wrld
        self.start = start
        self.end = end
        self.path = []

    def backtrack(self, finish: Node):
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
            return Node.WAll
        elif self.wrld.bomb_at(x, y):
            return Node.BOMB
        elif self.wrld.explosion_at(x, y):
            return Node.EXPLOSION
        elif self.wrld.monsters_at(x, y):
            return Node.MONSTER
        elif self.wrld.characters_at(x, y):
            return Node.CHARACTER

    def solve(self, wallClip=False) -> list[Node]:
        '''
        1 2 3
        4 x 5
        6 7 8
        '''
        # list of tuples in dx,dy form
        moves = [(-1, 1), (0, 1), (1, 1), (-1, 0),
                 (1, 0), (-1, -1), (0, -1), (1, -1)]
        open: list[Node] = []
        heapq.heapify(open)
        closed: list[Node] = []
        heapq.heapify(closed)

        heapq.heappush(self.start)
        while open:
            current: Node = heapq.heappop(open)
            closed.append(current)

            # target is found, get path
            if current.type == self.end.type:
                return self.backtrack(current)

            # add all valid neighbors
            neighbors: list[Node] = []
            for dx, dy in moves:
                x_val = current+dx
                y_val = current+dy

                if x_val > self.wrld.width() or x_val < 0 or y_val > self.wrld.height() or y_val < 0:
                    continue  # out of bounds
                type = self.what_is(x_val, y_val)
                if type == Node.WAll and not wallClip:
                    continue  # can't clip through walls
                n = Node(type, current, x_val, y_val)
                neighbors.append(n)
            for next in neighbors:
                if next in closed:
                    continue  # neighbor in closed list
                next.g = current.g+1
                next.h = (next.x-self.end.x)**2 + (next.y-self.end.y)**2
                if next in open:
                    continue  # neighbor in open list
                heapq.heappush(open, next)
            return None  # no path found
