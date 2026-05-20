let senhaAdmin = null;

async function loginAdmin() {
  const senha = document.getElementById("adminSenha").value.trim();
  const status = document.getElementById("loginStatus");
  status.className = "status";
  status.textContent = "⏳ Verificando...";
  status.classList.remove("hidden");

  try {
    const res = await fetch("/admin/revendedores", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ senha })
    });
    const data = await res.json();
    if (data.error) { status.textContent = "❌ Senha incorreta."; status.classList.add("error"); return; }
    senhaAdmin = senha;
    document.getElementById("loginBox").classList.add("hidden");
    document.getElementById("painelAdmin").classList.remove("hidden");
    renderRevs(data.revendedores);
  } catch {
    status.textContent = "⚠️ Erro ao conectar."; status.classList.add("error");
  }
}

async function criarRev() {
  const username = document.getElementById("novoUser").value.trim();
  const senhaRev = document.getElementById("novaSenha").value.trim();
  const status = document.getElementById("criarStatus");
  status.className = "status";

  const res = await fetch("/admin/revendedor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha: senhaAdmin, username, senhaRev })
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
    body: JSON.stringify({ senha: senhaAdmin, username, quantidade })
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
    body: JSON.stringify({ senha: senhaAdmin, username })
  });
  carregarRevs();
}

async function carregarRevs() {
  const res = await fetch("/admin/revendedores", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha: senhaAdmin })
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
        <div class="rev-stat"><span>${r.totalKeys}</span><small>Total Keys</small></div>
        <div class="rev-stat"><span>${r.vendasSemana}</span><small>Semana</small></div>
        <div class="rev-stat"><span>${r.vendas}</span><small>Total</small></div>
      </div>
      <button class="del-btn" onclick="deletarRev('${r.username}')">🗑️</button>
    </div>
  `).join("");
}

function sair() {
  senhaAdmin = null;
  document.getElementById("loginBox").classList.remove("hidden");
  document.getElementById("painelAdmin").classList.add("hidden");
  document.getElementById("adminSenha").value = "";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("adminSenha").addEventListener("keydown", e => { if (e.key === "Enter") loginAdmin(); });
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
