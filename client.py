import sys
import socket
import tkinter, tkinter.ttk

client = None

window = tkinter.Tk()
window.title('CN Message')
window.geometry('700x450')

title = tkinter.Label(window, text = 'CN Message', font = ('Courier', 48, 'bold'))
title.place(relx = 0.5, rely = 0.2, anchor = tkinter.CENTER)

host_label = tkinter.Label(window, text = 'Host', font = ('Courier', 24))
host_label.place(relx = 0.25, rely = 0.4, anchor = tkinter.CENTER)

port_label = tkinter.Label(window, text = 'Port', font = ('Courier', 24))
port_label.place(relx = 0.75, rely = 0.4, anchor = tkinter.CENTER)

host_var = tkinter.StringVar()
port_var = tkinter.StringVar()

host_input = tkinter.Entry(width = 12, bd = 3, textvariable = host_var, font = ('Courier', 16))
host_input.place(relx = 0.25, rely = 0.5, anchor = tkinter.CENTER)

port_input = tkinter.Entry(width = 12, bd = 3, textvariable = port_var, font = ('Courier', 16))
port_input.place(relx = 0.75, rely = 0.5, anchor = tkinter.CENTER)

column = tkinter.Label(window, text = ':', font = ('Courier', 16))
column.place(relx = 0.5, rely = 0.5, anchor = tkinter.CENTER)

def connect():
	host = host_var.get()
	port = port_var.get()

	global client
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client.connect((host, port))
	except:
		client = None

connect_button = tkinter.Button(window, text = 'Connect', command = connect, font = ('Courier', 24, 'bold'), bg = 'DodgerBlue2')
connect_button.place(relx = 0.5, rely = 0.65, anchor = tkinter.CENTER)

window.mainloop()


