async function checkKey() {
  const input = document.getElementById("keyInput").value.trim();
  const status = document.getElementById("status");
  const scriptBox = document.getElementById("scriptBox");
  const scriptCode = document.getElementById("scriptCode");

  status.className = "status";
  scriptBox.classList.add("hidden");
  status.textContent = "⏳ Verificando...";
  status.classList.remove("hidden");

  try {
    const res = await fetch("/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: input })
    });
    const data = await res.json();
    if (data.valid) {
      status.textContent = "✅ Key válida! Acesso liberado.";
      status.classList.add("success");
      scriptCode.textContent = data.script;
      scriptBox.classList.remove("hidden");
    } else {
      status.textContent = "❌ Key inválida. Verifique e tente novamente.";
      status.classList.add("error");
    }
  } catch {
    status.textContent = "⚠️ Erro ao conectar ao servidor.";
    status.classList.add("error");
  }
}

function copyScript() {
  navigator.clipboard.writeText(document.getElementById("scriptCode").textContent).then(() => {
    const btn = document.querySelector(".copy-btn");
    btn.textContent = "✅ Copiado!";
    setTimeout(() => btn.textContent = "📋 Copiar Script", 2000);
  });
}

async function carregarRanking() {
  const list = document.getElementById("rankingList");
  try {
    const res = await fetch("/ranking");
    const data = await res.json();
    if (!data.ranking.length) { list.innerHTML = '<p class="desc">Nenhuma venda ainda esta semana.</p>'; return; }
    const medalhas = ["🥇", "🥈", "🥉"];
    const classes = ["top1", "top2", "top3"];
    list.innerHTML = data.ranking.map((r, i) => `
      <div class="rank-item ${classes[i] || ''}">
        <span class="rank-pos">${medalhas[i] || `#${i+1}`}</span>
        <span class="rank-name">${r.username}</span>
        <span class="rank-vendas">${r.vendasSemana} vendas</span>
      </div>
    `).join("");
  } catch {
    list.innerHTML = '<p class="desc">Erro ao carregar ranking.</p>';
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("keyInput").addEventListener("keydown", e => { if (e.key === "Enter") checkKey(); });
  carregarRanking();

  const container = document.getElementById("particles");
  for (let i = 0; i < 40; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    p.style.left = Math.random() * 100 + "vw";
    p.style.animationDuration = (4 + Math.random() * 8) + "s";
    p.style.animationDelay = (Math.random() * 8) + "s";
    p.style.width = p.style.height = (1 + Math.random() * 3) + "px";
    container.appendChild(p);
  }
});
