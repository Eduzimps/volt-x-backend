const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const ADMIN_PASSWORD = "Eduardo123R";
const MONGO_URI = process.env.MONGO_URI;

mongoose.connect(MONGO_URI).then(() => console.log("MongoDB conectado!"));

// ===== SCHEMAS =====

const userSchema = new mongoose.Schema({
  username: { type: String, unique: true },
  senha: String,
  role: { type: String, default: "cliente" }, // cliente, revendedor
  creditos: { type: Number, default: 0 },
  vendas: { type: Number, default: 0 },
  vendasSemana: { type: Number, default: 0 },
  ultimaSemana: { type: String, default: "" }
});

const keySchema = new mongoose.Schema({
  key: { type: String, unique: true },
  revendedor: String,
  dias: Number,
  dispositivos: { type: Number, default: 1 }, // -1 = ilimitado
  dispositvosUsados: { type: [String], default: [] },
  status: { type: String, default: "ativa" }, // ativa, expirada
  criadaEm: { type: Date, default: Date.now },
  ativadaEm: { type: Date, default: null },
  expiraEm: { type: Date, default: null },
  script: { type: String, default: "" }
});

const ticketSchema = new mongoose.Schema({
  id: { type: String, unique: true },
  username: String,
  categoria: String,
  titulo: String,
  status: { type: String, default: "aberto" }, // aberto, aguardando, resolvido
  mensagens: [{
    autor: String,
    texto: String,
    data: { type: Date, default: Date.now }
  }],
  criadoEm: { type: Date, default: Date.now }
});

const Ticket = mongoose.model("Ticket", ticketSchema);
const Key = mongoose.model("Key", keySchema);

// ===== UTILS =====

const PLANOS_REV = { "1": 1, "7": 5, "30": 15, "0": 30 };
const PLANOS_CLI = { "1": 3, "7": 13, "30": 38, "0": 75 };

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

async function verificarExpiradas() {
  await Key.updateMany(
    { status: "ativa", expiraEm: { $lt: new Date(), $ne: null } },
    { status: "expirada" }
  );
}

// ===== ADMIN =====

app.post("/admin/login", (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Senha incorreta" });
  res.json({ ok: true });
});

app.post("/admin/revendedores", async (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const lista = await User.find({ role: "revendedor" });
  const result = await Promise.all(lista.map(async r => {
    const totalKeys = await Key.countDocuments({ revendedor: r.username });
    const keysAtivas = await Key.countDocuments({ revendedor: r.username, status: "ativa" });
    return { username: r.username, creditos: r.creditos, totalKeys, keysAtivas, vendas: r.vendas, vendasSemana: r.vendasSemana };
  }));
  res.json({ revendedores: result });
});

// Lista clientes (não revendedores)
app.post("/admin/clientes", async (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const lista = await User.find({ role: "cliente" }, "username");
  res.json({ clientes: lista });
});

// Promover cliente para revendedor
app.post("/admin/promover", async (req, res) => {
  const { senha, username } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const user = await User.findOne({ username });
  if (!user) return res.status(404).json({ error: "Usuário não encontrado" });
  user.role = "revendedor";
  await user.save();
  res.json({ ok: true });
});

// Rebaixar revendedor para cliente
app.post("/admin/rebaixar", async (req, res) => {
  const { senha, username } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const user = await User.findOne({ username });
  if (!user) return res.status(404).json({ error: "Usuário não encontrado" });
  user.role = "cliente";
  await user.save();
  res.json({ ok: true });
});

app.delete("/admin/revendedor", async (req, res) => {
  const { senha, username } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  await User.deleteOne({ username });
  await Key.deleteMany({ revendedor: username });
  res.json({ ok: true });
});

app.post("/admin/creditos", async (req, res) => {
  const { senha, username, quantidade } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const user = await User.findOne({ username, role: "revendedor" });
  if (!user) return res.status(404).json({ error: "Revendedor não encontrado" });
  user.creditos += quantidade;
  await user.save();
  res.json({ ok: true, creditos: user.creditos });
});

app.post("/admin/gerarkey", async (req, res) => {
  const { senha, dias, dispositivos, quantidade } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const novas = [];
  for (let i = 0; i < quantidade; i++) {
    const key = gerarKey();
    await Key.create({ key, revendedor: "admin", dias: parseInt(dias), dispositivos: parseInt(dispositivos) });
    novas.push(key);
  }
  res.json({ keys: novas });
});

// ===== REVENDEDOR =====

// Registro de novo usuário (vira cliente)
app.post("/registro", async (req, res) => {
  const { username, senha } = req.body;
  if (!username || !senha) return res.status(400).json({ error: "Preencha todos os campos" });
  try {
    await User.create({ username, senha, role: "cliente" });
    res.json({ ok: true });
  } catch {
    res.status(400).json({ error: "Usuário já existe" });
  }
});

app.post("/rev/login", async (req, res) => {
  const { username, senha } = req.body;
  const user = await User.findOne({ username, senha });
  if (!user) return res.status(403).json({ error: "Login inválido" });
  res.json({ ok: true, role: user.role, creditos: user.creditos });
});

