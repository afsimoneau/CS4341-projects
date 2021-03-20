# This is necessary to find the main code
import numpy as np
from events import Event
from sensed_world import SensedWorld
from operator import itemgetter
from entity import CharacterEntity
from colorama import Fore, Back
from astar import Node, Solver
from collections import namedtuple
import time
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
        self.weights = weights
        self.wallClip = wallClip

        # changes across runs
        self.exitNode = None
        self.bombNode = None
        self.monsterNodes = []
        self.explosionNodes = []

        self.exitPath = None
        self.bombPath = None
        self.monsterPath = None  # closest monster
        self.explosionPath = None

        # q specific data
        self.alpha = .01
        self.gamma = .75
        self.adjustWeights = False
        self.previousAction = (0, 0)
        self.previousScore = 0
        self.previousQ = 0
        self.previousF = {}

    def reset(self):
        self.exitNode = None
        self.bombNode = None
        self.monsterNodes = []
        self.explosionNodes = []

        self.exitPath = None
        self.bombPath = None
        self.monsterPaths = []
        self.explosionPaths = []

    def do(self, wrld):
        qCharNode = Node(Node.CHARACTER, None,
                         wrld.me(self).x, wrld.me(self).y)
        
        if self.adjustWeights:
            self.weight_adjust_helper(wrld, qCharNode)
            
        self.reset()

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld, x, y)
                # print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    self.exitNode = Node(t, None, x, y)
                if t == Node.MONSTER:
                    self.monsterNodes.append(Node(t, None, x, y))
                if t == Node.BOMB:
                    self.bombNode = Node(t, None, x, y)
                if t == Node.EXPLOSION:
                    self.explosionNodes.append(
                        Node(t, None, x, y))

        # print(monsterNodes)
        # find paths to points
        # determine big brain time
        bigBrainTime = False  # this is true when we need to use big brain to not die
        self.exitPath = Solver.solve_path(
            wrld, qCharNode, self.exitNode, self.wallClip)
        if self.bombNode is not None:
            self.bombPath = Solver.solve_path(wrld, qCharNode, self.bombNode)
            # TODO: bombs explode in a cross pattern???
            if self.bombNode.x == self.x and np.abs(self.bombNode.x-self.x) < 4 or self.bombNode.y == self.y and np.abs(self.bombNode.y-self.y) < 4:
                bigBrainTime = True  # we are on path of bomb
        for mNode in self.monsterNodes:
            mPath = Solver.solve_path(wrld, qCharNode, mNode, noMonsters=False)
            if self.monsterPath is None or len(mPath) < len(self.monsterPath):
                self.monsterPath = mPath
            # pythagorean theorem. if we're on the buffer zone of the monster, we engage the ai
            rng = 2
            for m_names in wrld.monsters_at(mNode.x,mNode.y):
                name = m_names.name
                if name=="aggressive" or name == "selfpreserving":
                    rng = 4
            
            
            if np.abs(mNode.x-self.x) <= rng and np.abs(mNode.y-self.y) <=rng:
                print("big brain time")
                bigBrainTime = True  # plz do not die

        #print(f"path: {exitSolver.path}")
        # input("pause")  # comment this if you don't want to pause
        # time.sleep(.5)
        if self.exitPath:
            # for n in self.exitPath:
            #     self.set_cell_color(n.x, n.y, Fore.RED + Back.GREEN)
            if bigBrainTime:
                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                #input()
                print("weights:")
                print(self.weights)
                # check all actions for Q_approx
                # order by max q value
                all_q = self.Q_max_a(wrld, qCharNode)
                #print(all_q)
                # take the action with the highest q value
                # get the first element of all_q, then take the action tuple, then get dx/dy from it
                self.move(all_q[0][0][0], all_q[0][0][1])
                # store q and score of s so that when do() is called next it is under the "real" s' state with all monsters moved
                # we will perform weight adjustment at the beginning of that method

                self.adjustWeights = True
                self.previousAction = all_q[0][0]
                self.previousScore = wrld.scores[self.name]
                self.previousQ = all_q[0][1]

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
        # find the value of not moving

        for action in Solver.directions:
            x_val = qCharNode.x + action[0]  # destination coords
            y_val = qCharNode.y + action[1]
            if Solver.valid_action(wrld, (x_val, y_val), self.wallClip, noMonsters=True):
                # this check will tell us if the action won't put us out of bounds, through a wall, or into a monster
                # world is state, but we care about specific info from the state not the whole thing
                all_q.append((action, self.Q_approx(wrld, action)))

        # sort list of Q(s,a) by highest first
        all_q = sorted(all_q, key=itemgetter(1), reverse=True)
        return all_q

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

        # create/set up s' and state information
        copy = SensedWorld.from_world(wrld)
        copy.me(self).move(action[0],action[1])
        
        s_prime = copy.next()  # tuple (new_world, events)
        
        for e in s_prime[1]:
            if e.tpe == Event.BOMB_HIT_CHARACTER:
                return -10
            if e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                return -10
            if e.tpe == Event.CHARACTER_FOUND_EXIT:
                return 100

        s_prime_qCharNode = Node(Node.CHARACTER, None,
                                 s_prime[0].me(self).x, s_prime[0].me(self).y)

        s_prime_exitNode = None
        s_prime_bombNode = None
        s_prime_monsterNodes = []
        s_prime_explosionNodes = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld, x, y)
                # print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    s_prime_exitNode = Node(t, None, x, y)
                if t == Node.MONSTER:
                    s_prime_monsterNodes.append(Node(t, None, x, y))
                if t == Node.BOMB:
                    s_prime_bombNode = Node(t, None, x, y)
                if t == Node.EXPLOSION:
                    s_prime_explosionNodes.append(Node(t, None, x, y))

        # begin q approximation value calculations -----
        self.previousF[action] = []

        s_prime_exitPath = Solver.solve_path(
            wrld, s_prime_qCharNode, s_prime_exitNode, self.wallClip)  # solve path to exit
        
        # add weighted manhattan distance to exit
        f_exit = self.value_func(len(s_prime_exitPath))
        self.previousF[action].append(f_exit)
        q_value = self.weights[0]*f_exit

        if s_prime_bombNode is not None:
            # solve path to bomb if there is one
            s_prime_bombPath = Solver.solve_path(
                wrld, s_prime_qCharNode, s_prime_bombNode)
            # add weighted manhattan distance to bomb
            f_bomb = self.value_func(len(s_prime_bombPath))
            self.previousF[action].append(f_bomb)
            q_value += self.weights[1]*f_bomb
        else:
            self.previousF[action].append(0)

        s_prime_monsterPath = None
        for s_p_mNode in s_prime_monsterNodes:
            path = Solver.solve_path(
                wrld, s_prime_qCharNode, s_p_mNode, noMonsters=False)
            if s_prime_monsterPath is None or len(path) < len(s_prime_monsterPath):
                s_prime_monsterPath = path
        f_mon = self.value_func(len(s_prime_monsterPath))
        self.previousF[action].append(f_mon)
        q_value += self.weights[2]*f_mon
        
        '''
        exit node       [1]
        monster node    [1]
        
        [mx,my] dot [ex,ey]
        -------------------
        ||CM|| * ||CE||
        '''
        #print(self.exitPath)
        exit_vector = np.array([self.exitPath[1].x,self.exitPath[1].y])
        monster_vector = np.array([self.monsterPath[1].x,self.monsterPath[1].y])
        f_product = (monster_vector.dot(exit_vector))/(len(monster_vector)*len(exit_vector))
        if f_product>1:
            f_product=1
        elif f_product<1:
            f_product=-1
        self.previousF[action].append(f_product)
        q_value+= self.weights[3]*f_product
        
        
        #TODO: do this here
        
        
        
        
        
        
        
        
        print(f"a: ({action[0]}, {action[1]}) | f: {f_exit}, {f_mon}, {f_product} | q: {q_value}")
        
        

        return q_value

    def value_func(self, d):
        return 1/(1+d)

    def weight_adjust_helper(self, wrld, qCharNode):
        all_q = self.Q_max_a(wrld, qCharNode)
        reward = self.previousScore-wrld.scores[self.name]
        print(f"reward:{reward}")
        delta_correction = (reward+(self.gamma*all_q[0][1]))-self.previousQ
        for i,w in enumerate(self.weights):
            self.weights[i] = self.weights[i] + \
                (self.alpha*delta_correction *
                 self.previousF[self.previousAction][i])

        self.adjustWeights = False
        self.previousAction = (0, 0)
        self.previousScore = 0
        self.previousQ = 0
        self.previousF = {}


'''
1 2 3
4 x 5    9 actions with bomb 
6 7 8

xxxxxxx
x-----x
x-----x
x--m--x
x-----x
x-----x
xxxxxxx
'''
