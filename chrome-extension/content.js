// PasteScribe: script que se inyecta en la pestaña activa (marco principal y
// iframes del mismo origen). Escribe el texto carácter a carácter en el campo
// editable que tenga el foco. Se puede inyectar varias veces sin efectos.
(() => {
  if (window.__pastescribe) return;

  const TEXT_INPUT_TYPES = new Set(["", "text", "search", "url", "tel", "email", "password", "number"]);
  const WAIT_FOR_FIELD_MS = 60000;

  const state = { running: false, stop: false, phase: "idle", typed: 0, total: 0, message: "" };

  // ---------- utilidades ----------
  function deepActiveElement() {
    let el = document.activeElement;
    for (;;) {
      if (!el) return null;
      if (el.shadowRoot && el.shadowRoot.activeElement) {
        el = el.shadowRoot.activeElement;
        continue;
      }
      if (el.tagName === "IFRAME" || el.tagName === "FRAME") {
        try {
          const inner = el.contentDocument && el.contentDocument.activeElement;
          if (inner) {
            el = inner;
            continue;
          }
        } catch (_) { /* iframe de otro origen: no accesible */ }
      }
      return el;
    }
  }

  function isTextarea(el) { return el && el.tagName === "TEXTAREA"; }
  function isInput(el) { return el && el.tagName === "INPUT"; }

  function isEditable(el) {
    if (!el) return false;
    if (isTextarea(el)) return !el.readOnly && !el.disabled;
    if (isInput(el)) return TEXT_INPUT_TYPES.has((el.type || "").toLowerCase()) && !el.readOnly && !el.disabled;
    return el.isContentEditable === true;
  }

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // Duerme en trozos para poder detenerse al instante.
  async function interruptibleSleep(ms) {
    let left = ms;
    while (left > 0 && !state.stop) {
      const step = Math.min(30, left);
      await sleep(step);
      left -= step;
    }
    return state.stop;
  }

  function charDelay(base, humanize, ch) {
    let d = Math.max(0, base);
    if (!humanize) return d;
    d *= 0.5 + Math.random();
    if (ch === " " || ch === "\n") d *= 1.8;
    else if (".,;:!?".includes(ch)) d *= 2.5;
    return d;
  }

  // ---------- escritura ----------
  function dispatchKey(el, type, ch) {
    try {
      el.dispatchEvent(new KeyboardEvent(type, { key: ch, bubbles: true, cancelable: true, composed: true }));
    } catch (_) { /* no es crítico */ }
  }

  // Alternativa si execCommand no está disponible: asigna el valor con el
  // setter nativo (compatible con React/Vue) y lanza el evento "input".
  function insertViaSetter(el, text) {
    const proto = isTextarea(el) ? el.ownerDocument.defaultView.HTMLTextAreaElement.prototype
                                 : el.ownerDocument.defaultView.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    const start = el.selectionStart ?? el.value.length;
    const end = el.selectionEnd ?? el.value.length;
    setter.call(el, el.value.slice(0, start) + text + el.value.slice(end));
    try { el.setSelectionRange(start + text.length, start + text.length); } catch (_) { /* tipos sin selección */ }
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: text, inputType: "insertText" }));
    return true;
  }

  function insertChar(el, ch) {
    const doc = el.ownerDocument;
    if (ch === "\n") {
      if (isTextarea(el)) return doc.execCommand("insertText", false, "\n") || insertViaSetter(el, "\n");
      if (isInput(el)) return doc.execCommand("insertText", false, " ") || insertViaSetter(el, " ");
      return doc.execCommand("insertParagraph") || doc.execCommand("insertLineBreak");
    }
    dispatchKey(el, "keydown", ch);
    let ok = doc.execCommand("insertText", false, ch);
    if (!ok && (isTextarea(el) || isInput(el))) ok = insertViaSetter(el, ch);
    dispatchKey(el, "keyup", ch);
    return ok;
  }

  // ---------- indicador en pantalla ----------
  let overlayHost = null;
  let overlayText = null;

  function showOverlay(message) {
    if (window !== window.top) return;
    if (!overlayHost) {
      overlayHost = document.createElement("div");
      overlayHost.style.cssText = "all:initial;position:fixed;right:16px;bottom:16px;z-index:2147483647;";
      const root = overlayHost.attachShadow({ mode: "closed" });
      const box = document.createElement("div");
      box.style.cssText = "font:13px/1.4 system-ui,sans-serif;background:#1f2937;color:#fff;padding:8px 12px;" +
        "border-radius:8px;box-shadow:0 4px 14px rgba(0,0,0,.35);display:flex;gap:10px;align-items:center;max-width:340px;";
      overlayText = document.createElement("span");
      const btn = document.createElement("button");
      btn.textContent = "Detener";
      btn.style.cssText = "font:inherit;cursor:pointer;border:0;border-radius:5px;padding:3px 9px;background:#ef4444;color:#fff;";
      btn.addEventListener("click", () => stop());
      box.append(overlayText, btn);
      root.append(box);
      (document.body || document.documentElement).append(overlayHost);
    }
    overlayText.textContent = message;
  }

  function hideOverlay() {
    if (overlayHost) overlayHost.remove();
    overlayHost = overlayText = null;
  }

  function onKeydown(e) {
    if (e.key === "Escape" && state.running) {
      e.preventDefault();
      e.stopPropagation();
      stop();
    }
  }

  // ---------- flujo principal ----------
  async function waitForField() {
    const deadline = Date.now() + WAIT_FOR_FIELD_MS;
    let announced = false;
    while (!state.stop && Date.now() < deadline) {
      const el = deepActiveElement();
      if (isEditable(el) && document.hasFocus()) return el;
      if (!announced) {
        state.phase = "waiting";
        showOverlay("PasteScribe: haz clic en un campo de texto para empezar (Esc cancela)");
        announced = true;
      }
      await sleep(120);
    }
    return null;
  }

  async function start(cfg) {
    if (state.running) return { ok: false, error: "Ya hay una escritura en curso." };
    const text = String(cfg.text ?? "").replace(/\r\n?/g, "\n");
    if (!text) return { ok: false, error: "No hay texto que escribir." };

    Object.assign(state, { running: true, stop: false, phase: "waiting", typed: 0, total: text.length, message: "" });
    document.addEventListener("keydown", onKeydown, true);
    run(text, cfg).catch((err) => finish(`Error: ${err && err.message ? err.message : err}`));
    return { ok: true };
  }

  async function run(text, cfg) {
    const target = await waitForField();
    if (!target) return finish(state.stop ? "Cancelado." : "No se encontró ningún campo de texto.");

    state.phase = "typing";
    const chars = Array.from(text); // respeta emojis y caracteres compuestos
    state.total = chars.length;
    const delay = Number(cfg.delayMs) || 0;
    let skipped = 0;

    for (let i = 0; i < chars.length; i++) {
      if (state.stop) break;
      if (deepActiveElement() !== target) {
        return finish(`Detenido: el campo perdió el foco (${state.typed} de ${chars.length} caracteres).`);
      }
      showOverlay(`PasteScribe: escribiendo ${i + 1}/${chars.length} (Esc para detener)`);
      if (insertChar(target, chars[i])) state.typed++;
      else skipped++;
      if (i < chars.length - 1 && (await interruptibleSleep(charDelay(delay, !!cfg.humanize, chars[i])))) break;
    }

    let msg = state.stop
      ? `Detenido: ${state.typed} de ${chars.length} caracteres escritos.`
      : `Listo: ${state.typed} caracteres escritos.`;
    if (skipped) msg += ` (${skipped} no se pudieron escribir; ¿el campo es un editor propio como Google Docs?)`;
    finish(msg);
  }

  function finish(message) {
    state.running = false;
    state.phase = "idle";
    state.message = message;
    document.removeEventListener("keydown", onKeydown, true);
    hideOverlay();
  }

  function stop() {
    if (state.running) state.stop = true;
  }

  window.__pastescribe = {
    start,
    stop,
    status: () => ({ running: state.running, phase: state.phase, typed: state.typed, total: state.total, message: state.message }),
  };
})();
