import sys
import time
import threading
import requests

if len(sys.argv) < 2 or len(sys.argv[1].split(':')) != 2:
    print('informe ip:porta do server')
    exit(1)

peers = [sys.argv[1]]
SYNC_EVERY_SECONDS = 10


def comprar_produto():
    global peers

    id_produto = input('ID: ')
    qtde = input('Quantidade: ')

    if not id_produto:
        print('ID do produto obrigatório')
        return
    if not qtde:
        print('quantidade do produto obrigatória')
        return

    dados = {
        'id': int(id_produto),
        'qtde': int(qtde)
    }

    for peer in peers:
        try:
            r = requests.put('http://{}/comprar'.format(peer), json=dados)
        except:
            continue
        else:
            print(r.json())
            return

    print('Nenhum servidor disponível')


def lista_produtos():
    global peers

    for peer in peers:
        try:
            r = requests.get('http://{}/produtos'.format(peer))
        except:
            continue
        else:
            print(r.json())
            return

    print('Nenhum servidor disponível')


def menu():
    comando = None

    while comando != 'q':
        print("""-------------------------------------
--------- Sistema de compras --------
-------------------------------------

1 - Listar produtos
2 - Comprar produto""")
        comando = input('Opção: ')

        if comando == '1':
            lista_produtos()
        elif comando == '2':
            comprar_produto()
        elif comando == 'q':
            return
        else:
            print('Opção inválida!')


def get_peers():
    """
    Atualiza os servers disponíveis
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
