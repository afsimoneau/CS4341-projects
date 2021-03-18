# This is necessary to find the main code
from collections import namedtuple
from astar import Node, Solver
from colorama import Fore, Back
from entity import CharacterEntity
from operator import itemgetter
from sensed_world import SensedWorld
import numpy as np
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff


class QCharacter(CharacterEntity):

    #wallclip = true when doing scenario 2
    def __init__(self, name, avatar, x, y, weights,wallClip = False, train=True):
        super().__init__(name, avatar, x, y,)
        # initialize weights table here
        self.train = train
        self.weights = [] #import this?
        self.wallClip = wallClip
        self.exitPath = None
        self.bombPath = None
        self.monsterPaths = []
        self.explosionNodes = []

    def do(self, wrld):
        # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
        qCharNode = Node(Node.CHARACTER, None,
                         wrld.me(self).x, wrld.me(self).y)
        exitNode = None
        monsterNodes = []
        bombNode = None

        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld,x, y)
                #print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    exitNode = Node(t, None, x, y)
                elif t == Node.MONSTER:
                    monsterNodes.append(Node(t, None, x, y))
                elif t == Node.BOMB:
                    bombNode = Node(t, None, x, y)
                elif t == Node.EXPLOSION:
                    self.explosionNodes.append(Node(t,None,x,y)) # hopefully none?

        # print(monsterNodes)
        # find paths to points
        # determine big brain time
        bigBrainTime = False  # this is true when we need to use big brain to not die
        self.exitPath = Solver.solve_path(wrld,qCharNode,exitNode,self.wallClip)
        if bombNode is not None:
            self.bombPath = Solver.solve_path(wrld,qCharNode,bombNode)
            if self.bombPath<=6:
                bigBrainTime=True # we have a bomb nearby so think ahead here
        for mNode in monsterNodes:
            self.monsterPaths.append(Solver.solve_path(wrld,qCharNode,mNode,noMonsters=False))
            if len(self.monsterPaths[-1])<=5:
                print("big brain time")
                bigBrainTime = True  # plz do not die
        
        # ok so we have distances, we know if we need to use q approximation
        

        #print(f"path: {exitSolver.path}")
        input("pause") #comment this if you don't want to pause
        if self.exitPath:
            for n in self.exitPath:
                self.set_cell_color(n.x, n.y, Fore.RED + Back.GREEN)
            if bigBrainTime:
                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                # this code is responsible for setting up the "state" for our big brain calculations
                # get list of distances to monsters

                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                # check all actions for Q_approx
                all_q = [] # list of tuples (action, approx Q value)
                for action in Solver.directions:
                    x_val = qCharNode.x + action[0]
                    y_val = qCharNode.y + action[1]
                    if Solver.valid_action(wrld,(x_val, y_val), wallClip = False, noMonsters = False):
                        # this check will tell us if the action won't put us out of bounds, through a wall, or into a monster

                        # world is state, but we care about specific info from the state not the whole thing
                        all_q.append((action,self.Q_approx(wrld, action))) 
                
                all_q = sorted(all_q, key = itemgetter(1), reverse=True) # sort list of Q(s,a) by highest first

                # take the action with the highest q value
                # get the dx dy from the action tuple
                self.move(all_q[0][0], all_q[0][1])


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

    def Q_approx(self, wrld, action):
        
        # move all monsters/characters
        s_clone = SensedWorld.from_world(wrld)
        print("monsters:")
        print(s_clone.monsters)
        for m in s_clone.monsters.values():
            print(m)
            dangerPath = Solver.solve_path() #need q char node from above. add to self? TODO!!!!!!!!!!!
            worst_dx = 0 # need to find "worst possible move" for a given m monster
            worst_dy = 0
            m[0].move(worst_dx,worst_dy) #move each monster to the worst possible location 
        s_clone.me(self).move(action[0],action[1]) #move the character according to this action
        
        s_prime = wrld.next() # tuple (new_world, events).

        newCharNode = Node(Node.CHARACTER, None,
                         wrld.me(self).x, wrld.me(self).y)
        prime_exitNode = None
        prime_monsterNodes = []
        prime_bombNode = None
        prime_explosionNodes = []
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                t = Solver.what_is(wrld,x, y)
                #print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    prime_exitNode = Node(t, None, x, y)
                elif t == Node.MONSTER:
                    prime_monsterNodes.append(Node(t, None, x, y))
                elif t == Node.BOMB:
                    prime_bombNode = Node(t, None, x, y)
                elif t == Node.EXPLOSION:
                    prime_explosionNodes.append(Node(t,None,x,y))

        #Calculate paths for s'

        # perform sum of weight*f(distance) for distances to 
        # exit
        # bomb
        # closest monster
        # explosion?

        # return q value

        '''
        qCharNode = Node(Node.CHARACTER, None, state_prime.me(self).x, state_prime.me(self).y)

        monsterNodes = []

        exitSolver = Solver(state_prime, qCharNode, None)
        bombSolver = Solver(state_prime, qCharNode, None)
        for x in range(state_prime.width()):
            for y in range(state_prime.height()):
                t = exitSolver.what_is(x, y)
                #print(f"{t},{x},{y}")
                if t == Node.EXIT:
                    exitSolver.end = Node(t, None, x, y)
                elif t == Node.MONSTER:
                    monsterNodes.append(Node(t, None, x, y))
                elif t == Node.BOMB:
                    bombSolver.end = Node(t, None, x, y)
                # elif t == Node.EXPLOSION:
                #     explosionNodes.append(Node(t,None,x,y))

        #print(monsterNodes)
        #find the exit
        exitSolver.solve()
        if bombSolver.end is not None:
            bombSolver.solve()
        monsterSolvers = self.eval_solvers(state_prime, qCharNode, monsterNodes)

        monsterDistance = 1000
        for mSolver in monsterSolvers:
            if monsterDistance > len(mSolver.path):
                monsterDistance = len(mSolver.path)

        # state is tuple of lengths to (exit, bomb, closest monster)
        state = (len(exitSolver.path), len(bombSolver.path), monsterDistance)
        
        this_q = self.weights[state][0] * self.value_func(state_prime[0]) + self.weights[state][1] * self.value_func(state_prime[1])+ self.weights[state][2] * self.value_func(state_prime[2])
        
        #need to compare this_q???
        action = state_prime.me(self.weights[this_q]).move(dx, dy)
        return action
        '''

    def value_func(self,d):
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