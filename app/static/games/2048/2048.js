(() => {
  console.log("2048 script loaded");

  const SIZE = 4;
  const START_TILES = 2;
  const boardEl = document.getElementById('gameBoard');
  const scoreEl = document.getElementById('score');
  const bestEl = document.getElementById('best');
  const newBtn = document.getElementById('newGameBtn');
  const undoBtn = document.getElementById('undoBtn');

  if (!boardEl) {
    console.error("2048: #gameBoard element not found.");
    return;
  }

  let grid = createEmptyGrid();
  let score = 0;
  let best = loadBest();
  let history = [];

  function createEmptyGrid() {
    const g = [];
    for (let y = 0; y < SIZE; y++) {
      g[y] = [];
      for (let x = 0; x < SIZE; x++) g[y][x] = 0;
    }
    return g;
  }

  function cloneGrid(g) { return g.map(row => row.slice()); }
  function saveHistory() { history.push({ g: cloneGrid(grid), s: score }); if (history.length > 20) history.shift(); }
  function undo() { if (!history.length) return; const last = history.pop(); grid = cloneGrid(last.g); score = last.s; updateScoreUI(); render(); }

  function loadBest() { try { const b = localStorage.getItem('2048_best_v1'); return b ? parseInt(b, 10) : 0; } catch (e) { return 0; } }
  function saveBest() { try { localStorage.setItem('2048_best_v1', String(best)); } catch (e) {} }

  function buildBoardDOM() {
    boardEl.innerHTML = '';
    boardEl.classList.add('game-2048-board');
    for (let y = 0; y < SIZE; y++) {
      const row = document.createElement('div'); row.className = 'row'; row.style.display = 'flex'; row.style.gap = '12px'; row.style.justifyContent = 'center';
      for (let x = 0; x < SIZE; x++) {
        const cell = document.createElement('div'); cell.className = 'tile cell'; cell.dataset.x = x; cell.dataset.y = y;
        cell.style.width = '110px'; cell.style.height = '110px'; cell.style.borderRadius = '8px'; cell.style.display = 'flex';
        cell.style.alignItems = 'center'; cell.style.justifyContent = 'center'; cell.style.fontSize = '28px'; cell.style.fontWeight = '700';
        cell.style.background = 'rgba(255,255,255,0.02)'; cell.style.boxShadow = 'inset 0 0 0 2px rgba(0,200,200,0.05)';
        row.appendChild(cell);
      }
      boardEl.appendChild(row);
    }
  }

  function render() {
    for (let y = 0; y < SIZE; y++) {
      for (let x = 0; x < SIZE; x++) {
        const val = grid[y][x];
        const cell = boardEl.querySelector(`.cell[data-x="${x}"][data-y="${y}"]`);
        if (!cell) continue;
        if (val === 0) {
          cell.textContent = '';
          cell.style.background = 'rgba(255,255,255,0.02)';
          cell.style.color = 'transparent';
          cell.style.boxShadow = 'inset 0 0 0 2px rgba(0,200,200,0.05)';
        } else {
          cell.textContent = val;
          const colors = {
            2: ['#efeee4','#776e65'],
            4: ['#eee0c8','#776e65'],
            8: ['#f2b179','#fff'],
            16: ['#f59563','#fff'],
            32: ['#f57c5f','#fff'],
            64: ['#f65d3b','#fff'],
            128:['#edce71','#fff'],
            256:['#edc85c','#fff'],
            512:['#edc53b','#fff'],
            1024:['#ecc23c','#fff'],
            2048:['#ebc21a','#fff']
          };
          const c = colors[val] || ['#3c3a32','#fff'];
          cell.style.background = c[0];
          cell.style.color = c[1];
        }
      }
    }
    updateScoreUI();
  }

  function updateScoreUI() { if (scoreEl) scoreEl.textContent = score; if (bestEl) bestEl.textContent = best; }

  function getEmptyCells() { const empties = []; for (let y = 0; y < SIZE; y++) for (let x = 0; x < SIZE; x++) if (grid[y][x] === 0) empties.push({x,y}); return empties; }
  function spawnRandom() { const empties = getEmptyCells(); if (empties.length === 0) return false; const idx = Math.floor(Math.random() * empties.length); const cell = empties[idx]; grid[cell.y][cell.x] = (Math.random() < 0.1) ? 4 : 2; return true; }

  function compressAndMergeRow(row) {
    const filtered = row.filter(v => v !== 0);
    const result = [];
    let gained = 0;
    let moved = false;
    for (let i = 0; i < filtered.length; i++) {
      if (i + 1 < filtered.length && filtered[i] === filtered[i+1]) {
        const val = filtered[i] * 2;
        result.push(val);
        gained += val;
        i++;
        moved = true;
      } else {
        result.push(filtered[i]);
      }
    }
    while (result.length < SIZE) result.push(0);
    for (let i = 0; i < SIZE; i++) if (row[i] !== result[i]) moved = true;
    return { arr: result, gained, moved };
  }

  function moveLeft() {
    saveHistory();
    let movedAny = false;
    let gainedTotal = 0;
    for (let y = 0; y < SIZE; y++) {
      const row = grid[y].slice();
      const r = compressAndMergeRow(row);
      grid[y] = r.arr.slice();
      if (r.moved) movedAny = true;
      gainedTotal += r.gained;
    }
    if (movedAny) {
      score += gainedTotal;
      if (score > best) { best = score; saveBest(); }
      spawnRandom();
      render();
      if (!canMove()) gameOverCheck();
    } else {
      history.pop();
    }
  }

  function moveRight() {
    saveHistory();
    let movedAny = false;
    let gainedTotal = 0;
    for (let y = 0; y < SIZE; y++) {
      const row = grid[y].slice().reverse();
      const r = compressAndMergeRow(row);
      grid[y] = r.arr.reverse().slice();
      if (r.moved) movedAny = true;
      gainedTotal += r.gained;
    }
    if (movedAny) {
      score += gainedTotal;
      if (score > best) { best = score; saveBest(); }
      spawnRandom();
      render();
      if (!canMove()) gameOverCheck();
    } else {
      history.pop();
    }
  }

  function moveUp() {
    saveHistory();
    let movedAny = false;
    let gainedTotal = 0;
    for (let x = 0; x < SIZE; x++) {
      const col = [];
      for (let y = 0; y < SIZE; y++) col.push(grid[y][x]);
      const r = compressAndMergeRow(col);
      for (let y = 0; y < SIZE; y++) grid[y][x] = r.arr[y];
      if (r.moved) movedAny = true;
      gainedTotal += r.gained;
    }
    if (movedAny) {
      score += gainedTotal;
      if (score > best) { best = score; saveBest(); }
      spawnRandom();
      render();
      if (!canMove()) gameOverCheck();
    } else {
      history.pop();
    }
  }

  function moveDown() {
    saveHistory();
    let movedAny = false;
    let gainedTotal = 0;
    for (let x = 0; x < SIZE; x++) {
      const col = [];
      for (let y = SIZE-1; y >= 0; y--) col.push(grid[y][x]);
      const r = compressAndMergeRow(col);
      for (let y = SIZE-1, i = 0; y >= 0; y--, i++) grid[y][x] = r.arr[i];
      if (r.moved) movedAny = true;
      gainedTotal += r.gained;
    }
    if (movedAny) {
      score += gainedTotal;
      if (score > best) { best = score; saveBest(); }
      spawnRandom();
      render();
      if (!canMove()) gameOverCheck();
    } else {
      history.pop();
    }
  }

  function canMove() {
    if (getEmptyCells().length > 0) return true;
    for (let y = 0; y < SIZE; y++) {
      for (let x = 0; x < SIZE; x++) {
        const v = grid[y][x];
        if ((x + 1 < SIZE && grid[y][x+1] === v) || (y + 1 < SIZE && grid[y+1][x] === v)) return true;
      }
    }
    return false;
  }

  function gameOverCheck() {
    if (!canMove()) {
      setTimeout(() => {
        alert("Game Over — no moves left. Press New Game to restart.");
      }, 50);
    }
  }

  function newGame(initial=false) {
    grid = createEmptyGrid();
    score = 0;
    history = [];
    for (let i = 0; i < START_TILES; i++) spawnRandom();
    render();
    if (!initial) {
      boardEl.tabIndex = -1;
      boardEl.focus();
    }
  }

  window.addEventListener('keydown', (e) => {
    const key = e.key;
    if (['ArrowUp','w','W'].includes(key)) { e.preventDefault(); moveUp(); }
    else if (['ArrowDown','s','S'].includes(key)) { e.preventDefault(); moveDown(); }
    else if (['ArrowLeft','a','A'].includes(key)) { e.preventDefault(); moveLeft(); }
    else if (['ArrowRight','d','D'].includes(key)) { e.preventDefault(); moveRight(); }
    else if (key === 'r' || key === 'R') { newGame(); }
    else if (key === 'z' || key === 'Z') { undo(); }
  });

  if (newBtn) newBtn.addEventListener('click', () => newGame());
  if (undoBtn) undoBtn.addEventListener('click', () => undo());

  buildBoardDOM();
  newGame(true);

  window._game2048 = {
    grid, getEmptyCells, spawnRandom, moveLeft, moveRight, moveUp, moveDown, newGame, undo
  };

})();
