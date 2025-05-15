from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import random
import os

app = Flask(__name__)
CORS(app)

# Determine o caminho absoluto para o diretório do script atual
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Construa o caminho para o arquivo policy.pkl
POLICY_PATH = os.path.join(APP_DIR, '..', 'data', 'policy.pkl')
data = pickle.load(open(POLICY_PATH, 'rb'))

@app.route('/')
def index():
    return "Tic Tac Toe RL Agent"

@app.route('/move', methods=['POST'])
def move():
    content = request.get_json()
    state = content['state']
    key = ''.join(state)
    values = {i: data.get(''.join(state[:i] + ['O'] + state[i+1:]), 0) for i, v in enumerate(state) if v == ' '}
    action = min(values, key=values.get) if values else random.choice([i for i, v in enumerate(state) if v == ' '])
    state[action] = 'O'
    return jsonify({'state': state})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)