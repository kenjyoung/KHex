from program import Program
import sys
import argparse
from gamestate import gamestate

def move_to_cell(move):
	x =	ord(move[0].lower())-ord('a')
	y = int(move[1][1:])-1
	if(x<0 or y<0 or x>=self.game.size or y>=self.game.size):
		raise ValueError("Cell out of bounds")
	return (x,y)

parser = argparse.ArgumentParser(description="Referee a game of Kriegspiel Hex between two executable agents.")
parser.add_argument("program1", type=str, help="first (black) player executable")
parser.add_argument("program2", type=str, help="second (white) player executable")
parser.add_argument("--boardsize", "-b", type=int, help="side length of (square) board.")
parser.add_argument("--time", "-t", type=int, help="total time allowed for each move in seconds.")
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
while(True):
	while(True):
		move = blackAgent.sendCommand("genmove black")
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			blackAgent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			blackAgent.sendCommand("occupied")
	if(game.winner() != game.PLAYERS["none"]):
		break
	while(True):
		move = whiteAgent.sendCommand("genmove white")
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			blackAgent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			blackAgent.sendCommand("occupied")


