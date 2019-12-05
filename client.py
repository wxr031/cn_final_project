import sys
import socket
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import CENTER, NORMAL, DISABLED, END

CMD_MAX_LEN = 16

client = None

def connect():
	global client
	
	if connect_button['text'] == 'Disconnect':
		client.send(b'CLOSE')
		client.close()
		host_input['state'] = NORMAL
		port_input['state'] = NORMAL
		connect_button['text'] = 'Connect'
		status_text['text'] = ''
		register_status_text['text'] = ''
		messaging_status_text['text'] = ''
		tabs.tab(1, state = DISABLED)
		tabs.tab(2, state = DISABLED)

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
		tabs.tab(2, state = NORMAL)

def signup():
	
	username = username_var.get()
	password = password_var.get()
	password_validation = password_validation_var.get()

	if len(username) == 0 or len(password) == 0:
		register_status_text['text'] = 'Please provide username and password'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return
	
	if len(username) > 1024 or len(password) > 1024:
		register_status_text['text'] = 'username and password must be less than 1024 characters'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return
	
	if password != password_validation:
		register_status_text['text'] = 'Password double confirmation failed. Please enter your password again'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return

	if not username.isalnum() or not password.isalnum():
		register_status_text['text'] = 'username and password must only contains alphanumeric values'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)
		return
	
	assert client is not None
	client.send(b'SIGNUP')

	response = client.recv(CMD_MAX_LEN)
	assert response == b'USER&PASS'
	
	client.send(username.encode() + b'&' + password.encode())
	response = client.recv(CMD_MAX_LEN)
	if response == b'OK':
		register_status_text['text'] = 'Registration OK'
		register_status_text['fg'] = 'green'
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)

	elif response == b'DUP':
		register_status_text['text'] = 'Username already exist'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)
		password_validation_input.delete(0, END)

def signin():
	print('Sign in')
	pass

def sign_in_up_toggle():
	if sign_in_up_button['text'] == 'Sign In':
		register_title['text'] = 'Sign In'
		register_button['command'] = signin
		sign_in_up_title['text'] = 'Don\'t have an account?' 
		sign_in_up_button['text'] = 'Sign Up'
		sign_in_up_button.place(relx = 0.7, rely = 0.8, anchor = CENTER)
		register_status_text['text'] = ''
		password_validation_input.place_forget()
		password_validation_image_label.place_forget()
	
	elif sign_in_up_button['text'] == 'Sign Up':
		register_title['text'] = 'Sign Up'
		register_button['command'] = signup
		sign_in_up_title['text'] = 'Have an account?' 
		sign_in_up_button['text'] = 'Sign In'
		sign_in_up_button.place(relx = 0.6, rely = 0.8, anchor = CENTER)
		register_status_text['text'] = ''
		password_validation_input.place(relx = 0.5, rely = 0.6, anchor = CENTER)
		password_validation_image_label.place(relx = 0.35, rely = 0.6, anchor = CENTER)

	
#def get_history(event):
	#client.send(b'HISTORY')
	#assert client.recv(CMD_MAX_LEN) == b'USER'
	#client.send()

def messaging():
	pass

window = tk.Tk()
window.title('CN Message')
window.geometry('1024x768')


# Tabs
tabs = ttk.Notebook(window)
tab_home = ttk.Frame(tabs)
tab_register = ttk.Frame(tabs)
tab_messaging = ttk.Frame(tabs)
tabs.add(tab_home, text = 'Home')
tabs.add(tab_register, text = 'Registration', state = DISABLED)
tabs.add(tab_messaging, text = 'Messaging', state = NORMAL)

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
username_var = tk.StringVar()
username_input = tk.Entry(tab_register, width = 32, bd = 3, textvariable = username_var)
username_input.focus()
username_input.place(relx = 0.5, rely = 0.4, anchor = CENTER)

password_image = tk.PhotoImage(file = './images/password.png')
password_image_label = tk.Label(tab_register, image = password_image)
password_image_label.place(relx = 0.35, rely = 0.5, anchor = CENTER)
password_var = tk.StringVar()
password_input = tk.Entry(tab_register, width = 32, bd = 3, textvariable = password_var)
password_input.place(relx = 0.5, rely = 0.5, anchor = CENTER)

password_validation_image = tk.PhotoImage(file = './images/check.png')
password_validation_image_label = tk.Label(tab_register, image = password_validation_image)
password_validation_image_label.place(relx = 0.35, rely = 0.6, anchor = CENTER)
password_validation_var = tk.StringVar()
password_validation_input = tk.Entry(tab_register, width = 32, bd = 3, textvariable = password_validation_var)
password_validation_input.place(relx = 0.5, rely = 0.6, anchor = CENTER)

register_button = tk.Button(tab_register, text = 'Submit', command = signup, font = ('Inconsolata', 24, 'bold'))
register_button.place(relx = 0.5, rely = 0.7, anchor = CENTER)

sign_in_up_title = tk.Label(tab_register, text = 'Have an account?', font = ('Inconsolata', 18))
sign_in_up_title.place(relx = 0.4, rely = 0.8, anchor = CENTER)

sign_in_up_button = tk.Button(tab_register, text = 'Sign In', command = sign_in_up_toggle, font = ('Inconsolata', 16, 'bold'))
sign_in_up_button.place(relx = 0.6, rely = 0.8, anchor = CENTER)

register_status_text = tk.Label(tab_register, text = '', font = ('Inconsolata', 16, 'bold'))
register_status_text.place(relx = 0.5, rely = 0.9, anchor = CENTER)


# Messaging
#messaging_title = tk.Label(tab_messaging, text = 'Messaging', font = ('Inconsolata', 32, 'bold'))
#messaging_title.place(relx = 0.5, rely = 0.15, anchor = CENTER)
#
#dest_label = tk.Label(tab_messaging, text = 'Send to : ', font = ('Inconsolata', 24))
#dest_label.place(relx = 0.15, rely = 0.25, anchor = CENTER)
#dest_var = tk.StringVar()
#dest_input = tk.Entry(tab_messaging, width = 48, bd = 3, textvariable = dest_var, font = ('Inconsolata', 18))
#dest_input.place(relx = 0.6, rely = 0.25, anchor = CENTER)
#
#history_label = tk.Label(tab_messaging, text = 'Send to : ', font = ('Inconsolata', 24))
#history_label.place(relx = 0.15, rely = 0.25, anchor = CENTER)
#history_combo = ttk.Combobox(tab_messaging, width = 48, state='readonly', font = ('Inconsolata', 18))
#history_combo['values'] = ('---history---')
#history_combo.current(0)
#history_combo.bind('<Button-1>', get_history)
#history_combo.place(relx = 0.6, rely = 0.35, anchor = CENTER)
#
#messaging_button = tk.Button(tab_messaging, text = 'Send', command = messaging, font = ('Inconsolata', 24, 'bold'))
#messaging_button.place(relx = 0.5, rely = 0.7, anchor = CENTER)
#
#messaging_status_text = tk.Label(tab_messaging, text = '')
#messaging_status_text.place(relx = 0.5, rely = 0.8, anchor = CENTER)

# render tabs
tabs.pack(expand = 1, fill = 'both')

window.mainloop()
