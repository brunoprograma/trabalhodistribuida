import socket
import threading
import time
import hashlib

tLock = threading.Lock()
tLock1 = threading.Semaphore()
h = hashlib.md5()
shutdown = False
produtos = {}
tempo_i = 0
alias = ''


def timing():
    global tempo_i
    while not shutdown:
        tLock1.acquire()
        tempo_i = tempo_i + 1
        tLock1.release()
        time.sleep(2)


def receiving(name, sock):
    global tempo_i
    while not shutdown:
        try:
            tLock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                decoded_data = data.decode('utf-8')
                print(decoded_data)
                t = decoded_data.split(':Tempo:')
                if int(t[1]) > (int(tempo_i)+2):
                    tLock1.acquire()
                    tempo_i = int(t[1]) + 2
                    tLock1.release()

                m = decoded_data.split(':')
                cod = int(m[1])
                h.update('{}-{}'.format(alias, cod).encode('utf-8'))
                pos = h.hexdigest()

                if pos in produtos:
                    if produtos[pos]['quantidade'] - int(m[2]) >= 0:
                        produtos[pos]['quantidade'] -= int(m[2])
                        acept = 'Loja 1:Confirmado, :Tempo:' + str(tempo_i)
                        print(acept, produtos[pos]['codigo'], produtos[pos]['quantidade'])
                        acept = acept.encode('utf-8')
                        s.sendto(acept, server)
                    else:
                        acept = 'Loja 1:Rejeitado, :Tempo:' + str(tempo_i)
                        print(acept, produtos[pos]['codigo'], produtos[pos]['quantidade'])
                        acept = acept.encode('utf-8')
                        s.sendto(acept, server)
                else:
                    print('Produto não cadastrado')
                    acept = '{}:Sem este Endereço:Tempo:{}'.format(alias, tempo_i)
                    acept = acept.encode('utf-8')
                    s.sendto(acept, server)
        except:
            pass
        finally:
            tLock.release()


host = '127.0.0.1'
port = 0
server = ('127.0.0.1', 5000)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(False)
receivingThread = threading.Thread(target=receiving, args=("RecvThread", s))
receivingThread.start()
timingThread = threading.Thread(target=timing)
timingThread.start()

alias = input("Nome da Loja: ")
message = alias + ":Tempo:" + str(tempo_i)
message = message.encode('utf-8')

# Envio da mensagem
s.sendto(message, server)

print("Cadastro:")
codigo = input("Codigo: ")
nome = input("Nome: ")
quantidade = input("Quantidade: ")

h.update('{}-{}'.format(alias, codigo).encode('utf-8'))
posicao = h.hexdigest()
if posicao not in produtos:
    produtos[posicao] = {}
produtos[posicao]['quantidade'] = int(quantidade)
produtos[posicao]['codigo'] = int(codigo)
print(codigo, posicao, produtos[posicao]['quantidade'])

message = alias + ":" + str(codigo) + ":" + str(nome) + ":" + str(quantidade) + ":Tempo:" + str(tempo_i)
message = message.encode('utf-8')
s.sendto(message, server)

mes = input("'q' para sair, enter para continuar cadastrando: ")

while mes != 'q':
    print("Cadastro:")
    codigo = input("Codigo: ")
    nome = input("Nome: ")
    quantidade = input("Quantidade: ")

    h.update('{}-{}'.format(alias, codigo).encode('utf-8'))
    posicao = h.hexdigest()
    if posicao not in produtos:
        produtos[posicao] = {}
    produtos[posicao]['quantidade'] = int(quantidade)
    produtos[posicao]['codigo'] = int(codigo)
    print(codigo, posicao, produtos[posicao]['quantidade'])

    message = alias + ":" + str(codigo) + ":" + str(nome) + ":" + str(quantidade) + ":Tempo:" + str(tempo_i)
    message = message.encode('utf-8')
    s.sendto(message, server)
    mes = input("'q' para sair, enter para continuar cadastrando: ")

message = 'Desconectando'
message = (alias + ": " + message)
message = message.encode('utf-8')
s.sendto(message, server)
shutdown = True
timingThread.join()
receivingThread.join()
s.close()
