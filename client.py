import json
import os
import random
import sys
import socket
import tempfile
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as st
from tkinter import messagebox
from tkinter import CENTER, NORMAL, DISABLED, END, INSERT
from tkinter.filedialog import askopenfilename

CMD_MAX_LEN = 16
TXT_MAX_LEN = 4096
USER_MAX_LEN = 1024
PASS_MAX_LEN = 1024
BUFF_SIZE = 4096

client = None
current_user = None

send_files = []

n_message = 0
messages = []
files = []

infos = []
file_infos = []

def port_in_use(port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		return sock.connect_ex(('localhost', port)) == 0

def connect():
	global client
	
	if connect_button['text'] == 'Disconnect':
		client.send(b'CLOSE')
		client.close()

		host_input['state'] = NORMAL
		port_input['state'] = NORMAL
		
		connect_button['text'] = 'Connect'
		status_text['text'] = ''

		register_button['text'] = 'Submit'
		username_input['state'] = NORMAL
		password_input['state'] = NORMAL
		sign_in_up_button['state'] = NORMAL

		tabs.tab(1, state = DISABLED)
		tabs.tab(2, state = DISABLED)
		tabs.tab(3, state = DISABLED)

	else:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		if len(host_var.get()) == 0 or len(port_var.get()) == 0:
			status_text['text'] = 'Please provide host and port'
			status_text['fg'] = 'red'
			return

		host = host_var.get()
		
		# check if the port value is a valid integer
		try:
			port = int(port_var.get())
		except:
			status_text['text'] = 'Invalid port number'
			status_text['fg'] = 'red'
			return

		if port < 0 or port > 65535:
			status_text['text'] = 'Invalid port number'
			status_text['fg'] = 'red'
			return
	
		try:
			client.connect((host, port))
		except:
			status_text['text'] = 'Cannot connect to {}:{}'.format(host, port)
			status_text['fg'] = 'red'
			return

		status_text['text'] = 'Connection to {}:{} established'.format(host, port)
		status_text['fg'] = 'green'
		connect_button['text'] = 'Disconnect'
		host_input['state'] = DISABLED
		port_input['state'] = DISABLED
		tabs.tab(1, state = NORMAL)

def signup():
	username = username_input.get()
	password = password_input.get()
	password_validation = password_validation_input.get()

	if len(username) == 0 or len(password) == 0:
		messagebox.showerror('', 'Please provide username and password')
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return
	
	if len(username) > 1024 or len(password) > 1024:
		messagebox.showerror('', 'username and password must be less than 1024 characters')
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return
	
	if password != password_validation:
		messagebox.showerror('', 'Password double confirmation failed. Please enter your password again')
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return

	if not username.isalnum() or not password.isalnum():
		messagebox.showerror('', 'username and password must only contains alphanumeric values')
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return
	
	client.send(b'SIGNUP')

	response = client.recv(CMD_MAX_LEN)
	assert response == b'USER&PASS'
	
	client.send(username.encode() + b'&' + password.encode())
	response = client.recv(CMD_MAX_LEN)
	if response == b'OK':
		messagebox.showinfo('', 'Registration OK')
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)

	elif response == b'DUP':
		messagebox.showerror('', 'Username already exist')
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)

