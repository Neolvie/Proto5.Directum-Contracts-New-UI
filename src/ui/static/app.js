const ROLE_DEFAULTS = {
  sales: [
    {
      id: "sales-1",
      title: "Согласованность сумм",
      prompt:
        "Проверь, что все суммы в КП согласованы (объем, количество, цена за единицу).",
    },
    {
      id: "sales-2",
      title: "Лимиты скидок",
      prompt:
        "Проверь, что применяемые скидки находятся в пределах разрешенных лимитов.",
    },
    {
      id: "sales-3",
      title: "Обязательные поля КП",
      prompt:
        "Проверь наличие обязательных полей КП (реквизиты, условия доставки, сроки платежа).",
    },
    {
      id: "sales-4",
      title: "Корректность НДС",
      prompt: "Проверь корректность расчета НДС (если применимо).",
    },
    {
      id: "sales-5",
      title: "Срок действия КП",
      prompt: "Проверь, что срок действия КП указан и не истек.",
    },
  ],
  bu: [
    {
      id: "bu-1",
      title: "Соответствие стратегии БЕ",
      prompt:
        "Проверь соответствие условий договора стратегии БЕ и бизнес-процессам.",
    },
    {
      id: "bu-2",
      title: "Сроки и обязательства",
      prompt:
        "Проверь наличие и корректность сроков (поставки, выполнения, платежей).",
    },
    {
      id: "bu-3",
      title: "Согласованность комплекта",
      prompt:
        "Проверь согласованность документов в комплекте (КП, договор, приложения).",
    },
    {
      id: "bu-4",
      title: "Риски условий",
      prompt:
        "Проверь наличие рисков (штрафные санкции, форс-мажор, условия расторжения).",
    },
    {
      id: "bu-5",
      title: "Реквизиты и сумма",
      prompt:
        "Проверь, что реквизиты сторон и сумма одинаковы во всех документах.",
    },
  ],
  legal: [
    {
      id: "legal-1",
      title: "Юридические условия",
      prompt:
        "Проверь наличие обязательных юридических условий (ответственность, конфиденциальность, форс-мажор, споры).",
    },
    {
      id: "legal-2",
      title: "Определения и термины",
      prompt: "Проверь корректность определений и терминов в договоре.",
    },
    {
      id: "legal-3",
      title: "Соответствие законодательству",
      prompt:
        "Проверь соответствие договора действующему законодательству (ГК/НК).",
    },
    {
      id: "legal-4",
      title: "Интеллектуальная собственность",
      prompt:
        "Проверь условия ИС и авторских прав (если релевантно).",
    },
    {
      id: "legal-5",
      title: "Расторжение и ответственность",
      prompt:
        "Проверь условия расторжения договора и ответственность сторон.",
    },
  ],
};

const STORAGE_KEYS = {
  role: "ai_contract_role",
  session: "ai_contract_session",
  customChecks: "ai_contract_custom_checks",
  hiddenDefaults: "ai_contract_hidden_defaults",
  overrides: "ai_contract_overrides",
};

const state = {
  role: null,
  mode: "short",
  documents: [],
  editingCheck: null,
};

const elements = {
  roleChip: document.getElementById("roleChip"),
  roleModal: document.getElementById("roleModal"),
  checkModal: document.getElementById("checkModal"),
  checkModalTitle: document.getElementById("checkModalTitle"),
  checkTitleInput: document.getElementById("checkTitleInput"),
  checkPromptInput: document.getElementById("checkPromptInput"),
  uploadBtn: document.getElementById("uploadBtn"),
  fileInput: document.getElementById("fileInput"),
  docList: document.getElementById("docList"),
  checksContainer: document.getElementById("checksContainer"),
  addCheckBtn: document.getElementById("addCheckBtn"),
  chatWindow: document.getElementById("chatWindow"),
  chatInput: document.getElementById("chatInput"),
  sendBtn: document.getElementById("sendBtn"),
  modeToggle: document.getElementById("modeToggle"),
  saveCheckBtn: document.getElementById("saveCheckBtn"),
  cancelCheckBtn: document.getElementById("cancelCheckBtn"),
  improvePromptBtn: document.getElementById("improvePromptBtn"),
};

function getSessionId() {
  let sessionId = localStorage.getItem(STORAGE_KEYS.session);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.session, sessionId);
  }
  return sessionId;
}

function setRole(role) {
  state.role = role;
  localStorage.setItem(STORAGE_KEYS.role, role);
  elements.roleChip.textContent = `Роль: ${roleLabel(role)}`;
  renderChecks();
}

