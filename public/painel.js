const tipo = sessionStorage.getItem("tipo");
const senha = sessionStorage.getItem("senha");
const username = sessionStorage.getItem("username");

if (!tipo) window.location.href = "login.html";

const PLANOS_REV = { "1": 1, "7": 5, "30": 15, "0": 30 };
const PLANOS_CLI = { "1": 3, "7": 13, "30": 38, "0": 75 };
const PLANOS = tipo === "cliente" ? PLANOS_CLI : PLANOS_REV;
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
      { id: "clientes", icon: "👤", label: "Clientes" },
      { id: "tickets", icon: "🎫", label: "Tickets" },
      { id: "ranking", icon: "🏆", label: "Ranking" }
    ]
  : [
      { id: "gerarKey", icon: "🔑", label: "Gerar Keys" },
      { id: "minhasKeys", icon: "📋", label: "Minhas Keys" },
      { id: "tickets", icon: "🎫", label: "Suporte" },
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
  if (pagina === "clientes") renderClientes();
  if (pagina === "tickets") renderTickets();
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
            <option value="1">1 Dia (${PLANOS["1"]} crédito${PLANOS["1"]>1?'s':''})</option>
            <option value="7">7 Dias (${PLANOS["7"]} créditos)</option>
            <option value="30">30 Dias (${PLANOS["30"]} créditos)</option>
            <option value="0">Permanente (${PLANOS["0"]} créditos)</option>
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

// ===== TICKETS =====

const CATEGORIAS = ["Erro na Key", "Pagamento", "Login", "Bug", "Outros"];
const STATUS_CORES = { aberto: "#00FF62", aguardando: "#ffcc00", resolvido: "#888" };

async function renderTickets() {
  const el = document.getElementById("pageTickets");
  const isAdmin = tipo === "admin";

  el.innerHTML = `
    <div class="page-title">${isAdmin ? "🎫 Tickets de Suporte" : "🎫 Suporte"}</div>
    <p class="page-sub">${isAdmin ? "Gerencie todos os tickets" : "Abra um ticket para receber ajuda"}</p>

    ${!isAdmin ? `
    <div class="card" style="margin-bottom:16px">
      <div class="section-header"><span class="section-title">➕ Abrir Ticket</span></div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <select class="select-input" id="tkCategoria">
          ${CATEGORIAS.map(c => `<option>${c}</option>`).join("")}
        </select>
        <input type="text" class="input-inline" id="tkTitulo" placeholder="Título do problema"/>
        <textarea class="input-inline" id="tkMensagem" placeholder="Descreva seu problema..." rows="3" style="resize:vertical"></textarea>
        <button class="btn-green" onclick="abrirTicket()" style="padding:11px 20px;align-self:flex-start">📨 Enviar Ticket</button>
      </div>
      <div id="tkStatus" class="status-msg" style="margin-top:10px"></div>
    </div>` : ""}

    <div class="card">
      <div class="section-header">
        <span class="section-title">${isAdmin ? "Todos os Tickets" : "Meus Tickets"}</span>
        <button class="btn-outline" onclick="renderTickets()">🔄 Atualizar</button>
      </div>
      <div id="tkLista"><p style="color:var(--gray-dim)">Carregando...</p></div>
    </div>

    <!-- MODAL TICKET -->
    <div id="tkModal" class="hidden" style="position:fixed;inset:0;background:#000000cc;display:flex;align-items:center;justify-content:center;z-index:999">
      <div style="background:#0d0d0d;border:1px solid #1f1f1f;border-radius:16px;padding:28px;width:100%;max-width:520px;max-height:80vh;overflow-y:auto">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h3 id="tkModalTitulo" style="font-size:1rem;font-weight:700"></h3>
          <button onclick="fecharModal()" style="background:none;border:none;color:#888;font-size:1.2rem;cursor:pointer">✕</button>
        </div>
        <div id="tkMensagens" style="display:flex;flex-direction:column;gap:10px;margin-bottom:16px"></div>
        <textarea class="input-inline" id="tkResposta" placeholder="Digite sua resposta..." rows="3" style="resize:vertical;margin-bottom:10px"></textarea>
        <div style="display:flex;gap:10px">
          <button class="btn-green" onclick="responderTicket()" style="padding:10px 20px">Responder</button>
          ${isAdmin ? `
            <button class="btn-outline" onclick="mudarStatus('resolvido')" style="color:#00FF62;border-color:#00FF62">✅ Resolver</button>
            <button class="btn-outline" onclick="mudarStatus('aberto')" style="color:#ffcc00;border-color:#ffcc00">🔄 Reabrir</button>
          ` : ""}
        </div>
      </div>
    </div>
  `;

  carregarTickets();
}

let ticketAtual = null;

async function carregarTickets() {
  const isAdmin = tipo === "admin";
  const url = isAdmin ? "/admin/tickets" : "/ticket/meus";
  const body = isAdmin ? { senha } : { username, senha };
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  const lista = data.tickets || [];
  const el = document.getElementById("tkLista");
  if (!lista.length) { el.innerHTML = '<p style="color:var(--gray-dim)">Nenhum ticket encontrado.</p>'; return; }

  el.innerHTML = lista.map(t => `
    <div style="display:flex;align-items:center;gap:12px;background:#111;border:1px solid #1f1f1f;border-radius:10px;padding:12px 16px;margin-bottom:8px;cursor:pointer" onclick="abrirModal('${t.id}')">
      <div style="flex:1">
        <div style="font-weight:600;font-size:0.88rem">${t.titulo}</div>
        <div style="color:#7D7D7D;font-size:0.75rem">${t.categoria} • ${isAdmin ? t.username + " • " : ""}${t.mensagens.length} mensagem(s)</div>
      </div>
      <span style="padding:3px 10px;border-radius:999px;font-size:0.72rem;font-weight:600;border:1px solid ${STATUS_CORES[t.status]};color:${STATUS_CORES[t.status]}">${t.status}</span>
    </div>
  `).join("");

  // Guarda tickets para o modal
  window._tickets = lista;
}

async function abrirTicket() {
  const categoria = document.getElementById("tkCategoria").value;
  const titulo = document.getElementById("tkTitulo").value.trim();
  const mensagem = document.getElementById("tkMensagem").value.trim();
  const status = document.getElementById("tkStatus");
  status.className = "status-msg";
  if (!titulo || !mensagem) { status.className = "status-msg error"; status.textContent = "❌ Preencha todos os campos."; return; }
  const res = await fetch("/ticket/abrir", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, senha, categoria, titulo, mensagem }) });
  const data = await res.json();
  if (data.ok) {
    status.className = "status-msg success";
    status.textContent = "✅ Ticket aberto com sucesso!";
    document.getElementById("tkTitulo").value = "";
    document.getElementById("tkMensagem").value = "";
    carregarTickets();
  } else {
    status.className = "status-msg error";
    status.textContent = `❌ ${data.error}`;
  }
}

