# This is necessary to find the main code
from collections import namedtuple
from astar import Node, Solver
from colorama import Fore, Back
from entity import CharacterEntity
from operator import itemgetter
from sensed_world import SensedWorld

import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff


class QCharacter(CharacterEntity):

    # wallclip = true when doing scenario 2
    def __init__(self, name, avatar, x, y, weights, wallClip=False, train=True):
        super().__init__(name, avatar, x, y,)
        # initialize weights table here
        # Across runs, this is constant
        self.train = train
        self.weights = []  # import this?
        self.wallClip = wallClip

        # changes across runs
        self.exitPath = None
        self.bombPath = None
        self.monsterPaths = []
        self.explosionPaths = []

        # q specific data
        self.alpha = .1
        self.gamma = .9
        self.adjustWeights = False
        self.previousScore = 0
        self.previousQ = 0
        self.f_exit = 0
        self.f_bomb = 0
        self.f_monsters = []

    def do(self, wrld):

        # TODO: reset paths
        qCharNode = Node(Node.CHARACTER, None,
                         wrld.me(self).x, wrld.me(self).y)
        exitNode = None
        monsterNodes = []
        explosionNodes = []
        bombNode = None
        self.exitPath = None
        self.bombPath = None
        self.monsterPaths = []
        self.explosionNodes = []

        if self.adjustWeights:
            # delta = [R- gamma(max_Q(s',a'))]-Q(s,a)
            # this code runs in the s' state after we find the "real" outcome of the action
            # the reward is the difference in score from s' and score of s (self.previousScore)
            R = wrld.scores.get(self.name)-self.previousScore
            all_q = self.Q_max_a(wrld, qCharNode)
            # all_q[0][1] is the Q value of the best next action we estimate from current state (s' in this frame of reference)
            delta = (R - self.gamma * all_q[0][1]) - self.previousQ

            # weight 0 is exit
            self.weights[0] = self.weights[0] + self.alpha*delta*self.f_exit
            self.weights[1] = self.weights[1] + self.alpha*delta*self.f_bomb
            for f_mon in self.f_monsters:
                self.weights[2] = self.weights[2] + self.alpha*delta * f_mon

            # finished adjusting, reset all temporary information and continue on
            self.adjustWeights = False
        
        self.previousScore = 0
        self.previousQ = 0
        self.f_exit = 0
        self.f_bomb = 0
        self.f_monsters = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld, x, y)
                # print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    exitNode = Node(t, None, x, y)
                elif t == Node.MONSTER:
                    monsterNodes.append(Node(t, None, x, y))
                elif t == Node.BOMB:
                    bombNode = Node(t, None, x, y)
                elif t == Node.EXPLOSION:
                    explosionNodes.append(
                        Node(t, None, x, y))  # hopefully none?

        # print(monsterNodes)
        # find paths to points
        # determine big brain time
        bigBrainTime = False  # this is true when we need to use big brain to not die
        self.exitPath = Solver.solve_path(
            wrld, qCharNode, exitNode, self.wallClip)
        if bombNode is not None:
            self.bombPath = Solver.solve_path(wrld, qCharNode, bombNode)
            # TODO: bombs explode in a cross pattern???
            if self.bombPath <= 6:
                bigBrainTime = True  # we have a bomb nearby so think ahead here
        for mNode in monsterNodes:
            self.monsterPaths.append(Solver.solve_path(
                wrld, qCharNode, mNode, noMonsters=False))
            # TODO: remember pythagoras
            if len(self.monsterPaths[-1]) <= 5:
                print("big brain time")
                bigBrainTime = True  # plz do not die

        # ok so we have distances, we know if we need to use q approximation

        #print(f"path: {exitSolver.path}")
        input("pause")  # comment this if you don't want to pause
        if self.exitPath:
            for n in self.exitPath:
                self.set_cell_color(n.x, n.y, Fore.RED + Back.GREEN)
            if bigBrainTime:
                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                # check all actions for Q_approx
                # order by max q value
                all_q = self.Q_max_a(wrld, qCharNode)

                # take the action with the highest q value
                # get the dx dy from the action tuple
                self.move(all_q[0][0], all_q[0][1])
                # store q and score of s so that when do() is called next it is under the "real" s' state with all monsters moved
                # we will perform weight adjustment at the beginning of that method

                self.previousQ = all_q[0][1]
                self.previousScore = wrld.scores.get(self.name)
                # for bomb logic, add a bomb at the first adjacent node on the path where

            else:
                # do not engage big brain, we use small brain monke pathfinding
                dx = self.exitPath[1].x-self.x
                dy = self.exitPath[1].y-self.y
                #print(f"move: {dx},{dy}")
                self.move(dx, dy)
        else:
            print("no path")
            pass

    # returns list of tuple: (action tuple, Q approx value for action)
    def Q_max_a(self, wrld, qCharNode):
        all_q = []  # list of tuples (action, approx Q value)
        for action in Solver.directions:
            x_val = qCharNode.x + action[0]  # destination coords
            y_val = qCharNode.y + action[1]
            if Solver.valid_action(wrld, (x_val, y_val), self.wallClip, noMonsters=False):
                # this check will tell us if the action won't put us out of bounds, through a wall, or into a monster

                # world is state, but we care about specific info from the state not the whole thing
                all_q.append((action, self.Q_approx(wrld, action)))

        # sort list of Q(s,a) by highest first
        all_q = sorted(all_q, key=itemgetter(1), reverse=True)

    def Q_approx(self, wrld, action):

        # change assumption to monsters don't move
        # triggering big brain needs to use pythogras
        # ideally have "buffer" zone
        #   get away from monster if within the buffer zone
        # initialize weights
        # store/save weights after trial
        # make sure to reset paths at start of self.do()
        # if in path of explosion, dont be (binary feature) (if true, very high negative weight)
        # exploitation/exploration logic
        # bomb logic
        # (adjust a* to put walls at lowest priority overall)
        # for path to exit, place bomb at first empty node before a wall (when using wall clip)

        # clone world because... reasons?
        s_clone = SensedWorld.from_world(wrld)
        # move the character according to this action
        s_clone.me(self).move(action[0], action[1])

        s_prime = s_clone.next()  # tuple (new_world, events).

        s_prime_qCharNode = Node(Node.CHARACTER, None,
                                 s_prime[0].me(self).x, s_prime[0].me(self).y)
        s_prime_exitNode = None
        s_prime_monsterNodes = []
        s_prime_bombNode = None
        s_prime_explosionNodes = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld, x, y)
                # print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    s_prime_exitNode = Node(t, None, x, y)
                elif t == Node.MONSTER:
                    s_prime_monsterNodes.append(Node(t, None, x, y))
                elif t == Node.BOMB:
                    s_prime_bombNode = Node(t, None, x, y)
                elif t == Node.EXPLOSION:
                    s_prime_explosionNodes.append(Node(t, None, x, y))

        s_prime_exitPath = Solver.solve_path(
            wrld, s_prime_qCharNode, s_prime_exitNode, self.wallClip)  # solve path to exit
        # add weighted manhattan distance to exit
        self.f_exit = self.value_func(len(s_prime_exitPath))
        q_value = self.weights[0]*self.f_exit
        if s_prime_bombNode is not None:
            # solve path to bomb if there is one
            s_prime_bombPath = Solver.solve_path(
                wrld, s_prime_qCharNode, s_prime_bombNode)
            # add weighted manhattan distance to bomb
            self.f_bomb = self.value_func(len(s_prime_bombPath))
            q_value += self.weights[1]*self.f_bomb
        s_prime_monsterPaths = []

        for s_p_mNode in s_prime_monsterNodes:
            s_prime_monsterPaths.append(Solver.solve_path(
                wrld, s_prime_qCharNode, s_p_mNode, noMonsters=False))  # solve path to a monster
            # add weighted manhattan distance to monster
            self.f_monsters.append(self.value_func(len(s_prime_monsterPaths[-1])))
            q_value += self.weights[2] * self.f_monsters[-1]

        return q_value

        # Calculate paths for s'

        # perform sum of weight*f(distance) for distances to
        # exit
        # bomb
        # closest monster
        # explosion?

        # return q value

    def value_func(self, d):
        return 1/(1+d)


'''
1 2 3
4 x 5    9 actions with bomb
6 7 8
'''
'''
s = (d_exit,d_monster,d_bomb)
f = 1/(1+d)
Q_approx(s,a) = w[s][0]*f(exit) + w[s][1]*f(n monsters) + w[s][2]*f(bomb)
Q_approx(s,NW) = w*f(exit) + w*f(1 monster)
Q_approx(s,W) = w*f(exit) + w*f(1 monster)
'''

'''
buffer zone corner is sqrt(3^2 + 3^2) as hypotenuse distance
anything equal/less than that distance means we need to trigger Q learning to move away/down?
xxxxxxx
x-----x
x-----x
x--m--x
x-----x
x-----x
xxxxxxx
'''
