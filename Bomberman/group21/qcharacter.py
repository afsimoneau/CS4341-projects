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
        self.gamma = .5
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
        self.monsterPath = None
        self.explosionPath = None

    def do(self, wrld):
        qCharNode = Node(Node.CHARACTER, None,
                         wrld.me(self).x, wrld.me(self).y)

        if self.adjustWeights and self.train:
            self.weight_adjust_helper(wrld, qCharNode)

        self.reset()
        
        things = self.find_things(wrld)
        self.exitNode = things[0]
        self.bombNode = things[1]
        self.monsterNodes = things[2]
        self.explosionNodes = things[3]
        
        # print(monsterNodes)
        # find paths to points
        # determine big brain time
        bigBrainTime = False  # this is true when we need to use big brain to not die
        self.exitPath = Solver.solve_path(
            wrld, qCharNode, self.exitNode, self.wallClip,findExplosion = True) # we can go through the explosion to find the path, but don't take the path
        if self.bombNode is not None:
            self.bombPath = Solver.solve_path(wrld, qCharNode, self.bombNode)
            # TODO: bombs explode in a cross pattern???
            if np.abs(self.bombNode.x-self.x) < 4 or np.abs(self.bombNode.y-self.y) < 4:
                bigBrainTime = True  # we are on path of bomb
        for mNode in self.monsterNodes:
            mPath = Solver.solve_path(wrld, qCharNode, mNode, noMonsters=False)
            if self.monsterPath is None or len(mPath) < len(self.monsterPath):
                self.monsterPath = mPath
            
            rng = 2
            for m_names in wrld.monsters_at(mNode.x,mNode.y):
                name = m_names.name
                if name=="aggressive" or name == "selfpreserving":
                    rng = 3
            if np.abs(mNode.x-self.x) <= rng and np.abs(mNode.y-self.y) <=rng:
                print("big brain time")
                bigBrainTime = True  # plz do not die
                
        for eNode in self.explosionNodes:
            ePath = Solver.solve_path(wrld, qCharNode, eNode, findExplosion = True)
            if self.explosionPath is None or len(ePath) < len(self.explosionPath):
                self.explosionPath = ePath
            
            if len(self.explosionPath) <= 2:
                bigBrainTime = True  # plz do not die

        #print(f"path: {exitSolver.path}")
        # input("pause")  # comment this if you don't want to pause
        # time.sleep(.5)
        if self.exitPath:
            # for n in self.exitPath:
            #     self.set_cell_color(n.x, n.y, Fore.RED + Back.GREEN)
            
            if self.exitPath[1].type == Node.WALL and self.bombNode is None:
                self.place_bomb()
                return
            
            if bigBrainTime:
                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -

                print("weights:")
                print(self.weights)
                # check all actions for Q_approx
                # order by max q value
                all_q = self.Q_max_a(wrld, qCharNode)
                print(all_q)
                # take the action with the highest q value
                # get the first element of all_q, then take the action tuple, then get dx/dy from it
                self.move(all_q[0][0][0], all_q[0][0][1])
                # store q and score of s so that when do() is called next it is under the "real" s' state with all monsters moved
                # we will perform weight adjustment at the beginning of that method

                self.adjustWeights = True
                print(self.previousF)
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
            if Solver.valid_action(wrld, (x_val, y_val), wallClip = False, noMonsters=True, findExplosion = False):
                # this check will tell us if the action won't put us out of bounds, through a wall, or into a monster
                # world is state, but we care about specific info from the state not the whole thing
                all_q.append((action, self.Q_approx(wrld, action)))

        # sort list of Q(s,a) by highest first
        all_q = sorted(all_q, key=itemgetter(1), reverse=True)
        return all_q

    def Q_approx(self, wrld, action):
        # create/set up s' and state information
        copy = SensedWorld.from_world(wrld)
        copy.me(self).move(action[0],action[1])

        s_prime = copy.next()  # tuple (new_world, events)

        for e in s_prime[1]:
            if e.tpe == Event.BOMB_HIT_CHARACTER or e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                return -100
            if e.tpe == Event.CHARACTER_FOUND_EXIT:
                return 100
        
        for e in s_prime[0].next()[1]:
            # check 2 steps ahead since explosions update before characters do 
            # we don't want to move into path of explosion and then can't move away in time
            if e.tpe == Event.BOMB_HIT_CHARACTER or e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                return -100
            if e.tpe == Event.CHARACTER_FOUND_EXIT:
                return 100
        
        #if we get here the character is alive on the board
            
        s_prime_qCharNode = Node(Node.CHARACTER, None,
                                 s_prime[0].me(self).x, s_prime[0].me(self).y)

        things = self.find_things(s_prime[0])
        s_prime_exitNode = things[0]
        s_prime_bombNode = things[1]
        s_prime_monsterNodes = things[2]
        s_prime_explosionNodes = things[3] 
        
        # begin q approximation value calculations -----------------------------------
        
        self.previousF[action] = []
        
        # 7 weights are in order of:
        #
        # w0: exit distance
        # w1: bomb distance
        # w2: dot product of bomb and exit vectors
        # w3: monster distance
        # w4: dot product of monster and exit vectors
        # w5: monster distance
        # w6: dot product of monster and exit vectors
        # w7: distance to closest x
        # w8: distance to closest y

        s_prime_exitPath = Solver.solve_path(
            wrld, s_prime_qCharNode, s_prime_exitNode, self.wallClip,findExplosion = True)  # solve path to exit which can include explosions
        
        # we will need this later
        exit_vector = np.array(
            [self.exitPath[1].x-self.exitPath[0].x, self.exitPath[1].y-self.exitPath[0].y])

        # exit term ------------------------------------------------------------------
        
        f_exit = self.value_dist(len(s_prime_exitPath))
        self.previousF[action].append(f_exit)
        q_value = self.weights[0]*f_exit
        
        # bomb terms ------------------------------------------------------------------
        s_prime_bombNode = None
        if s_prime_bombNode is not None:
            # solve path to bomb
            s_prime_bombPath = Solver.solve_path(
                s_prime[0], s_prime_qCharNode, s_prime_bombNode)
            
            # add weighted manhattan distance to bomb
            f_bomb = self.value_dist(len(s_prime_bombPath))
            self.previousF[action].append(f_bomb)
            q_value += self.weights[1]*f_bomb
            
            #vector term -------------------------------
            bomb_vector = np.array(
            [s_prime_bombPath[1].x-s_prime_bombPath[0].x, s_prime_bombPath[1].y-s_prime_bombPath[0].y])
            f_BE_product = np.dot(bomb_vector, exit_vector)
            if f_BE_product>1:
                f_BE_product = 1
            elif f_BE_product<1:
                f_BE_product=-1
            self.previousF[action].append(f_BE_product)
            q_value += self.weights[2]*f_BE_product
            
        else:
            self.previousF[action].append(0) #w1
            self.previousF[action].append(0) #w2

        # monster terms ------------------------------------------------------------------
        if len(s_prime_monsterNodes) != 0:
            s_prime_monsterPath = None
            for s_p_mNode in s_prime_monsterNodes:
                path = Solver.solve_path(
                    wrld, s_prime_qCharNode, s_p_mNode,wallClip = self.wallClip,noMonsters=False, findExplosion = True)
                if s_prime_monsterPath is None or len(path) < len(s_prime_monsterPath):
                    s_prime_monsterPath = path
            f_mon = self.value_dist(len(s_prime_monsterPath))
            self.previousF[action].append(f_mon)
            q_value += self.weights[3]*f_mon

            monster_vector = np.array(
                [s_prime_monsterPath[1].x-s_prime_monsterPath[0].x, s_prime_monsterPath[1].y-s_prime_monsterPath[0].y])
            
            f_ME_product = np.dot(monster_vector, exit_vector)
            if f_ME_product>1:
                f_ME_product = 1
            elif f_ME_product<1:
                f_ME_product=-1
            self.previousF[action].append(f_ME_product)
            q_value += self.weights[4]*f_ME_product
        else:
            self.previousF[action].append(0) #w3
            self.previousF[action].append(0) #w4
            
        # explosion terms ------------------------------------------------------------------
        if len(s_prime_explosionNodes) != 0:
            s_prime_explosionPath = None
            for s_p_eNode in s_prime_explosionNodes:
                path = Solver.solve_path(
                    s_prime[0], s_prime_qCharNode, s_p_eNode,wallClip = self.wallClip,findExplosion = True)
                if s_prime_explosionPath is None or len(path) < len(s_prime_explosionPath):
                    s_prime_explosionPath = path
                    
            f_exp = self.value_dist(len(s_prime_explosionPath))
            self.previousF[action].append(f_exp)
            q_value += self.weights[5]*f_exp

            explosion_vector = np.array(
                [s_prime_explosionPath[1].x-s_prime_explosionPath[0].x, s_prime_explosionPath[1].y-s_prime_explosionPath[0].y])
            
            f_ExpE_product = np.dot(explosion_vector, exit_vector)
            if f_ExpE_product>1:
                f_ExpE_product = 1
            elif f_ExpE_product<1:
                f_ExpE_product=-1
            self.previousF[action].append(f_ExpE_product)
            q_value += self.weights[6]*f_ExpE_product
        else:
            self.previousF[action].append(0) #w5
            self.previousF[action].append(0) #w6

        # x/y proximity terms ------------------------------------------------------------------
        
        f_x_short = self.value_dist(self.xWall_distance(s_prime[0],s_prime_qCharNode))
        self.previousF[action].append(f_x_short)
        q_value += self.weights[7]*f_x_short
        
        f_y_short = self.value_dist(self.yWall_distance(s_prime[0],s_prime_qCharNode))
        self.previousF[action].append(f_y_short)
        q_value += self.weights[8]*f_y_short
        
        return q_value

    def value_dist(self, d):
        return 1/(1+d)

    def weight_adjust_helper(self, wrld, qCharNode):
        all_q = self.Q_max_a(wrld, qCharNode)
        reward = self.previousScore-wrld.scores[self.name]
        print(f"reward:{reward}")
        delta_correction = (reward+(self.gamma*all_q[0][1]))-self.previousQ
        for i, w in enumerate(self.weights):
            self.weights[i] = self.weights[i] + (self.alpha*delta_correction * self.previousF[self.previousAction][i])

        self.adjustWeights = False
        self.previousAction = (0, 0)
        self.previousScore = 0
        self.previousQ = 0
        self.previousF = {}

    # find character.x to wall distance
    def xWall_distance(self, wrld, qCharNode):
        x_pos_count = 0
        while(qCharNode.x+x_pos_count < wrld.width()-1):
            x_pos_count += 1
            if wrld.wall_at(qCharNode.x+x_pos_count, qCharNode.y):
                break
        x_neg_count = 0
        while(qCharNode.x-x_neg_count > 0):
            x_neg_count += 1
            if wrld.wall_at(qCharNode.x-x_neg_count, qCharNode.y):
                break
        return min(x_pos_count, x_neg_count)

    # find character.y to wall distance
    def yWall_distance(self, wrld, qCharNode):
        y_pos_count = 0
        while(qCharNode.y+y_pos_count < wrld.height()-1):
            y_pos_count += 1
            if wrld.wall_at(qCharNode.x, qCharNode.y+y_pos_count):
                break
        y_neg_count = 0
        while(qCharNode.y-y_neg_count > 0):
            y_neg_count += 1
            if wrld.wall_at(qCharNode.x, qCharNode.y-y_neg_count):
                break
        return min(y_pos_count, y_neg_count)
    
    def find_things(self,wrld):
        eN = None
        bN = None
        mNds = []
        expNds = []

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld, x, y)
                # print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    eN = Node(t, None, x, y)
                if t == Node.BOMB:
                    bN = Node(t, None, x, y)
                if t == Node.MONSTER:
                    mNds.append(Node(t, None, x, y))
                if t == Node.EXPLOSION:
                    expNds.append(Node(t, None, x, y))
        return (eN,bN,mNds,expNds)

'''
1 2 3
4 x 5    9 actions with bomb 
6 7 8


xxxxxxx
x-----x
xWW---x
x-----x
x-----x
x-----x
xxxxxxx
'''


'''
exit node       [1]
monster node    [1]
[mx,my] dot [ex,ey]
-------------------
||CM|| * ||CE||
'''
# print(self.exitPath)