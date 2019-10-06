from flask import Flask, jsonify, request, abort
from threading import Lock

app = Flask(__name__)
lock = Lock()
tempo = -1


def set_tempo():
    """
    Incremento de tempo no relógio lógico
    """
    global tempo
    with lock:
        tempo += 1
        return tempo


class DB(object):
    """
    Classe que implementa um banco de dados
    """
    def __init__(self):
        self.pk = 0
        self.produtos = dict()
        self.peers = list()
        self.eventos = list()

    def get_produto_pk(self):
        with lock:
            self.pk += 1
            return self.pk

    def insert_produto(self, produto):
        with lock:
            self.produtos.update({self.get_produto_pk(): produto})
            self.evento("produto", "insert", produto.to_dict())
            return True

    def update_produto(self, id, nome=None, qtde=None):
        with lock:
            if nome:
                self.produtos[id].nome = nome
            if qtde:
                self.produtos[id].qtde = qtde
            self.evento("produto", "update", self.produtos[id].to_dict())
            return True

    def select_produto(self):
        return self.produtos

    def comprar(self, id, qtde):
        with lock:
            if self.produtos[id].qtde >= qtde:
                self.produtos[id] -= qtde
                self.evento("produto", "update", self.produtos[id].to_dict())
                return True
            return False

    def insert_peer(self, peer):
        with lock:
            self.peers.append(peer)
            self.evento("peer", "insert", peer.to_dict())
            return True

    def delete_peer(self, peer):
        with lock:
            self.peers.remove(peer)
            self.evento("peer", "delete", peer.to_dict())
            return True

    def select_peer(self):
        return self.peers

    def evento(self, tipo, acao, dados):
        with lock:
            self.eventos.append(Evento(tempo=set_tempo(), tipo=tipo, acao=acao, dados=dados))

    def insert_evento(self, evento):
        with lock:
            self.eventos.append(evento)
            return True

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
    def __init__(self, ip):
        self.ip = ip

    def to_dict(self):
        return {"ip": self.ip}


class Evento(object):
    def __init__(self, tempo, tipo, acao, dados):
        """
        Registra um evento ocorrido
        :param tempo: int: tempo do relógio lógico
        :param tipo: str: tipo do objeto envolvido no evento: "Produto" ou "Peer"
        :param acao: str: "insert" ou "delete" (não existe update, o update é um insert que sobrescreve o registro atual)
        :param dados: dict: dados do objeto
        """
        self.tempo = tempo
        self.tipo = tipo
        self.acao = acao
        self.dados = dados

    def to_dict(self):
        return {
            "tempo": self.tempo,
            "tipo": self.tipo,
            "acao": self.acao,
            "dados": self.dados
        }


db = DB()  # BANCO DE DADOS


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/peers', methods=['GET'])
def listar_peers():
    return jsonify({'peers': db.select_peer()})


@app.route('/produtos', methods=['GET'])
def listar_produtos():
    return jsonify({'produtos': db.select_produto()})


@app.route('/produtos', methods=['POST'])
def inserir_produto():
    if not request.json:
        abort(400)
    elif 'nome' in request.json and type(request.json['nome']) != str:
        abort(400)
    elif 'qtde' in request.json and type(request.json['qtde']) != int:
        abort(400)

    produto = Produto(seller=request.remote_addr, nome=request.json['nome'], qtde=request.json['qtde'])
    db.insert_produto(produto)

    return jsonify({'sucesso': 'cadastrado com sucesso'})


@app.route('/produtos/<int:id_produto>', methods=['PUT'])
def atualiza_produto(id_produto):
    if not request.json:
        abort(400)
    elif id_produto not in db.select_produto().keys():
        return jsonify({'erro', 'produto não existe'}), 404
    elif 'nome' in request.json and type(request.json['nome']) != str:
        abort(400)
    elif 'qtde' in request.json and type(request.json['qtde']) != int:
        abort(400)

    db.update_produto(id=id_produto, nome=request.json.get('nome'), qtde=request.json.get('qtde'))

    return jsonify({'sucesso': 'atualizado com sucesso'})


@app.route('/comprar', methods=['POST'])
def comprar_produto():
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


if __name__ == '__main__':
    app.run(debug=True)
