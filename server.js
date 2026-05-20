const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const ADMIN_PASSWORD = "Eduardo123R";
const SCRIPT = `loadstring(game:HttpGet("https://seusite.com/script.lua"))()`;
const MONGO_URI = process.env.MONGO_URI;

mongoose.connect(MONGO_URI).then(() => console.log("MongoDB conectado!"));

// ===== SCHEMAS =====

const keySchema = new mongoose.Schema({
  key: { type: String, unique: true },
  usada: { type: Boolean, default: false },
  revendedor: String
});

const revSchema = new mongoose.Schema({
  username: { type: String, unique: true },
  senha: String,
  vendas: { type: Number, default: 0 },
  vendasSemana: { type: Number, default: 0 },
  ultimaSemana: { type: String, default: "" }
});

const Key = mongoose.model("Key", keySchema);
const Revendedor = mongoose.model("Revendedor", revSchema);

// ===== UTILS =====

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

// ===== ADMIN =====

app.post("/admin/revendedores", async (req, res) => {
  const { senha } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const lista = await Revendedor.find();
  const result = await Promise.all(lista.map(async r => {
    const totalKeys = await Key.countDocuments({ revendedor: r.username });
    const keysDisponiveis = await Key.countDocuments({ revendedor: r.username, usada: false });
    return { username: r.username, totalKeys, keysDisponiveis, vendas: r.vendas, vendasSemana: r.vendasSemana };
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

app.post("/admin/addkeys", async (req, res) => {
  const { senha, username, quantidade } = req.body;
  if (senha !== ADMIN_PASSWORD) return res.status(403).json({ error: "Acesso negado" });
  const rev = await Revendedor.findOne({ username });
  if (!rev) return res.status(404).json({ error: "Revendedor não encontrado" });
  const novas = [];
  for (let i = 0; i < quantidade; i++) {
    const key = gerarKey();
    await Key.create({ key, revendedor: username });
    novas.push(key);
  }
  res.json({ keys: novas });
});

// ===== REVENDEDOR =====

app.post("/rev/login", async (req, res) => {
  const { username, senha } = req.body;
  const rev = await Revendedor.findOne({ username, senha });
  if (!rev) return res.status(403).json({ error: "Login inválido" });
  res.json({ ok: true });
});

app.post("/rev/keys", async (req, res) => {
  const { username, senha } = req.body;
  const rev = await Revendedor.findOne({ username, senha });
  if (!rev) return res.status(403).json({ error: "Acesso negado" });
  const keys = await Key.find({ revendedor: username });
  res.json({ keys });
});

app.post("/rev/distribuir", async (req, res) => {
  const { username, senha, key } = req.body;
  const rev = await Revendedor.findOne({ username, senha });
  if (!rev) return res.status(403).json({ error: "Acesso negado" });
  const item = await Key.findOne({ key, revendedor: username, usada: false });
  if (!item) return res.status(404).json({ error: "Key não encontrada ou já usada" });
  item.usada = true;
  await item.save();

  const semana = semanaAtual();
  if (rev.ultimaSemana !== semana) { rev.vendasSemana = 0; rev.ultimaSemana = semana; }
  rev.vendas++;
  rev.vendasSemana++;
  await rev.save();

  res.json({ ok: true });
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
  const { key } = req.body;
  const item = await Key.findOne({ key, usada: true });
  if (item) {
    res.json({ valid: true, script: SCRIPT });
  } else {
    res.json({ valid: false });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Volt-X rodando na porta ${PORT}`));
