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

const revSchema = new mongoose.Schema({
  username: { type: String, unique: true },
  senha: String,
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

const Revendedor = mongoose.model("Revendedor", revSchema);
const Key = mongoose.model("Key", keySchema);

// ===== UTILS =====

const PLANOS = {
  "1": 1,
  "7": 5,
  "30": 15,
  "0": 30 // 0 = permanente
};

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
  const lista = await Revendedor.find();
  const result = await Promise.all(lista.map(async r => {
    const totalKeys = await Key.countDocuments({ revendedor: r.username });
    const keysAtivas = await Key.countDocuments({ revendedor: r.username, status: "ativa" });
    return { username: r.username, creditos: r.creditos, totalKeys, keysAtivas, vendas: r.vendas, vendasSemana: r.vendasSemana };
  }));
  res.json({ revendedores: result });
});

app.post("/admin/revendedor", async (req, res) => {
  const { senha, username, senhaRev } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  try {
    await Revendedor.create({ username, senha: senhaRev });
    res.json({ ok: true });
  } catch {
    res.status(400).json({ error: "Revendedor já existe" });
  }
});

app.delete("/admin/revendedor", async (req, res) => {
  const { senha, username } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  await Revendedor.deleteOne({ username });
  await Key.deleteMany({ revendedor: username });
  res.json({ ok: true });
});

app.post("/admin/creditos", async (req, res) => {
  const { senha, username, quantidade } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const rev = await Revendedor.findOne({ username });
  if (!rev) return res.status(404).json({ error: "Revendedor não encontrado" });
  rev.creditos += quantidade;
  await rev.save();
  res.json({ ok: true, creditos: rev.creditos });
});

// Admin gera key com opção de dispositivos
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

app.post("/rev/login", async (req, res) => {
  const { username, senha } = req.body;
  const rev = await Revendedor.findOne({ username, senha });
  if (!rev) return res.status(403).json({ error: "Login inválido" });
  res.json({ ok: true, creditos: rev.creditos });
});

app.post("/rev/gerar", async (req, res) => {
  const { username, senha, dias, quantidade } = req.body;
  const rev = await Revendedor.findOne({ username, senha });
  if (!rev) return res.status(403).json({ error: "Acesso negado" });

  const custoUnitario = PLANOS[String(dias)];
  if (!custoUnitario) return res.status(400).json({ error: "Plano inválido" });
  const custoTotal = custoUnitario * quantidade;

  if (rev.creditos < custoTotal) return res.status(400).json({ error: "Créditos insuficientes" });

  const novas = [];
  for (let i = 0; i < quantidade; i++) {
    const key = gerarKey();
    await Key.create({ key, revendedor: username, dias: parseInt(dias), dispositivos: 1 });
    novas.push(key);
  }

  rev.creditos -= custoTotal;
  rev.vendas += quantidade;
  const semana = semanaAtual();
  if (rev.ultimaSemana !== semana) { rev.vendasSemana = 0; rev.ultimaSemana = semana; }
  rev.vendasSemana += quantidade;
  await rev.save();

  res.json({ keys: novas, creditosRestantes: rev.creditos });
});

app.post("/rev/keys", async (req, res) => {
  const { username, senha } = req.body;
  const rev = await Revendedor.findOne({ username, senha });
  if (!rev) return res.status(403).json({ error: "Acesso negado" });
  await verificarExpiradas();
  const keys = await Key.find({ revendedor: username }).sort({ criadaEm: -1 });
  res.json({ keys, creditos: rev.creditos });
});

// ===== RANKING =====

app.get("/ranking", async (req, res) => {
  const semana = semanaAtual();
  const lista = await Revendedor.find();
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
