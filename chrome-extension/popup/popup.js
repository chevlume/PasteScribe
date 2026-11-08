const $ = (id) => document.getElementById(id);
const textEl = $("text");
const delayEl = $("delay");
const humanizeEl = $("humanize");
const startBtn = $("start");
const stopBtn = $("stop");
const statusEl = $("status");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

function updateDelayLabel() {
  $("delayOut").textContent = `${delayEl.value} ms`;
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

// Inyecta el script (idempotente) en la pestaña y ejecuta una función en él.
async function runInTab(tabId, func, args = []) {
  await chrome.scripting.executeScript({ target: { tabId }, files: ["content.js"] });
  const [injection] = await chrome.scripting.executeScript({
    target: { tabId },
    func: (name, argv) => window.__pastescribe[name](...argv),
    args: [func, args],
  });
  return injection.result;
}

function friendlyError(err) {
  const msg = String(err && err.message ? err.message : err);
  if (/cannot access|chrome:\/\/|extensions gallery|not be scripted/i.test(msg)) {
    return "Esta página no permite extensiones (p. ej. chrome:// o la Chrome Web Store). Abre una página web normal.";
  }
  return `Error: ${msg}`;
}

async function saveSettings() {
  try {
    await chrome.storage.local.set({ delay: Number(delayEl.value), humanize: humanizeEl.checked });
    // El texto puede ser sensible: solo se guarda durante la sesión del navegador.
    await chrome.storage.session.set({ text: textEl.value });
  } catch (_) { /* no es crítico */ }
}

async function loadSettings() {
  try {
    const local = await chrome.storage.local.get({ delay: 60, humanize: true });
    const session = await chrome.storage.session.get({ text: "" });
    delayEl.value = local.delay;
    humanizeEl.checked = local.humanize;
    textEl.value = session.text;
  } catch (_) { /* valores por defecto */ }
  updateDelayLabel();
}

async function refreshStatus() {
  try {
    const tab = await getActiveTab();
    if (!tab) return;
    const st = await runInTab(tab.id, "status");
    if (st.running) {
      startBtn.disabled = true;
      stopBtn.disabled = false;
      setStatus(st.phase === "waiting"
        ? "Esperando a que hagas clic en un campo de texto…"
        : `Escribiendo… ${st.typed}/${st.total}`);
    } else if (st.message) {
      setStatus(st.message);
    }
  } catch (err) {
    setStatus(friendlyError(err), true);
    startBtn.disabled = true;
  }
}

startBtn.addEventListener("click", async () => {
  const text = textEl.value;
  if (!text) {
    setStatus("Pega primero el texto que quieres escribir.", true);
    return;
  }
  try {
    const tab = await getActiveTab();
    const res = await runInTab(tab.id, "start", [{
      text,
      delayMs: Number(delayEl.value),
      humanize: humanizeEl.checked,
    }]);
    if (!res.ok) {
      setStatus(res.error, true);
      return;
    }
    // Cerrar el popup devuelve el foco a la página y a su campo de texto.
    window.close();
  } catch (err) {
    setStatus(friendlyError(err), true);
  }
});

stopBtn.addEventListener("click", async () => {
  try {
    const tab = await getActiveTab();
    await runInTab(tab.id, "stop");
    stopBtn.disabled = true;
    startBtn.disabled = false;
    setStatus("Detenido.");
  } catch (err) {
    setStatus(friendlyError(err), true);
  }
});

delayEl.addEventListener("input", () => { updateDelayLabel(); saveSettings(); });
humanizeEl.addEventListener("change", saveSettings);
textEl.addEventListener("input", saveSettings);

(async () => {
  await loadSettings();
  await refreshStatus();
})();
