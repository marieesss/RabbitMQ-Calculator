let intervalId = null;
let awaitingResult = false;
let expectedResults = [];
let currentLogs = new Set();
let lastSeenLogs = new Set();

function snapshotLogsBeforeSubmit(callback) {
  fetch('/logs')
    .then(res => res.json())
    .then(logs => {
      lastSeenLogs = new Set(logs.map(normalizeLog));
      callback(); 
    })
    .catch(err => {
      console.error("Erreur snapshot logs :", err);
      lastSeenLogs = new Set(); 
      callback();
    });
}

document.getElementById('calc-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const n1 = document.getElementById('n1').value;
  const n2 = document.getElementById('n2').value;
  const operation = document.getElementById('operation').value;

  snapshotLogsBeforeSubmit(() => {
    currentLogs = new Set(); 

    if (operation === 'all') {
      expectedResults = ['add', 'sub', 'div', 'mul'].map(op => normalizeLog(`${n1} ${op} ${n2} =`));
    } else {
      expectedResults = [normalizeLog(`${n1} ${operation} ${n2} =`)];
    }

    awaitingResult = true;

    fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ n1, n2, operation })
    })
      .then(res => res.json())
      .then(data => {
        addToHistory(`[Envoi] ${n1} ${operation} ${n2} envoyé`);
        addToHistory(`[Attente] Résultat en cours de traitement...`);

        if (!intervalId) {
          intervalId = setInterval(fetchLogs, 3000);
        }
      })
      .catch(err => {
        console.error(err);
        addToHistory("Erreur lors de l'envoi.");
      });
  });
});

function addToHistory(text) {
  const li = document.createElement('li');
  li.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
  document.getElementById('history').prepend(li);
}

function normalizeLog(log) {
  return log.trim().replace(/\s+/g, ' ');
}

function fetchLogs() {
  fetch('/logs')
    .then(res => res.json())
    .then(logs => {
      if (!logs || logs.length === 0) return;

      logs.forEach(log => {
        const normalized = normalizeLog(log);

        if (!lastSeenLogs.has(normalized) && !currentLogs.has(normalized)) {
          addToHistory(`[Résultat] ${log}`);
          currentLogs.add(normalized);
        }
      });

      if (awaitingResult) {
        const allFound = expectedResults.every(expected =>
          Array.from(currentLogs).some(log => log.includes(expected))
        );

        if (allFound) {
          awaitingResult = false;
          expectedResults = [];
          clearInterval(intervalId);
          intervalId = null;
        }
      }
    })
    .catch(err => console.error("Erreur récupération logs :", err));
}