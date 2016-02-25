import argparse
import socket
import threading
import time
from tournament import *
from gamestate import gamestate
import sys
"""
Some socket code taken from https://docs.python.org/2/howto/sockets.html, authored by Gordon McMillan."
"""

parser = argparse.ArgumentParser(description="Server for running a tournament between several Khex clients.")
parser.add_argument("num_clients", type=int, help="number of agents in tournament.")
parser.add_argument("num_games", type=int, help="number of *pairs* of games (one as black, one as white) to play between each pair of agents.")
parser.add_argument("--boardsize", "-b", type=int, help="side length of (square) board.")
parser.add_argument("--time", "-t", type=int, help="total time allowed for each move in seconds.")
parser.add_argument("--port", "-p", type=int, help="specify which port to open socket on.")
args = parser.parse_args()

if args.boardsize:
	boardsize = args.boardsize
else:
	boardsize = 11

if args.time:
	time = args.time
else:
	time = 10

if args.port:
	port = args.port
else:
	port = 1235

num_clients = args.num_clients
if(num_clients<2):
	print('Need at least two programs for a tournament')
	exit(1)
num_games = args.num_games

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = socket.gethostname()
serversocket.bind((address, port))

clients=[]

serversocket.listen(5)
print("server address: "+socket.gethostbyname(socket.gethostname())+":"+str(port))

while len(clients)<num_clients:
    (clientsocket, address) = serversocket.accept()
    clients.append(web_agent(clientsocket))

print("Client quota reached, starting tournament...")
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