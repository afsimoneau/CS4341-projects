# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../group21')
from testcharacter import TestCharacter
from qcharacter import QCharacter


wins = 0
total = 10
for i in range(total):
    # Create the game
    g = Game.fromfile('map.txt')

    # TODO Add your character
    # g.add_character(TestCharacter("me", # name
    #                               "C",  # avatar
    #                               0, 0  # position
    # ))
    with open("weights2-1.txt", "r") as reader:
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
    with open("weights2-1.txt", "w") as writer:
        for w in weights:
            writer.write(str(w))
            writer.write(str("\n"))
    writer.close()
print(f"win/total:{wins}/{total} == {wins/total}")

