const $ = (id) => document.getElementById(id);
const langEl = $("lang");

// Idioma de la interfaz: inglés por defecto; el usuario puede cambiarlo y se recuerda.
// Los textos salen de _locales/<idioma>/messages.json (los mismos que usa la tienda).
let messages = {};
let lang = "en";

function format(entry, subs) {
  const text = entry.message.replace(/\$([A-Za-z0-9_@]+)\$/g,
    (_, name) => ((entry.placeholders && entry.placeholders[name.toLowerCase()]) || { content: "" }).content);
  return text.replace(/\$([1-9])/g, (_, i) => (subs[i - 1] === undefined ? "" : String(subs[i - 1])));
}

const t = (key, ...subs) => (messages[key] ? format(messages[key], subs) : key);

async function loadMessages(wanted) {
  try {
    const res = await fetch(chrome.runtime.getURL(`_locales/${wanted}/messages.json`));
    messages = await res.json();
    lang = wanted;
  } catch (_) {
    if (wanted !== "en") await loadMessages("en");
  }
}

function applyI18n() {
  document.documentElement.lang = lang;
  langEl.value = lang;
  for (const el of document.querySelectorAll("[data-i18n]")) el.textContent = t(el.dataset.i18n);
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) el.placeholder = t(el.dataset.i18nPlaceholder);
  document.body.classList.add("ready");
}

// Los textos que el script de la página necesita para sus avisos en pantalla.
function pageMessages() {
  return Object.fromEntries(Object.entries(messages).filter(([key]) => key.startsWith("cs")));
}

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
    return t("popupErrRestricted");
  }
  return t("popupErrGeneric", msg);
}

async function saveSettings() {
  try {
    await chrome.storage.local.set({ delay: Number(delayEl.value), humanize: humanizeEl.checked });
    // El texto puede ser sensible: solo se guarda durante la sesión del navegador.
    await chrome.storage.session.set({ text: textEl.value });
  } catch (_) { /* no es crítico */ }
}

let wantedLang = "en";

async function loadSettings() {
  try {
    const local = await chrome.storage.local.get({ delay: 60, humanize: true, lang: "en" });
    const session = await chrome.storage.session.get({ text: "" });
    delayEl.value = local.delay;
    humanizeEl.checked = local.humanize;
    textEl.value = session.text;
    wantedLang = local.lang;
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
      setStatus(st.phase === "waiting" ? t("popupWaiting") : t("popupTyping", st.typed, st.total));
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
    setStatus(t("popupErrNoText"), true);
    return;
  }
  try {
    const tab = await getActiveTab();
    const res = await runInTab(tab.id, "start", [{
      text,
      delayMs: Number(delayEl.value),
      humanize: humanizeEl.checked,
      messages: pageMessages(),
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
    setStatus(t("popupStopped"));
  } catch (err) {
    setStatus(friendlyError(err), true);
  }
});

delayEl.addEventListener("input", () => { updateDelayLabel(); saveSettings(); });
humanizeEl.addEventListener("change", saveSettings);
textEl.addEventListener("input", saveSettings);

langEl.addEventListener("change", async () => {
  await loadMessages(langEl.value);
  applyI18n();
  try { await chrome.storage.local.set({ lang }); } catch (_) { /* no es crítico */ }
});

(async () => {
  await loadSettings();
  await loadMessages(wantedLang);
  applyI18n();
  await refreshStatus();
})();
