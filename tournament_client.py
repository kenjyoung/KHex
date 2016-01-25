import argparse
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

#create an INET, STREAMing socket
s = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
#now connect to the web server on port 80
# - the normal http port
s.connect((server_addr, int(server_port)))