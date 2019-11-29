import sys
import socket
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import CENTER, NORMAL, DISABLED, END

client = None

def connect():
	global client
	
	if connect_button['text'] == 'Disconnect':
		client.close()
		host_input['state'] = NORMAL
		port_input['state'] = NORMAL
		connect_button['text'] = 'Connect'
		status_text['text'] = ''
		register_status_text['text'] = ''
		tabs.tab(1, state = DISABLED)

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

def register():
	
	username = username_var.get()
	password = password_var.get()

	if len(username) == 0 or len(password) == 0:
		register_status_text['text'] = 'Please provide username and password'
		register_status_text['fg'] = 'red'
		password_input.delete(0, END)
		return
	
	if len(username) > 1024 or len(password) > 1024:
		register_status_text['text'] = 'username and password must be less than 1024 characters'
		register_status_text['fg'] = 'red'
		password_input.delete(0, END)
		return
	
	if not username.isalnum() or not password.isalnum():
		register_status_text['text'] = 'username and password must only contains alphanumeric values'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)
		return
	
	assert client is not None
	client.send(b'REGISTER')

	response = client.recv(16)
	assert response == b'USER&PASS'
	
	client.send(username.encode() + b'&' + password.encode())
	response = client.recv(16)
	if response == b'OK':
		register_status_text['text'] = 'Registration OK'
		register_status_text['fg'] = 'green'
		username_input.delete(0, END)
		password_input.delete(0, END)

	elif response == b'DUP':
		register_status_text['text'] = 'Username already exist'
		register_status_text['fg'] = 'red'
		username_input.delete(0, END)
		password_input.delete(0, END)

window = tk.Tk()
window.title('CN Message')
window.geometry('700x450')


# Tabs
tabs = ttk.Notebook(window)
tab_home = ttk.Frame(tabs)
tab_register = ttk.Frame(tabs)
tabs.add(tab_home, text = 'Home')
tabs.add(tab_register, text = 'Registration', state = DISABLED)

# User Interface

# Home Page
home_title = tk.Label(tab_home, text = 'CN Message', font = ('Inconsolata', 48, 'bold'))
home_title.place(relx = 0.5, rely = 0.2, anchor = CENTER)

host_label = tk.Label(tab_home, text = 'Host', font = ('Inconsolata', 16))
host_label.place(relx = 0.3, rely = 0.4, anchor = CENTER)

port_label = tk.Label(tab_home, text = 'Port', font = ('Inconsolata', 16))
port_label.place(relx = 0.7, rely = 0.4, anchor = CENTER)

host_var = tk.StringVar()
port_var = tk.StringVar()

host_input = tk.Entry(tab_home, width = 12, bd = 3, textvariable = host_var, font = ('Inconsolata', 14))
host_input.place(relx = 0.3, rely = 0.5, anchor = CENTER)

port_input = tk.Entry(tab_home, width = 12, bd = 3, textvariable = port_var, font = ('Inconsolata', 14))
port_input.place(relx = 0.7, rely = 0.5, anchor = CENTER)

column = tk.Label(tab_home, text = ':', font = ('Inconsolata', 16))
column.place(relx = 0.5, rely = 0.5, anchor = CENTER)

status_text = tk.Label(tab_home, text = '')
status_text.place(relx = 0.5, rely = 0.8, anchor = CENTER)

connect_button = tk.Button(tab_home, text = 'Connect', command = connect, font = ('Inconsolata', 24, 'bold'))
connect_button.place(relx = 0.5, rely = 0.65, anchor = CENTER)

# Registration
register_title = tk.Label(tab_register, text = 'Registration', font = ('Inconsolata', 24, 'bold'))
register_title.place(relx = 0.5, rely = 0.2, anchor = CENTER)

username_image = tk.PhotoImage(file = './images/username.png')
username_image_label = tk.Label(tab_register, image = username_image)
username_image_label.place(relx = 0.35, rely = 0.4, anchor = CENTER)
username_var = tk.StringVar()
username_input = tk.Entry(tab_register, width = 20, bd = 3, textvariable = username_var)
username_input.focus()
username_input.place(relx = 0.5, rely = 0.4, anchor = CENTER)

password_image = tk.PhotoImage(file = './images/password.png')
password_image_label = tk.Label(tab_register, image = password_image)
password_image_label.place(relx = 0.35, rely = 0.5, anchor = CENTER)
password_var = tk.StringVar()
password_input = tk.Entry(tab_register, width = 20, bd = 3, textvariable = password_var)
password_input.place(relx = 0.5, rely = 0.5, anchor = CENTER)

register_button = tk.Button(tab_register, text = 'Register', command = register, font = ('Inconsolata', 16, 'bold'))
register_button.place(relx = 0.5, rely = 0.7, anchor = CENTER)

register_status_text = tk.Label(tab_register, text = '')
register_status_text.place(relx = 0.5, rely = 0.8, anchor = CENTER)

# render tabs
tabs.pack(expand = 1, fill = 'both')

window.mainloop()
