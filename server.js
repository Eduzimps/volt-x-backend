const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const SCRIPT = `loadstring(game:HttpGet("https://seusite.com/script.lua"))()`;

// Banco de keys ativas
const keys = new Set();

function gerarKey() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const parte = () => Array.from({length: 4}, () => chars[Math.floor(Math.random() * chars.length)]).join("");
  return `VOLT-X-${parte()}-${parte()}-${parte()}`;
}

// Gera uma key nova
app.get("/gerar", (req, res) => {
  const senha = req.query.senha;
  if (senha !== "voltxadmin") return res.status(403).json({ error: "Acesso negado" });
  const key = gerarKey();
  keys.add(key);
  res.json({ key });
});

// Lista todas as keys ativas
app.get("/keys", (req, res) => {
  const senha = req.query.senha;
  if (senha !== "voltxadmin") return res.status(403).json({ error: "Acesso negado" });
  res.json({ keys: [...keys] });
});

// Remove uma key
app.get("/remover", (req, res) => {
  const senha = req.query.senha;
  if (senha !== "voltxadmin") return res.status(403).json({ error: "Acesso negado" });
  const key = req.query.key;
  keys.delete(key);
  res.json({ removida: key });
});

// Verifica key
app.post("/verify", (req, res) => {
  const { key } = req.body;
  if (keys.has(key)) {
    res.json({ valid: true, script: SCRIPT });
  } else {
    res.json({ valid: false });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Volt-X rodando na porta ${PORT}`));