app.post("/rev/gerar", async (req, res) => {
  const { username, senha, dias, quantidade } = req.body;
  const user = await User.findOne({ username, senha });
  if (!user || (user.role !== "revendedor" && user.role !== "cliente")) return res.status(403).json({ error: "Acesso negado" });

  const planos = user.role === "cliente" ? PLANOS_CLI : PLANOS_REV;
  const custoUnitario = planos[String(dias)];
  if (!custoUnitario) return res.status(400).json({ error: "Plano inválido" });
  const custoTotal = custoUnitario * quantidade;

  if (user.creditos < custoTotal) return res.status(400).json({ error: "Créditos insuficientes" });

  const novas = [];
  for (let i = 0; i < quantidade; i++) {
    const key = gerarKey();
    await Key.create({ key, revendedor: username, dias: parseInt(dias), dispositivos: 1 });
    novas.push(key);
  }

  user.creditos -= custoTotal;
  user.vendas += quantidade;
  const semana = semanaAtual();
  if (user.ultimaSemana !== semana) { user.vendasSemana = 0; user.ultimaSemana = semana; }
  user.vendasSemana += quantidade;
  await user.save();

  res.json({ keys: novas, creditosRestantes: user.creditos });
});

app.post("/rev/keys", async (req, res) => {
  const { username, senha } = req.body;
  const user = await User.findOne({ username, senha });
  if (!user || (user.role !== "revendedor" && user.role !== "cliente")) return res.status(403).json({ error: "Acesso negado" });
  await verificarExpiradas();
  const keys = await Key.find({ revendedor: username }).sort({ criadaEm: -1 });
  res.json({ keys, creditos: user.creditos, planos: user.role === "cliente" ? PLANOS_CLI : PLANOS_REV });
});

// Limpar todos usuários exceto admin (não tem usuário admin no banco)
app.post("/admin/limpar-usuarios", async (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  await User.deleteMany({});
  await Key.deleteMany({});
  res.json({ ok: true });
});

// ===== TICKETS =====

function gerarIdTicket() {
  return "TKT-" + Date.now().toString(36).toUpperCase();
}

// Abrir ticket
app.post("/ticket/abrir", async (req, res) => {
  const { username, senha, categoria, titulo, mensagem } = req.body;
  const user = await User.findOne({ username, senha });
  if (!user) return res.status(403).json({ error: "Acesso negado" });
  const ticket = await Ticket.create({
    id: gerarIdTicket(),
    username,
    categoria,
    titulo,
    mensagens: [{ autor: username, texto: mensagem }]
  });
  res.json({ ok: true, ticket });
});

// Ver tickets do usuário
app.post("/ticket/meus", async (req, res) => {
  const { username, senha } = req.body;
  const user = await User.findOne({ username, senha });
  if (!user) return res.status(403).json({ error: "Acesso negado" });
  const tickets = await Ticket.find({ username }).sort({ criadoEm: -1 });
  res.json({ tickets });
});

// Responder ticket (usuário ou admin)
app.post("/ticket/responder", async (req, res) => {
  const { username, senha, ticketId, mensagem } = req.body;
  const isAdmin = senha === ADMIN_PASSWORD;
  if (!isAdmin) {
    const user = await User.findOne({ username, senha });
    if (!user) return res.status(403).json({ error: "Acesso negado" });
  }
  const ticket = await Ticket.findOne({ id: ticketId });
  if (!ticket) return res.status(404).json({ error: "Ticket não encontrado" });
  ticket.mensagens.push({ autor: isAdmin ? "Admin" : username, texto: mensagem });
  ticket.status = isAdmin ? "aguardando" : "aberto";
  await ticket.save();
  res.json({ ok: true });
});

// Admin: ver todos os tickets
app.post("/admin/tickets", async (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const tickets = await Ticket.find().sort({ criadoEm: -1 });
  res.json({ tickets });
});

// Admin: mudar status do ticket
app.post("/admin/ticket/status", async (req, res) => {
  const { senha, ticketId, status } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  await Ticket.updateOne({ id: ticketId }, { status });
  res.json({ ok: true });
});

// ===== RANKING =====

app.get("/ranking", async (req, res) => {
  const semana = semanaAtual();
  const lista = await User.find({ role: "revendedor" });
  const ranking = lista.map(r => ({
    username: r.username,
    vendasSemana: r.ultimaSemana === semana ? r.vendasSemana : 0,
    vendas: r.vendas
  })).sort((a, b) => b.vendasSemana - a.vendasSemana).slice(0, 10);
  res.json({ ranking });
});

// ===== CLIENTE =====

app.post("/verify", async (req, res) => {
  const { key, hwid } = req.body;
  await verificarExpiradas();
  const item = await Key.findOne({ key });
  if (!item || item.status === "expirada") return res.json({ valid: false, motivo: "Key inválida ou expirada" });

  // Primeira vez usando
  if (!item.ativadaEm) {
    item.ativadaEm = new Date();
    if (item.dias > 0) {
      item.expiraEm = new Date(Date.now() + item.dias * 24 * 60 * 60 * 1000);
    }
    if (hwid && !item.dispositvosUsados.includes(hwid)) {
      item.dispositvosUsados.push(hwid);
    }
    await item.save();
    return res.json({ valid: true });
  }

  // Verificar dispositivo
  if (hwid) {
    if (item.dispositivos !== -1 && !item.dispositvosUsados.includes(hwid)) {
      if (item.dispositvosUsados.length >= item.dispositivos) {
        return res.json({ valid: false, motivo: "Limite de dispositivos atingido" });
      }
      item.dispositvosUsados.push(hwid);
      await item.save();
    }
  }

  res.json({ valid: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Volt-X rodando na porta ${PORT}`));
