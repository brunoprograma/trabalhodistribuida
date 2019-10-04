from flask import Flask, jsonify

app = Flask(__name__)
produtos = {}
peers = []
eventos = []


@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)