function roleLabel(role) {
  if (role === "sales") return "Руководитель продаж";
  if (role === "bu") return "Руководитель БЕ";
  return "Юрист";
}

function loadRole() {
  const stored = localStorage.getItem(STORAGE_KEYS.role);
  if (!stored) {
    elements.roleModal.classList.add("show");
    return;
  }
  setRole(stored);
}

function loadCustomChecks() {
  const raw = localStorage.getItem(STORAGE_KEYS.customChecks);
  return raw ? JSON.parse(raw) : {};
}

function saveCustomChecks(data) {
  localStorage.setItem(STORAGE_KEYS.customChecks, JSON.stringify(data));
}

function loadHiddenDefaults() {
  const raw = localStorage.getItem(STORAGE_KEYS.hiddenDefaults);
  return raw ? JSON.parse(raw) : {};
}

function saveHiddenDefaults(data) {
  localStorage.setItem(STORAGE_KEYS.hiddenDefaults, JSON.stringify(data));
}

function loadOverrides() {
  const raw = localStorage.getItem(STORAGE_KEYS.overrides);
  return raw ? JSON.parse(raw) : {};
}

function saveOverrides(data) {
  localStorage.setItem(STORAGE_KEYS.overrides, JSON.stringify(data));
}

async function parseError(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    const data = await response.json();
    return data.detail || data.message || "Ошибка запроса.";
  }
  const text = await response.text();
  return text || "Ошибка запроса.";
}

function renderChecks() {
  if (!state.role) return;
  elements.checksContainer.innerHTML = "";
  const defaults = ROLE_DEFAULTS[state.role] || [];
  const overrides = loadOverrides()[state.role] || {};
  const hidden = new Set(loadHiddenDefaults()[state.role] || []);
  const custom = loadCustomChecks()[state.role] || [];

  defaults.forEach((check) => {
    if (hidden.has(check.id)) return;
    const merged = overrides[check.id] || check;
    elements.checksContainer.appendChild(
      buildCheckCard(merged, true)
    );
  });

  custom.forEach((check) => {
    elements.checksContainer.appendChild(
      buildCheckCard(check, false)
    );
  });
}

function buildCheckCard(check, isDefault) {
  const card = document.createElement("div");
  card.className = "check-card";
  const title = document.createElement("h4");
  title.textContent = check.title;
  card.appendChild(title);

  const actions = document.createElement("div");
  actions.className = "check-actions";

  const runBtn = document.createElement("button");
  runBtn.textContent = "Запустить";
  runBtn.onclick = () => sendMessage(check.prompt);
  actions.appendChild(runBtn);

  const editBtn = document.createElement("button");
  editBtn.textContent = "Редактировать";
  editBtn.onclick = () => openCheckModal(check, isDefault);
  actions.appendChild(editBtn);

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = isDefault ? "Скрыть" : "Удалить";
  deleteBtn.onclick = () => handleDeleteCheck(check, isDefault);
  actions.appendChild(deleteBtn);

  card.appendChild(actions);
  return card;
}

function openCheckModal(check = null, isDefault = false) {
  state.editingCheck = check ? { ...check, isDefault } : null;
  elements.checkModalTitle.textContent = check
    ? "Редактировать проверку"
    : "Новая проверка";
  elements.checkTitleInput.value = check ? check.title : "";
  elements.checkPromptInput.value = check ? check.prompt : "";
  elements.checkModal.classList.add("show");
}

function closeCheckModal() {
  elements.checkModal.classList.remove("show");
  state.editingCheck = null;
}

function handleSaveCheck() {
  const title = elements.checkTitleInput.value.trim();
  const prompt = elements.checkPromptInput.value.trim();
  if (!title || !prompt) {
    alert("Заполните название и промт.");
    return;
  }
  const customData = loadCustomChecks();
  const overrides = loadOverrides();
  const roleChecks = customData[state.role] || [];
  const roleOverrides = overrides[state.role] || {};

  if (state.editingCheck?.isDefault) {
    roleOverrides[state.editingCheck.id] = {
      id: state.editingCheck.id,
      title,
      prompt,
    };
    overrides[state.role] = roleOverrides;
    saveOverrides(overrides);
  } else {
    const id = state.editingCheck?.id || crypto.randomUUID();
    const existingIndex = roleChecks.findIndex((item) => item.id === id);
    const payload = { id, title, prompt };
    if (existingIndex >= 0) {
      roleChecks[existingIndex] = payload;
    } else {
      roleChecks.push(payload);
    }
    customData[state.role] = roleChecks;
    saveCustomChecks(customData);
  }
  closeCheckModal();
  renderChecks();
}

