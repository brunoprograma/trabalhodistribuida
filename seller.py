import socket
import threading
import time

tLock = threading.Lock()
tLock1 = threading.Semaphore()
shutdown = False
produtos = {}
tempo = 0
alias = ''
s = None
server = None


def timing():
    global shutdown
    global produtos
    global tempo
    global alias
    global s
    global server
    while not shutdown:
        tLock1.acquire()
        tempo += 1
        tLock1.release()
        time.sleep(2)


def receiving(name, sock):
    global shutdown
    global produtos
    global tempo
    global alias
    global s
    global server
    while not shutdown:
        try:
            tLock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                decoded_data = eval(data.decode('utf-8'))
                t = decoded_data.get('tempo')

                if t > tempo + 2:
                    tLock1.acquire()
                    tempo = t + 2
                    tLock1.release()

                cod = decoded_data.get('codigo')

                if cod:  # cod pode ser None quando executa na mesma máquina cliente e fornecedor
                    if cod in produtos:
                        if produtos[cod]['quantidade'] - decoded_data.get('qtde') >= 0:
                            produtos[cod]['quantidade'] -= decoded_data.get('qtde')
                            message = str({'alias': alias, 'status': 'Confirmado', 'tempo': tempo})
                            print(message, produtos[cod]['codigo'], produtos[cod]['quantidade'])
                            message = message.encode('utf-8')
                            s.sendto(message, server)
                        else:
                            message = str({'alias': alias, 'status': 'Rejeitado', 'tempo': tempo})
                            print(message, produtos[cod]['codigo'], produtos[cod]['quantidade'])
                            message = message.encode('utf-8')
                            s.sendto(message, server)
                    else:
                        print('Produto não cadastrado')
                        message = str({'alias': alias, 'status': 'Produto não cadastrado', 'tempo': tempo})
                        message = message.encode('utf-8')
                        s.sendto(message, server)
        except:
            pass
        finally:
            tLock.release()


def init():
    global shutdown
    global produtos
    global tempo
    global alias
    global s
    global server

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
    message = str({'alias': alias, 'tempo': tempo})
    message = message.encode('utf-8')

    # Envio da mensagem
    s.sendto(message, server)

    print("Cadastro:")
    codigo = input("Codigo: ")
    nome = input("Nome: ")
    quantidade = input("Quantidade: ")
    posicao = '{}-{}'.format(alias, codigo)

    if posicao not in produtos:
        produtos[posicao] = {}
    produtos[posicao]['quantidade'] = int(quantidade)
    produtos[posicao]['codigo'] = int(codigo)
    print('Cadastrado', codigo, posicao, produtos[posicao]['quantidade'])

    message = str({'alias': alias, 'codigo': posicao, 'nome': nome, 'qtde': quantidade, 'tempo': tempo})
    message = message.encode('utf-8')
    s.sendto(message, server)

    mes = input("'q' para sair, enter para continuar cadastrando: ")

    while mes != 'q':
        print("Cadastro:")
        codigo = input("Codigo: ")
        nome = input("Nome: ")
        quantidade = input("Quantidade: ")

        posicao = '{}-{}'.format(alias, codigo)
        if posicao not in produtos:
            produtos[posicao] = {}
        produtos[posicao]['quantidade'] = int(quantidade)
        produtos[posicao]['codigo'] = int(codigo)
        print('Cadastrado', codigo, posicao, produtos[posicao]['quantidade'])

        message = str({'alias': alias, 'codigo': posicao, 'nome': nome, 'qtde': int(quantidade), 'tempo': tempo})
        message = message.encode('utf-8')
        s.sendto(message, server)
        mes = input("'q' para sair, enter para continuar cadastrando: ")

    message = 'Desconectando'
    message = str({'alias': alias, 'mensagem': message})
    message = message.encode('utf-8')
    s.sendto(message, server)
    shutdown = True
    timingThread.join()
    receivingThread.join()
    s.close()

init()
