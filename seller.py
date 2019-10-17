import time
import threading
import requests

peers = ['127.0.0.1:8000']
seller_id = None
SYNC_EVERY_SECONDS = 3

def adiciona_produto():
    global peers
    global seller_id
    pass


def atualiza_produto():
    global peers
    global seller_id
    pass


def lista_produtos():
    global peers
    global seller_id
    pass


def menu():
    global seller_id
    comando = None
    while not seller_id:
        seller_id = input('Digite seu identificador de vendedor: ')

    while comando != 'q':
        print("""-------------------------------------
---------- Sistema de vendas --------
-------------------------------------

1 - Listar produtos
2 - Cadastrar produto
3 - Atualizar produto""")
        comando = int(input('Opção: '))

        if comando == 1:
            lista_produtos()
        elif comando == 2:
            adiciona_produto()
        elif comando == 3:
            atualiza_produto()
        else:
            print('Opção inválida!')


def get_peers():
    """
    Atualiza os peers disponíveis
    """
    global peers
    time.sleep(SYNC_EVERY_SECONDS)
    while True:
        time.sleep(SYNC_EVERY_SECONDS)
        for peer in peers:
            try:
                r = requests.get('http://' + peer + '/peers')
            except:
                time.sleep(1)
                continue
            else:
                if r.status_code == 200:
                    _peers = r.json().get('peers')
                    peers[:] = list(set(peers + _peers))
                    time.sleep(1)

        print(peers)


t = threading.Thread(target=get_peers)
t.start()
menu()
exit(0)