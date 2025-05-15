from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import random

app = Flask(__name__)
CORS(app)
data = pickle.load(open('../data/policy.pkl', 'rb'))

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

if __name__ == '__main__':
    app.run(debug=True)