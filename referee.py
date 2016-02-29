from program import Program
import sys
import argparse
import threading
import time
from gamestate import gamestate

def make_valid_move(game, agent, color):
	move = agent.sendCommand("genmove "+color)
	while(True):
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			agent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			move = agent.sendCommand("occupied")
	return move

class moveThread(threading.Thread):
	def __init__(self, game, agent, color):
		threading.Thread.__init__(self)
		self.game = game
		self.agent = agent
		self.color = color
		self.move = "x"
	def run(self):
		self.move = make_valid_move(self.game, self.agent, self.color).strip()


def move_to_cell(move):
	x =	ord(move[0].lower())-ord('a')
	y = int(move[1:])-1
	return (x,y)

parser = argparse.ArgumentParser(description="Referee a game of Kriegspiel Hex between two executable agents.")
parser.add_argument("program1", type=str, help="first (black) player executable")
parser.add_argument("program2", type=str, help="second (white) player executable")
parser.add_argument("--boardsize", "-b", type=int, help="side length of (square) board.")
parser.add_argument("--time", "-t", type=int, help="total time allowed for each move in seconds.")
parser.add_argument("--verbose", "-v", dest="verbose", action='store_const',
					const=True, default=False,
					help="print board after each move.")
args = parser.parse_args()

if args.boardsize:
	boardsize = args.boardsize
else:
	boardsize = 11

if args.time:
	time = args.time
else:
	time = 10

blackAgent = Program(args.program1, True)
whiteAgent = Program(args.program2, True)
blackAgent.sendCommand("boardsize "+str(boardsize))
whiteAgent.sendCommand("boardsize "+str(boardsize))
blackAgent.sendCommand("set_time "+str(time))
whiteAgent.sendCommand("set_time "+str(time))

game = gamestate(boardsize)
winner = None
timeout = False
moves = []
while(True):
	t = moveThread(game, blackAgent, "black")
	t.start()
	t.join(time+0.5)
	moves.append(t.move)
	if args.verbose:
		print(game)
	#if black times out white wins
	if(t.isAlive()):
		timeout = True
		winner = game.PLAYERS["white"]
		break
	if(game.winner() != game.PLAYERS["none"]):
		winner = game.winner()
		break
	t = moveThread(game, whiteAgent, "white")
	t.start()
	t.join(time+0.5)
	moves.append(t.move)
	if args.verbose:
		print(game)
	#if white times out black wins
	if(t.isAlive()):
		timeout = True
		winner = game.PLAYERS["black"]
		break
	if(game.winner() != game.PLAYERS["none"]):
		winner = game.winner()
		break

print("Game over, " + game.PLAYER_STR[winner] + " wins" + (" by timeout." if timeout else "."))
print(game)
print(" ".join(moves))