def signin():
	
	global current_user
	global infos
	global messages
	global files
	global file_infos
	global n_message

	if register_button['text'] == 'Logout':

		client.send(b'LOGOUT')
		assert client.recv(CMD_MAX_LEN) == b'USER'
		client.send(current_user.encode())

		register_button['text'] = 'Submit'
		username_input['state'] = NORMAL
		password_input['state'] = NORMAL
		sign_in_up_button['state'] = NORMAL

		message_text.delete(1.0, END)
		files = []
		messages = []
		infos = []
		file_infos = []
		n_message = 0

		tabs.tab(0, state = NORMAL)
		tabs.tab(2, state = DISABLED)
		tabs.tab(3, state = DISABLED)
		tabs.tab(4, state = DISABLED)
		tabs.tab(5, state = DISABLED)

	else:

		username = username_input.get()
		password = password_input.get()

		current_user = username

		client.send(b'SIGNIN')

		response = client.recv(CMD_MAX_LEN)
		assert response == b'USER&PASS'

		client.send(username.encode() + b'&' + password.encode())
		response = client.recv(CMD_MAX_LEN)

		if response == b'OK':
			messagebox.showinfo('', 'Login OK')

			# Change UI
			username_input.delete(0, END)
			password_input.delete(0, END)
			register_button['text'] = 'Logout'
			username_input['state'] = DISABLED
			password_input['state'] = DISABLED
			sign_in_up_button['state'] = DISABLED

			tabs.tab(0, state = DISABLED)
			tabs.tab(2, state = NORMAL)
			tabs.tab(3, state = NORMAL)
			tabs.tab(4, state = NORMAL)
			tabs.tab(5, state = NORMAL)

		elif response == b'REJ':
			messagebox.showerror('', 'Invalid username/password')
			username_input.delete(0, END)
			password_input.delete(0, END)
			current_user = None

		elif response == b'ONL':
			messagebox.showerror('', 'User already online')
			username_input.delete(0, END)
			password_input.delete(0, END)
			current_user = None
	

def sign_in_up_toggle():
	if sign_in_up_button['text'] == 'Sign In':
		register_title['text'] = 'Sign In'
		register_button['command'] = signin
		sign_in_up_title['text'] = 'Don\'t have an account?' 
		sign_in_up_button['text'] = 'Sign Up'
		sign_in_up_button.place(relx = 0.65, rely = 0.8, anchor = CENTER)
		register_button.place(relx = 0.5, rely = 0.6, anchor = CENTER)
		password_validation_input.place_forget()
		password_validation_image_label.place_forget()
	
	elif sign_in_up_button['text'] == 'Sign Up':
		register_title['text'] = 'Sign Up'
		register_button['command'] = signup
		sign_in_up_title['text'] = 'Have an account?' 
		sign_in_up_button['text'] = 'Sign In'
		sign_in_up_button.place(relx = 0.6, rely = 0.8, anchor = CENTER)
		register_button.place(relx = 0.5, rely = 0.7, anchor = CENTER)
		password_validation_input.place(relx = 0.5, rely = 0.6, anchor = CENTER)
		password_validation_image_label.place(relx = 0.35, rely = 0.6, anchor = CENTER)
		
def get_history(_):
	client.send(b'HISTORY')
	assert client.recv(CMD_MAX_LEN) == b'USER'
	client.send(current_user.encode())
	hist_json = client.recv(TXT_MAX_LEN)
	history = json.loads(hist_json)
	history_combo['values'] = tuple(history)

def set_message(_):
	text = history_combo.get()
	message_text.delete(1.0, END)
	message_text.insert(INSERT, text)
	message_text.insert(END, '')


def messaging():
	receiver = receiver_input.get()
	text = message_text.get(1.0, END)

	if len(receiver) == 0:
		messagebox.showerror('', 'Please provide receiver')
		return
	
	if len(text) == 0:
		messagebox.showerror('', 'Please provide text')
		return
	
	if receiver == current_user:
		messagebox.showerror('', 'Please don\'t send message to yourself')
		return

	client.send(b'MESSAGE')
	assert client.recv(CMD_MAX_LEN) == b'FROM'
	client.send(current_user.encode())
	assert client.recv(CMD_MAX_LEN) == b'TO'
	client.send(receiver.encode())
	assert client.recv(CMD_MAX_LEN) == b'TEXT'
	client.send(text.encode())

	messagebox.showinfo('', 'Message sent')

