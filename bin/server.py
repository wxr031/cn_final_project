import sys
import os
import socket
import json
import hashlib
import binascii
import threading
import tempfile

online = set()
online_lock = threading.Lock()

threads = []

CMD_MAX_LEN = 16
TXT_MAX_LEN = 4096
USER_MAX_LEN = 1024
PASS_MAX_LEN = 1024
BUFF_SIZE = 4096

host = '0.0.0.0'
port = int(sys.argv[1])

auth_file = '../etc/auth.json'
auth_file_lock = threading.Lock()
hist_file = '../etc/hist.json'
hist_file_lock = threading.Lock()

msg_unsent = dict()
msg_unsent_lock = threading.Lock()

file_store = dict()
file_store_lock = threading.Lock()

def communicate(conn):
	curr_user = None
	while True:
		command = conn.recv(CMD_MAX_LEN)
		if command == b'SIGNUP':
			conn.send(b'USER&PASS')
			request = conn.recv(USER_MAX_LEN + 1 + PASS_MAX_LEN)
			username, password = tuple(request.split(b'&'))
			username = username.decode()
			password = password.decode()

			auth_file_lock.acquire()
			if not os.path.exists(auth_file):
				with open(auth_file, 'w') as fw:
					json.dump({}, fw)
			with open(auth_file, 'r') as fr:
				auth = json.load(fr)
				if username in auth:
					conn.send(b'DUP')
				else:
					auth[username] = hash_password(password)
					conn.send(b'OK')
					with open(auth_file, 'w') as fw:
						json.dump(auth, fw)
			auth_file_lock.release()

		elif command == b'SIGNIN':
			conn.send(b'USER&PASS')
			request = conn.recv(USER_MAX_LEN + 1 + PASS_MAX_LEN)
			username, password = request.split(b'&')
			username = username.decode()
			password = password.decode()

			if username in online:
				conn.send(b'ONL')
			
			else:
				auth_file_lock.acquire()
				if not os.path.exists(auth_file):
					with open(auth_file, 'w') as fw:
						json.dump({}, fw)
				with open(auth_file, 'r') as fr:
					auth = json.load(fr)
					if username in auth:
						password_hash = auth[username]
						if verify_password(password_hash, password):
							online_lock.acquire()
							online.add(username)
							online_lock.release()

							curr_user = username
							conn.send(b'OK')
							
						else:
							conn.send(b'REJ')
					else:
						conn.send(b'REJ')
				auth_file_lock.release()

		elif command == b'LOGOUT':
			conn.send(b'USER')
			username = conn.recv(USER_MAX_LEN).decode()
			online_lock.acquire()
			online.remove(username)
			online_lock.release()

		elif command == b'HISTORY':
			conn.send(b'USER')
			username = conn.recv(USER_MAX_LEN)
			username = username.decode()

			hist_file_lock.acquire()
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
			hist_file_lock.release()

		elif command == b'MESSAGE':
			conn.send(b'FROM')
			sender = conn.recv(USER_MAX_LEN).decode()
			conn.send(b'TO')
			receiver = conn.recv(USER_MAX_LEN).decode()
			conn.send(b'TEXT')
			text = conn.recv(TXT_MAX_LEN).decode().strip()

			# write message to message buffer
			msg_unsent_lock.acquire()
			if not receiver in msg_unsent:
				msg_unsent[receiver] = []
			msg_unsent[receiver].append((sender, text))
			msg_unsent_lock.release()
			
			# store message to history
			hist_file_lock.acquire()
			if not os.path.exists(hist_file):
				with open(hist_file, 'w') as fw:
					json.dump({}, fw)
			with open(hist_file, 'r') as fr:
				hists = json.load(fr)
				if not sender in hists:
					hists[sender] = []
				if not text in hists:
					hists[sender].append(text)
				with open(hist_file, 'w') as fw:
					json.dump(hists, fw)
			hist_file_lock.release()

		elif command == b'FILE':
			conn.send(b'FROM')
			sender = conn.recv(USER_MAX_LEN).decode()
			conn.send(b'TO')
			receiver = conn.recv(USER_MAX_LEN).decode()
			
			if receiver not in online:
				conn.send(b'NOT_ONLINE')
				continue

			conn.send(b'#FLE')
			file_num = int(conn.recv(CMD_MAX_LEN).decode())

			for i in range(file_num):
			
				conn.send(b'FILENAME')
				file_name = conn.recv(USER_MAX_LEN).decode()
				conn.send(b'FILESIZE')
				file_size = int(conn.recv(CMD_MAX_LEN).decode())

				conn.send(b'CONTENT')

				tmp_file = tempfile.mktemp()
				curr = 0
				with open(tmp_file, 'wb') as f:
					while curr < file_size:
						byte = conn.recv(BUFF_SIZE)
						f.write(byte)
						curr += len(byte)

				file_store_lock.acquire()
				if not receiver in file_store:
					file_store[receiver] = []
				file_store[receiver].append((sender, tmp_file, file_name, file_size))
				file_store_lock.release()

				

		elif command == b'RECEIVE':
			conn.send(b'RECEIVER')
			receiver = conn.recv(USER_MAX_LEN).decode()
			
			# messages
			msg_unsent_lock.acquire()
			if receiver in msg_unsent:
				message = msg_unsent[receiver]
				del msg_unsent[receiver]
			else:
				message = []
			message_num = len(message)
			msg_unsent_lock.release()

			# pass messages
			conn.send(b'#MSG=' + str(message_num).encode())
			for sender, text in message:
				assert conn.recv(CMD_MAX_LEN) == b'SENDER'
				conn.send(sender.encode())
				assert conn.recv(CMD_MAX_LEN) == b'TEXT'
				conn.send(text.encode())

		elif command == b'RECEIVE_FILE':
			conn.send(b'RECEIVER')
			receiver = conn.recv(USER_MAX_LEN).decode()

			# messages
			file_store_lock.acquire()
			if receiver in file_store:
				files = file_store[receiver]
				del file_store[receiver]
			else:
				files = []
			file_num = len(files)
			file_store_lock.release()

			# send files
			conn.send(b'#FILE=' + str(file_num).encode())
			for sender, tmp_file, file_name, file_size in files:
				assert conn.recv(CMD_MAX_LEN) == b'SENDER'
				conn.send(sender.encode())
				assert conn.recv(CMD_MAX_LEN) == b'FILE_NAME'
				conn.send(file_name.encode())
				assert conn.recv(CMD_MAX_LEN) == b'FILE_SIZE'
				conn.send(str(file_size).encode())

				curr = 0
				with open(tmp_file, 'rb') as f:
					while curr < file_size:
						byte = f.read(BUFF_SIZE)
						conn.send(byte)
						curr += len(byte)

		elif command == b'CLOSE':
			conn.close()
			break

		else:
			if curr_user is not None:
				online_lock.acquire()
				online.remove(curr_user)
				online_lock.release()
			break
	

def hash_password(password):
	password = password.encode()
	
	salt = os.urandom(64)
	password_hash = hashlib.pbkdf2_hmac('sha256', password, salt, 2048)
	password_hash = salt + password_hash
	return binascii.hexlify(password_hash).decode()

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

#for thread in threads:
	#thread.join()

socket.close()
