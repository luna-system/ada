// src/scripts/app.ts
// Get API base URL from config (set via config.js)
var API_BASE_URL = window.API_BASE_URL || '/api';

var messagesEl = document.getElementById("messages");
var healthDot = document.querySelector("header .brand .dot");
var form = document.getElementById("composer");
var input = document.getElementById("prompt");
var includeThinkingEl = document.getElementById("includeThinking");
var entityInput = document.getElementById("entity");
var panelMenuBtn = document.getElementById("panelMenuButton");
var panelMenu = document.getElementById("panelMenu");
var debugPanel = document.getElementById("debugPanel");
var closeDebugBtn = document.getElementById("closeDebug");
var memPanel = document.getElementById("memPanel");
var closeMemBtn = document.getElementById("closeMem");
var refreshMemBtn = document.getElementById("refreshMem");
var memListEl = document.getElementById("memList");
var memFilterEntityEl = document.getElementById("memFilterEntity");
var addMemBtn = document.getElementById("addMem");
var memTextEl = document.getElementById("memText");
var memImportanceEl = document.getElementById("memImportance");
var memEntityScopedEl = document.getElementById("memEntityScoped");
var memEntityRow = document.getElementById("memEntityRow");
var memEntityInput = document.getElementById("memEntityInput");
var refreshStatusBtn = document.getElementById("refreshStatus");
var statusBoxEl = document.getElementById("statusBox");
var clientLibsEl = document.getElementById("clientLibs");
var refreshClientLibsBtn = document.getElementById("refreshClientLibs");
var thinkingEl = null;
var lastAssistantText = "";
var conversationId = localStorage.getItem("conversation_id");
if (!conversationId && window.crypto && crypto.randomUUID) {
  conversationId = crypto.randomUUID();
  localStorage.setItem("conversation_id", conversationId);
}
var currentEntity = localStorage.getItem("entity") || "";
if (entityInput) {
  entityInput.value = currentEntity;
  entityInput.addEventListener("change", () => {
    currentEntity = entityInput.value.trim();
    localStorage.setItem("entity", currentEntity);
  });
}
function hidePanels() {
  if (memPanel) memPanel.hidden = true;
  if (debugPanel) debugPanel.hidden = true;
}
function hideMenu() {
  if (panelMenu) panelMenu.hidden = true;
  if (panelMenuBtn) panelMenuBtn.setAttribute("aria-expanded", "false");
}
function wireEntityToggle() {
  if (!memEntityScopedEl) return;
  if (memEntityRow) memEntityRow.hidden = !memEntityScopedEl.checked;
  memEntityScopedEl.addEventListener("change", () => {
    if (!memEntityRow) return;
    memEntityRow.hidden = !memEntityScopedEl.checked;
    if (memEntityScopedEl.checked && memEntityInput) {
      const scopeEntity = (entityInput?.value || memFilterEntityEl?.value || "").trim();
      memEntityInput.value = scopeEntity;
      memEntityInput.focus();
    }
  });
}
function attachSaveMemoryButton(stackEl, text) {
  if (!stackEl || !text) return;
  const btn = document.createElement("button");
  btn.className = "ghost save-mem";
  btn.type = "button";
  btn.textContent = "Save to memory";
  btn.addEventListener("click", () => {
    if (memTextEl) memTextEl.value = text;
    if (memFilterEntityEl) memFilterEntityEl.value = currentEntity || "";
    if (memEntityInput) memEntityInput.value = currentEntity || "";
    if (memEntityScopedEl) memEntityScopedEl.checked = !!currentEntity;
    if (memEntityRow) memEntityRow.hidden = !(memEntityScopedEl?.checked ?? false);
    hidePanels();
    hideMenu();
    if (memPanel) memPanel.hidden = false;
  });
  stackEl.appendChild(btn);
}
async function refreshHealth() {
  if (!healthDot) return;
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const ok = !!data.ok;
    healthDot.classList.toggle("ok", ok);
    healthDot.classList.toggle("bad", !ok);
    healthDot.title = ok ? "Brain: healthy" : "Brain: unavailable";
    healthDot.setAttribute("aria-label", healthDot.title);
  } catch (err) {
    healthDot.classList.remove("ok");
    healthDot.classList.add("bad");
    healthDot.title = "Brain: unavailable";
    healthDot.setAttribute("aria-label", healthDot.title);
  }
}
refreshHealth();
setInterval(refreshHealth, 1e4);
function addMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "me" ? "\u{1F9D1}" : "\u{1F916}";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  renderMarkdownToElement(bubble, String(text || ""), { allowBlocks: true });
  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "smooth" });
  updateClientLibStatus();
}
function showThinking() {
  if (thinkingEl) return;
  thinkingEl = document.createElement("div");
  thinkingEl.className = "msg thinking";
  const spin = document.createElement("div");
  spin.className = "spinner";
  spin.setAttribute("aria-hidden", "true");
  spin.title = "Thinking...";
  thinkingEl.appendChild(spin);
  messagesEl.appendChild(thinkingEl);
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "smooth" });
}
function hideThinking() {
  if (thinkingEl) {
    thinkingEl.remove();
    thinkingEl = null;
  }
}
function replaceThinkingWithBot(text) {
  const wrap = document.createElement("div");
  wrap.className = "msg bot";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "\u{1F916}";
  const stack = document.createElement("div");
  stack.className = "stack";
  const thinkMatch = /<think>([\s\S]*?)<\/think>([\s\S]*)/i.exec(text || "");
  if (includeThinkingEl.checked && thinkMatch) {
    const thinkDetails = document.createElement("details");
    thinkDetails.className = "bubble think";
    const summary = document.createElement("summary");
    summary.textContent = "Thinking";
    const content = document.createElement("div");
    content.className = "think-content";
    renderMarkdownToElement(content, (thinkMatch[1] || "").trim(), { allowBlocks: true });
    thinkDetails.appendChild(summary);
    thinkDetails.appendChild(content);
    stack.appendChild(thinkDetails);
    const answerBubble = document.createElement("div");
    answerBubble.className = "bubble answer";
    renderMarkdownToElement(answerBubble, (thinkMatch[2] || "").trim(), { allowBlocks: true });
    stack.appendChild(answerBubble);
  } else {
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    renderMarkdownToElement(bubble, (thinkMatch ? thinkMatch[2] || "" : text || "") || "", { allowBlocks: true });
    stack.appendChild(bubble);
  }
  wrap.appendChild(avatar);
  wrap.appendChild(stack);
  if (thinkingEl && thinkingEl.parentNode) {
    thinkingEl.replaceWith(wrap);
    thinkingEl = null;
  } else {
    messagesEl.appendChild(wrap);
  }
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "smooth" });
  lastAssistantText = (thinkMatch ? thinkMatch[2] || "" : text || "").trim();
  attachSaveMemoryButton(stack, lastAssistantText);
}
function renderMarkdownToElement(el, markdownText, options = { allowBlocks: false }) {
  const { allowBlocks = false } = options || {};
  if (!el) return;
  const md = String(markdownText || "");
  try {
    const fencedRegex = /(^|\n)```(\w+)?\n([\s\S]*?)\n```/m;
    const hasFenced = fencedRegex.test(md);
    const otherBlockRegex = /(^|\n)( {4,}|\#{1,6}\s+|>\s+|[-*+]\s+|\d+\.\s+)/m;
    const hasOtherBlocks = otherBlockRegex.test(md);
    let rawHtml;
    if (allowBlocks) {
      if (typeof marked !== "undefined" && typeof marked.parse === "function") {
        try {
          if (typeof hljs !== "undefined" && typeof hljs.highlight !== "undefined") {
            marked.setOptions({
              highlight: function(code, lang) {
                try {
                  if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                  }
                  return hljs.highlightAuto(code).value;
                } catch (e) {
                  return code;
                }
              }
            });
          }
          rawHtml = marked.parse(md);
        } catch (e) {
          rawHtml = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
        }
      } else {
        rawHtml = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
      }
    } else if (hasFenced && !hasOtherBlocks) {
      if (typeof marked !== "undefined" && typeof marked.parse === "function") {
        try {
          if (typeof hljs !== "undefined" && typeof hljs.highlight !== "undefined") {
            marked.setOptions({
              highlight: function(code, lang) {
                try {
                  if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                  }
                  return hljs.highlightAuto(code).value;
                } catch (e) {
                  return code;
                }
              }
            });
          }
          rawHtml = marked.parse(md);
        } catch (e) {
          rawHtml = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
        }
      } else {
        rawHtml = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
      }
    } else if (!hasOtherBlocks) {
      if (typeof marked !== "undefined" && typeof marked.parseInline === "function") {
        rawHtml = marked.parseInline(md);
      } else if (typeof marked !== "undefined" && typeof marked.parse === "function") {
        rawHtml = marked.parse(md);
        rawHtml = rawHtml.replace(/^<p>([\s\S]*)<\/p>\s*$/i, "$1");
      } else {
        rawHtml = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
      }
    } else {
      rawHtml = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>");
    }
    const sanitizeConfig = typeof DOMPurify !== "undefined" ? allowBlocks ? {
      ALLOWED_TAGS: ["a", "b", "i", "strong", "em", "del", "code", "pre", "p", "br", "ul", "ol", "li", "span", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "img"],
      ALLOWED_ATTR: ["href", "title", "class", "src", "alt"]
    } : {
      ALLOWED_TAGS: ["a", "b", "i", "strong", "em", "code", "pre", "p", "br", "ul", "ol", "li", "span"],
      ALLOWED_ATTR: ["href", "title", "class"]
    } : void 0;
    const clean = typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(rawHtml, sanitizeConfig) : rawHtml;
    el.innerHTML = clean;
    const anchors = el.querySelectorAll("a");
    anchors.forEach((a) => {
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener noreferrer");
    });
    if (typeof hljs !== "undefined" && typeof hljs.highlightElement === "function") {
      el.querySelectorAll("pre code").forEach((codeEl) => {
        try {
          hljs.highlightElement(codeEl);
        } catch (e) {
        }
      });
    }
  } catch (e) {
    el.textContent = markdownText;
  }
}
function setBusy(busy) {
  form.querySelectorAll("textarea,button").forEach((el) => el.disabled = busy);
  messagesEl.setAttribute("aria-busy", String(busy));
  if (busy) showThinking();
  else hideThinking();
}
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const prompt = input.value.trim();
  if (!prompt) return;
  const lower = prompt.toLowerCase();
  if (lower === "memory: help") {
    addMessage("bot", "Memory commands:\n- memory: list\n- memory: delete <id>");
    input.value = "";
    return;
  }
  if (lower === "memory: list") {
    try {
      setBusy(true);
      const q = new URLSearchParams();
      q.set("limit", "20");
      if (currentEntity) q.set("entity", currentEntity);
      const res = await fetch(`${API_BASE_URL}/memory?${q.toString()}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      const items = data.items || [];
      if (!items.length) {
        addMessage("bot", "No memories stored.");
      } else {
        const lines = items.map((it) => {
          const meta = it.meta || {};
          const imp = meta.importance != null ? ` (importance=${meta.importance})` : "";
          const id = it.id ? `id=${it.id}` : "";
          return `\u2022 ${id}${imp} ${it.text}`;
        });
        addMessage("bot", `Memories:
${lines.join("\n")}`);
      }
    } catch (err) {
      addMessage("bot", `Error listing memories: ${err.message}`);
    } finally {
      setBusy(false);
      input.value = "";
    }
    return;
  }
  if (lower.startsWith("memory: delete ")) {
    const memId = prompt.slice("memory: delete ".length).trim();
    if (!memId) {
      addMessage("bot", "Please provide a memory id to delete.");
    } else {
      try {
        setBusy(true);
        const res = await fetch(`${API_BASE_URL}/memory/${encodeURIComponent(memId)}`, { method: "DELETE" });
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
        addMessage("bot", `Deleted memory ${memId}.`);
      } catch (err) {
        addMessage("bot", `Error deleting memory: ${err.message}`);
      } finally {
        setBusy(false);
        input.value = "";
      }
    }
    return;
  }
  addMessage("me", prompt);
  input.value = "";
  setBusy(true);
  try {
    const res = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        include_thinking: !!includeThinkingEl.checked,
        conversation_id: conversationId,
        entity: currentEntity || void 0
      })
    });
    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }
    hideThinking();
    const wrap = document.createElement("div");
    wrap.className = "msg bot";
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "\u{1F916}";
    const stack = document.createElement("div");
    stack.className = "stack";
    const spinner = document.createElement("div");
    spinner.className = "spinner";
    spinner.setAttribute("aria-hidden", "true");
    spinner.title = "Generating...";
    stack.appendChild(spinner);
    wrap.appendChild(avatar);
    wrap.appendChild(stack);
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    let thinkDetailsEl = null;
    let thinkContentEl = null;
    let answerBubbleEl = null;
    let spinnerRef = spinner;
    let accumulatedText = "";
    let accumulatedThinking = "";
    const reader = res.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const dataStr = line.slice(6);
        try {
          const data = JSON.parse(dataStr);
          if (data.type === "token") {
            if (spinnerRef && spinnerRef.parentNode) {
              spinnerRef.remove();
              spinnerRef = null;
            }
            if (!answerBubbleEl) {
              answerBubbleEl = document.createElement("div");
              answerBubbleEl.className = "bubble answer";
              stack.appendChild(answerBubbleEl);
            }
            accumulatedText += data.content;
            renderMarkdownToElement(answerBubbleEl, accumulatedText, { allowBlocks: true });
            messagesEl.scrollTop = messagesEl.scrollHeight;
          } else if (data.type === "thinking" && includeThinkingEl.checked) {
            if (spinnerRef && spinnerRef.parentNode) {
              spinnerRef.remove();
              spinnerRef = null;
            }
            if (!thinkDetailsEl) {
              thinkDetailsEl = document.createElement("details");
              thinkDetailsEl.className = "bubble think";
              thinkDetailsEl.open = true;
              const summary = document.createElement("summary");
              summary.textContent = "Thinking";
              thinkDetailsEl.appendChild(summary);
              thinkContentEl = document.createElement("div");
              thinkContentEl.className = "think-content";
              thinkDetailsEl.appendChild(thinkContentEl);
              if (answerBubbleEl) {
                stack.insertBefore(thinkDetailsEl, answerBubbleEl);
              } else {
                stack.appendChild(thinkDetailsEl);
              }
            }
            accumulatedThinking += data.content;
            if (thinkContentEl) {
              renderMarkdownToElement(thinkContentEl, accumulatedThinking, { allowBlocks: true });
            }
            messagesEl.scrollTop = messagesEl.scrollHeight;
          } else if (data.type === "done") {
            if (data.conversation_id && data.conversation_id !== conversationId) {
              conversationId = data.conversation_id;
              localStorage.setItem("conversation_id", conversationId);
            }
            lastAssistantText = accumulatedText;
          } else if (data.type === "error") {
            throw new Error(data.error || "Stream error");
          }
        } catch (err) {
          console.error("Error parsing SSE data:", err);
        }
      }
    }
    if (thinkContentEl && accumulatedThinking) {
      renderMarkdownToElement(thinkContentEl, accumulatedThinking, { allowBlocks: true });
    }
    if (answerBubbleEl && accumulatedText) {
      renderMarkdownToElement(answerBubbleEl, accumulatedText, { allowBlocks: true });
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
    attachSaveMemoryButton(stack, accumulatedText.trim());
    if (spinnerRef && spinnerRef.parentNode) {
      spinnerRef.remove();
    }
  } catch (err) {
    console.error(err);
    replaceThinkingWithBot(`Error: ${err.message}`);
  } finally {
    setBusy(false);
    input.focus();
  }
});
addMessage("bot", "Hello! Ask me anything.");
if (typeof window !== "undefined") {
  window.addEventListener("DOMContentLoaded", updateClientLibStatus);
}
input.focus();
function renderStatusBox(data) {
  if (!statusBoxEl) return;
  try {
    const ok = !!data.ok;
    const parts = [];
    parts.push(`Brain: ${ok ? "healthy" : "unavailable"}`);
    if (data.python) parts.push(`Python: ${data.python}`);
    if (data.config) {
      if (data.config.OLLAMA_MODEL) parts.push(`Model: ${data.config.OLLAMA_MODEL}`);
      if (data.config.OLLAMA_BASE_URL) parts.push(`Ollama: ${data.config.OLLAMA_BASE_URL}`);
      if (data.config.CHROMA_URL) parts.push(`Chroma: ${data.config.CHROMA_URL}`);
    }
    if (data.persona && typeof data.persona.loaded !== "undefined") {
      parts.push(`Persona: ${data.persona.loaded ? "loaded" : "missing"}`);
    }
    if (data.chroma) {
      const cOK = data.chroma.ok;
      parts.push(`Chroma heartbeat: ${cOK === null ? "n/a" : cOK ? "ok" : "fail"}`);
    }
    statusBoxEl.textContent = parts.join(" \u2022 ");
    statusBoxEl.classList.toggle("bad", !ok);
  } catch (e) {
    statusBoxEl.textContent = `Status error: ${e.message}`;
    statusBoxEl.classList.add("bad");
  }
}
function updateClientLibStatus() {
  if (!clientLibsEl) return;
  const libs = [
    ["marked", typeof marked !== "undefined"],
    ["DOMPurify", typeof DOMPurify !== "undefined"],
    ["hljs", typeof hljs !== "undefined"]
  ];
  clientLibsEl.textContent = libs.map(([n, ok]) => `${n}:${ok ? "\u2713" : "\u2715"}`).join(" ");
  if (typeof console !== "undefined" && console.debug) console.debug("Client libs:", libs);
}
refreshClientLibsBtn?.addEventListener("click", () => {
  updateClientLibStatus();
});
async function refreshStatusPanel() {
  if (!statusBoxEl) return;
  statusBoxEl.textContent = "Loading\u2026";
  statusBoxEl.classList.remove("bad");
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    const data = await res.json();
    renderStatusBox(data);
  } catch (e) {
    renderStatusBox({ ok: false });
  }
}
function renderMemList(items) {
  memListEl.innerHTML = "";
  if (!items || !items.length) {
    const p = document.createElement("div");
    p.className = "muted";
    p.textContent = "No memories found.";
    memListEl.appendChild(p);
    return;
  }
  items.forEach((it) => {
    const row = document.createElement("div");
    row.className = "mem-item";
    const meta = it.meta || {};
    const scope = meta.scope || "global";
    const imp = meta.importance != null ? ` (importance=${meta.importance})` : "";
    const txt = document.createElement("div");
    txt.className = "mem-text";
    txt.textContent = `[${scope}]${imp} ${it.text}`;
    const actions = document.createElement("div");
    actions.className = "mem-actions";
    if (it.id) {
      const del = document.createElement("button");
      del.className = "icon danger";
      del.title = "Delete memory";
      del.textContent = "\u{1F5D1}";
      del.addEventListener("click", async () => {
        del.disabled = true;
        try {
          const r = await fetch(`${API_BASE_URL}/memory/${encodeURIComponent(it.id)}`, { method: "DELETE" });
          const d = await r.json();
          if (!r.ok || d.error) throw new Error(d.error || `HTTP ${r.status}`);
          await refreshMemList();
        } catch (e) {
          alert(`Delete failed: ${e.message}`);
        } finally {
          del.disabled = false;
        }
      });
      actions.appendChild(del);
    }
    row.appendChild(txt);
    row.appendChild(actions);
    memListEl.appendChild(row);
  });
}
async function refreshMemList() {
  const q = new URLSearchParams();
  q.set("limit", "50");
  const filterEntity = (memFilterEntityEl?.value || "").trim();
  if (filterEntity) q.set("entity", filterEntity);
  const res = await fetch(`/api/memory?${q.toString()}`);
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  renderMemList(data.items || []);
}
closeMemBtn?.addEventListener("click", () => {
  hidePanels();
});
closeDebugBtn?.addEventListener("click", () => {
  hidePanels();
});
panelMenuBtn?.addEventListener("click", () => {
  if (!panelMenu) return;
  const willOpen = !!panelMenu.hidden;
  panelMenu.hidden = !willOpen;
  panelMenuBtn.setAttribute("aria-expanded", String(willOpen));
});
panelMenu?.addEventListener("click", async (e) => {
  const target = e.target;
  if (!(target instanceof HTMLElement)) return;
  const which = target.getAttribute("data-target");
  if (which === "debug") {
    hidePanels();
    hideMenu();
    if (debugPanel) debugPanel.hidden = false;
    try {
      await refreshStatusPanel();
    } catch (err) {
    }
    try {
      updateClientLibStatus();
    } catch (err) {
    }
  } else if (which === "mem") {
    hidePanels();
    hideMenu();
    if (memPanel) {
      memPanel.hidden = false;
      memFilterEntityEl.value = currentEntity || "";
      try {
        await refreshMemList();
      } catch (err) {
      }
    }
  }
});
document.addEventListener("click", (e) => {
  if (!panelMenu || !panelMenuBtn) return;
  if (panelMenu.hidden) return;
  const inside = panelMenu.contains(e.target) || panelMenuBtn.contains(e.target);
  if (!inside) hideMenu();
});
refreshMemBtn?.addEventListener("click", async () => {
  try {
    await refreshMemList();
  } catch (e) {
    alert(e.message);
  }
});
refreshStatusBtn?.addEventListener("click", async () => {
  try {
    await refreshStatusPanel();
  } catch (e) {
    alert(e.message);
  }
});
addMemBtn?.addEventListener("click", async () => {
  const text = (memTextEl.value || "").trim() || lastAssistantText || "";
  if (!text) {
    alert("Nothing to save.");
    return;
  }
  const body = {
    text,
    importance: parseInt(memImportanceEl.value || "3", 10) || 3
  };
  if (memEntityScopedEl?.checked) {
    const scopeEntity = (memEntityInput?.value || entityInput?.value || memFilterEntityEl?.value || "").trim();
    if (scopeEntity) body.entity = scopeEntity;
  }
  if (addMemBtn) addMemBtn.disabled = true;
  try {
    const res = await fetch(`${API_BASE_URL}/memory`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
    memTextEl.value = "";
    if (memEntityInput) memEntityInput.value = "";
    if (memEntityScopedEl) memEntityScopedEl.checked = false;
    if (memEntityRow) memEntityRow.hidden = true;
    await refreshMemList();
  } catch (e) {
    alert(`Add failed: ${e.message}`);
  } finally {
    if (addMemBtn) addMemBtn.disabled = false;
  }
});
wireEntityToggle();
