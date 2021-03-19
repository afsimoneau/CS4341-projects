# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster
from qcharacter import QCharacter
import numpy as np
# TODO This is your code!
sys.path.insert(1, '../group21')
from testcharacter import TestCharacter

# Create the game
random.seed() # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
))

with open("weights1-2.txt", "r") as reader:
	lines = reader.readlines()
reader.close()
weights = []
for line in lines:
    weights.append(float(line))

q_char = QCharacter("ai","Q",0,0,weights)
g.add_character(q_char)

# Run!
g.go(1)

with open("weights1-2.txt", "w") as writer:
    for w in weights:
        writer.write(str(w))
        writer.write(str("\n"))
writer.close()
    






