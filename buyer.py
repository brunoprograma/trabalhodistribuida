import socket
import threading
import time

tLock = threading.Lock()
tSem = threading.Semaphore()
shutdown = False
tempo = 0
alias = ''


def timing():
    global tempo
    global shutdown
    global alias
    while not shutdown:
        tSem.acquire()
        tempo += 1
        tSem.release()
        time.sleep(2)


def receiving(name, sock):
    global tempo
    global shutdown
    global alias
    while not shutdown:
        try:
            tLock.acquire()
            while True:
                data, addr = sock.recvfrom(1024)
                decoded_data = eval(data.decode('utf-8'))
                print(decoded_data)

                t = decoded_data.get('tempo')
                if t > tempo + 2:
                    tSem.acquire()
                    tempo = t + 2
                    tSem.release()
        except:
            pass
        finally:
            tLock.release()


def init():
    global tempo
    global shutdown
    global alias

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

    alias = 'Cliente'
    message = str({'alias': alias, 'tempo': tempo})
    message = message.encode('utf-8')

    # Envio da mensagem ao servidor
    s.sendto(message, server)
    print("Loja Enviará Codigo: Nome : Quantidade")
    print("Pedido:")
    codigo = input("Código: ")
    quantidade = input("Quantidade: ")

    message = str({'alias': alias, 'codigo': codigo, 'qtde': int(quantidade), 'tempo': tempo})
    message = message.encode('utf-8')
    s.sendto(message, server)

    mes = input("'q' para sair, enter para continuar comprando: ")

    while mes != 'q':
        print("Pedido:")
        codigo = input("Código: ")
        quantidade = input("Quantidade: ")
        message = str({'alias': alias, 'codigo': codigo, 'qtde': int(quantidade), 'tempo': tempo})
        message = message.encode('utf-8')
        s.sendto(message, server)
        mes = input("'q' para sair, enter para continuar comprando: ")

    message = 'Desconectando'
    message = str({'alias': alias, 'mensagem': message})
    message = message.encode('utf-8')
    s.sendto(message, server)
    shutdown = True
    timingThread.join()
    receivingThread.join()
    s.close()

init()
