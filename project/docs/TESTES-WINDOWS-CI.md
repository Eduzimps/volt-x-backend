# Testes nativos Windows no GitHub Actions

Executados nesta execucao: https://github.com/Eduzimps/volt-x-backend/actions/runs/42035770309

- Dependencias Windows instaladas e suite pytest concluida sem falhas; contagens no JUnit audit-evidence/windows-tests.xml.
- Compilacao nativa PyInstaller concluida no Windows x64 com Python 3.11.
- O executavel compilado foi iniciado de verdade em modo headless: HTML e bootstrap locais responderam; estado publico de licenciamento preservado; FPS zero rejeitado com HTTP 400.
- Nao foram testados janela grafica pywebview, GPU, Android/ADB/scrcpy, partidas ou integracoes externas autenticadas.
