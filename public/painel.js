const tipo = sessionStorage.getItem("tipo");
const senha = sessionStorage.getItem("senha");
const username = sessionStorage.getItem("username");

if (!tipo) window.location.href = "login.html";

const PLANOS = { "1": 1, "7": 5, "30": 15, "0": 30 };
const PLANO_NOMES = { "1": "1 Dia", "7": "7 Dias", "30": "30 Dias", "0": "Permanente" };

let creditos = parseInt(sessionStorage.getItem("creditos") || "0");

// ===== INIT =====
document.getElementById("topUser").textContent = username;

if (tipo === "rev") {
  document.getElementById("topCreditos").style.display = "block";
  atualizarCreditos();
}

const menus = tipo === "admin"
  ? [
      { id: "gerarKey", icon: "🔑", label: "Gerar Keys" },
      { id: "adminKeys", icon: "📋", label: "Todas as Keys" },
      { id: "revendedores", icon: "👥", label: "Revendedores" },
      { id: "ranking", icon: "🏆", label: "Ranking" }
    ]
  : [
      { id: "gerarKey", icon: "🔑", label: "Gerar Keys" },
      { id: "minhasKeys", icon: "📋", label: "Minhas Keys" },
      { id: "ranking", icon: "🏆", label: "Ranking" }
    ];

const sidebar = document.getElementById("sidebarMenu");
menus.forEach((m, i) => {
  const el = document.createElement("div");
  el.className = "menu-item" + (i === 0 ? " active" : "");
  el.innerHTML = `<span class="icon">${m.icon}</span>${m.label}`;
  el.onclick = () => navegar(m.id, el);
  sidebar.appendChild(el);
});

navegar(menus[0].id, sidebar.firstChild);

// ===== NAVEGAÇÃO =====
function navegar(pagina, el) {
  document.querySelectorAll(".menu-item").forEach(m => m.classList.remove("active"));
  el.classList.add("active");
  document.querySelectorAll("[id^='page']").forEach(p => p.innerHTML = "");

  if (pagina === "gerarKey") renderGerarKey();
  if (pagina === "minhasKeys") renderMinhasKeys();
  if (pagina === "revendedores") renderRevendedores();
  if (pagina === "adminKeys") renderAdminKeys();
  if (pagina === "ranking") renderRanking();
}

function atualizarCreditos() {
  document.getElementById("topCreditos").textContent = `💳 ${creditos} créditos`;
}

function sair() {
  sessionStorage.clear();
  window.location.href = "login.html";
}

// ===== GERAR KEY =====
function renderGerarKey() {
  const isAdmin = tipo === "admin";
  const dispositivosOpts = isAdmin
    ? `<option value="1">1 Dispositivo</option><option value="2">2 Dispositivos</option><option value="5">5 Dispositivos</option><option value="-1">Ilimitado</option>`
    : `<option value="1">1 Dispositivo</option>`;

  document.getElementById("pageGerarKey").innerHTML = `
    <div class="page-title">Gerar Keys</div>
    <p class="page-sub">Crie novas keys para seus clientes de forma rápida e eficiente</p>

    <div class="card">
      <div class="form-grid">
        <div class="form-group">
          <label class="field-label">Validade *</label>
          <select class="select-input" id="gDias" onchange="calcularCusto()">
            <option value="1">1 Dia (1 crédito)</option>
            <option value="7">7 Dias (5 créditos)</option>
            <option value="30">30 Dias (15 créditos)</option>
            <option value="0">Permanente (30 créditos)</option>
          </select>
        </div>

        <div class="form-group">
          <label class="field-label">Quantidade *</label>
          <input type="number" class="field-input" id="gQtd" value="1" min="1" max="100" oninput="calcularCusto()" style="margin-bottom:0"/>
        </div>

        <div class="form-group">
          <label class="field-label">Dispositivos *</label>
          <select class="select-input" id="gDisp">${dispositivosOpts}</select>
        </div>

        <div class="form-group">
          <label class="field-label">Créditos necessários</label>
          <div class="info-box" id="gCreditosInfo">1 crédito</div>
          ${!isAdmin ? '<p class="info-hint">Preenchido automaticamente conforme a validade</p>' : ''}
        </div>
      </div>

      <div class="custo-box">
        <div class="custo-item">
          <div class="custo-label">Total de Créditos</div>
          <div class="custo-val" id="custoTotal">1</div>
        </div>
        <div class="custo-divider"></div>
        <div class="custo-item">
          <div class="custo-label">${isAdmin ? "Admin" : "Seus Créditos"}</div>
          <div class="custo-val green" id="creditosDisp">${isAdmin ? "∞" : creditos}</div>
        </div>
      </div>

      <button class="btn-green" id="btnGerar" onclick="gerarKeys()">
        ➕ Gerar Keys
      </button>

      <div id="gerarStatus" class="status-msg" style="margin-top:14px"></div>
      <div id="keysGeradas" class="keys-geradas-box hidden"></div>
    </div>
  `;
  calcularCusto();
}

