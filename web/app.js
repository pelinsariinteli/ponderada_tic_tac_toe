const boardDiv = document.getElementById('board');
const statusMessageDiv = document.getElementById('status-message');
let state = Array(9).fill(' ');
let gameActive = true;
let isPlayerTurn = true;

function drawBoard() {
  boardDiv.innerHTML = '';
  state.forEach((cell, idx) => {
    const div = document.createElement('div');
    div.className = 'cell';
    if (cell === 'X') div.classList.add('x');
    if (cell === 'O') div.classList.add('o');
    div.textContent = cell;
    div.onclick = () => makeMove(idx);
    if (cell === ' ' && isPlayerTurn) div.classList.add('cell-hover');
    boardDiv.appendChild(div);
  });
}

async function makeMove(idx) {
  if (!isPlayerTurn || state[idx] !== ' ' || !gameActive) return;

  // Jogada do jogador
  state[idx] = 'X';
  drawBoard();
  isPlayerTurn = false;
  statusMessageDiv.textContent = 'Máquina está pensando...';
  boardDiv.style.pointerEvents = 'none';

  checkGameStatus();
  if (!gameActive) {
    boardDiv.style.pointerEvents = 'auto';
    return;
  }

  try {
    await new Promise(resolve => setTimeout(resolve, 600));
    const res = await fetch('http://localhost:5000/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state })
    });

    if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);

    const data = await res.json();
    state = data.state;
    drawBoard();
    checkGameStatus();

    if (gameActive) {
      statusMessageDiv.textContent = 'Sua vez (X)';
      statusMessageDiv.style.background = '#f2fff5';
    }
  } catch (error) {
    console.error("Erro na jogada da máquina:", error);
    statusMessageDiv.textContent = 'Erro ao comunicar com o servidor.';
    statusMessageDiv.style.background = '#fff0f0';
    gameActive = false;
  } finally {
    if (gameActive) isPlayerTurn = true;
    boardDiv.style.pointerEvents = 'auto';
  }
}

function checkGameStatus() {
  // Verifica vitória ou empate
  const winningCombinations = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Linhas
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Colunas
    [0, 4, 8], [2, 4, 6]  // Diagonais
  ];

  for (const [a, b, c] of winningCombinations) {
    if (state[a] !== ' ' && state[a] === state[b] && state[a] === state[c]) {
      statusMessageDiv.textContent = state[a] === 'X' ? 'Você venceu! 🎉' : 'Máquina venceu!';
      statusMessageDiv.style.background = state[a] === 'X' ? '#e8f5e9' : '#ffebee';
      highlightWinningCells([a, b, c]);
      gameActive = false;
      isPlayerTurn = false;
      return;
    }
  }

  if (!state.includes(' ')) {
    statusMessageDiv.textContent = 'Empate! 😐';
    statusMessageDiv.style.background = '#e8eaf6';
    gameActive = false;
    isPlayerTurn = false;
  }
}

function highlightWinningCells(cells) {
  setTimeout(() => {
    document.querySelectorAll('.cell').forEach((cell, idx) => {
      if (cells.includes(idx)) cell.style.background = '#b3e5fc';
    });
  }, 100);
}

document.getElementById('reset').onclick = () => {
  state = Array(9).fill(' ');
  gameActive = true;
  isPlayer
  // Destaca as células da combinação vencedora
  setTimeout(() => {
    document.querySelectorAll('.cell').forEach((cell, idx) => {
      if (combination.includes(idx)) {
        cell.style.background = '#b3e5fc';
      }
    });
  }, 100);

  gameActive = false;
  isPlayerTurn = false; // Impede mais jogadas
  return;
}

if (!state.includes(' ')) {
  statusMessageDiv.textContent = 'Empate! 😐';
  statusMessageDiv.style.background = '#e8eaf6';
  gameActive = false;
  isPlayerTurn = false; // Impede mais jogadas
  return;
}

// Não limpa a mensagem aqui, makeMove ou reset definirão a próxima mensagem de status.
document.getElementById('reset').onclick = () => {
  state = Array(9).fill(' ');
  gameActive = true;
  isPlayerTurn = true;
  statusMessageDiv.textContent = 'Sua vez (X)';
  statusMessageDiv.style.background = '#f2fff5'; // Verde claro para indicar turno do jogador
  boardDiv.style.pointerEvents = 'auto'; // Garante que o tabuleiro esteja clicável

  // Efeito visual de reset
  boardDiv.style.opacity = '0.5';
  setTimeout(() => {
    drawBoard();
    boardDiv.style.opacity = '1';
  }, 300);
};

drawBoard();
statusMessageDiv.textContent = 'Sua vez (X)'; // Mensagem inicial
statusMessageDiv.style.background = '#f2fff5'; // Verde claro para indicar turno do jogador