def receiving(_):

	global n_message
	
	client.send(b'RECEIVE')
	assert client.recv(CMD_MAX_LEN) == b'RECEIVER'
	client.send(current_user.encode())
	client_info = client.recv(CMD_MAX_LEN)
	command, message_num = client_info.split(b'=')
	assert command == b'#MSG'
	message_num = int(message_num.decode())

	for i in range(message_num):
		client.send(b'SENDER')
		sender = client.recv(USER_MAX_LEN).decode()
		client.send(b'TEXT')
		text = client.recv(TXT_MAX_LEN).decode()

		n_message += 1
		message_info = 'Message #{0} From {1}'.format(n_message, sender)
		message_formatted = 'From: {0}\nTo: {1}\n\n{2}'.format(sender, current_user, text)
		infos.append(message_info)
		messages.append(message_formatted)
	
	receiving_combo['values'] = infos

def get_message(_):
	index = receiving_combo.current()
	receiving_text['state'] = NORMAL
	receiving_text.delete(1.0, END)
	receiving_text.insert(INSERT, messages[index])
	receiving_text.insert(END, '')
	receiving_text['state'] = DISABLED

def add_file():
	global send_files
	file_name = askopenfilename()
	if file_name in send_files:
		send_files.remove(file_name)
	send_files.append(file_name)
	messagebox.showinfo('', 'File Added')
	file_message = ', '.join(send_files[-2:])
	if len(send_files) > 2:
		file_message += ' ...'
	file_show_table['text'] = file_message
	file_show_table.place(relx = 0.5, rely = 0.8, anchor = CENTER)


def del_file():
	global send_files
	send_files = []
	file_show_table['text'] = ''
	file_show_table.place(relx = 0.5, rely = 0.8, anchor = CENTER)
	messagebox.showwarning('', 'Files deleted')

def file_send():
	global send_files
	
	receiver = file_receiver_input.get()
	print(receiver)

	if len(receiver) == 0:
		messagebox.showerror('', 'Please provide receiver')
		return

	if len(send_files) == 0:
		messagebox.showerror('', 'Please provide at least one file')
		return
	
	if receiver == current_user:
		messagebox.showerror('', 'Please don\'t send file to toyourself')
		return
	
	print(send_files)

	for file_name in send_files:
		if not os.path.exists(file_name):
			messagebox.showerror('', 'File {0} does not exist'.format(file_name))
			return
		
		try:
			f = open(file_name, 'rb')
			f.close()
		except:
			messagebox.showerror('', 'Unable to open the file {0}'.format(file_name))
			return

	client.send(b'FILE')
	assert client.recv(CMD_MAX_LEN) == b'FROM'
	client.send(current_user.encode())
	assert client.recv(CMD_MAX_LEN) == b'TO'
	client.send(receiver.encode())
	res = client.recv(CMD_MAX_LEN)

	if res == b'NOT_ONLINE':
		messagebox.showerror('', 'User not online')
		return
	
	assert res == b'#FLE'
	client.send(str(len(send_files)).encode())
	
	for file_name in send_files:
		file_size = os.path.getsize(file_name)

		assert client.recv(CMD_MAX_LEN) == b'FILENAME'
		client.send(file_name.encode())
		assert client.recv(CMD_MAX_LEN) == b'FILESIZE'
		client.send(str(file_size).encode())
		assert client.recv(CMD_MAX_LEN) == b'CONTENT'
		
		curr = 0
		with open(file_name, 'rb') as f:
			while curr < file_size:
				byte = f.read(BUFF_SIZE)
				client.send(byte)
				curr += len(byte)
	
	messagebox.showinfo('', 'File sent')
	send_files = []
	file_show_table['text'] = ''

	
