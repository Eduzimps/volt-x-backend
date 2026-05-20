const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// 🔑 Adicione suas keys aqui
const keys = [
  "VOLTX-XXXX-XXXX-XXXX"
];

const SCRIPT = `loadstring(game:HttpGet("https://seusite.com/script.lua"))()`;

app.post("/verify", (req, res) => {
  const { key } = req.body;
  if (keys.includes(key)) {
    res.json({ valid: true, script: SCRIPT });
  } else {
    res.json({ valid: false });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Volt-X rodando na porta ${PORT}`));
