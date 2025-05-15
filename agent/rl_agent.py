import numpy as np
import pickle
import random

class TicTacToeEnv:
    def __init__(self):
        # Tabuleiro 3x3: 0 = vazio, 1 = X (agente), -1 = O (oponente)
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1  # Agente começa

    def reset(self):
        # Reinicia o tabuleiro
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1
        return self.get_state()

    def get_state(self):
        # Retorna o estado atual como tupla
        return tuple(self.board.flatten())

    def get_available_actions(self):
        # Retorna posições vazias
        return [(i, j) for i in range(3) for j in range(3) if self.board[i, j] == 0]

    def is_winner(self, player):
        # Verifica vitória em linhas, colunas ou diagonais
        return any(np.all(self.board[i, :] == player) for i in range(3)) or \
               any(np.all(self.board[:, j] == player) for j in range(3)) or \
               np.all(np.diag(self.board) == player) or \
               np.all(np.diag(np.fliplr(self.board)) == player)

    def is_draw(self):
        # Verifica empate (tabuleiro cheio sem vencedor)
        return np.all(self.board != 0) and not self.is_winner(1) and not self.is_winner(-1)

    def get_reward(self, player_perspective):
        # Retorna recompensa: 1 = vitória, -1 = derrota, 0.5 = empate
        if self.is_winner(player_perspective):
            return 1
        elif self.is_winner(-player_perspective):
            return -1
        elif self.is_draw():
            return 0.5
        return 0

    def step(self, action):
        # Executa uma jogada
        if self.board[action[0], action[1]] != 0:
            return self.get_state(), -10, True, {"error": "Invalid action"}
        self.board[action[0], action[1]] = self.current_player
        reward = self.get_reward(self.current_player)
        done = reward in [1, -1, 0.5]
        self.current_player *= -1
        return self.get_state(), reward, done, {}

    def render(self):
        # Mostra o tabuleiro
        chars = {1: 'X', -1: 'O', 0: ' '}
        print("\n".join([" | ".join([chars[x] for x in row]) for row in self.board]))
        print("---" * 3)

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.999, epsilon_min=0.01):
        # Inicializa o agente Q-learning
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def get_q_value(self, state, action):
        # Retorna Q(s, a) ou 0 se não existir
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, available_actions):
        # Escolhe ação com epsilon-greedy
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions)
        q_values = [self.get_q_value(state, a) for a in available_actions]
        max_q = max(q_values)
        return random.choice([a for a, q in zip(available_actions, q_values) if q == max_q])

    def update_q_table(self, state, action, reward, next_state, next_available_actions, done):
        # Atualiza Q(s, a) com a equação de Bellman
        old_q = self.get_q_value(state, action)
        next_max_q = max([self.get_q_value(next_state, a) for a in next_available_actions], default=0.0)
        target_q = reward if done else reward + self.gamma * next_max_q
        self.q_table[(state, action)] = old_q + self.alpha * (target_q - old_q)

    def decay_epsilon(self):
        # Reduz epsilon ao longo do tempo
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

def train_agent(episodes=50000):
    # Treina o agente
    env = TicTacToeEnv()
    agent = QLearningAgent(alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_decay=0.9999, epsilon_min=0.05)
    for episode in range(episodes):
        state = env.reset()
        done = False
        while not done:
            if env.current_player == 1:
                action = agent.choose_action(state, env.get_available_actions())
                next_state, reward, done, _ = env.step(action)
                agent.update_q_table(state, action, reward, next_state, env.get_available_actions(), done)
                state = next_state
            else:
                action = random.choice(env.get_available_actions())
                state, _, done, _ = env.step(action)
        agent.decay_epsilon()
    with open('../data/policy.pkl', 'wb') as f:
        pickle.dump({s: max([q for (s_, a), q in agent.q_table.items() if s_ == s], default=0) for s in set(s for s, _ in agent.q_table)}, f)

if __name__ == '__main__':
    train_agent(episodes=100000)
