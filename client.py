import sys
import socket
import tkinter, tkinter.ttk

client = None

window = tkinter.Tk()
window.title('CN Message')
window.geometry('700x450')

def connect():
	global client
	
	if connect_button['text'] == 'Disconnect':
		client.close()
		host_input['state'] = tkinter.NORMAL
		port_input['state'] = tkinter.NORMAL
		connect_button['text'] = 'Connect'

	else:
		
		host = host_var.get()
		port = int(port_var.get())

		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client.connect((host, port))
		except:
			status_text['text'] = 'Cannot connect to {}:{}'.format(host, port)
			status_text['fg'] = 'red'
			return
		else:
			status_text['text'] = 'Connection to {}:{} established'.format(host, port)
			status_text['fg'] = 'green'
			connect_button['text'] = 'Disconnect'
			host_input['state'] = tkinter.DISABLED
			port_input['state'] = tkinter.DISABLED
		finally:
			status_text.place(relx = 0.5, rely = 0.8, anchor = tkinter.CENTER)


title = tkinter.Label(window, text = 'CN Message', font = ('Courier', 48, 'bold'))
title.place(relx = 0.5, rely = 0.2, anchor = tkinter.CENTER)

host_label = tkinter.Label(window, text = 'Host', font = ('Courier', 24))
host_label.place(relx = 0.3, rely = 0.4, anchor = tkinter.CENTER)

port_label = tkinter.Label(window, text = 'Port', font = ('Courier', 24))
port_label.place(relx = 0.7, rely = 0.4, anchor = tkinter.CENTER)

host_var = tkinter.StringVar()
port_var = tkinter.StringVar()

host_input = tkinter.Entry(width = 12, bd = 3, textvariable = host_var, font = ('Courier', 16))
host_input.place(relx = 0.3, rely = 0.5, anchor = tkinter.CENTER)

port_input = tkinter.Entry(width = 12, bd = 3, textvariable = port_var, font = ('Courier', 16))
port_input.place(relx = 0.7, rely = 0.5, anchor = tkinter.CENTER)

column = tkinter.Label(window, text = ':', font = ('Courier', 16))
column.place(relx = 0.5, rely = 0.5, anchor = tkinter.CENTER)

status_text = tkinter.Label(window, text = '')

connect_button = tkinter.Button(window, text = 'Connect', command = connect, font = ('Courier', 24, 'bold'))
connect_button.place(relx = 0.5, rely = 0.65, anchor = tkinter.CENTER)

window.mainloop()
