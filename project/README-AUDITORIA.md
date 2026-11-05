# Pyla v0.8.19 — edição pública auditada

Este projeto continua a análise e a reconstrução realizadas nesta conversa. Não é uma recuperação por descompilação integral: as fontes públicas do commit `763c38926fbb3e2edc074db1c3ca2ddb9350d325` foram comparadas com os 19 módulos do executável fornecido, com correspondência dos campos de bytecode de 512 objetos de código. As alterações da auditoria são documentadas em `docs/ALTERACOES.md` e podem divergir intencionalmente do original.

Preserva a interface do próprio Pyla e a licença original **CC BY-NC 4.0**. A licença não permite remover a restrição de uso comercial. A edição pública já trabalha em modo local, sem servidor de assinatura; recursos premium ausentes não foram desbloqueados ou simulados. Nenhuma credencial deve ser publicada com este projeto.

## Executar no Windows

Extraia o pacote Windows inteiro e execute `start.bat`. O `.exe` fica em `internal/pyla_main.exe` e depende de `internal/_internal`, `cfg`, `models`, `images`, `api/assets`, `static`, `templates` e `playstyles`. Não mova apenas o executável.

Para executar pelas fontes, instale Python 3.11 x64 e rode no PowerShell:

```powershell
py -3.11 -m venv .venv-win
.venv-win/Scripts/python.exe -m pip install -r requirements.txt
.venv-win/Scripts/python.exe main.py --headless
```

Use `--desktop` para a janela pywebview ou `--web` para o navegador. A janela desktop depende dos componentes WebView2/.NET do Windows; a aplicação tem fallback para o navegador. A interface web escuta somente em `127.0.0.1`, com porta livre a partir de 5185 e token de sessão local. Não exponha essa porta na Internet.

## Compilar o executável nativo

```powershell
./scripts/build-windows.ps1
```

O script usa `pyla.spec`, instala as dependências declaradas, compila com PyInstaller e monta `dist/pyla-v0.8.19-auditado-r2-windows.zip`. Ele substitui apenas suas próprias saídas de build. O runtime padrão de inferência declarado pelo projeto é DirectML com CPU disponível; CUDA não é instalado automaticamente por esse script. `setup.py` original permanece para referência, mas não é necessário para essa compilação.

## Auditar em Linux

Linux não é a plataforma oficialmente suportada para a automação. É possível testar API, interface no Chromium e inferência CPU:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-linux-audit.txt -r requirements-test.txt
.venv/bin/python -m pytest tests -q --timeout=45 --junitxml=test-results/tests.xml
.venv/bin/python scripts/serve_audit.py
# Em outro terminal, com Chromium instalado:
CHROMIUM_EXECUTABLE=/usr/bin/chromium .venv/bin/python scripts/browser_audit.py
```

O script de navegador modifica temporariamente uma configuração e cria/remove uma entrada de fila. Execute-o apenas em uma cópia de teste, sem dados de produção ou bot em execução. `serve_audit.py` inicia a API e interface reais sem conectar o Discord; não substitui o fluxo de inicialização normal.

## Configuração e dependências

`cfg/general_config.toml` controla FPS, threads, CPU/GPU, modo de interface, pacote Android e porta do emulador. `cfg/bot_config.toml`, `cfg/buttons_config.toml`, `cfg/lobby_config.toml` e `cfg/time_tresholds.toml` controlam a automação. `cfg/webhook_config.toml` recebe credenciais opcionais de Discord/Telegram apenas na máquina do usuário. Configure `discord_id` antes de ativar o controle remoto Discord. Arquivos `.pyla` contêm código e exigem confiança no autor.

O modo público local usa o catálogo e os modelos incluídos. Não precisa do backend antigo Volt-X, MongoDB ou de um servidor de pagamentos. A automação requer emulador/aparelho Android com ADB autorizado e o jogo; os comandos ADB/scrcpy e o reconhecimento de tela dependem dessa conexão. O jogo e serviços opcionais continuam dependendo da sua própria infraestrutura e autenticação legítima. Consulte `docs/BACKEND-E-INTEGRACOES.md`.

Os relatórios finais ficam em `docs/` e `audit-evidence/`. Distinguem testes de componentes, testes da interface real e cenários de Windows/dispositivo que não tenham sido executados.
