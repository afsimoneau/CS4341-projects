import random
import game
import agent
import alpha_beta_agent as aba

# Set random seed for reproducibility
random.seed()
'''
g1 = game.Game(7, # width
              6, # height
              4, # tokens in a row to win
              aba.THE_AGENT,       # player 1
              agent.RandomAgent("random2"))       # player 2

outcome = g1.go()
'''

win = 0
total = 10
w = 7
h = 6
t = 4
for i in range(total):
    a1 = aba.THE_AGENT
    a2 = agent.RandomAgent("random2")
    g = game.Game(w,h,t,a1,a2)      
    if (g.go()==1):
        win+=1
print(f"\nTOTAL WIN/LOSS:\nTotal: {total}\nWins: {win}\nRatio: {win/total}")
'''
g2 = game.Game(7, # width
              6, # height
              5, # tokens in a row to win
              aba.THE_AGENT,       # player 1
              agent.RandomAgent("random2"))       # player 2

outcome = g2.go()

g3 = game.Game(10, # width
              8, # height
              4, # tokens in a row to win
              aba.THE_AGENT,       # player 1
              agent.RandomAgent("random2"))       # player 2

outcome = g3.go()



g4 = game.Game(10, # width
              8, # height
              5, # tokens in a row to win
              aba.THE_AGENT,       # player 1
              agent.RandomAgent("random2"))       # player 2

outcome = g4.go()
'''
#
# Human vs. Random
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human"),    # player 1
#               agent.RandomAgent("random"))        # player 2

#
# Random vs. AlphaBeta
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.RandomAgent("random"),        # player 1
#               aba.AlphaBetaAgent("alphabeta", 4)) # player 2

#
# Human vs. AlphaBeta
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human"),    # player 1
#               aba.AlphaBetaAgent("alphabeta", 4)) # player 2

#
# Human vs. Human
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human1"),   # player 1
#               agent.InteractiveAgent("human2"))   # player 2
