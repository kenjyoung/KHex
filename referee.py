from program import Program
import sys
import argparse
import threading
import time
from gamestate import gamestate
from tournament import *

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

blackAgent = agent(Program(args.program1, True))
whiteAgent = agent(Program(args.program2, True))
blackAgent.sendCommand("boardsize "+str(boardsize))
whiteAgent.sendCommand("boardsize "+str(boardsize))
blackAgent.sendCommand("set_time "+str(time))
whiteAgent.sendCommand("set_time "+str(time))

run_game(blackAgent, whiteAgent, boardsize, time, args.verbose)