function handleDeleteCheck(check, isDefault) {
  if (isDefault) {
    const hidden = loadHiddenDefaults();
    const list = new Set(hidden[state.role] || []);
    list.add(check.id);
    hidden[state.role] = Array.from(list);
    saveHiddenDefaults(hidden);
  } else {
    const customData = loadCustomChecks();
    const roleChecks = (customData[state.role] || []).filter(
      (item) => item.id !== check.id
    );
    customData[state.role] = roleChecks;
    saveCustomChecks(customData);
  }
  renderChecks();
}

async function improvePrompt() {
  const prompt = elements.checkPromptInput.value.trim();
  if (!prompt) return;
  try {
    const response = await fetch("/api/prompt/improve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, role: state.role }),
    });
    if (!response.ok) {
      const error = await parseError(response);
      throw new Error(error);
    }
    const data = await response.json();
    elements.checkPromptInput.value = data.improved_prompt;
  } catch (error) {
    alert(error.message);
  }
}

async function uploadFiles() {
  const files = Array.from(elements.fileInput.files);
  if (!files.length) {
    alert("Выберите файлы.");
    return;
  }
  if (files.length > 5) {
    alert("Можно загрузить максимум 5 файлов.");
    return;
  }
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const sessionId = getSessionId();
  try {
    const response = await fetch(`/api/upload?session_id=${sessionId}`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const error = await parseError(response);
      throw new Error(error);
    }
    const data = await response.json();
    state.documents = data.documents;
    renderDocuments();
  } catch (error) {
    alert(error.message);
  }
}

function renderDocuments() {
  elements.docList.innerHTML = "";
  state.documents.forEach((doc) => {
    const chip = document.createElement("span");
    chip.textContent = doc.name;
    elements.docList.appendChild(chip);
  });
}

function appendMessage(role, text, messageId = null, question = "") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  wrapper.textContent = text;
  if (role === "assistant" && messageId) {
    const rating = document.createElement("div");
    rating.className = "rating";
    const up = document.createElement("button");
    up.textContent = "👍";
    up.onclick = () => submitRating(messageId, "up", question);
    const down = document.createElement("button");
    down.textContent = "👎";
    down.onclick = () => submitRating(messageId, "down", question);
    rating.appendChild(up);
    rating.appendChild(down);
    wrapper.appendChild(rating);
  }
  elements.chatWindow.appendChild(wrapper);
  elements.chatWindow.scrollTop = elements.chatWindow.scrollHeight;
}

async function sendMessage(textOverride = null) {
  const message = textOverride || elements.chatInput.value.trim();
  if (!message) return;
  if (!state.role) {
    alert("Сначала выберите роль.");
    return;
  }
  if (!state.documents.length) {
    alert("Сначала загрузите документы.");
    return;
  }
  appendMessage("user", message);
  elements.chatInput.value = "";
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        message,
        role: state.role,
        mode: state.mode,
      }),
    });
    if (!response.ok) {
      const error = await parseError(response);
      throw new Error(error);
    }
    const data = await response.json();
    appendMessage("assistant", data.answer, data.message_id, message);
  } catch (error) {
    appendMessage("assistant", `Ошибка: ${error.message}`);
  }
}

async function submitRating(messageId, rating, question) {
  try {
    await fetch("/api/rating", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        message_id: messageId,
        rating,
        role: state.role,
        mode: state.mode,
        question: question || "",
      }),
    });
  } catch (error) {
    console.error(error);
  }
}

function bindEvents() {
  elements.roleModal.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      elements.roleModal.classList.remove("show");
      setRole(button.dataset.role);
    });
  });

  elements.addCheckBtn.addEventListener("click", () => openCheckModal());
  elements.saveCheckBtn.addEventListener("click", handleSaveCheck);
  elements.cancelCheckBtn.addEventListener("click", closeCheckModal);
  elements.improvePromptBtn.addEventListener("click", improvePrompt);
  elements.uploadBtn.addEventListener("click", uploadFiles);
  elements.sendBtn.addEventListener("click", () => sendMessage());

  elements.modeToggle.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      elements.modeToggle
        .querySelectorAll("button")
        .forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      state.mode = button.dataset.mode;
    });
  });

  elements.chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
}

bindEvents();
loadRole();
