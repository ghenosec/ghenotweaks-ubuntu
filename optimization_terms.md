# GhenoTweaks - Glossário de Termos de Otimização

Este documento explica os principais termos e conceitos utilizados nas opções de otimização do GhenoTweaks para Ubuntu. Compreender esses termos pode ajudar você a tomar decisões mais informadas sobre quais otimizações aplicar e entender o que cada otimização realiza no sistema.

---

## 1. Swappiness do Kernel

*   **O que é:** O `swappiness` é um parâmetro do kernel Linux que controla a agressividade com que o sistema move os dados da memória RAM para o espaço de troca (swap) no disco.
*   **Como funciona:**
    *   Um valor alto (padrão geralmente é 60) significa que o kernel tentará mover mais agressivamente os dados para a swap, liberando a RAM. Isso pode ser útil em servidores, mas em desktops pode levar a lentidão quando o sistema acessa o disco.
    *   Um valor baixo (como 10) indica que o kernel preferirá manter os dados na RAM pelo maior tempo possível, usando a swap apenas como último recurso.
*   **Benefício da otimização:** Reduzir o `swappiness` pode melhorar a responsividade do sistema em desktops com RAM suficiente, pois o disco (mesmo um SSD) é sempre muito mais lento que a RAM.

---

## 2. VFS Cache Pressure do Kernel

*   **O que é:** O `vfs_cache_pressure` é outro parâmetro do kernel que afeta a tendência do kernel de recuperar (liberar) memória usada para cache de "inodes" e "dentries". Inodes são estruturas de dados que armazenam informações sobre arquivos e diretórios, e dentries são entradas de diretório (caminhos de arquivo).
*   **Como funciona:**
    *   Um valor alto (padrão é 100) significa que o kernel tentará liberar esses caches mais agressivamente.
    *   Um valor menor (como 50) faz o kernel reter mais esses caches na memória, o que significa que informações sobre arquivos e diretórios (seus metadados) serão mantidas na RAM por mais tempo.
*   **Benefício da otimização:** Diminuir o `vfs_cache_pressure` pode acelerar operações relacionadas a arquivos e diretórios, pois o sistema pode encontrá-los e acessá-los mais rapidamente sem precisar ir ao disco para recarregar seus metadados.

---

## 3. Serviços Systemd Desnecessários

*   **O que é Systemd:** `Systemd` é o sistema de inicialização (init system) e gerenciador de serviços padrão na maioria das distribuições Linux modernas, incluindo o Ubuntu. Ele é responsável por iniciar, parar e gerenciar todos os processos e serviços do sistema.
*   **Serviços Desnecessários:** Ao longo do tempo, ou dependendo da instalação padrão, seu sistema pode ter serviços rodando em segundo plano que você nunca usa (ex: serviço de Bluetooth se você não tem ou não usa dispositivos Bluetooth, servidor de impressão CUPS se você não tem impressora, etc.).
*   **Benefício da otimização:** Desabilitar esses serviços libera memória RAM, reduz o consumo de CPU e pode acelerar o tempo de boot do sistema, já que menos processos precisam ser iniciados. É crucial saber o que cada serviço faz antes de desabilitá-lo para evitar problemas.

---

## 4. Configurações do GRUB

*   **O que é GRUB:** GRUB (GRand Unified Bootloader) é o carregador de boot padrão no Ubuntu e em muitas outras distribuições Linux. Ele é a primeira coisa que seu computador executa após o BIOS/UEFI e permite que você escolha qual sistema operacional iniciar (se você tiver múltiplos) e quais opções de inicialização usar para o Linux.
*   **GRUB_TIMEOUT:** Define por quantos segundos o menu do GRUB (onde você pode escolher o sistema operacional ou opções avançadas) é exibido antes de iniciar automaticamente a opção padrão.
*   **quiet splash:** São parâmetros passados para o kernel Linux durante a inicialização.
    *   `quiet`: Suprime a maioria das mensagens do kernel durante o boot.
    *   `splash`: Habilita a tela de "splash" (animação de carregamento do Ubuntu).
