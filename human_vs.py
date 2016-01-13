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
def get_human_move(game, human_game, color):
	human_game.set_turn(game.PLAYERS[color])
	while(True):
		print(human_game)
		move = input("Please type a move:")
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			print("valid (move was played)")
			game.play(move_to_cell(move))
			human_game.play(move_to_cell(move))
			break
		else:
			print("cell occupied (try another move)")
			opponent = game.OPPONENT[game.turn()]
			human_game.place(opponent, move_to_cell(move))
			

def move_to_cell(move):
	x =	ord(move[0].lower())-ord('a')
	y = int(move[1:])-1
	return (x,y)

parser = argparse.ArgumentParser(description="Referee a game of Kriegspiel Hex between a human and an executable agent")
parser.add_argument("program", type=str, help="executable")
parser.add_argument("--first", "-f", dest="first", action='store_const',
					const=True, default=False,
					help="human plays first (if not present default to second)")
parser.add_argument("--boardsize", "-b", type=int, help="side length of (square) board")
parser.add_argument("--time", "-t", type=int, help="total time allowed for each move in seconds")
args = parser.parse_args()

if args.boardsize:
	boardsize = args.boardsize
else:
	boardsize = 11

if args.time:
	time = args.time
else:
	time = 10

agent = Program(args.program, False)
agent.sendCommand("boardsize "+str(boardsize))
agent.sendCommand("set_time "+str(time))

human_game = gamestate(boardsize)
game = gamestate(boardsize)
winner = None

while(True):
	if(args.first):
		get_human_move(game, human_game, "black")
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
		print("waiting for opponent...")
		make_valid_move(game, agent, "white")
		print("done")
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
	else:
		print("waiting for opponent...")
		make_valid_move(game, agent, "black")
		print("done")
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
		get_human_move(game, human_game, "white")
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break


print("Game over, " + game.PLAYER_STR[winner]+" wins.")
print(game)


