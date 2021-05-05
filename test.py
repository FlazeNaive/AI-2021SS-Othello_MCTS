import random
# from AI_player import AIPlayer
from board import Board
import numpy
from copy import deepcopy

board = Board()
a = [111, 2]
b = {}
b[("a", tuple(numpy.ravel(board._board)))] = 2
board2 = deepcopy(board)
print(b[("a", tuple(numpy.ravel(board._board)))])
board._move("F4", "O")
print("sss")
print(b.get(("a", tuple(numpy.ravel(board._board)))))
print("sss")
print(b.get(("a", tuple(numpy.ravel(board2._board)))))

print("sss")
print(b[("a", tuple(numpy.ravel(board2._board)))])

quit()

list_x = []
if len(list_x) == 0:
    x = None
else:
    x = random.choice(list_x)
print(x)


X = AIPlayer("X")
board = Board()
# a, b = X.Simulate(board, "X")
X.Simulate(board, "X")
board.display()
print(a, b)