function abrirModal(id) {
  ticketAtual = (window._tickets || []).find(t => t.id === id);
  if (!ticketAtual) return;
  document.getElementById("tkModalTitulo").textContent = `${ticketAtual.id} — ${ticketAtual.titulo}`;
  renderMensagens();
  document.getElementById("tkModal").classList.remove("hidden");
  document.getElementById("tkModal").style.display = "flex";
}

function renderMensagens() {
  const el = document.getElementById("tkMensagens");
  el.innerHTML = ticketAtual.mensagens.map(m => `
    <div style="background:${m.autor === "Admin" ? "#001a0d" : "#111"};border:1px solid ${m.autor === "Admin" ? "#00FF6233" : "#1f1f1f"};border-radius:10px;padding:12px 14px">
      <div style="font-size:0.75rem;color:#7D7D7D;margin-bottom:4px">${m.autor} • ${new Date(m.data).toLocaleString("pt-BR")}</div>
      <div style="font-size:0.88rem">${m.texto}</div>
    </div>
  `).join("");
}

function fecharModal() {
  document.getElementById("tkModal").classList.add("hidden");
  document.getElementById("tkModal").style.display = "none";
  ticketAtual = null;
}

async function responderTicket() {
  const texto = document.getElementById("tkResposta").value.trim();
  if (!texto) return;
  const isAdmin = tipo === "admin";
  await fetch("/ticket/responder", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: isAdmin ? "Admin" : username, senha: isAdmin ? senha : senha, ticketId: ticketAtual.id, mensagem: texto })
  });
  document.getElementById("tkResposta").value = "";
  // Atualiza mensagens localmente
  ticketAtual.mensagens.push({ autor: isAdmin ? "Admin" : username, texto, data: new Date() });
  renderMensagens();
  carregarTickets();
}

async function mudarStatus(status) {
  await fetch("/admin/ticket/status", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ senha, ticketId: ticketAtual.id, status })
  });
  ticketAtual.status = status;
  carregarTickets();
}

// ===== CLIENTES =====
async function renderClientes() {
  document.getElementById("pageClientes").innerHTML = `
    <div class="page-title">Clientes</div>
    <p class="page-sub">Gerencie os clientes e promova para revendedor</p>
    <div class="card"><p style="color:var(--gray-dim)">Carregando...</p></div>
  `;
  const res = await fetch("/admin/clientes", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha }) });
  const data = await res.json();
  const lista = data.clientes || [];

  document.getElementById("pageClientes").innerHTML = `
    <div class="page-title">Clientes</div>
    <p class="page-sub">Gerencie os clientes e promova para revendedor</p>
    <div class="card">
      <div class="rev-grid">
        ${lista.length ? lista.map(c => `
          <div class="rev-row">
            <span class="rev-name">👤 ${c.username}</span>
            <span class="badge pendente">Cliente</span>
            <button class="btn-green" onclick="promover('${c.username}')" style="padding:7px 14px;font-size:0.8rem">⬆️ Promover</button>
            <button class="btn-red" onclick="deletarUser('${c.username}')">🗑️</button>
          </div>
        `).join("") : '<p style="color:var(--gray-dim)">Nenhum cliente cadastrado.</p>'}
      </div>
    </div>
  `;
}

async function promover(user) {
  if (!confirm(`Promover "${user}" para revendedor?`)) return;
  const res = await fetch("/admin/promover", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha, username: user }) });
  const data = await res.json();
  if (data.ok) renderClientes();
}

async function deletarUser(user) {
  if (!confirm(`Remover usuário "${user}"?`)) return;
  await fetch("/admin/revendedor", { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ senha, username: user }) });
  renderClientes();
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
