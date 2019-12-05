import sys
import os
import socket
import json
import hashlib
import binascii

online = set()

USER_LEN_MAX = 1024
PASS_LEN_MAX = 1024

host = 'localhost'
port = int(sys.argv[1])

auth_file = 'auth.json'
hist_file = 'hist.json'

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
	while True:
		command = conn.recv(16)
		print(command)
		if command == b'SIGNUP':
			conn.send(b'USER&PASS')
			request = conn.recv(USER_LEN_MAX + 1 + PASS_LEN_MAX)
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
			request = conn.recv(USER_LEN_MAX + 1 + PASS_LEN_MAX)
			username, password = tuple(request.split(b'&'))
			username = username.decode('ascii')
			password = password.decode('ascii')
			if not os.path.exists(auth_file):
				with open(auth_file, 'w') as fw:
					json.dump({}, fw)
			with open(auth_file, 'r') as fr:
				auth = json.load(fr)
				password_hash = auth[username]
				if verify_password(password_hash, password):
					conn.send(b'OK')
				else:
					conn.send(b'REJ')
			
		#elif command == b'HISTORY':
			#conn.send(b'USER')
			#username = conn.recv(USER_LEN_MAX)
			#username = username.decode('ascii')
			#if not os.path.exists(hist_file):
				#with open(hist_file, 'w') as fw:
					#json.dump({}, fw)
			#with open(hist_file, 'r') as fr:
				#hists = json.load(fr)[username]
				#conn.send(json.dumps(hist))
				


		elif command == b'CLOSE':
			conn.close()
			break

socket.close()
