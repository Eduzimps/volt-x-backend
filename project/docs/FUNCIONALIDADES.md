# Funcionalidades e estado de validação

| Área | Identificado na implementação | Evidência e limite |
|---|---|---|
| Painel | Estado, início, pausa, retomada, parada, fila e prévia de estilo | Tela real carregada em Chromium. Estado vazio testado na API. Ciclo de execução testado com trabalhador simulado; jogo não executado. |
| Fila | Adicionar/editar/remover, limpar, reordenar, importar JSON, metas por troféus/vitórias, autopick e ordenação | CRUD/persistência/reordenação na API; inclusão por botão real no navegador. Importação e ordenação dinâmica não receberam validação ponta a ponta completa. |
| Estilos | Biblioteca, busca, importação, ativação e exclusão | Biblioteca no navegador; importar/ativar/excluir, proteção contra caminho inválido e rejeição de seis formatos inválidos/vazios testados na API. Execução de estilos no jogo não testada. |
| Histórico | CSV, resumo, sessões, gráficos, filtros por data/brawler e detalhes | Tela carregada e datas inválidas rejeitadas. Nenhuma partida real gerada; gráficos com histórico real e todas as combinações de filtros permanecem pendentes. |
| Logs | Visualização, atualização e limpeza de buffer | API e tela carregadas; não é benchmark de sessões longas. |
| Configurações | Geral, combate, temporização, depuração e webhooks; autosave, reset, importação de instalação antiga | Cinco seções e resets via API; autosave com recarga no navegador; validação numérica e sigilo das credenciais testados. Migração de cada versão antiga não testada. |
| Navegação e visual | Seis telas, ícones, tema, tooltips, barras de rolagem, dicas, carrossel, menu responsivo | Seis telas e menu móvel exercitados; sem erro JavaScript e sem falha de assets locais na execução registrada. Tema e CSS preservados; HTML/JS ajustados na R3 para retirar promoções. Nem cada animação, tooltip ou gesto recebeu asserção individual. |
| Idiomas | Inglês, espanhol, francês, coreano e russo | Mudança para espanhol e recarga testadas. Qualidade de todas as traduções não revisada; português não implementado. |
| Desktop | Janela pywebview, ícone, tamanho, console e fallback para navegador | Código preservado e build configurado. A abertura gráfica da janela no Windows não integra os testes Linux; consultar relatório Windows para smoke test headless. |
| ADB/scrcpy | Descoberta de emuladores, scan profundo, captura, toque e reinício do jogo | Código presente. Nenhum dispositivo foi conectado durante esta auditoria. |
| Inferência | Três modelos ONNX, CPU/DirectML/CUDA e pós-processamento | Os três modelos rodaram em CPU com tensores sintéticos; pipeline Detect rodou com imagem preta. Sem benchmark de acurácia ou teste GPU. |
| Automação | Movimento, combate, recuperação, lobby, seleção de brawler, detecção de estado, temporizadores e observação de troféus | Implementação incluída; nenhuma partida/emulador/jogo foi automatizado na auditoria. |
| Depuração | Preview por memória compartilhada, overlays, clipes e logs de partidas | Implementação presente; captura/visualização/clipes exigem execução real e não foram testados. |
| Discord | Bot opcional, autorização por ID, comandos de controle e screenshot | Negação sem ID autorizado testada com interação simulada. Comandos reais, conexão e permissões do bot não testados. |
| Telegram/webhook | Notificações de status/evento e imagem | Credenciais mascaradas/preservadas/limpas na API; entrega real não testada, sem credenciais. |
| Perfis locais R4 | Criar, abrir e encerrar instâncias com dados separados | Implementação própria; processos reais verificam isolamento. Emuladores simultâneos pendentes. |
| Estatísticas R4 | Importar JSON, consulta explícita à API oficial, ordenação e Push All | Importação/Push All testados na API; cliente remoto testado com mocks, sem chave real. |
| Discord R4 | Adicionar/remover/limpar fila e ativar estilo | 45 testes de callbacks e autorização, sem conexão Discord real. |
| Edição Premium | Backend privado e algoritmos ausentes | Não recuperados. Os recursos locais acima são implementações independentes; assinatura continua falsa. |

Os nomes de todas as rotas locais estão em `ROTAS-LOCAIS.json`. O inventário de funções/classes está em `MODULOS.md`/`INVENTARIO.json`. A presença de código não é apresentada como comprovação de funcionamento.
