import json
import random
import sys
import socket
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as st
from tkinter import messagebox
from tkinter import CENTER, NORMAL, DISABLED, END, INSERT

CMD_MAX_LEN = 16
TXT_MAX_LEN = 4096
USER_MAX_LEN = 1024
PASS_MAX_LEN = 1024

client = None
current_user = None
n_message = 0
messages = []
infos = []

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
	password_validation = password_validation.get()

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
		infos = []
		messages = []
		n_message = 0

		tabs.tab(0, state = NORMAL)
		tabs.tab(2, state = DISABLED)
		tabs.tab(3, state = DISABLED)

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

		elif response == b'REJ':
			messagebox.showerror('', 'Invalid username/password')
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
	print('receiving')

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
	
def tab_switching(event):
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
		receiving_text.delete(1.0, END)


window = tk.Tk()
window.title('CN Message')
window.geometry('1024x768')


# Tabs
tabs = ttk.Notebook(window)
tab_home = ttk.Frame(tabs)
tab_register = ttk.Frame(tabs)
tab_messaging = ttk.Frame(tabs)
tab_receiving = ttk.Frame(tabs)
tabs.add(tab_home, text = 'Home')
tabs.add(tab_register, text = 'Registration', state = DISABLED)
tabs.add(tab_messaging, text = 'Messaging', state = DISABLED)
tabs.add(tab_receiving, text = 'Receiving', state = DISABLED)

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
password_input = tk.Entry(tab_register, width = 32, bd = 3)
password_input.place(relx = 0.5, rely = 0.5, anchor = CENTER)

password_validation_image = tk.PhotoImage(file = './images/check.png')
password_validation_image_label = tk.Label(tab_register, image = password_validation_image)
password_validation_image_label.place(relx = 0.35, rely = 0.6, anchor = CENTER)
password_validation_input = tk.Entry(tab_register, width = 32, bd = 3)
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


# render tabs
tabs.bind('<<NotebookTabChanged>>', tab_switching)
tabs.pack(expand = 1, fill = 'both')

window.mainloop()
