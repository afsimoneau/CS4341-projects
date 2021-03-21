# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '../group21')
from testcharacter import TestCharacter
from qcharacter import QCharacter

# Create the game
random.seed() # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
))

# # TODO Add your character
# g.add_character(TestCharacter("me", # name
#                             "C",  # avatar
#                             0, 0  # position
# ))

with open("weights2-2.txt", "r") as reader:
    lines = reader.readlines()
reader.close()
weights = []
for line in lines:
    weights.append(float(line))

q_char = QCharacter("ai","Q",0,0,weights,wallClip=True)
g.add_character(q_char)

# Run!
g.go(1)

with open("weights2-2.txt", "w") as writer:
    for w in weights:
        writer.write(str(w))
        writer.write(str("\n"))
writer.close()