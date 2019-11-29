import sys
import os
import socket
import dbm
import hashlib
import binascii

online = set()

host = 'localhost'
port = int(sys.argv[1])

def hash_password(password):
	password = password.encode()
	
	salt = os.urandom(64)
	password_hash = hashlib.pbkdf2_hmac('sha256', password, salt, 2048)
	password_hash = salt + password_hash
	return binascii.hexlify(password_hash)

def verify_password(password_hash, password):
	password_hash = binascii.unhexlify(password_hash)
	password = password.encode()

	salt = password_hash[:64]
	password_hash_verify = hashlib.pbkdf2_hmac('sha256', password, salt, 2048)
	return password_hash_verify == password_hash[64:]

	

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((host, port))
	server.listen(5)
	while True:
		conn, (host, port) = server.accept()
		with conn:
			while True:
				online.add((host, port))
				command = conn.recv(16)
				if command == b'REGISTER':
					conn.send(b'USER&PASS')
					request = conn.recv(2049)
					username, password = tuple(request.split(b'&'))
					username = username.decode('ascii')
					password = password.decode('ascii')
					with dbm.open('auth', 'c') as db:
						try:
							db[username]
							conn.send(b'DUP')
						except KeyError:
							db[username] = hash_password(password)
							conn.send(b'OK')
