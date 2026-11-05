# Recursos locais próprios — R4

Esta revisão adiciona implementações próprias à edição pública. Não contém o backend privado Premium. A licença original CC BY-NC 4.0 e o estado de assinatura da edição pública são preservados.

## Perfis

No Dashboard, digite um nome e clique em Create profile. Launch abre outra instância em uma aba do navegador; Stop instance pede a parada da automação e só encerra o processo após confirmação. Configure uma porta de emulador diferente em cada instância antes de iniciar partidas.

Cada perfil possui cfg, fila, histórico, estilos e modelos próprios em `profiles/<id>/`. Ícones e runtime imutável podem ser compartilhados por links, com cópia como fallback. Credenciais de webhook/Discord/Telegram não são copiadas; configure-as separadamente. A API oficial usa a variável de ambiente herdada da máquina. Não há limite comercial de quantidade; memória, disco e capacidade do computador limitam o uso. O encerramento pelo painel só controla filhos iniciados por aquela instância principal. Após reiniciar a principal, abra o perfil existente e encerre-o pela sua própria interface quando necessário.

Testes com processos reais verificam isolamento de fila e configurações e abertura/encerramento HTTP. Vários emuladores jogando simultaneamente não foram testados.

## Estatísticas e Push All

Em Brawlers, Import player JSON aceita um snapshot local ou resposta oficial. Dados importados ficam explicitamente identificados como Imported snapshot; não são sincronização ao vivo. O formato local é:

```json
{
  "player_tag": "PYLQGR",
  "player_name": "EXEMPLO FICTICIO",
  "stats": {
    "SHELLY": {"trophies": 120, "power_level": 5},
    "COLT": {"trophies": 1500, "power_level": 7}
  }
}
```

Este exemplo é sintético. Use seus dados reais. Campos ausentes permanecem ausentes; sequência de vitórias não é inventada. Também é aceito o formato da API oficial com `tag`, `name` e `brawlers`. O arquivo máximo é de 2 MiB. `player-data.json` guarda o snapshot de cada perfil.

Push All adiciona os brawlers conhecidos no snapshot abaixo de Default Trophy Target. Preserva progresso já existente e ignora registros sem troféus. A ordenação por troféus/poder usa os valores importados; dados ausentes aparecem como travessão.

Para Sync official API, obtenha sua própria chave autorizada em https://developer.brawlstars.com e configure os IPs permitidos no portal. No PowerShell, defina localmente `BRAWL_STARS_API_TOKEN` para sua chave e inicie `start.bat` no mesmo terminal. Não publique a chave nem a coloque no repositório. O cliente consulta apenas `https://api.brawlstars.com/v1/players/%23TAG`, com TLS, timeout, limite de resposta e sem redirecionamentos. Nenhuma consulta é feita automaticamente ao abrir a interface. A chave não é gravada no snapshot nem enviada ao navegador.

A integração foi testada com respostas simuladas e erros de rede/autorização. Sem chave disponível, uma consulta externa real permanece pendente.

## Depuração e Discord

Os controles públicos de overlays avançados e gravação de preview foram expostos em Settings. As rotinas de desenho foram exercitadas com imagens sintéticas. A gravação de clipes e a captura de jogo real permanecem pendentes.

Discord ganhou `/add_to_queue`, `/remove_from_queue`, `/clear_queue` e `/activate_playstyle`, com validação de parâmetros e exigência do ID de proprietário autorizado. Os testes executam callbacks reais contra arquivos temporários, com interação Discord simulada. A entrega por bot autenticado não foi testada. Configure token e `discord_id` em `cfg/webhook_config.toml` somente na sua máquina.

## O que não está incluído

Não se afirma reproduzir todas as funções comerciais. Mira preditiva, pathfinding proprietário, backend Premium, sincronização privada e qualquer algoritmo ausente das fontes públicas não foram recuperados ou simulados. Nenhuma partida, emulador, GPU ou integração externa autenticada foi validada nesta revisão. Os relatórios de testes distinguem esses limites das funções locais verificadas.
