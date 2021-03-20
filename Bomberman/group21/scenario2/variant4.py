# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../group21')
from testcharacter import TestCharacter
from qcharacter import QCharacter


wins = 0
total = 10
for i in range(total):
    # Create the game
    random.seed(123) # TODO Change this if you want different random choices
    g = Game.fromfile('map.txt')
    g.add_monster(SelfPreservingMonster("aggressive", # name
                                        "A",          # avatar
                                        3, 13,        # position
                                        2             # detection range
    ))

    with open("weights2-4.txt", "r") as reader:
        lines = reader.readlines()
    reader.close()
    weights = []
    for line in lines:
        weights.append(float(line))
        
    q_char = QCharacter("ai","Q",0,0,weights,wallClip=True)
    g.add_character(q_char)

    # Run!
    g.go(1)
    if g.world.scores["ai"]>0:
        wins+=1
    with open("weights2-4.txt", "w") as writer:
        for w in weights:
            writer.write(str(w))
            writer.write(str("\n"))
    writer.close()
print(f"win/total:{wins}/{total} == {wins/total}")