*   **Benefício da otimização:**
    *   Reduzir `GRUB_TIMEOUT` (especialmente para 0) acelera o boot, pois o sistema inicia imediatamente sem esperar no menu.
    *   Remover `quiet splash` pode acelerar ligeiramente o boot em algumas configurações e, mais importante, permite que você veja as mensagens do kernel durante a inicialização, o que é útil para depuração em caso de problemas.

---

## 5. 'noatime' em FSTAB

*   **O que é FSTAB:** O arquivo `/etc/fstab` (file systems table) contém uma lista de sistemas de arquivos que o kernel deve montar durante a inicialização do sistema. Ele define onde e como as partições (como sua raiz `/`, `/home`, etc.) são acessadas.
*   **A opção 'atime':** Por padrão, quando você lê (acessa) um arquivo, o Linux atualiza um metadado chamado "access time" (`atime`) no disco. Isso significa uma operação de escrita para cada leitura de arquivo.
*   **A opção 'noatime' / 'relatime':**
    *   `noatime`: Impede que o sistema atualize o `atime` toda vez que um arquivo é lido. Isso elimina um grande número de operações de escrita desnecessárias.
    *   `relatime` (geralmente o padrão moderno): É um meio-termo, ele só atualiza o `atime` se o arquivo já foi modificado (mtime) ou se o `atime` anterior for mais antigo que 24 horas.
*   **Benefício da otimização:** Usar `noatime` (ou garantir que `relatime` esteja ativo, embora a otimização force `noatime`) reduz significativamente as operações de escrita em disco, o que pode prolongar a vida útil de SSDs (devido à menor quantidade de células reescritas) e, em alguns casos, melhorar o desempenho do sistema de arquivos ao reduzir a carga de I/O. Não é recomendado para sistemas onde o "access time" é criticamente importante (ex: alguns servidores de backup ou web).

---

## 6. Caches do APT

*   **O que é APT:** APT (Advanced Package Tool) é o gerenciador de pacotes do Ubuntu (e de distribuições baseadas em Debian). Ele é usado para instalar, remover e gerenciar softwares no seu sistema.
*   **Caches do APT:** Quando você instala um pacote usando `apt install`, ele baixa os arquivos `.deb` para um diretório de cache (`/var/cache/apt/archives/`). Esses arquivos ficam armazenados mesmo após a instalação para futuras reinstalações ou para caso você queira fazer downgrade.
*   **Comandos de limpeza:**
    *   `apt autoremove`: Remove pacotes que foram instalados como dependências de outros pacotes e que não são mais necessários por nenhum software instalado.
    *   `apt clean`: Limpa o cache local de arquivos `.deb` baixados, liberando espaço em disco.
*   **Benefício da otimização:** Liberar espaço em disco removendo pacotes e caches desnecessários, o que é especialmente útil em sistemas com armazenamento limitado.

---

## 7. ZRAM

*   **O que é ZRAM:** ZRAM (também conhecido como zswap, mas `zram-config` é a implementação mais comum no Ubuntu) é uma tecnologia do kernel Linux que cria um dispositivo de bloco na RAM que é **comprimido**. Ele pode ser usado como um espaço de troca (swap).
*   **Como funciona:** Em vez de usar uma partição de swap lenta no seu disco rígido ou SSD, o ZRAM permite que o sistema use uma área da RAM como swap, mas de forma comprimida. Isso significa que mais dados cabem na RAM "virtual" criada pelo ZRAM, e o acesso a esses dados é muito mais rápido do que ir ao disco, mesmo que haja um custo de CPU para a compressão/descompressão.
*   **Benefício da otimização:** Melhora a responsividade do sistema, especialmente em máquinas com pouca memória RAM (4GB ou menos) ou que frequentemente esgotam a RAM e começam a usar a swap. Ele efetivamente expande sua capacidade de RAM, evitando o gargalo de desempenho do disco ao usar a swap.