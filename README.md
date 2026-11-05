# Pyla v0.8.19 — executável reconstruído

Extraia primeiro o ZIP original do Pyla. Feche o programa, guarde uma cópia do executável antigo e substitua `internal/pyla_main.exe` pelo arquivo desta branch. Mantenha todas as demais pastas e execute `start.bat`. Este .exe depende dos arquivos do pacote original.

Os 19 módulos da aplicação foram recompilados de fontes públicas verificadas contra o bytecode original. O carregador Windows e as dependências originais foram preservados. A reconstrução foi verificada estaticamente; a execução no Windows ainda não foi testada. Não foram adicionadas funcionalidades ou removidas verificações.

Fontes: https://github.com/PylaAI/PylaAI — commit 763c38926fbb3e2edc074db1c3ca2ddb9350d325. Licença: CC BY-NC 4.0, conforme LICENSE.

SHA-256 do executável: 17c4d88095794f162578969d698dab674facae553331dea64b3ed6507f1be4ee
