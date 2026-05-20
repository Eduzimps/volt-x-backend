let sessao = null;

async function fazerLogin() {
  const username = document.getElementById("loginUser").value.trim();
  const senha = document.getElementById("loginSenha").value.trim();
  const status = document.getElementById("loginStatus");

  status.className = "status";
  status.textContent = "⏳ Entrando...";
  status.classList.remove("hidden");

  // Tenta admin
  try {
    const res = await fetch("/admin/revendedores", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ senha })
    });
    const data = await res.json();
    if (!data.error) {
      sessao = { tipo: "admin", senha };
      document.getElementById("loginBox").classList.add("hidden");
      document.getElementById("painelAdmin").classList.remove("hidden");
      renderRevs(data.revendedores);
      return;
    }
  } catch {}

  // Tenta revendedor
  try {
    const res = await fetch("/rev/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, senha })
    });
    const data = await res.json();
    if (data.ok) {
      sessao = { tipo: "rev", username, senha };
      document.getElementById("loginBox").classList.add("hidden");
      document.getElementById("painelRev").classList.remove("hidden");
      document.getElementById("nomeRev").textContent = username;
      carregarKeys();
      return;
    }
  } catch {}

  status.textContent = "❌ Usuário ou senha incorretos.";
  status.classList.add("error");
}

// ===== ADMIN =====

async function criarRev() {
  const username = document.getElementById("novoUser").value.trim();
  const senhaRev = document.getElementById("novaSenha").value.trim();
  const status = document.getElementById("criarStatus");
  status.className = "status";

  const res = await fetch("/admin/revendedor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha: sessao.senha, username, senhaRev })
  });
  const data = await res.json();
  status.classList.remove("hidden");
  if (data.ok) {
    status.textContent = `✅ Revendedor "${username}" criado!`;
    status.classList.add("success");
    document.getElementById("novoUser").value = "";
    document.getElementById("novaSenha").value = "";
    carregarRevs();
  } else {
    status.textContent = `❌ ${data.error}`;
    status.classList.add("error");
  }
}

async function adicionarKeys() {
  const username = document.getElementById("revAlvo").value.trim();
  const quantidade = parseInt(document.getElementById("qtdKeys").value);
  const status = document.getElementById("addKeyStatus");
  const geradas = document.getElementById("keysGeradas");
  status.className = "status";

  const res = await fetch("/admin/addkeys", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha: sessao.senha, username, quantidade })
  });
  const data = await res.json();
  status.classList.remove("hidden");
  if (data.keys) {
    status.textContent = `✅ ${data.keys.length} key(s) adicionadas para "${username}"!`;
    status.classList.add("success");
    geradas.classList.remove("hidden");
    geradas.innerHTML = `<p>Keys geradas:</p>` + data.keys.map(k => `<code>${k}</code>`).join("");
    carregarRevs();
  } else {
    status.textContent = `❌ ${data.error}`;
    status.classList.add("error");
    geradas.classList.add("hidden");
  }
}

async function deletarRev(username) {
  if (!confirm(`Remover revendedor "${username}"?`)) return;
  await fetch("/admin/revendedor", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha: sessao.senha, username })
  });
  carregarRevs();
}

async function carregarRevs() {
  const res = await fetch("/admin/revendedores", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha: sessao.senha })
  });
  const data = await res.json();
  renderRevs(data.revendedores);
}

function renderRevs(lista) {
  const el = document.getElementById("revList");
  if (!lista.length) { el.innerHTML = '<p class="desc">Nenhum revendedor cadastrado.</p>'; return; }
  el.innerHTML = lista.map(r => `
    <div class="rev-item">
      <span class="rev-name">👤 ${r.username}</span>
      <div class="rev-stats">
        <div class="rev-stat"><span>${r.keysDisponiveis}</span><small>Disponíveis</small></div>
        <div class="rev-stat"><span>${r.totalKeys}</span><small>Total</small></div>
        <div class="rev-stat"><span>${r.vendasSemana}</span><small>Semana</small></div>
        <div class="rev-stat"><span>${r.vendas}</span><small>Total Vendas</small></div>
      </div>
      <button class="del-btn" onclick="deletarRev('${r.username}')">🗑️</button>
    </div>
  `).join("");
}

// ===== REVENDEDOR =====

async function carregarKeys() {
  const res = await fetch("/rev/keys", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: sessao.username, senha: sessao.senha })
  });
  const data = await res.json();
  const keys = data.keys || [];
  document.getElementById("totalKeys").textContent = keys.length;
  document.getElementById("dispKeys").textContent = keys.filter(k => !k.usada).length;
  document.getElementById("usadasKeys").textContent = keys.filter(k => k.usada).length;

  const list = document.getElementById("keysList");
  if (!keys.length) { list.innerHTML = '<p class="desc">Nenhuma key disponível ainda.</p>'; return; }
  list.innerHTML = keys.map(k => `
    <div class="key-item ${k.usada ? 'usada' : ''}">
      <span class="key-code">${k.key}</span>
      <span class="key-badge ${k.usada ? 'usada-badge' : 'disponivel'}">${k.usada ? 'Usada' : 'Disponível'}</span>
      ${!k.usada ? `<button class="dist-btn" onclick="distribuir('${k.key}')">Distribuir</button>` : ''}
    </div>
  `).join("");
}

async function distribuir(key) {
  if (!confirm(`Distribuir a key ${key}?\nEla será ativada para o cliente.`)) return;
  const res = await fetch("/rev/distribuir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: sessao.username, senha: sessao.senha, key })
  });
  const data = await res.json();
  if (data.ok) carregarKeys();
}

// ===== GERAL =====

function sair() {
  sessao = null;
  document.getElementById("loginBox").classList.remove("hidden");
  document.getElementById("painelAdmin").classList.add("hidden");
  document.getElementById("painelRev").classList.add("hidden");
  document.getElementById("loginUser").value = "";
  document.getElementById("loginSenha").value = "";
  document.getElementById("loginStatus").classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("loginSenha").addEventListener("keydown", e => { if (e.key === "Enter") fazerLogin(); });
  const container = document.getElementById("particles");
  for (let i = 0; i < 30; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    p.style.left = Math.random() * 100 + "vw";
    p.style.animationDuration = (4 + Math.random() * 8) + "s";
    p.style.animationDelay = (Math.random() * 8) + "s";
    p.style.width = p.style.height = (1 + Math.random() * 3) + "px";
    container.appendChild(p);
  }
});
