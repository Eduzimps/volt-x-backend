# Relatório de testes

## Linux, instância atual

- Baseline: 41 casos executados, 27 passaram e 14 falharam, antes das correções.
- Suíte final: **51 passaram, 0 falharam, 0 ignorados**, após correções e usando OpenCV da faixa 4.x do projeto. Evidências JUnit e texto em `audit-evidence/all-tests.*`.
- 47 casos cobrem rotas, CRUD/persistência de fila, configurações/reset, validações, proteção de host/origem/token, mascaramento de credenciais, estilos, datas, controle de estado e autorização Discord. O trabalhador de automação e a interação Discord são simulados nos testes de controle/autorização; isso não comprova integração externa.
- Seis regressões adicionais reproduziram importações de estilos inválidos; todos passaram após a correção (baseline adicional em `audit-evidence/import-baseline.*`).
- Quatro casos executam inferência real em CPU nos três modelos ONNX distribuídos e o pipeline Detect em dois desses modelos. São entradas sintéticas, não partidas nem avaliação de acurácia.
- Navegador Chromium real: **13 verificações concluídas**, 0 erros JavaScript capturados e 0 falhas HTTP dos assets locais. Incluem seis telas, inclusão de fila pelo botão, autosave com recarga, biblioteca, ausência de pedidos de assinatura e carrossel de dicas, espanhol e menu móvel. As requisições de Google Fonts foram bloqueadas intencionalmente, para verificar a operação com fallback; não é prova de aparência tipográfica idêntica com/sem rede.
- Capturas das seis telas e do modo móvel em `audit-evidence/browser/`. CSS, HTML e JavaScript originais preservados; os testes não cobrem individualmente cada botão, animação ou gesto.
- Aviso de depreciação `audioop` do discord.py no Python 3.11, sem falha.

## Windows e hardware

Os scripts e o workflow preparam compilação nativa no Windows e smoke test real do .exe headless. O resultado será registrado separadamente em `TESTES-WINDOWS-CI.md`/relatórios da execução no GitHub. Até existir esse relatório, não se declara compilação nem execução Windows comprovadas nesta etapa.

Permanecem sem validação: janela pywebview gráfica, emulador/aparelho, ADB/scrcpy real, jogo/partidas, GPU CUDA/DirectML, notificações Discord/Telegram/webhook com credenciais, precisão dos modelos e estabilidade sob carga prolongada. Nenhuma credencial externa foi solicitada ou inventada.

## Revisão R3

51 testes automatizados passaram novamente em Linux. O teste do navegador agora verifica a ausência de anúncios de Premium nas seis telas e em todas as dicas, além de confirmar que a assinatura continua falsa e a fila vazia continua vazia. O teste de modal antigo da R2 foi substituído por essas verificações. O relatório do build Windows desta revisão deve ser consultado separadamente.

A verificação da R3 concluiu 13 casos de navegador, sem erros JavaScript e sem assets locais ausentes. Nenhum teste de navegação ativa o estado premium; ele é explicitamente verificado como falso.
