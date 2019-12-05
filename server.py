import sys
import os
import socket
import json
import hashlib
import binascii
import threading

online = {}
threads = []

CMD_MAX_LEN = 16
TXT_MAX_LEN = 4096
USER_MAX_LEN = 1024
PASS_MAX_LEN = 1024

host = 'localhost'
port = int(sys.argv[1])

auth_file = 'auth.json'
hist_file = 'hist.json'

def communicate(conn):
	while True:
		command = conn.recv(CMD_MAX_LEN)
		if command == b'SIGNUP':
			conn.send(b'USER&PASS')
			request = conn.recv(USER_MAX_LEN + 1 + PASS_MAX_LEN)
			username, password = tuple(request.split(b'&'))
			username = username.decode('ascii')
			password = password.decode('ascii')
			if not os.path.exists(auth_file):
				with open(auth_file, 'w') as fw:
					json.dump({}, fw)
			with open(auth_file, 'r') as fr:
				auth = json.load(fr)
				print(auth)
				if username in auth:
					conn.send(b'DUP')
				else:
					auth[username] = hash_password(password)
					conn.send(b'OK')
					with open(auth_file, 'w') as fw:
						json.dump(auth, fw)

		elif command == b'SIGNIN':
			conn.send(b'USER&PASS')
			request = conn.recv(USER_MAX_LEN + 1 + PASS_MAX_LEN)
			username, password = request.split(b'&')
			username = username.decode('ascii')
			password = password.decode('ascii')
			print(username, password)
			if not os.path.exists(auth_file):
				with open(auth_file, 'w') as fw:
					json.dump({}, fw)
			with open(auth_file, 'r') as fr:
				auth = json.load(fr)
				if username in auth:
					password_hash = auth[username]
					if verify_password(password_hash, password):
						conn.send(b'OK')
						print(conn.getpeername())
						
					else:
						conn.send(b'REJ')
				else:
					conn.send(b'REJ')
			
		elif command == b'HISTORY':
			conn.send(b'USER')
			username = conn.recv(USER_MAX_LEN)
			username = username.decode('ascii')
			if not os.path.exists(hist_file):
				with open(hist_file, 'w') as fw:
					json.dump({}, fw)
			with open(hist_file, 'r') as fr:
				hists = json.load(fr)
				if username in hists:
					history = hists[username]
					conn.send(json.dumps(history).encode())
				else:
					conn.send(json.dumps([]).encode())

		elif command == b'MESSAGE':
			conn.send(b'FROM')
			sender = conn.recv(USER_MAX_LEN).decode('ascii')
			conn.send(b'TO')
			reveicer = conn.recv(USER_MAX_LEN).decode('ascii')
			conn.send(b'TEXT')
			text = conn.recv(TXT_MAX_LEN).decode('ascii')
			
			# store message to history
			if not os.path.exists(hist_file):
				with open(hist_file, 'w') as fw:
					json.dump({}, fw)
			with open(hist_file, 'r') as fr:
				hists = json.load(fr)
				if not sender in hists:
					hists[sender] = []
				hists[sender].append()
				with open(auth_file, 'w') as fw:
					json.dump(hists, fw)

		elif command == b'CLOSE':
			conn.close()
			break
	

def hash_password(password):
	password = password.encode()
	
	salt = os.urandom(64)
	password_hash = hashlib.pbkdf2_hmac('sha256', password, salt, 2048)
	password_hash = salt + password_hash
	return binascii.hexlify(password_hash).decode('ascii')

def verify_password(password_hash, password):
	password_hash = binascii.unhexlify(password_hash)
	password = password.encode()

	salt = password_hash[:64]
	password_hash_verify = hashlib.pbkdf2_hmac('sha256', password, salt, 2048)
	return password_hash_verify == password_hash[64:]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(5)
while True:
	conn, (host, port) = server.accept()
	thread = threading.Thread(target = communicate, args = (conn,))
	threads.append(thread)
	thread.start()

for thread in threads:
	thread.join()

socket.close()
