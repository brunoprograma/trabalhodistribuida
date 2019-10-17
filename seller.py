import sys
import time
import threading
import requests

if len(sys.argv) < 2 or len(sys.argv[1].split(':')) != 2:
    print('informe ip:porta do server')
    exit(1)

peers = [sys.argv[1]]
seller_id = None
SYNC_EVERY_SECONDS = 10


def adiciona_produto():
    global peers
    global seller_id

    nome = input('Nome: ')
    qtde = input('Quantidade: ')

    if not nome:
        print('nome do produto obrigatório')
        return
    if not qtde:
        print('quantidade do produto obrigatória')
        return

    dados = {
        'nome': nome,
        'qtde': int(qtde)
    }

    for peer in peers:
        try:
            r = requests.post('http://{}/produtos'.format(peer), json=dados)
        except:
            continue
        else:
            print(r.json())
            return

    print('Nenhum servidor disponível')


def atualiza_produto():
    global peers
    global seller_id

    dados = {}
    id_produto = input('Digite o id do produto: ')
    nome = input('Nome (enter para manter): ')
    qtde = input('Quantidade (enter para manter): ')

    if nome:
        dados['nome'] = nome
    if qtde:
        dados['qtde'] = int(qtde)

    for peer in peers:
        try:
            r = requests.put('http://{}/produtos/{}'.format(peer, id_produto), json=dados)
        except:
            continue
        else:
            print(r.json())
            return

    print('Nenhum servidor disponível')


def lista_produtos():
    global peers
    global seller_id

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
        comando = input('Opção: ')

        if comando == '1':
            lista_produtos()
        elif comando == '2':
            adiciona_produto()
        elif comando == '3':
            atualiza_produto()
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
