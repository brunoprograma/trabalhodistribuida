import socket
import threading
import time

tLock1 = threading.Lock()
host = '127.0.0.1'
port = 5000
clients = []
vendedores = []
tempo_i = 0
shutdown = False
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(False)

print("Servidor inicializado.")

while True:
	try:
		data, addr = s.recvfrom(1024)
		decoded_data = data.decode('utf-8')
		t = decoded_data.split(':Tempo:')
		x = decoded_data.split(':')

		if decoded_data == "poweroff":
			print("Desligando...")
			shutdown = True
			continue

		if addr not in clients:
			if str(t[0]) == 'Cliente':
				print("Cliente ", addr, "conectou-se.")
				clients.append(addr)

		if addr not in vendedores:
			if str(t[0]) != 'Cliente':
				print("Vendedor ", addr, "conectou-se.")
				vendedores.append(addr)

		if str(x[0]) != 'Cliente':
			for client in clients:
				if addr != client:
					s.sendto(data, client)
		else:
			for vd in vendedores:
				if addr != vd:
					s.sendto(data, vd)

		print(time.ctime(time.time()), addr, ":", decoded_data)
		time.sleep(0.2)
	except:
		pass

s.close()
