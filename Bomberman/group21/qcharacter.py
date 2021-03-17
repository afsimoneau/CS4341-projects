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

    def __init__(self, name, avatar, x, y, weights, train=True):
        super().__init__(name, avatar, x, y,)
        # initialize weights table here
        self.train = train
        self.weights = {}

    def do(self, wrld):
        # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
        qCharNode = Node(Node.CHARACTER, None,
                         wrld.me(self).x, wrld.me(self).y)

        monsterNodes = []

        exitSolver = Solver(wrld, qCharNode, None)
        bombSolver = Solver(wrld, qCharNode, None)
        for x in range(wrld.width()):
            for y in range(wrld.height()):
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
        # find the exit
        exitSolver.solve()
        if bombSolver.end is not None:
            bombSolver.solve()
        monsterSolvers = self.eval_solvers(wrld, qCharNode, monsterNodes)

        bigBrainTime = False  # this is true when we need to use big brain to not die
        
        for mSolve in monsterSolvers:
            if mSolve.path and len(mSolve.path) <= 5:
                print("big brain time")
                bigBrainTime = True  # plz do not die
        print(bombSolver.path)
        if bombSolver.path and len(bombSolver.path) <= 6 :
            print("big brain time")
            bigBrainTime = True  # we have a bomb nearby so think ahead here

        # TODO: if you're copying this code get rid of the stuff about using big brain lol
        # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -

        #print(f"path: {exitSolver.path}")
        input("pause") #comment this if you don't want to pause
        if exitSolver.path:
            for n in exitSolver.path:
                self.set_cell_color(n.x, n.y, Fore.RED + Back.GREEN)
            if bigBrainTime:
                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                # this code is responsible for setting up the "state" for our big brain calculations
                # get list of distances to monsters

                monsterDistance = 1000
                for mSolver in monsterSolvers:
                    if monsterDistance > len(mSolver.path):
                        monsterDistance = len(mSolver.path)

                # state is tuple of lengths to (exit, bomb, closest monster)
                state = (len(exitSolver.path), len(bombSolver.path), monsterDistance)

                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                # check all actions for Q_approx
                all_q = [] # list of tuples of an action/value association
                for action in Solver.directions:
                    x_val = qCharNode.x + action[0]
                    y_val = qCharNode.y + action[1]
                    if exitSolver.valid_action((x_val, y_val), wallClip = False, noMonsters = False):
                        # used exit solver because this method needs self.wrld
                        # this will tell us if the action won't put us out of bounds, through a wall, or into a monster
                        all_q.append((action,self.Q_approx(wrld, state, action)))
                
                all_q = sorted(all_q, key = itemgetter(1), reverse=True) # sort list by highest first
                # take the first action/value pair as it will be the highest
                # get the dx dy from the action tuple
                self.move(all_q[0][0], all_q[0][1])

                #actions (dx,dy)
                # find best neighbor, find dx,dy using neighbor-current for each x,y
            else:
                # do not engage big brain, we use small brain monke pathfinding
                dx = exitSolver.path[1].x-exitSolver.path[0].x
                dy = exitSolver.path[1].y-exitSolver.path[0].y
                #print(f"move: {dx},{dy}")
                self.move(dx, dy)
        else:
            print("no path")
            pass

    def Q_approx(self, wrld, state, action):
        if self.weights.get(state) is None:
            self.weights[state] = np.ones(3)

        wrld.me(self.weights[state]).move(dx, dy)
        state_prime = SensedWorld.from_world(wrld)
        #state_prime.me(self).move(dx, dy)

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

    def eval_solvers(self, wrld, qcn, nodes, wallClip=False, noMonsters=True):
        solverlist = []
        for node in nodes:
            solverlist.append(Solver(wrld, qcn, node))

        for slvr in solverlist:
            slvr.solve(wallClip, noMonsters)
        return solverlist

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