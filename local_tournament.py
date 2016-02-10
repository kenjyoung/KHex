import argparse
from program import Program
import threading
import time
from gamestate import gamestate
import sys

def make_valid_move(game, agent, color):
	move = agent.sendCommand("genmove "+color)
	while(True):
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			agent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			move = agent.sendCommand("occupied")

class moveThread(threading.Thread):
	def __init__(self, game, agent, color):
		threading.Thread.__init__(self)
		self.game = game
		self.agent = agent
		self.color = color
	def run(self):
		make_valid_move(self.game, self.agent, self.color)

class agent:
	def __init__(self, program):
		self.name = program.sendCommand("name").strip()
		self.program = program
	def sendCommand(self, command):
		return self.program.sendCommand(command)


def move_to_cell(move):
	x =	ord(move[0].lower())-ord('a')
	y = int(move[1:])-1
	return (x,y)

def make_names_unique(clients):
	for client_1 in clients:
		for client_2 in clients:
			if(client_1 != client_2 and client_1.name == client_2.name):
				client_2.name = client_2.name+"I"


def run_game(blackAgent, whiteAgent, boardsize, time):
	game = gamestate(boardsize)
	winner = None
	timeout = False
	blackAgent.sendCommand("clear_board")
	whiteAgent.sendCommand("clear_board")
	while(True):
		t = moveThread(game, blackAgent, "black")
		t.start()
		t.join(time+0.5)
		#if black times out white wins
		if(t.isAlive()):
			timeout = True
			winner = game.PLAYERS["white"]
			break
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
		sys.stdout.flush()
		t = moveThread(game, whiteAgent, "white")
		t.start()
		t.join(time+0.5)
		#if white times out black wins
		if(t.isAlive()):
			timeout = True
			winner = game.PLAYERS["black"]
			break
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
		sys.stdout.flush()
	winner_name = blackAgent.name if winner == game.PLAYERS["white"] else whiteAgent.name
	print("Game over, " + winner_name+ " ("+game.PLAYER_STR[winner]+") " + "wins" + (" by timeout." if timeout else "."))
	print(game)
	return winner

class win_stats:
	def __init__(self, clients):
		self.stats = {}
		for client_1 in clients:
			for client_2 in clients:
				if(client_1!=client_2):
					if(not client_1.name in self.stats):
						self.stats[client_1.name] = {}
					self.stats[client_1.name][client_2.name] = [0,0]

	def print_stats(self):
		agents = self.stats.keys()
		entry_size = max(max([len(x) for x in agents])+2,8)
		print(" "*entry_size, end="")
		for agent in agents:
			print(agent+" "*(entry_size-len(agent)), end="")
		print()
		for agent1 in agents:
			print(agent1+" "*(entry_size-len(agent1)), end="")
			for agent2 in agents:
				if(agent1!=agent2):
					win_lose = self.stats[agent2][agent1]
					entry = str(win_lose[0])+", "+str(win_lose[1])
				else:
					entry = 'x'*(entry_size-2)+'  '
				print(entry+" "*(entry_size-len(entry)),end="")
			print()


	def add_outcome(self, blackAgent, whiteAgent, winner):
		if(not (self.stats[blackAgent.name] and self.stats[blackAgent.name][whiteAgent.name])):
			raise ValueError("Unknown agent.")
		if(winner == gamestate.PLAYERS["black"]):
			#increment wins
			self.stats[blackAgent.name][whiteAgent.name][0]+=1
		else:
			#increment loses
			self.stats[blackAgent.name][whiteAgent.name][1]+=1

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