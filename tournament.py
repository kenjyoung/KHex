import argparse
from program import Program
import threading
import time
from gamestate import gamestate
import sys

def make_valid_move(game, agent, color, timeout_flag):
	move = agent.sendCommand("genmove "+color)
	if(timeout_flag[0]):
		return move
	while(True):
		if(game.cell_color(move_to_cell(move))==game.PLAYERS["none"]):
			agent.sendCommand("valid")
			game.play(move_to_cell(move))
			break
		else:
			move = agent.sendCommand("occupied")
			if(timeout_flag[0]):
				break
	return move

class moveThread(threading.Thread):
	def __init__(self, game, agent, color):
		threading.Thread.__init__(self)
		self.game = game
		self.agent = agent
		self.color = color
		self.move = "x"
		self.timeout_flag = [False]
	def run(self):
		try:
			self.move = make_valid_move(self.game, self.agent, self.color, self.timeout_flag).strip()
		except Program.Died:
			pass

class agent:
	def __init__(self, exe):
		self.exe = exe 
		self.program = Program(self.exe, True)
		self.name = self.program.sendCommand("name").strip()
		self.lock  = threading.Lock()

	def sendCommand(self, command):
		self.lock.acquire()
		answer = self.program.sendCommand(command)
		self.lock.release()
		return answer

	def reconnect(self):
		self.program.terminate()
		self.program = Program(self.exe,True)
		self.lock = threading.Lock()


class web_agent:
	"""
	Provide an interface to a socket connected to a Khex agent
	which looks like an ordinary Khex agent.
	"""
	def __init__(self, client):
		self.client = client
		self.name = self.sendCommand("name").strip()
		self.lock = threading.Lock()

	def sendCommand(self, command):
		self.lock.acquire()
		totalsent = 0
		while totalsent < len(command):
			sent = self.client.send(bytes(command[totalsent:],'UTF-8'))
			if sent == 0:
				self.lock.release()
				raise RuntimeError("client disconnected")
			totalsent += sent
		command = ''
		bytes_recd = 0
		while True:
		    chunk=self.client.recv(2048)
		    if chunk == b'':
		    	self.lock.release()
		    	raise RuntimeError("client disconnected")
		    command+=chunk.decode('UTF-8')
		    if(chunk[-1]!='\n'):
		    	break
		self.lock.release()
		return command

	def reconnect(self):
		#defined for interface compatibility
		pass


def move_to_cell(move):
	x =	ord(move[0].lower())-ord('a')
	y = int(move[1:])-1
	return (x,y)

def make_names_unique(clients):
	for client_1 in clients:
		for client_2 in clients:
			if(client_1 != client_2 and client_1.name == client_2.name):
				client_2.name = client_2.name+"I"


def run_game(blackAgent, whiteAgent, boardsize, time, verbose = False):
	game = gamestate(boardsize)
	time = time
	winner = None
	timeout = False
	moves = []
	blackAgent.sendCommand("clear_board")
	whiteAgent.sendCommand("clear_board")
	while(True):
		t = moveThread(game, blackAgent, "black")
		t.start()
		t.join(time+0.5)
		moves.append(t.move)
		if verbose:
			print(blackAgent.name+" v.s. "+whiteAgent.name)
			print(game)
		#if black times out white wins
		if(t.isAlive()):
			timeout = True
			t.timeout_flag[0] = True
			winner = game.PLAYERS["white"]
			blackAgent.reconnect()
			blackAgent.sendCommand("boardsize "+str(boardsize))
			blackAgent.sendCommand("set_time "+str(time))
			break
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
		sys.stdout.flush()
		t = moveThread(game, whiteAgent, "white")
		t.start()
		t.join(time+0.5)
		moves.append(t.move)
		if verbose:
			print(blackAgent.name+" v.s. "+whiteAgent.name)
			print(game)
		#if white times out black wins
		if(t.isAlive()):
			timeout = True
			t.timeout_flag[0] = True
			winner = game.PLAYERS["black"]
			whiteAgent.reconnect()
			whiteAgent.sendCommand("boardsize "+str(boardsize))
			whiteAgent.sendCommand("set_time "+str(time))
			break
		if(game.winner() != game.PLAYERS["none"]):
			winner = game.winner()
			break
		sys.stdout.flush()
	winner_name = blackAgent.name if winner == game.PLAYERS["black"] else whiteAgent.name
	loser_name =  whiteAgent.name if winner == game.PLAYERS["black"] else blackAgent.name
	print("Game over, " + winner_name+ " ("+game.PLAYER_STR[winner]+") " + "wins against "+loser_name+(" by timeout." if timeout else "."))
	print(game)
	print(" ".join(moves))
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
					win_lose = self.stats[agent1][agent2]
					entry = str(win_lose[0])+", "+str(win_lose[1])
				else:
					entry = 'x'*(entry_size-2)+'  '
				print(entry+" "*(entry_size-len(entry)),end="")
			print()

	def print_winrate(self):
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
					win_lose1 = self.stats[agent1][agent2]
					win_lose2 = self.stats[agent2][agent1]
					wins = win_lose1[0]+win_lose2[1]
					loses = win_lose1[1]+win_lose2[0]
					entry = str(wins/float(wins+loses)*100)[0:5]+"%"
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