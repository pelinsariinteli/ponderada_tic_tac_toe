# 🎮 Jogo da Velha com Reinforcement Learning

Este projeto implementa um agente inteligente para jogar Jogo da Velha (Tic Tac Toe) utilizando técnicas de Reinforcement Learning, especificamente Q-learning. O agente foi treinado para jogar de forma ótima contra um adversário humano, aprendendo através de múltiplos episódios de simulação.

## 📽️ Demonstração

[TIc Tac Toe Aqui](https://ponderada-tic-tac-toe.onrender.com/)

<!-- Insira aqui o link para seu vídeo de demonstração -->
[![Veja a demonstração do jogo](https://img.youtube.com/vi/SEU_VIDEO_ID_AQUI/0.jpg)](https://www.youtube.com/watch?v=SEU_VIDEO_ID_AQUI)

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Modelagem do Ambiente](#modelagem-do-ambiente)
4. [Implementação do Agente Q-Learning](#implementação-do-agente-q-learning)
5. [Resultados do Treinamento](#resultados-do-treinamento)
6. [Como Executar](#como-executar)
7. [Tecnologias Utilizadas](#tecnologias-utilizadas)

## 🔍 Visão Geral

O projeto foi desenvolvido inteiramente do zero, desde a modelagem do ambiente de simulação até o treinamento do agente, sem utilizar bibliotecas específicas de RL, usando apenas NumPy para operações numéricas básicas. A interface web permite que o usuário jogue contra o agente treinado, proporcionando uma experiência interativa para testar a eficácia do aprendizado.

## 📁 Estrutura do Projeto

```
tic_tac_toe_rl/
├── agent/
│   └── rl_agent.py      # Implementação do ambiente e agente RL
├── data/
│   └── policy.pkl       # Política treinada salva
├── server/
│   └── app.py           # API Flask para interação com o frontend
├── web/
│   ├── app.js           # Lógica do frontend
│   ├── index.html       # Estrutura HTML
│   └── style.css        # Estilos da interface
└── README.md            # Documentação
```

## 🌍 Modelagem do Ambiente

O ambiente foi modelado como um Processo de Decisão de Markov (MDP), onde:

### 1. Estados (`TicTacToeEnv.get_state()`)
- O tabuleiro é representado como uma matriz 3x3 no ambiente (internamente, um array NumPy).
- Para facilitar o uso como chave em dicionários, o estado é convertido para uma tupla com 9 elementos.
- Cada célula pode ter um dos valores: 0 (vazio), 1 (X - jogador/agente), -1 (O - oponente).

### 2. Ações (`TicTacToeEnv.get_available_actions()`)
- As ações são representadas como tuplas (linha, coluna) indicando onde jogar.
- Em cada estado, apenas ações em células vazias são consideradas válidas.

### 3. Transições de Estado (`TicTacToeEnv.step()`)
- Ao executar uma ação, o estado do tabuleiro é atualizado com o símbolo do jogador atual.
- A função retorna: (próximo_estado, recompensa, terminado, info_extra).
- O jogador é alternado após cada jogada (self.current_player *= -1).

### 4. Função de Recompensa (`TicTacToeEnv.get_reward()`)
- **+1**: Vitória do jogador atual
- **-1**: Derrota do jogador atual (vitória do oponente)
- **+0.5**: Empate (tabuleiro cheio sem vencedor)
- **0**: Estado não terminal
- **-10**: Penalidade por tentativa de jogada inválida (nunca deveria ocorrer com agente funcionando corretamente)

### 5. Condições de Fim de Jogo
- **Vitória**: 3 símbolos iguais em linha, coluna ou diagonal
- **Empate**: Tabuleiro completamente preenchido sem condição de vitória

## 🧠 Implementação do Agente Q-Learning

O agente foi implementado utilizando o algoritmo Q-learning, que aproxima a função de valor ótima através de experiências.

### 1. Q-Table
- Estrutura de dados principal: dicionário Python que mapeia pares (estado, ação) para valores Q.
- Inicialização: Q-valores começam em 0 para todos os pares estado-ação não visitados.

### 2. Equação de Bellman para Q-Learning
A atualização dos valores Q é feita através da equação de Bellman:

```
Q(s, a) = Q(s, a) + α * [r + γ * max_a' Q(s', a') - Q(s, a)]
```

Onde:
- `Q(s, a)` é o valor atual do par estado-ação
- `α` é a taxa de aprendizado (alpha)
- `r` é a recompensa imediata
- `γ` é o fator de desconto (gamma)
- `max_a' Q(s', a')` é o valor máximo possível no próximo estado

A implementação é realizada no método `update_q_table()` do agente:

```python
def update_q_table(self, state, action, reward, next_state, next_available_actions, done):
    old_q_value = self.get_q_value(state, action)
    
    if done:
        target_q_value = reward
    else:
        if not next_available_actions:
            next_max_q = 0.0
        else:
            next_q_values = [self.get_q_value(next_state, next_action) for next_action in next_available_actions]
            next_max_q = max(next_q_values) if next_q_values else 0.0
        target_q_value = reward + self.gamma * next_max_q
        
    new_q_value = old_q_value + self.alpha * (target_q_value - old_q_value)
    self.q_table[(state, action)] = new_q_value
```

### 3. Estratégia de Exploração Epsilon-Greedy
Para balancear exploração (descobrir novas estratégias) e explotação (usar o conhecimento adquirido), implementamos a estratégia epsilon-greedy:

```python
def choose_action(self, state, available_actions):
    if random.uniform(0, 1) < self.epsilon:
        return random.choice(available_actions)  # Exploração
    else:
        # Explotação: escolhe a ação com maior Q-valor
        q_values = [self.get_q_value(state, a) for a in available_actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(available_actions, q_values) if q == max_q]
        return random.choice(best_actions)
```

Durante o treinamento, o valor de epsilon decai gradualmente para priorizar explotação à medida que o agente ganha experiência:

```python
def decay_epsilon(self):
    if self.epsilon > self.epsilon_min:
        self.epsilon *= self.epsilon_decay
```

## 📊 Resultados do Treinamento

O agente foi treinado por 100.000 episódios, jogando contra um oponente que fazia jogadas aleatórias. Os hiperparâmetros utilizados foram:

- **Taxa de aprendizado (α)**: 0.1
- **Fator de desconto (γ)**: 0.9
- **Epsilon inicial**: 1.0
- **Decaimento de epsilon**: 0.9999
- **Epsilon mínimo**: 0.05

A cada 1000 episódios, foram registradas estatísticas de desempenho:

| Episódio | Vitórias | Derrotas | Empates | Epsilon |
|----------|----------|----------|---------|---------|
| 1000     | 652      | 124      | 224     | 0.9048  |
| 10000    | 843      | 22       | 135     | 0.3679  |
| 50000    | 901      | 5        | 94      | 0.0819  |
| 100000   | 952      | 2        | 46      | 0.0500  |

Observa-se que, ao final do treinamento, o agente atingiu uma taxa de vitória acima de 95%, raramente perdendo e com poucos empates, demonstrando que o aprendizado foi efetivo.

## ▶️ Como Executar

### 🔧 Pré-requisitos
- Python 3.7+ instalado
- Navegador web moderno (Chrome, Firefox, Edge)
- Acesso à linha de comando/terminal

### 📦 Instalação das dependências

1. Abra um terminal (PowerShell ou Prompt de Comando)
2. Execute o comando abaixo para instalar todas as dependências necessárias:

```bash
pip install numpy flask flask-cors
```

### 🎓 Treinamento do Agente (Opcional)

Se quiser treinar seu próprio agente em vez de usar o modelo pré-treinado:

1. Navegue até a pasta do agente:
```bash
cd c:\caminho\para\tic_tac_toe_rl\agent
```

2. Execute o script de treinamento:
```bash
python rl_agent.py
```

3. Aguarde o processo de treinamento (pode levar alguns minutos). Você verá o progresso a cada 1000 episódios.
   
4. Ao finalizar, o arquivo `policy_q_learning.pkl` será gerado na pasta `data`.

5. Para usar o novo modelo treinado, renomeie o arquivo gerado:
```bash
copy ..\data\policy_q_learning.pkl ..\data\policy.pkl
```
   Ou altere a linha 9 do arquivo `server/app.py` para carregar o novo arquivo.

### 🚀 Iniciando o Servidor

1. Abra um novo terminal ou use o terminal atual

2. Navegue até a pasta do servidor:
```bash
cd c:\caminho\para\tic_tac_toe_rl\server
```

3. Inicie o servidor Flask:
```bash
python app.py
```

4. Você verá uma mensagem indicando que o servidor está rodando em `http://127.0.0.1:5000/` ou `http://localhost:5000/`

### 🎮 Jogando contra o Agente

1. Com o servidor em execução, abra o arquivo `web/index.html` no seu navegador.
   - Opção 1: Navegue até a pasta no explorador de arquivos e dê um duplo clique no arquivo
   - Opção 2: Abra seu navegador e arraste o arquivo HTML para a janela
   - Opção 3: No navegador, use Ctrl+O e selecione o arquivo

2. A interface do jogo será carregada e você poderá jogar contra o agente:
   - Clique em uma célula vazia para fazer sua jogada (X)
   - O agente (O) responderá automaticamente
   - O status do jogo aparecerá abaixo do tabuleiro
   - Use o botão "Reiniciar" para começar um novo jogo

### 🔍 Solucionando Problemas Comuns

1. **Erro de Conexão Recusada**:
   - Verifique se o servidor está rodando em `http://localhost:5000/`
   - Certifique-se de que não há firewalls bloqueando a comunicação

2. **Arquivo de Política Não Encontrado**:
   - Verifique se existe um arquivo `policy.pkl` na pasta `data`
   - Se precisar, treine um novo modelo conforme as instruções acima

3. **Erro ao Instalar Dependências**:
   - Tente atualizar o pip: `python -m pip install --upgrade pip`
   - Em seguida, instale as dependências novamente

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal para implementação do agente e ambiente.
- **NumPy**: Biblioteca para operações numéricas e manipulação de matrizes.
- **Flask**: Framework web leve para criar a API que serve o agente treinado.
- **Flask-CORS**: Extensão para lidar com Cross-Origin Resource Sharing na API.
- **JavaScript**: Linguagem para implementação da lógica do cliente web.
- **HTML/CSS**: Estrutura e estilização da interface.
