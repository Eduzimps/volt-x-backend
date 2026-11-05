# Backend, serviços e edição gratuita

## Núcleo local

O backend deste aplicativo é Flask, criado por `webui/app.py`, servido no loopback pelo próprio processo. O código e o catálogo públicos selecionam `api_base_url = localhost` por padrão quando não existe o módulo proprietário Early Access. Isso é uma opção da implementação pública já existente, não uma emulação de autenticação ou de licença.

Não há banco MongoDB/SQL obrigatório para a aplicação. Configurações usam TOML/JSON; fila usa `latest_brawler_data.json`; histórico e logs usam arquivos CSV e pastas locais. O Volt-X antigo não é necessário. O aplicativo exige permissão de leitura/escrita na pasta de dados. Escritas individuais de fila/configuração agora são atômicas; operações concorrentes de leitura-modificação-gravação ainda podem sobrepor alterações (não foi implementado um banco transacional).

## Serviços externos identificados

| Serviço/destino no código | Uso | Obrigatório para núcleo local? | Validação |
|---|---|---|---|
| ADB local, porta configurada (e portas de emuladores descobertas) | Conectar ao Android, scrcpy e comandos de controle | Para automação, sim; para UI, não | Sem dispositivo conectado; pendente |
| `api.brawlapi.com/v1/brawlers` e URLs de ícones retornadas | Atualizar/download de ícones e dados de catálogo | Não; catálogo/ícones incluídos são usados localmente | Não consultado pela auditoria |
| Host configurado em `api_base_url` | Endpoints `/get_brawler_list`, `/get_brawler_info`, `/check_version`, `/announcements`, `/get_discord_link`, `/get_wall_model_hash`, `/get_wall_model_file`, `/get_wall_model_classes` | Não no modo público localhost | Endpoints identificados no código; não foram inventados nem testados remotamente |
| Discord (discord.py, URL de webhook configurada, `discord.gg/xUusk3fw4A`) | Bot, notificações e link comunitário | Não | Sem credenciais/conexão; apenas fronteira de autorização em teste unitário |
| `api.telegram.org` com token fornecido localmente | Notificações por bot | Não | Não testado remotamente |
| `fonts.googleapis.com`, `fonts.gstatic.com` | Fonte Inter da interface | Não; há fallback CSS | Interface testada com esses pedidos bloqueados |
| `pyla-ai.angelfirela.dev`, Patreon | Downloads, divulgação, preço e assinatura externos | Não para núcleo público | Links identificados; pagamento não implementado localmente nem testado |
| Servidores do jogo/Supercell | Funcionamento normal do jogo Android | Sim para partidas | Não testados; autenticação legítima continua necessária |

`api/api.py` é um utilitário legado de download de imagens, com acesso remoto no nível superior do arquivo; não é o servidor Flask utilizado pela interface. Ele não foi importado/executado nos testes.

## Planos, pagamentos e licença

`WebDataService.get_auth_state()` já retorna `required=False`, `authenticated=True`, `premium=False` na edição pública correspondente ao binário. `get_player_info`/`get_brawler_stats` têm retornos vazios nessa edição e não implementam sincronização remota real. Os arquivos ignorados `api/licensing_backend.py`/`api/licensing_bot.py` e o módulo Early Access não estão presentes no código entregue; não se afirma recuperar seus serviços.

Não foi fornecida prova de propriedade desses serviços privados. Portanto não foram removidas restrições premium, forjado estado de assinatura, reproduzidos endpoints de autenticação ou incluídas credenciais. A edição local gratuita legítima foi mantida. Funcionalidades proprietárias indisponíveis foram documentadas; não foram criadas alternativas próprias completas para estatísticas remotas, multiprofile ou pagamento nesta auditoria. Qualquer alternativa futura deve ser implementação independente e testada, com APIs e autorizações legítimas.

A licença CC BY-NC 4.0 original e a atribuição permanecem. Uma edição sem cobrança é possível sob seus termos; transformar isso em software sem restrições de uso comercial exige autorização adicional do titular. O sistema não foi relicenciado.

## Limitações de estabilidade e desempenho

- Requests remotos legados sem timeout ainda existem em `utils.py` e `api/api.py`. Não são chamados no percurso público local testado; configurar API remota pode causar demora/travamento e exige auditoria específica antes de uso.
- Descoberta ADB profunda pode tentar dezenas de milhares de portas do loopback; é opcional, protegida por lock e pode consumir tempo. Não foi executada neste ambiente sem emulador.
- CPU/GPU, acurácia, FPS sustentado, memória de sessões longas e mudanças futuras no jogo não foram benchmarkados. Os tempos dos testes sintéticos não representam FPS de jogo.
- `.pyla` contém código Python. A proteção de nomes/caminhos não transforma um estilo importado em código confiável. Importe apenas de autores confiáveis; não há sandbox completa para extensões.
- Credenciais opcionais são armazenadas no TOML da máquina do usuário e mascaradas nas respostas da interface; não há cofre de segredos/criptografia de disco implementado.
- A integração Discord agora exige `discord_id`; instalações antigas que deixavam esse campo vazio devem configurá-lo explicitamente.
