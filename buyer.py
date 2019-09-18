import socket
import threading
import time

tLock = threading.Lock()
tSem = threading.Semaphore()
shutdown = False
tempo = 0


def timing():
    global tempo
    while not shutdown:
        tSem.acquire()
        tempo = tempo + 1
        tSem.release()
        time.sleep(2)


def receving(name, sock):
    while not shutdown:
        try:
            tLock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                decoded_data = data.decode('utf-8')
                print(decoded_data)

                t = decoded_data.split(':Tempo:')
                if int(t[1]) > (int(tempo)+2):
                    tSem.acquire()
                    tempo = int(t[1]) + 2
                    tSem.release()
        except:
            pass
        finally:
            tLock.release()

host = '127.0.0.1'
port = 0
server = ('127.0.0.1', 5000)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

receivingThread = threading.Thread(target=receving, args=("RecvThread", s))
receivingThread.start()
timingThread = threading.Thread(target=timing)
timingThread.start()

alias = "Cliente"
message = alias + ":Tempo:" + str(tempo)
message = message.encode('utf-8')

# Envio da mensagem ao servidor
s.sendto(message, server)
print("Loja Enviará Codigo: Nome : Quantidade")
print("Pedido:")
codigo = input("Código: ")
quantidade = input("Quantidade: ")

message = (alias + ":" + str(codigo) + ":" + str(quantidade) + ":Tempo:" + str(tempo))
message = message.encode('utf-8')
s.sendto(message, server)

mes = input("'q' para sair, enter para continuar comprando: ")

while mes != 'q':
    print("Pedido:")
    codigo = input("Código: ")
    quantidade = input("Quantidade: ")
    message = (alias + ":" + str(codigo) + ":" + str(quantidade) + ":Tempo:" + str(tempo))
    message = message.encode('utf-8')
    s.sendto(message, server)
    mes = input("'q' para sair, enter para continuar comprando: ")

message = 'Desconectando'
message = (alias + ": " + message)
message = message.encode('utf-8')
s.sendto(message, server)
shutdown = True
timingThread.join()
receivingThread.join()
s.close()
