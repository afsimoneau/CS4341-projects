# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

import Node 

class QCharacter(CharacterEntity):

    def do(self, wrld):
        pass
        '''
        
        '''
    
    def score(self, wrld, depth):
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
        
    def pathfind(self, wrld, entity):

        start = Node(None, (self.x, self.y))
        #wronf 
        path = search(wrld, start, wrld.exitcell)
    return path

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
