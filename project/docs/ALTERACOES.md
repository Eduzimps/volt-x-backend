# Alterações da auditoria

As fontes públicas verificadas foram preservadas em `/workspace/pyla-analysis/recovered/verified-source` na máquina de trabalho. A entrega auditada mantém a organização original e identifica aqui as diferenças.

1. `utils.py`: gravação de TOML e da fila por arquivo temporário + flush/fsync + substituição atômica. Uma falha de serialização não trunca o arquivo anterior; a atualização de cache ocorre apenas depois de salvar.
2. `webui/services.py`: falha de disco ao salvar fila deixa de ser ocultada. O estado em memória só é atualizado após sucesso. A reordenação rejeita nomes duplicados e formatos inválidos. Configurações numéricas rejeitam valores não finitos, negativos, FPS/threads zero, portas fora de 1–65535 e confiança fora de 0–1.
3. `webui/app.py`: requisições JSON de escrita precisam conter um objeto; listas, escalares e JSON malformado retornam 400, preservando a proteção de host, origem e token.
4. `discord_bot.py`: controle remoto nega comandos se `discord_id` não estiver configurado. A ausência de autorização deixa de liberar qualquer usuário. A integração continua opcional e não se conecta durante os testes locais.
5. `start.bat`: fixa o diretório de trabalho na pasta do aplicativo e encaminha argumentos, evitando depender da pasta de onde o usuário o abriu.
6. `utils.py`/`webui/services.py`: importação de estilos valida que o cabeçalho é um objeto com campos textuais/listas de nomes e que existe código. Cabeçalhos JSON de tipos inadequados deixam de contaminar a biblioteca e quebrar o bootstrap. Se um estilo inválido já existir em disco, o carregamento degrada para metadados vazios, sem quebrar a API.
7. Scripts de build nativo Windows, execução, inventário, smoke test do executável e auditoria do navegador; suíte de regressão e documentação foram adicionados.

Até a revisão R2, os arquivos da interface não foram alterados. Na R3, HTML e app.js retiram anúncios, botões de upgrade, cartões demonstrativos de outros perfis e campos indisponíveis da edição local. O aviso de recurso ausente passa a ser informativo, sem pedir assinatura. CSS, traduções, modelos e estilos existentes são preservados. Não foram removidos bloqueios premium ou controles de acesso. A dependência de autorizações legítimas de Discord, Telegram, ADB e jogo permanece.

Os 14 casos de regressão que falhavam na primeira execução passaram depois dessas correções. A inspeção adicional da importação reproduziu outros seis casos que falhavam; os seis também passaram após a correção. A suíte final tem 51 casos. Isso representa os casos testados, não a garantia de ausência de defeitos em toda a aplicação.

## Revisão R3 — interface local sem anúncios

Removidos: link lateral Explore Premium, cartões de perfis bloqueados, dicas comerciais, botão Push All bloqueado, campo de player tag sem backend e opções de ordenação por dados remotos indisponíveis. As funções existentes da fila, configurações e execução continuam. O estado de assinatura permanece `premium=False`; não foram ativados recursos privados nem alteradas autorizações. A mensagem sobre modos não suportados descreve a limitação desta build, sem anunciar um plano pago.


## R4 — funções próprias e integração

- `profiles.py` cria diretórios isolados, inicia o aplicativo em processos separados, verifica identidade e disponibilidade HTTP e encerra somente após parada confirmada.
- `main.py` seleciona o perfil antes de importar módulos que leem configuração. O lançador preserva o caminho do Python virtualenv; falha detectada pelo teste de integração real foi corrigida.
- `player_data.py` valida snapshots, persiste atomicamente e consulta a API oficial somente mediante ação explícita e chave local legítima.
- `webui` e `static/js/app.js` conectam perfis, importação, ordenação, Push All e depuração à interface existente.
- `discord_bot.py` implementa comandos de fila e ativação de estilos com autorização por proprietário.
- Empacotamento exclui perfis, snapshots pessoais e marcadores de execução. Scripts de teste exercitam processos reais e dados sintéticos isolados.
