let usuarioLogado = null;
let senhaLogada = null;

async function loginRev() {
  const username = document.getElementById("revUser").value.trim();
  const senha = document.getElementById("revSenha").value.trim();
  const status = document.getElementById("loginStatus");

  status.className = "status";
  status.textContent = "⏳ Entrando...";
  status.classList.remove("hidden");

  try {
    const res = await fetch("/rev/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, senha })
    });
    const data = await res.json();
    if (data.ok) {
      usuarioLogado = username;
      senhaLogada = senha;
      document.getElementById("loginBox").classList.add("hidden");
      document.getElementById("painelRev").classList.remove("hidden");
      document.getElementById("nomeRev").textContent = username;
      carregarKeys();
    } else {
      status.textContent = "❌ Usuário ou senha incorretos.";
      status.classList.add("error");
    }
  } catch {
    status.textContent = "⚠️ Erro ao conectar.";
    status.classList.add("error");
  }
}

async function carregarKeys() {
  const res = await fetch("/rev/keys", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: usuarioLogado, senha: senhaLogada })
  });
  const data = await res.json();
  const keys = data.keys || [];
  const disponiveis = keys.filter(k => !k.usada);
  const usadas = keys.filter(k => k.usada);

  document.getElementById("totalKeys").textContent = keys.length;
  document.getElementById("dispKeys").textContent = disponiveis.length;
  document.getElementById("usadasKeys").textContent = usadas.length;

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
  if (!confirm(`Distribuir a key ${key}?\nEla será marcada como usada e ativada para o cliente.`)) return;
  const res = await fetch("/rev/distribuir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: usuarioLogado, senha: senhaLogada, key })
  });
  const data = await res.json();
  if (data.ok) carregarKeys();
}

function sair() {
  usuarioLogado = null; senhaLogada = null;
  document.getElementById("loginBox").classList.remove("hidden");
  document.getElementById("painelRev").classList.add("hidden");
  document.getElementById("loginStatus").classList.add("hidden");
  document.getElementById("revUser").value = "";
  document.getElementById("revSenha").value = "";
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("revSenha").addEventListener("keydown", e => { if (e.key === "Enter") loginRev(); });
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
