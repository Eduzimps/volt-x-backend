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
  const code = document.getElementById("scriptCode").textContent;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.querySelector(".copy-btn");
    btn.textContent = "✅ Copiado!";
    setTimeout(() => btn.textContent = "📋 Copiar Script", 2000);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("keyInput").addEventListener("keydown", e => {
    if (e.key === "Enter") checkKey();
  });

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
