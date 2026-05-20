const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const ADMIN_PASSWORD = "Eduardo123R";
const SCRIPT = `loadstring(game:HttpGet("https://seusite.com/script.lua"))()`;

// Banco de dados em memória
const revendedores = {}; // { username: { senha, keys: [], vendas: 0, vendasSemana: 0, ultimaSemana: "" } }
const keysAtivas = new Set(); // keys válidas para clientes

function gerarKey() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const parte = () => Array.from({length: 4}, () => chars[Math.floor(Math.random() * chars.length)]).join("");
  return `VOLT-X-${parte()}-${parte()}-${parte()}`;
}

function semanaAtual() {
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 1);
  const week = Math.ceil(((now - start) / 86400000 + start.getDay() + 1) / 7);
  return `${now.getFullYear()}-W${week}`;
}

// ==================== ADMIN ====================

// Criar revendedor
app.post("/admin/revendedor", (req, res) => {
  const { senha, username, senhaRev } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  if (revendedores[username]) return res.status(400).json({ error: "Revendedor já existe" });
  revendedores[username] = { senha: senhaRev, keys: [], vendas: 0, vendasSemana: 0, ultimaSemana: semanaAtual() };
  res.json({ ok: true });
});

// Remover revendedor
app.delete("/admin/revendedor", (req, res) => {
  const { senha, username } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  delete revendedores[username];
  res.json({ ok: true });
});

// Adicionar keys para revendedor
app.post("/admin/addkeys", (req, res) => {
  const { senha, username, quantidade } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  if (!revendedores[username]) return res.status(404).json({ error: "Revendedor não encontrado" });
  const novas = [];
  for (let i = 0; i < quantidade; i++) {
    const key = gerarKey();
    novas.push(key);
    revendedores[username].keys.push({ key, usada: false });
  }
  res.json({ keys: novas });
});

// Ver todos revendedores
app.post("/admin/revendedores", (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const lista = Object.entries(revendedores).map(([username, data]) => ({
    username,
    totalKeys: data.keys.length,
    keysDisponiveis: data.keys.filter(k => !k.usada).length,
    vendas: data.vendas,
    vendasSemana: data.vendasSemana
  }));
  res.json({ revendedores: lista });
});

// ==================== REVENDEDOR ====================

// Login revendedor
app.post("/rev/login", (req, res) => {
  const { username, senha } = req.body;
  const rev = revendedores[username];
  if (!rev || rev.senha !== senha) return res.status(403).json({ error: "Login inválido" });
  res.json({ ok: true });
});

// Ver keys do revendedor
app.post("/rev/keys", (req, res) => {
  const { username, senha } = req.body;
  const rev = revendedores[username];
  if (!rev || rev.senha !== senha) return res.status(403).json({ error: "Acesso negado" });
  res.json({ keys: rev.keys });
});

// Revendedor distribui key (marca como usada e ativa para cliente)
app.post("/rev/distribuir", (req, res) => {
  const { username, senha, key } = req.body;
  const rev = revendedores[username];
  if (!rev || rev.senha !== senha) return res.status(403).json({ error: "Acesso negado" });
  const item = rev.keys.find(k => k.key === key && !k.usada);
  if (!item) return res.status(404).json({ error: "Key não encontrada ou já usada" });
  item.usada = true;
  keysAtivas.add(key);

  // Atualiza vendas
  const semana = semanaAtual();
  if (rev.ultimaSemana !== semana) { rev.vendasSemana = 0; rev.ultimaSemana = semana; }
  rev.vendas++;
  rev.vendasSemana++;

  res.json({ ok: true });
});

// ==================== RANKING ====================

app.get("/ranking", (req, res) => {
  const semana = semanaAtual();
  const lista = Object.entries(revendedores).map(([username, data]) => ({
    username,
    vendasSemana: data.ultimaSemana === semana ? data.vendasSemana : 0,
    vendas: data.vendas
  }));
  lista.sort((a, b) => b.vendasSemana - a.vendasSemana);
  res.json({ ranking: lista.slice(0, 10) });
});

// ==================== CLIENTE ====================

app.post("/verify", (req, res) => {
  const { key } = req.body;
  if (keysAtivas.has(key)) {
    res.json({ valid: true, script: SCRIPT });
  } else {
    res.json({ valid: false });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Volt-X rodando na porta ${PORT}`));
