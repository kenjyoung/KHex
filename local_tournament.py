import argparse
from program import Program
import threading
import time
from gamestate import gamestate
import sys
from tournament import *

parser = argparse.ArgumentParser(description="Server for running a tournament between several Khex clients.")
parser.add_argument("client_list", type=str, help="file containing newline seperated list of executable agents.")
parser.add_argument("num_games", type=int, help="number of *pairs* of games (one as black, one as white) to play between each pair of agents.")
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

client_list = args.client_list
num_games = args.num_games

with open(client_list) as f:
	client_exes = f.readlines()

clients = []
for exe in client_exes:
	clients.append(agent(Program(exe, True)))

if(len(clients)<2):
	print('Need at least two programs for a tournament')
	exit(1)


print("Starting tournament...")
for client in clients:
	client.sendCommand("boardsize "+str(boardsize))
	client.sendCommand("set_time "+str(time))

#win_stats[client_1][client_2] = (number of client_1 wins as black against client_2, number of client_1 losses as black against client_2)
make_names_unique(clients)
stats = win_stats(clients)


for game in range(num_games):
	for client_1 in clients:
		for client_2 in clients:
			if(client_1.name!=client_2.name):
				winner = run_game(client_1, client_2, boardsize, time)
				stats.add_outcome(client_1, client_2, winner)
				stats.print_stats()
				sys.stdout.flush()
print("Tournament Complete")
print("Final win statistics:")
stats.print_stats()
print()
stats.print_winrate()