def file_recv(_):

	client.send(b'RECEIVE_FILE')
	assert client.recv(CMD_MAX_LEN) == b'RECEIVER'
	client.send(current_user.encode())
	client_info = client.recv(CMD_MAX_LEN)
	command, file_num = client_info.split(b'=')
	assert command == b'#FILE'
	file_num = int(file_num.decode())
	print('file num = ' + str(file_num))

	for i in range(file_num):
		client.send(b'SENDER')
		sender = client.recv(USER_MAX_LEN).decode()
		client.send(b'FILE_NAME')
		file_name = client.recv(TXT_MAX_LEN).decode()
		client.send(b'FILE_SIZE')
		file_size = client.recv(CMD_MAX_LEN).decode()
		file_size = int(file_size)

		message_info = 'File {0} From {1}'.format(file_name, sender)
		file_infos.append(message_info)
		tmp_file = tempfile.mktemp()
		print(tmp_file)
		
		curr = 0
		with open(tmp_file, 'wb') as f:
			while curr < file_size:
				byte = client.recv(BUFF_SIZE)
				print(byte)
				f.write(byte)
				curr += len(byte)

		files.append((tmp_file, file_size))

	file_recv_combo['values'] = file_infos
	

def get_file_name(_):
	index = file_recv_combo.current()
	file_recv_text['state'] = NORMAL
	file_recv_text.delete(1.0, END)

	tmp_file, file_size = files[index]
	curr = 0
	with open(tmp_file, 'rb') as f:
		while curr < file_size:
			byte = f.read(BUFF_SIZE)
			file_recv_text.insert(INSERT, byte)
			print(byte)
			curr += len(byte)
	file_recv_text.insert(END, '')
	file_recv_text['state'] = DISABLED
	
def tab_switching(event):
	
	global receiving_combo

	clicked_tab = tabs.index(tabs.select())
	print(clicked_tab)

	if clicked_tab == tabs.index(tab_register):
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input['text'] = ''

	elif clicked_tab == tabs.index(tab_messaging):
		receiver_input.delete(0, END)
		history_combo['values'] = ('---history---')
		history_combo.current(0)
		message_text.delete(1.0, END)

	elif clicked_tab == tabs.index(tab_receiving):
		receiving_combo['values'] = ()
		receiving_text['state'] = NORMAL
		receiving_text.delete(1.0, END)
		receiving_text['state'] = DISABLED
	
	elif clicked_tab == tabs.index(tab_file_send):
		file_receiver_input.delete(0, END)
		file_show_table['text'] = ''
		send_files = []
	
	elif clicked_tab == tabs.index(tab_file_recv):
		file_recv_combo['values'] = ()
		file_recv_text['state'] = NORMAL
		file_recv_text.delete(1.0, END)
		file_recv_text['state'] = DISABLED
		
# main window
window = tk.Tk()
window.title('CN Message')
window.geometry('1024x768')

# Tabs
tabs = ttk.Notebook(window)
tab_home = ttk.Frame(tabs)
tab_register = ttk.Frame(tabs)
tab_messaging = ttk.Frame(tabs)
tab_receiving = ttk.Frame(tabs)
tab_file_send = ttk.Frame(tabs)
tab_file_recv = ttk.Frame(tabs)
tabs.add(tab_home, text = 'Home')
tabs.add(tab_register, text = 'Registration', state = DISABLED)
tabs.add(tab_messaging, text = 'Messaging', state = DISABLED)
tabs.add(tab_receiving, text = 'Receiving', state = DISABLED)
tabs.add(tab_file_send, text = 'File Transmission', state = DISABLED)
tabs.add(tab_file_recv, text = 'File Receiving', state = DISABLED)

# User Interface

# Home Page
home_title = tk.Label(tab_home, text = 'CN Message', font = ('Inconsolata', 48, 'bold'))
home_title.place(relx = 0.5, rely = 0.2, anchor = CENTER)

host_label = tk.Label(tab_home, text = 'Host', font = ('Inconsolata', 24))
host_label.place(relx = 0.3, rely = 0.425, anchor = CENTER)
port_label = tk.Label(tab_home, text = 'Port', font = ('Inconsolata', 24))
port_label.place(relx = 0.7, rely = 0.425, anchor = CENTER)

host_var = tk.StringVar()
port_var = tk.StringVar()

host_input = tk.Entry(tab_home, width = 12, bd = 3, textvariable = host_var, font = ('Inconsolata', 18))
host_input.place(relx = 0.3, rely = 0.5, anchor = CENTER)

