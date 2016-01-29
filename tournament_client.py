import argparse
from program import Program
import socket
"""
Some socket code taken from https://docs.python.org/2/howto/sockets.html, authored by Gordon McMillan."
"""

parser = argparse.ArgumentParser(description="Client for interfacing a single KHex agent with a tournament server.")
parser.add_argument("server_addr", type=str, help="network address of server.")
parser.add_argument("server_port", type=int, help="port of server.")
parser.add_argument("program" , type=str, help="program to be connected.")

args = parser.parse_args()

server_addr = args.server_addr
server_port = args.server_port

s = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

s.connect((server_addr, int(server_port)))

agent = Program(args.program, True)

while(True):
	command = ''
	bytes_recd = 0
	while True:
	    chunk = s.recv(2048)
	    if chunk == b'':
	        raise RuntimeError("Connection to server lost")
	    command+=chunk.decode('UTF-8')
	    if(chunk[-1]!='\n'):
	    	break
	response = agent.sendCommand(command)
	totalsent=0
	while totalsent < len(response):
		sent = s.send(bytes(response[totalsent:],'UTF-8'))
		if sent == 0:
			raise RuntimeError("client disconnected")
		totalsent += sent
	bytes_recd = 0