function calcularCusto() {
  const dias = document.getElementById("gDias")?.value;
  const qtd = parseInt(document.getElementById("gQtd")?.value) || 1;
  const custo = (PLANOS[dias] || 1) * qtd;
  if (document.getElementById("gCreditosInfo")) document.getElementById("gCreditosInfo").textContent = `${PLANOS[dias]} crédito(s)`;
  if (document.getElementById("custoTotal")) document.getElementById("custoTotal").textContent = custo;
  if (tipo !== "admin" && document.getElementById("btnGerar")) {
    document.getElementById("btnGerar").disabled = custo > creditos;
  }
}

async function gerarKeys() {
  const dias = document.getElementById("gDias").value;
  const qtd = parseInt(document.getElementById("gQtd").value);
  const disp = document.getElementById("gDisp").value;
  const status = document.getElementById("gerarStatus");
  const box = document.getElementById("keysGeradas");
  status.className = "status-msg";

  const url = tipo === "admin" ? "/admin/gerarkey" : "/rev/gerar";
  const body = tipo === "admin"
    ? { senha, dias, quantidade: qtd, dispositivos: disp }
    : { username, senha, dias, quantidade: qtd };

  try {
    const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await res.json();
    if (data.keys) {
      status.className = "status-msg success";
      status.textContent = `✅ ${data.keys.length} key(s) gerada(s) com sucesso!`;
      box.classList.remove("hidden");
      box.innerHTML = `<p>Keys geradas — copie e envie para seus clientes:</p>` + data.keys.map(k => `<code>${k}</code>`).join("");
      if (tipo === "rev") { creditos = data.creditosRestantes; atualizarCreditos(); calcularCusto(); document.getElementById("creditosDisp").textContent = creditos; }
    } else {
      status.className = "status-msg error";
      status.textContent = `❌ ${data.error}`;
      box.classList.add("hidden");
    }
  } catch {
    status.className = "status-msg error";
    status.textContent = "⚠️ Erro ao conectar.";
  }
}

