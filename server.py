import sys
import socket

online = set()

host = 'localhost'
port = int(sys.argv[0])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)

while True:
	conn, (host, port) = server.accept()
	online.add((host, port))
