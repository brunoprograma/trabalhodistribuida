import socket
import threading
import time

tLock1 = threading.Lock()
host = '127.0.0.1'
port = 5000
clients = []
vendedores = []
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(False)

print("Servidor inicializado.")

while True:
	try:
		data, addr = s.recvfrom(1024)
		decoded_data = eval(data.decode('utf-8'))
		t = decoded_data.get('tempo')

		if addr not in clients:
			if decoded_data.get('alias') == 'Cliente':
				print("Cliente", addr, "conectou-se.")
				clients.append(addr)

		if addr not in vendedores:
			if decoded_data.get('alias') != 'Cliente':
				print("Vendedor", addr, "conectou-se.")
				vendedores.append(addr)

		if decoded_data.get('alias') == 'Cliente':
			for vd in vendedores:
				if addr != vd:
					s.sendto(data, vd)
		else:
			for client in clients:
				if addr != client:
					s.sendto(data, client)

		print(time.ctime(time.time()), addr, ":", decoded_data)
		time.sleep(0.2)
	except:
		pass
