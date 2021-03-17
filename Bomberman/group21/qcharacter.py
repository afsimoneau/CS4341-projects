# This is necessary to find the main code
from collections import namedtuple
from astar import Node, Solver
from colorama import Fore, Back
from entity import CharacterEntity
from operator import itemgetter
import numpy as np
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff


class QCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y, train=True):
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
                    if monsterDistance>len(mSolver.path):
                        monsterDistance = len(mSolver.path)

                # state is tuple of lengths to (exit,bomb,closest monster)
                state = (len(exitSolver.path), len(bombSolver.path), monsterDistance)

                # TODO:- - - - - - - - - - - - - - - - - - - - - - - - -
                # check all actions for Q_approx
                all_q = [] # list of tuples of an action/value association
                for action in Solver.directions:
                    x_val = qCharNode.x+action[0]
                    y_val = qCharNode.y+action[1]
                    if exitSolver.valid_action((x_val, y_val), wallClip=False, noMonsters=False):
                        # used exit solver because this method needs self.wrld
                        # this will tell us if the action won't put us out of bounds, through a wall, or into a monster
                        all_q.append((action,self.Q_approx(wrld, state, action)))
                
                all_q = sorted(all_q,key=itemgetter(1),reverse=True) # sort list by highest first
                # take the first action/value pair as it will be the highest
                # get the dx dy from the action tuple
                self.move(all_q[0][0],all_q[0][1])


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

    def eval_solvers(self, wrld, qcn, nodes, wallClip=False, noMonsters=True):
        solverlist = []
        for node in nodes:
            solverlist.append(Solver(wrld, qcn, node))

        for slvr in solverlist:
            slvr.solve(wallClip, noMonsters)
        return solverlist

    def value_function(self,d):
        return 1/(1+d)

    def Q_approx(self,wrld, state, action):
        if self.weights.get(state) is None:
            self.weights[state] = np.ones(3) #initialize weights of this state to zero
        
        # self.move(dx,dy) where dx and dy come from the tuple action
        state_prime = wrld.next() # i'm pretty sure you need to do self.move(dx,dy) before this

        # TODO: Maddy and Lily this line here is what i was working on:
        # this_q = self.weights[state][0]*self.value_func(state_prime[0]]) + self.weights[state][1]*self.value_func(state_prime[1])+ self.weights[state][1]*self.value_func(state_prime[2])

        # value_function is supposed to be using the distances in state s' so we need to estimate the next possible move using the current action
        # i suggest right now to try and copy paste the code from where I marked in do() and run it on the world returned by world.next
        # if you do self.move(dx,dy) for the current action and run wrld.next() you'll get a new world and be able to rerun the "solvers" for exit and other nodes and calculate
        

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
        return None


'''
        given an initial state
        evaluate best moves by considering 
        
        path length to exit
        proximity of threats
        
        recursively to a depth of x and returning a score
        discounting, follow bellman equation to assess overall score of a given branch of execution
            predict monsters
                aggro moving towards us if we're in range
                self preserving runs from bombs
                random and self preserving will move randomly
            make a safe move when next outcome will contain a threat
        
        '''

'''
List of threat states
Monster is close: linearly more important
    Need to make a decision
        de-vert from the path to get away
        place a bomb to kill the monster
Bomb goes off
    need to check and see if the character could be killed by the explosion
-------------------------------------------------
List of non-threat states
Monster is far: has some value, can be ignored
    Continue on the calculated path
Wall in our way
    not a threat but need to de-vert from the path
------------------------------------------------
Epsilon Greedy
Random probability
    probability < e
        pull a random action
    otherwise
        pull current-best action
Exploration-exploitation tradeoff (epsilon is usually around 10%)
    instruct the computer to explore (choose a random option with probability epsilon)
    or
    exploit (choose the best option which so far seems to be the best) the rmainder of the time

'''

'''
^
|\ 
O O
|\ \ 
^ ^ ^
| | |
O O O

1-8 player
2-8 monsters
8^3 options
8 | 2 monsters made the least ideal move
pick highest score when factoring in negative effect of monster's moves
predict further depths 
    self-preserving monster goes towards us, drop bomb?
    what will it do on it's next turn?
        Avoid the bomb, we know its decision
    

move away is +1
move closer is -1


   
   \|/
P  -R-
x  /
xxE

'''
