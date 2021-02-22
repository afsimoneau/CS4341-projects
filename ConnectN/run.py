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
lose = 0 
tie = 0
total = 0
max = 200
w = 10
h = 8
t = 5
d = 4
for i in range(max):
    a1 = aba.AlphaBetaAgent("Group21",d)
    a2 = agent.RandomAgent("random2")
    g = game.Game(w,h,t,a1,a2)
    result = g.timed_go(15)
    total+=1
    if result==0:
        tie+=1
    elif result == 1:
        win+=1
    else:
        lose+=1
    print(f"\nTOTAL W/L/T:\nTotal: {total}\nWins: {win}\Lose: {lose}\Tie: {tie}\n(W/L) Ratio: {win/total}")

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
