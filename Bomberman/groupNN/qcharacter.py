# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

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
        pass

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
