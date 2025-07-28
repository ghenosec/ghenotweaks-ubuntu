# Gheno Tweaks

**APENAS PARA LINUX UBUNTU**

Uma ferramenta simples em Python para aplicar otimizações de desempenho e jogos no Linux UBUNTU.
Criei com o intuito de, após o Sistema formatado, em poucos segundos terá seu linux pré otimizado.

<p align="center">
 <img src="https://github.com/ghenosec/ghenotweaks-ubuntu/blob/main/optimizer.png" alt="example" height=400></a>
</p>

## Funcionalidades

- Otimizar Swappiness do Kernel (Controle de uso da SWAP)
- Otimizar VFS cache Pressure do Kernel (Gerenciamento de cache do sistema de arquivos)
- Desabilitar Serviços Systemd Desnecessários
- Otimizar Configurações do GRUB (Acelerar o boot)
- Habilitar 'noatime' em FSTAB (Reduzir escritas em disco para SSDs)
- Limpeza de Pacotes e Caches do APT 
- Configurar ZRAM (Memória RAM Comprimida como SWAP)

---

## Como Usar

1.  Python 3 (geralmente já instalado no Ubuntu).
2.  Clone este repositório.
3.  Execute o comando para rodar o programa:
    ```bash
    sudo python3 optimizer.py
    ```

**AVISO:** Este programa modifica algumas funcionalidades do OS. Use por sua conta e risco.
**NOTA:** Algumas otimizações podem exigir que você reinicie o sistema para que as mudanças sejam aplicadas completamente.
---