port_input = tk.Entry(tab_home, width = 12, bd = 3, textvariable = port_var, font = ('Inconsolata', 18))
port_input.place(relx = 0.7, rely = 0.5, anchor = CENTER)

column = tk.Label(tab_home, text = ':', font = ('Inconsolata', 24))
column.place(relx = 0.5, rely = 0.5, anchor = CENTER)

status_text = tk.Label(tab_home, text = '', font = ('Inconsolata', 16, 'bold'))
status_text.place(relx = 0.5, rely = 0.8, anchor = CENTER)

connect_button = tk.Button(tab_home, text = 'Connect', command = connect, font = ('Inconsolata', 24, 'bold'))
connect_button.place(relx = 0.5, rely = 0.65, anchor = CENTER)

# Registration
register_title = tk.Label(tab_register, text = 'Sign Up', font = ('Inconsolata', 36, 'bold'))
register_title.place(relx = 0.5, rely = 0.2, anchor = CENTER)

username_image = tk.PhotoImage(file = './images/username.png')
username_image_label = tk.Label(tab_register, image = username_image)
username_image_label.place(relx = 0.35, rely = 0.4, anchor = CENTER)
username_input = tk.Entry(tab_register, width = 32, bd = 3)
username_input.focus()
username_input.place(relx = 0.5, rely = 0.4, anchor = CENTER)

password_image = tk.PhotoImage(file = './images/password.png')
password_image_label = tk.Label(tab_register, image = password_image)
password_image_label.place(relx = 0.35, rely = 0.5, anchor = CENTER)
password_input = tk.Entry(tab_register, width = 32, bd = 3, show = '*')
password_input.place(relx = 0.5, rely = 0.5, anchor = CENTER)

password_validation_image = tk.PhotoImage(file = './images/check.png')
password_validation_image_label = tk.Label(tab_register, image = password_validation_image)
password_validation_image_label.place(relx = 0.35, rely = 0.6, anchor = CENTER)
password_validation_input = tk.Entry(tab_register, width = 32, bd = 3, show = '*')
password_validation_input.place(relx = 0.5, rely = 0.6, anchor = CENTER)

register_button = tk.Button(tab_register, text = 'Submit', command = signup, font = ('Inconsolata', 24, 'bold'))
register_button.place(relx = 0.5, rely = 0.7, anchor = CENTER)

sign_in_up_title = tk.Label(tab_register, text = 'Have an account?', font = ('Inconsolata', 18))
sign_in_up_title.place(relx = 0.4, rely = 0.8, anchor = CENTER)

sign_in_up_button = tk.Button(tab_register, text = 'Sign In', command = sign_in_up_toggle, font = ('Inconsolata', 16, 'bold'))
sign_in_up_button.place(relx = 0.6, rely = 0.8, anchor = CENTER)


# Messaging
messaging_title = tk.Label(tab_messaging, text = 'Messaging', font = ('Inconsolata', 32, 'bold'))
messaging_title.place(relx = 0.5, rely = 0.15, anchor = CENTER)

receiver_label = tk.Label(tab_messaging, text = 'Send to : ', font = ('Inconsolata', 24))
receiver_label.place(relx = 0.15, rely = 0.25, anchor = CENTER)
receiver_input = tk.Entry(tab_messaging, width = 48, bd = 3, font = ('Inconsolata', 18))
receiver_input.place(relx = 0.6, rely = 0.25, anchor = CENTER)

history_label = tk.Label(tab_messaging, text = 'Send to : ', font = ('Inconsolata', 24))
history_label.place(relx = 0.15, rely = 0.25, anchor = CENTER)
history_combo = ttk.Combobox(tab_messaging, width = 48, state = 'readonly', font = ('Inconsolata', 18))
history_combo['values'] = ('---history---')
history_combo.current(0)
history_combo.bind('<Button-1>', get_history)
history_combo.bind('<<ComboboxSelected>>', set_message)
history_combo.place(relx = 0.5, rely = 0.33, anchor = CENTER)