// ===== MINHAS KEYS =====
async function renderMinhasKeys() {
  document.getElementById("pageMinhasKeys").innerHTML = `
    <div class="page-title">Minhas Keys</div>
    <p class="page-sub">Todas as keys que você gerou</p>
    <div class="card"><div class="table-wrap"><p style="color:var(--gray-dim)">Carregando...</p></div></div>
  `;
  const res = await fetch("/rev/keys", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, senha }) });
  const data = await res.json();
  const keys = data.keys || [];
  creditos = data.creditos;
  atualizarCreditos();

  const ativas = keys.filter(k => k.status === "ativa").length;
  const expiradas = keys.filter(k => k.status === "expirada").length;

  document.getElementById("pageMinhasKeys").innerHTML = `
    <div class="page-title">Minhas Keys</div>
    <p class="page-sub">Todas as keys que você gerou</p>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">Total</div><div class="stat-value">${keys.length}</div></div>
      <div class="stat-card"><div class="stat-label">Ativas</div><div class="stat-value green">${ativas}</div></div>
      <div class="stat-card"><div class="stat-label">Expiradas</div><div class="stat-value" style="color:#ff4444">${expiradas}</div></div>
    </div>
    <div class="card">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Key</th><th>Validade</th><th>Dispositivos</th><th>Status</th><th>Criada em</th><th>Expira em</th></tr></thead>
          <tbody>
            ${keys.length ? keys.map(k => `
              <tr>
                <td><span class="key-code">${k.key}</span></td>
                <td>${k.dias === 0 ? "Permanente" : k.dias + " dias"}</td>
                <td>${k.dispositivos === -1 ? "Ilimitado" : k.dispositivos}</td>
                <td><span class="badge ${k.status}">${k.status}</span></td>
                <td style="color:var(--gray-dim)">${new Date(k.criadaEm).toLocaleDateString("pt-BR")}</td>
                <td style="color:var(--gray-dim)">${k.expiraEm ? new Date(k.expiraEm).toLocaleDateString("pt-BR") : k.ativadaEm ? "—" : "Não ativada"}</td>
              </tr>
            `).join("") : `<tr><td colspan="6" style="color:var(--gray-dim);text-align:center;padding:24px">Nenhuma key gerada ainda.</td></tr>`}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// ===== ADMIN KEYS =====
async function renderAdminKeys() {
  document.getElementById("pageAdminKeys").innerHTML = `
    <div class="page-title">Todas as Keys</div>
    <p class="page-sub">Visão geral de todas as keys do sistema</p>
    <div class="card"><p style="color:var(--gray-dim)">Carregando...</p></div>
  `;
  // Busca keys de todos revendedores
  const res = await fetch("/admin/revendedores", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha }) });
  const data = await res.json();
  const revs = data.revendedores || [];
  const totalKeys = revs.reduce((a, r) => a + r.totalKeys, 0);
  const totalAtivas = revs.reduce((a, r) => a + r.keysAtivas, 0);

  document.getElementById("pageAdminKeys").innerHTML = `
    <div class="page-title">Todas as Keys</div>
    <p class="page-sub">Visão geral de todas as keys do sistema</p>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-label">Total de Keys</div><div class="stat-value">${totalKeys}</div></div>
      <div class="stat-card"><div class="stat-label">Keys Ativas</div><div class="stat-value green">${totalAtivas}</div></div>
      <div class="stat-card"><div class="stat-label">Revendedores</div><div class="stat-value">${revs.length}</div></div>
    </div>
    <div class="card">
      <p style="color:var(--gray-dim);font-size:0.85rem">Para ver as keys de um revendedor específico, acesse a aba <strong style="color:var(--white)">Revendedores</strong>.</p>
    </div>
  `;
}

// ===== REVENDEDORES =====
async function renderRevendedores() {
  document.getElementById("pageRevendedores").innerHTML = `
    <div class="page-title">Revendedores</div>
    <p class="page-sub">Gerencie seus revendedores</p>
    <div class="card" style="margin-bottom:16px">
      <div class="section-header"><span class="section-title">➕ Novo Revendedor</span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <input type="text" class="input-inline" id="novoUser" placeholder="Usuário" style="flex:1;min-width:120px"/>
        <input type="password" class="input-inline" id="novaSenha" placeholder="Senha" style="flex:1;min-width:120px"/>
        <button class="btn-green" onclick="criarRev()" style="padding:10px 20px">Criar</button>
      </div>
      <div id="criarStatus" class="status-msg" style="margin-top:10px"></div>
    </div>

    <div class="card" style="margin-bottom:16px">
      <div class="section-header"><span class="section-title">💳 Adicionar Créditos</span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <input type="text" class="input-inline" id="revCredAlvo" placeholder="Usuário do revendedor" style="flex:1;min-width:120px"/>
        <input type="number" class="input-inline" id="qtdCreditos" placeholder="Quantidade" min="1" value="10" style="flex:1;min-width:100px"/>
        <button class="btn-green" onclick="adicionarCreditos()" style="padding:10px 20px">Adicionar</button>
      </div>
      <div id="creditoStatus" class="status-msg" style="margin-top:10px"></div>
    </div>

    <div class="card">
      <div class="section-header">
        <span class="section-title">👥 Lista de Revendedores</span>
        <button class="btn-outline" onclick="renderRevendedores()">🔄 Atualizar</button>
      </div>
      <div id="revList"><p style="color:var(--gray-dim)">Carregando...</p></div>
    </div>
  `;
  carregarRevs();
}

async function criarRev() {
  const user = document.getElementById("novoUser").value.trim();
  const senhaRev = document.getElementById("novaSenha").value.trim();
  const status = document.getElementById("criarStatus");
  const res = await fetch("/admin/revendedor", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha, username: user, senhaRev }) });
  const data = await res.json();
  status.className = data.ok ? "status-msg success" : "status-msg error";
  status.textContent = data.ok ? `✅ Revendedor "${user}" criado!` : `❌ ${data.error}`;
  if (data.ok) { document.getElementById("novoUser").value = ""; document.getElementById("novaSenha").value = ""; carregarRevs(); }
}

async function adicionarCreditos() {
  const user = document.getElementById("revCredAlvo").value.trim();
  const qtd = parseInt(document.getElementById("qtdCreditos").value);
  const status = document.getElementById("creditoStatus");
  const res = await fetch("/admin/creditos", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha, username: user, quantidade: qtd }) });
  const data = await res.json();
  status.className = data.ok ? "status-msg success" : "status-msg error";
  status.textContent = data.ok ? `✅ ${qtd} créditos adicionados para "${user}"! Total: ${data.creditos}` : `❌ ${data.error}`;
  if (data.ok) carregarRevs();
}

async function carregarRevs() {
  const res = await fetch("/admin/revendedores", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha }) });
  const data = await res.json();
  const el = document.getElementById("revList");
  if (!el) return;
  const lista = data.revendedores || [];
  if (!lista.length) { el.innerHTML = '<p style="color:var(--gray-dim)">Nenhum revendedor cadastrado.</p>'; return; }
  el.innerHTML = `<div class="rev-grid">${lista.map(r => `
    <div class="rev-row">
      <span class="rev-name">👤 ${r.username}</span>
      <div class="rev-stats">
        <div class="rev-stat"><span>${r.creditos}</span><small>Créditos</small></div>
        <div class="rev-stat"><span>${r.keysAtivas}</span><small>Keys Ativas</small></div>
        <div class="rev-stat"><span>${r.vendas}</span><small>Total Vendas</small></div>
        <div class="rev-stat"><span>${r.vendasSemana}</span><small>Semana</small></div>
      </div>
      <button class="btn-red" onclick="deletarRev('${r.username}')">🗑️</button>
    </div>
  `).join("")}</div>`;
}

async function deletarRev(user) {
  if (!confirm(`Remover revendedor "${user}"? Todas as keys dele serão apagadas.`)) return;
  await fetch("/admin/revendedor", { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha, username: user }) });
  carregarRevs();
}

// ===== RANKING =====
async function renderRanking() {
  document.getElementById("pageRanking").innerHTML = `
    <div class="page-title">🏆 Ranking da Semana</div>
    <p class="page-sub">Top revendedores com mais vendas essa semana</p>
    <div class="card"><p style="color:var(--gray-dim)">Carregando...</p></div>
  `;
  const res = await fetch("/ranking");
  const data = await res.json();
  const lista = data.ranking || [];
  const medalhas = ["🥇", "🥈", "🥉"];
  const classes = ["top1", "top2", "top3"];

  document.getElementById("pageRanking").innerHTML = `
    <div class="page-title">🏆 Ranking da Semana</div>
    <p class="page-sub">Top revendedores com mais vendas essa semana</p>
    <div class="card">
      <div class="rank-list">
        ${lista.length ? lista.map((r, i) => `
          <div class="rank-item ${classes[i] || ''}">
            <span class="rank-pos">${medalhas[i] || `#${i+1}`}</span>
            <span class="rank-name">${r.username}</span>
            <span class="rank-vendas">${r.vendasSemana} vendas</span>
          </div>
        `).join("") : '<p style="color:var(--gray-dim)">Nenhuma venda ainda essa semana.</p>'}
      </div>
    </div>
  `;
}
