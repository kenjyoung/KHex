from program import Program
import sys
import argparse
from gamestate import gamestate

def move_to_cell(move):
	x =	ord(move[0].lower())-ord('a')
	y = int(move[1:])-1
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
#TODO: implement time control
while(True):
	move = blackAgent.sendCommand("genmove black")
	while(True):
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			blackAgent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			move = blackAgent.sendCommand("occupied")
	if(game.winner() != game.PLAYERS["none"]):
		break
	move = whiteAgent.sendCommand("genmove white")
	while(True):
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			whiteAgent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			move = whiteAgent.sendCommand("occupied")
	if(game.winner() != game.PLAYERS["none"]):
		break


