# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster
from qcharacter import QCharacter
# TODO This is your code!
sys.path.insert(1, '../group21')
from testcharacter import TestCharacter


wins = 0
total = 25
for i in range(total):
    # Create the game
    random.seed() # TODO Change this if you want different random choices
    g = Game.fromfile('map.txt')
    g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                        "S",              # avatar
                                        3, 9,             # position
                                        1                 # detection range
    ))


    with open("weights1-3.txt", "r") as reader:
        lines = reader.readlines()
    reader.close()
    weights = []
    for line in lines:
        weights.append(float(line))

    q_char = QCharacter("ai","Q",0,0,weights)
    g.add_character(q_char)


    # # TODO Add your character
    # g.add_character(TestCharacter("me", # name
    #                               "C",  # avatar
    #                               0, 0  # position
    # ))

    # Run!
    g.go(1)

    with open("weights1-3.txt", "w") as writer:
        for w in weights:
            writer.write(str(w))
            writer.write(str("\n"))
    writer.close()
print(f"win/total:{wins}/{total} == {wins/total}")