message_text = st.ScrolledText(tab_messaging, width = 60, height = 12, font = ('Courier', 16))
message_text.place(relx = 0.5, rely = 0.6, anchor = CENTER)

messaging_button = tk.Button(tab_messaging, text = 'Send', command = messaging, font = ('Inconsolata', 24, 'bold'))
messaging_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)

# receiving message
receiving_title = tk.Label(tab_receiving, text = 'Messaging Receiving', font = ('Inconsolata', 32, 'bold'))
receiving_title.place(relx = 0.5, rely = 0.15, anchor = CENTER)

receiving_combo = ttk.Combobox(tab_receiving, width = 48, state = 'readonly', font = ('Inconsolata', 18))
receiving_combo.place(relx = 0.5, rely = 0.3, anchor = CENTER)
receiving_combo.bind('<Button-1>', receiving)
receiving_combo.bind('<<ComboboxSelected>>', get_message)

receiving_text = st.Text(tab_receiving, relief = 'raised', width = 48, height = 12, state = DISABLED, font = ('Courier', 16), bg = 'khaki1')
receiving_text.place(relx = 0.5, rely = 0.6, anchor = CENTER)

# File Messaging
file_send_title = tk.Label(tab_file_send, text = 'File Sending', font = ('Inconsolata', 32, 'bold'))
file_send_title.place(relx = 0.5, rely = 0.15, anchor = CENTER)

file_receiver_label = tk.Label(tab_file_send, text = 'Send to : ', font = ('Inconsolata', 24))
file_receiver_label.place(relx = 0.15, rely = 0.35, anchor = CENTER)
file_receiver_input = tk.Entry(tab_file_send, width = 48, bd = 3, font = ('Inconsolata', 18))
file_receiver_input.place(relx = 0.6, rely = 0.35, anchor = CENTER)

file_name_label = tk.Label(tab_file_send, text = 'Choose to Add or Delete Files', font = ('Inconsolata', 24))
file_name_label.place(relx = 0.5, rely = 0.5, anchor = CENTER)

file_add_button = tk.Button(tab_file_send, text = 'Add File', command = add_file, font = ('Inconsolata', 24))
file_add_button.place(relx = 0.33, rely = 0.65, anchor = CENTER)

file_del_button = tk.Button(tab_file_send, text = 'Delete File', command = del_file, font = ('Inconsolata', 24))
file_del_button.place(relx = 0.67, rely = 0.65, anchor = CENTER)

file_show_table = tk.Label(tab_file_send, text = '', font = ('Noto Mono', 12))
file_show_table.place(relx = 0.5, rely = 0.8, anchor = CENTER)

file_send_button = tk.Button(tab_file_send, text = 'Send', command = file_send, font = ('Inconsolata', 24, 'bold'))
file_send_button.place(relx = 0.5, rely = 0.9, anchor = CENTER)

# receiving message
file_recv_title = tk.Label(tab_file_recv, text = 'File Receiving', font = ('Inconsolata', 32, 'bold'))
file_recv_title.place(relx = 0.5, rely = 0.15, anchor = CENTER)

file_recv_combo = ttk.Combobox(tab_file_recv, width = 48, state = 'readonly', font = ('Inconsolata', 18))
file_recv_combo.place(relx = 0.5, rely = 0.3, anchor = CENTER)
file_recv_combo.bind('<Button-1>', file_recv)
file_recv_combo.bind('<<ComboboxSelected>>', get_file_name)

file_recv_text = st.ScrolledText(tab_file_recv, relief = 'raised', width = 60, height = 15, state = DISABLED, font = ('Courier', 14), bg = 'khaki1')
file_recv_text.place(relx = 0.5, rely = 0.6, anchor = CENTER)


# render tabs
tabs.bind('<<NotebookTabChanged>>', tab_switching)
tabs.pack(expand = 1, fill = 'both')

window.mainloop()
