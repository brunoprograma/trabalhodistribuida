import sys
import time
import requests
import threading
from threading import Lock
from flask import Flask, jsonify, request, abort

app = Flask(__name__)
lock = Lock()
tempo = -1


def set_tempo(novo_tempo=None):
    """
    Incremento e atualização de tempo no relógio lógico
    :param novo_tempo: int: se passado, apenas atualiza o tempo para o valor informado
    :return: int: tempo
    """
    global lock
    global tempo
    with lock:
        if novo_tempo:
            tempo = novo_tempo
        else:
            tempo += 1
        return tempo


class DB(object):
    """
    Classe que implementa um banco de dados
    """
    def __init__(self):
        self.pk = 0
        self.produtos = dict()
        self.peers = dict()
        self.eventos = dict()

    def get_produto_pk(self, pk=None):
        global lock
        with lock:
            if pk:
                if pk > self.pk:
                    self.pk = pk
                return pk
            self.pk += 1
            return self.pk

    def insert_produto(self, seller, nome, qtde, pk=None):
        global lock
        with lock:
            produto = Produto(seller, nome, qtde)
            self.produtos.update({self.get_produto_pk(pk): produto})
            return produto

    def update_produto(self, pk, nome=None, qtde=None):
        global lock
        with lock:
            if nome:
                self.produtos[pk].nome = nome
            if qtde:
                self.produtos[pk].qtde = qtde
            return self.produtos[pk]

    def select_produto(self):
        return [prod.to_dict().update({'pk': k}) for k, prod in self.produtos.items()]

    def comprar(self, pk, qtde):
        global lock
        with lock:
            produto = self.produtos[pk]
            if produto.qtde >= qtde:
                nova_qtde = produto.qtde - qtde
                self.evento("produto", "update", pk=pk, qtde=nova_qtde)
                return True
            return False

    def insert_peer(self, ip, porta):
        global lock
        with lock:
            peer = Peer(ip, porta)
            self.peers['{}:{}'.format(ip, porta)] = peer
            return peer

    def delete_peer(self, ip, porta):
        global lock
        with lock:
            peer = Peer(ip, porta)
            self.peers.pop('{}:{}'.format(ip, porta), None)
            return peer

    def select_peer(self):
        return self.peers.keys()

    def evento(self, tipo, acao, tempo=None, **kwargs):
        """
        Registra um evento, ou seja, uma inserção, edição ou exclusão de um objeto.
        Altera o objeto e depois registra o evento.
        :param tipo: str: tipo do objeto
        :param acao: str: ação executada
        :param tempo: caso for uma sincronização de dados o tempo virá setado
        :param args: dados do objeto
        """
        global lock
        with lock:
            obj = getattr(self, '{}_{}'.format(acao, tipo))(**kwargs)
            tempo = set_tempo(tempo)
            self.eventos[tempo] = Evento(tipo=tipo, acao=acao, dados=obj.to_dict())

    def select_evento(self):
        return self.eventos


class Produto(object):
    def __init__(self, seller, nome, qtde):
        self.seller = seller
        self.nome = nome
        self.qtde = qtde

    def to_dict(self):
        return {
            "seller": self.seller,
            "nome": self.nome,
            "qtde": self.qtde
        }


class Peer(object):
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta

    def to_dict(self):
        return {"ip": self.ip, "porta": self.porta}


class Evento(object):
    def __init__(self, tipo, acao, dados):
        """
        Registra um evento ocorrido
        :param tipo: str: tipo do objeto envolvido no evento: "Produto" ou "Peer"
        :param acao: str: "insert" ou "delete" (não existe update, o update é um insert que sobrescreve o registro atual)
        :param dados: dict: dados do objeto
        """
        self.tipo = tipo
        self.acao = acao
        self.dados = dados

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "acao": self.acao,
            "dados": self.dados
        }


db = DB()  # BANCO DE DADOS

try:
    initial_peer = sys.argv[2]
    print(initial_peer)
except:
    initial_peer = None

if initial_peer and len(initial_peer.split(':')) != 2:
    print('quando informar um peer, informe ip:porta')
    exit(1)
elif initial_peer:
    db.evento("peer", "insert", **dict(ip=initial_peer.split(':')[0], porta=int(initial_peer.split(':')[0])))


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/peers', methods=['GET'])
def listar_peers():
    global db
    return jsonify({'peers': db.select_peer()})


@app.route('/produtos', methods=['GET'])
def listar_produtos():
    global db
    return jsonify({'produtos': db.select_produto()})


@app.route('/eventos', methods=['GET'])
def listar_eventos():
    global db
    return jsonify({'eventos': db.select_evento()})


@app.route('/produtos', methods=['POST'])
def inserir_produto():
    global db

    if not request.json:
        abort(400)
    elif 'nome' in request.json and type(request.json['nome']) != str:
        abort(400)
    elif 'qtde' in request.json and type(request.json['qtde']) != int:
        abort(400)

    db.evento("insert", "produto", **dict(seller=request.remote_addr, nome=request.json['nome'], qtde=request.json['qtde']))

    return jsonify({'sucesso': 'cadastrado com sucesso'})


@app.route('/produtos/<int:id_produto>', methods=['PUT'])
def atualiza_produto(id_produto):
    global db

    if not request.json:
        abort(400)
    elif id_produto not in db.select_produto().keys():
        return jsonify({'erro', 'produto não existe'}), 404
    elif 'nome' in request.json and type(request.json['nome']) != str:
        abort(400)
    elif 'qtde' in request.json and type(request.json['qtde']) != int:
        abort(400)

    db.evento("update", "produto", **dict(nome=request.json.get('nome'), qtde=request.json.get('qtde')))

    return jsonify({'sucesso': 'atualizado com sucesso'})


@app.route('/comprar', methods=['POST'])
def comprar_produto():
    global db

    if not request.json:
        abort(400)
    elif 'id' in request.json and type(request.json['id']) != int:
        abort(400)
    elif 'qtde' in request.json and type(request.json['qtde']) != int:
        abort(400)
    elif request.json['id'] not in db.select_produto().keys():
        return jsonify({'erro', 'produto não encontrado'}), 404
    elif db.select_produto().get(request.json['id']).qtde < request.json['qtde']:
        return jsonify({'erro': 'quantidade insuficiente'})

    resultado = db.comprar(request.json['id'], request.json['qtde'])

    if not resultado:
        return jsonify({'erro': 'quantidade insuficiente'})

    return jsonify({'sucesso': 'comprado com sucesso'})


def replicador():
    """
    Passa em todos os peers conhecidos e atualiza os eventos, inclusive os outros peers que foram conectados
    """
    global db
    global tempo

    time.sleep(5)
    while True:
        time.sleep(1)
        for peer in db.select_peer():
            r = requests.get(peer + '/eventos')
            if r.status_code == 200:
                eventos = r.json().get('eventos')
                # só atualizamos os eventos que não temos pra economizar tempo
                chaves = set(eventos.keys()) - set(db.eventos.keys())

                for chave in chaves:
                    # a chave é o tempo do evento
                    evento = eventos[chave]
                    db.evento(evento.tipo, evento.acao, chave, **evento.dados)

                time.sleep(1)

        print(', '.join(db.select_peer()), tempo)


t = threading.Thread(target=replicador)
t.start()
app.run(debug=True)
