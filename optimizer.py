import subprocess
import os
import shutil
import re
import datetime

SYSCTL_CONF = "/etc/sysctl.conf"
GRUB_DEFAULT = "/etc/default/grub"
FSTAB = "/etc/fstab"
BACKUP_BASE_DIR = "/var/backups/ghenotweaks_ubuntu/"


def run_command(command, check=True, shell=False, show_output=True):
    """
    Função auxiliar para executar comandos de shell.

        command (list ou str): O comando a ser executado.
        check (bool): Se True, levanta CalledProcessError para códigos de saída diferentes de zero.
        shell (bool): Se True, o comando é interpretado por um shell.
        show_output (bool): Se False, não imprime stdout/stderr para erros.
    Returns:
        str: A saída padrão do comando, ou None em caso de erro.
    """
    try:
        result = subprocess.run(
            command, check=check, shell=shell, capture_output=True, text=True
        )
        if show_output:
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(result.stderr.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"\nErro ao executar comando: {' '.join(command) if not shell else command}")
        print(f"Código de saída: {e.returncode}")
        if show_output:
            print(f"Stdout: {e.stdout.strip()}")
            print(f"Stderr: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print(f"\nComando não encontrado: {' '.join(command) if not shell else command}")
        return None
    except Exception as e:
        print(f"\nOcorreu um erro inesperado ao executar o comando: {e}")
        return None


def create_backup(filepath):
    if not os.path.exists(filepath):
        print(f"Aviso: Arquivo não encontrado para backup: {filepath}")
        return False

    os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(filepath)}_{timestamp}.ghenotweaks_bak"
    backup_path = os.path.join(BACKUP_BASE_DIR, backup_name)
    try:
        shutil.copy2(filepath, backup_path)
        print(f"Backup de '{filepath}' criado em '{backup_path}'.")
        return True
    except Exception as e:
        print(f"Erro ao criar backup de '{filepath}': {e}")
        return False


def check_root():
    if os.geteuid() != 0:
        print("Este script precisa ser executado com privilégios de root (sudo).")
        print("Por favor, execute: sudo python3 seu_script.py")
        exit(1)


def display_menu():
    """Exibe as opções do menu principal com espaçamento."""
    print("\n" * 3) 

    print("--- GhenoTweaks - Ubuntu - Menu de Otimização ---")
    print("\n") 

    print("1. Otimizar Swappiness do Kernel (Controle de uso da SWAP)")
    print("2. Otimizar VFS Cache Pressure do Kernel (Gerenciamento de cache do sistema de arquivos)")
    print("3. Desabilitar Serviços Systemd Desnecessários")
    print("4. Otimizar Configurações do GRUB (Acelerar o boot)")
    print("5. Habilitar 'noatime' em FSTAB (Reduzir escritas em disco para SSDs)")
    print("6. Limpeza de Pacotes e Caches do APT")
    print("7. Configurar ZRAM (Memória RAM Comprimida como SWAP)")
    print("0. Sair")
    
    print("\n" * 2) 
    print("---------------------------------------------")
    print("\n") 


def get_user_choice():
    while True:
        try:
            choice = input("Escolha uma opção (0-7): ")
            if choice.isdigit():
                choice = int(choice)
                if 0 <= choice <= 7:
                    return choice
            print("Opção inválida. Por favor, digite um número entre 0 e 7.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")


def apply_sysctl_setting(param, value, description):
    print(f"\n--- {description} ---")

    current_value = run_command(["sysctl", "-n", param], show_output=False)
    if current_value is None:
        print(f"Não foi possível ler o valor atual de '{param}'.")
        return

    print(f"Valor atual de '{param}': {current_value}")
    print(f"Valor sugerido para otimização: {value}")

    confirm = input(f"Deseja alterar '{param}' para '{value}'? (s/n): ").lower()
    if confirm == 's':
        if not create_backup(SYSCTL_CONF):
            print("Não foi possível continuar sem backup do sysctl.conf.")
            return

        try:
            with open(SYSCTL_CONF, 'r') as f:
                lines = f.readlines()

            found = False
            new_lines = []
            for line in lines:
                if line.strip().startswith(f"{param}="):
                    new_lines.append(f"{param}={value}\n")
                    found = True
                    print(f"'{param}' atualizado para '{value}' no arquivo.")
                else:
                    new_lines.append(line)

            if not found:
                new_lines.append(f"\n# Added by GhenoTweaks\n{param}={value}\n")
                print(f"'{param}' adicionado como '{value}' ao arquivo.")

            with open(SYSCTL_CONF, 'w') as f:
                f.writelines(new_lines)

            run_command(["sysctl", "--system"])
            print(f"Otimização de '{param}' concluída com sucesso.")
        except IOError as e:
            print(f"Erro ao modificar '{SYSCTL_CONF}': {e}")
    else:
        print("Alteração cancelada.")


def optimize_swappiness():
    print("Controla a frequência com que o kernel usa o espaço de troca (SWAP).")
    print("Valores menores fazem o sistema usar a RAM por mais tempo antes de recorrer à SWAP.")
    print("Recomendado '10' para a maioria dos desktops com mais de 4GB de RAM.")
    apply_sysctl_setting(
        "vm.swappiness", "10", "Otimizar Swappiness do Kernel"
    )


def optimize_vfs_cache_pressure():
    print("Controla a agressividade com que o kernel libera memória de caches de diretórios e inodes.")
    print("Um valor menor (ex: 50) faz o kernel manter mais cache, o que pode acelerar operações de arquivo.")
    apply_sysctl_setting(
        "vm.vfs_cache_pressure", "50", "Otimizar VFS Cache Pressure do Kernel"
    )


def disable_systemd_services():
    print("\n--- Desabilitar Serviços Systemd Desnecessários ---")
    print("Esta opção permite desabilitar serviços que podem consumir recursos (CPU/RAM).")
    print("ATENÇÃO: Desabilitar serviços essenciais pode causar instabilidade ou mau funcionamento.")
    print("Sempre pesquise o serviço antes de desabilitá-lo.")
    print("\nAlguns serviços comuns que você pode considerar desabilitar (se não os usar):")
    print("  - bluetooth.service (se não usa Bluetooth)")
    print("  - avahi-daemon.service (para descoberta de rede mDNS, não essencial para muitos)")
    print("  - cups.service (se não usa impressora local)")
    print("  - modemmanager.service (se não usa modem 3G/4G/discagem)")
    print("  - ufw.service (se não usa o firewall UFW e prefere gerenciar o firewall manualmente)")

    service_name = input(
        "Digite o nome COMPLETO do serviço a desabilitar (ex: bluetooth.service) ou '0' para voltar: "
    ).strip()
    if not service_name or service_name == '0':
        print("Operação cancelada.")
        return

    status = run_command(["systemctl", "is-active", service_name], check=False, show_output=False)
    
    if status is None:
        print(f"Erro ao verificar o status do serviço '{service_name}'. Pode não existir.")
        return

    print(f"Status atual de '{service_name}': {status.upper()}")
    
    if status == "active":
        confirm_disable = input(f"O serviço '{service_name}' está ATIVO. Tem certeza que deseja DESABILITAR e PARAR? (s/n): ").lower()
    else:
        confirm_disable = input(f"O serviço '{service_name}' não está ativo ou não existe. Mesmo assim, deseja tentar desabilitá-lo? (s/n): ").lower()

    if confirm_disable == 's':
        print(f"Desabilitando e parando '{service_name}'...")
        result = run_command(["systemctl", "disable", "--now", service_name])
        if result is not None:
            print(f"Serviço '{service_name}' desabilitado e parado com sucesso.")
        else:
            print(f"Falha ao desabilitar/parar '{service_name}'. Verifique o nome do serviço ou erros acima.")
    else:
        print("Operação cancelada.")


def optimize_grub():
    print("\n--- Otimizar Configurações do GRUB ---")
    print("Esta opção pode acelerar o tempo de inicialização do sistema.")
    print("ATENÇÃO: Modificações incorretas no GRUB podem impedir o sistema de iniciar.")
    
    if not create_backup(GRUB_DEFAULT):
        print("Não foi possível continuar sem backup do GRUB.")
        return

    current_grub_content = ""
    try:
        with open(GRUB_DEFAULT, 'r') as f:
            current_grub_content = f.read()
    except IOError as e:
        print(f"Erro ao ler '{GRUB_DEFAULT}': {e}")
        return

    new_grub_content = current_grub_content
    changes_made = False
    
    print("\n1. Ajustar GRUB_TIMEOUT (Tempo de espera no menu de boot):")
    timeout_match = re.search(r'^GRUB_TIMEOUT=(\d+)', new_grub_content, re.MULTILINE)
    current_timeout = timeout_match.group(1) if timeout_match else "10" 
    print(f"Valor atual de GRUB_TIMEOUT: {current_timeout} segundos.")
    
    confirm_timeout = input("Deseja alterar GRUB_TIMEOUT para '3' segundos (ou '0' para pular o menu)? (s/n): ").lower()
    if confirm_timeout == 's':
        target_timeout = input("Digite o novo valor para GRUB_TIMEOUT (ex: 3 para boot rápido, 0 para instantâneo): ")
        if target_timeout.isdigit():
            if timeout_match:
                new_grub_content = re.sub(
                    r'^GRUB_TIMEOUT=\d+', f'GRUB_TIMEOUT={target_timeout}', new_grub_content, flags=re.MULTILINE
                )
                print(f"GRUB_TIMEOUT alterado para {target_timeout}.")
            else:
                new_grub_content += f"\nGRUB_TIMEOUT={target_timeout}\n"
                print(f"GRUB_TIMEOUT adicionado como {target_timeout}.")
            changes_made = True
        else:
            print("Entrada inválida. GRUB_TIMEOUT não alterado.")
    else:
        print("Alteração de GRUB_TIMEOUT cancelada.")

    print("\n2. Remover 'quiet splash' de GRUB_CMDLINE_LINUX_DEFAULT:")
    print("   'quiet splash' oculta as mensagens de boot. Removê-lo pode ligeiramente acelerar")
    print("   o boot e permite ver mensagens do kernel, útil para depuração.")
    
    cmdline_match = re.search(r'^GRUB_CMDLINE_LINUX_DEFAULT="(.*?)"', new_grub_content, re.MULTILINE)
    current_cmdline = cmdline_match.group(1) if cmdline_match else ""
    print(f"Valor atual de GRUB_CMDLINE_LINUX_DEFAULT: \"{current_cmdline}\"")

    if 'quiet' in current_cmdline or 'splash' in current_cmdline:
        confirm_cmdline = input("Deseja remover 'quiet' e 'splash' desta linha? (s/n): ").lower()
        if confirm_cmdline == 's':
            if cmdline_match:
                new_cmdline = current_cmdline.replace("quiet", "").replace("splash", "").strip()
                new_cmdline = re.sub(r'\s+', ' ', new_cmdline).strip()
                new_grub_content = re.sub(
                    r'^GRUB_CMDLINE_LINUX_DEFAULT=".*?"',
                    f'GRUB_CMDLINE_LINUX_DEFAULT="{new_cmdline}"',
                    new_grub_content,
                    flags=re.MULTILINE,
                )
                print("'quiet' e 'splash' removidos.")
                changes_made = True
            else:
                print("Linha 'GRUB_CMDLINE_LINUX_DEFAULT' não encontrada. Não foi possível modificar.")
        else:
            print("Remoção de 'quiet splash' cancelada.")
    else:
        print("'quiet' e 'splash' não encontrados na linha GRUB_CMDLINE_LINUX_DEFAULT.")


    if changes_made:
        confirm_write = input("Deseja aplicar as mudanças no GRUB e executar 'update-grub'? (s/n): ").lower()
        if confirm_write == 's':
            try:
                with open(GRUB_DEFAULT, 'w') as f:
                    f.write(new_grub_content)
                print("Arquivo /etc/default/grub atualizado.")
                
                print("Executando 'update-grub' (isso pode levar alguns segundos)...")
                result = run_command(["update-grub"])
                if result is not None:
                    print("GRUB atualizado com sucesso. Reinicie para ver as mudanças.")
                else:
                    print("Falha ao executar 'update-grub'.")
            except IOError as e:
                print(f"Erro ao escrever em '{GRUB_DEFAULT}': {e}")
        else:
            print("Alterações no GRUB não foram salvas.")
    else:
        print("Nenhuma alteração significativa foi selecionada para o GRUB.")


def enable_noatime():
    print("\n--- Habilitar 'noatime' em FSTAB ---")
    print("A opção 'noatime' impede que o sistema registre a cada vez que um arquivo é acessado.")
    print("Isso reduz as operações de escrita em disco, o que pode prolongar a vida útil de SSDs")
    print("e melhorar ligeiramente o desempenho do sistema de arquivos.")
    print("ATENÇÃO: Não recomendado para servidores que dependem de 'atime' para backups ou serviços específicos.")

    if not create_backup(FSTAB):
        print("Não foi possível continuar sem backup do FSTAB.")
        return

    try:
        with open(FSTAB, 'r') as f:
            lines = f.readlines()
        
        modified_lines = []
        changes_made = False
        
        for i, line in enumerate(lines):
            original_line = line.strip()
            
            if original_line.startswith('#') or not original_line:
                modified_lines.append(line)
                continue

            parts = line.split()
            if len(parts) >= 4:
                options_str = parts[3]
                
                if 'noatime' in options_str or 'relatime' in options_str:
                    print(f"Partição '{parts[1]}' (tipo: {parts[2]}) já tem 'noatime' ou 'relatime'. Ignorando.")
                    modified_lines.append(line)
                elif parts[2] == "swap":
                    modified_lines.append(line)
                elif parts[1] == "/boot" or parts[1] == "/boot/efi":
                    modified_lines.append(line)
                else:
                    print(f"\nLinha {i+1}: '{original_line}'")
                    confirm_line = input(
                        f"Deseja adicionar 'noatime' à partição '{parts[1]}' (tipo: {parts[2]})? (s/n): "
                    ).lower()
                    if confirm_line == 's':
                        new_options_str = options_str + ",noatime" if options_str else "noatime"
                        
                        new_line_parts = parts[:]
                        new_line_parts[3] = new_options_str
                        modified_lines.append(" ".join(new_line_parts) + "\n")
                        
                        changes_made = True
                        print(f"'{parts[1]}' marcado para 'noatime'.")
                    else:
                        modified_lines.append(line)
            else:
                modified_lines.append(line)

        if changes_made:
            confirm_write = input("\nDeseja aplicar as mudanças no FSTAB? (s/n): ").lower()
            if confirm_write == 's':
                try:
                    with open(FSTAB, 'w') as f:
                        f.writelines(modified_lines)
                    print("Arquivo /etc/fstab atualizado. Algumas mudanças podem requerer reinicialização.")
                except IOError as e:
                    print(f"Erro ao escrever em '{FSTAB}': {e}")
            else:
                print("Alterações no FSTAB não foram salvas.")
        else:
            print("Nenhuma partição adequada encontrada ou todas já possuem 'noatime'/'relatime'.")

    except IOError as e:
        print(f"Erro ao acessar '{FSTAB}': {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao processar FSTAB: {e}")


def cleanup_apt_packages():
    print("\n--- Limpeza de Pacotes e Caches do APT ---")
    print("Esta opção irá remover pacotes que não são mais necessários (autoremove)")
    print("e limpar o cache de pacotes baixados do APT (clean), liberando espaço em disco.")

    confirm = input("Deseja continuar com a limpeza (apt autoremove e apt clean)? (s/n): ").lower()
    if confirm == 's':
        print("\nExecutando 'apt autoremove'...")
        run_command(["apt", "autoremove", "-y"])
        
        print("\nExecutando 'apt clean'...")
        run_command(["apt", "clean"])
        
        print("\nLimpeza concluída.")
    else:
        print("Limpeza cancelada.")


def configure_zram():
    print("\n--- Configurar ZRAM (Memória Comprimida) ---")
    print("ZRAM cria um dispositivo de bloco comprimido na RAM que é usado como swap.")
    print("Isso pode evitar o uso de swap lenta no disco rígido, melhorando a responsividade,")
    print("especialmente em sistemas com menos RAM ou que fazem muito uso de swap.")
    print("O Ubuntu geralmente usa o pacote 'zram-config'.")

    pkg_check = run_command(["dpkg", "-s", "zram-config"], check=False, show_output=False)
    
    if "install ok installed" in pkg_check:
        print("'zram-config' já está instalado.")
    else:
        confirm_install = input("'zram-config' não está instalado. Deseja instalá-lo agora? (s/n): ").lower()
        if confirm_install == 's':
            print("Atualizando lista de pacotes...")
            if run_command(["apt", "update", "-y"]) is None:
                print("Falha ao atualizar a lista de pacotes. Não foi possível instalar 'zram-config'.")
                return
            print("Instalando 'zram-config'...")
            if run_command(["apt", "install", "zram-config", "-y"]) is None:
                print("Falha ao instalar 'zram-config'. Não foi possível configurar ZRAM.")
                return
            print("'zram-config' instalado.")
        else:
            print("Instalação de 'zram-config' cancelada. Não é possível configurar ZRAM.")
            return

    zram_status = run_command(
        ["systemctl", "is-active", "zram-swap"], check=False, show_output=False
    )
    
    if zram_status == "active":
        print("ZRAM já está ativo e habilitado.")
    elif zram_status == "inactive":
        print("ZRAM está inativo. Ativando e habilitando o serviço 'zram-swap'...")
        result = run_command(["systemctl", "enable", "--now", "zram-swap"])
        if result is not None:
            print("ZRAM ativado e habilitado com sucesso. Reinicie para garantir o funcionamento.")
            print("Para configurar o tamanho do ZRAM, você pode editar o arquivo '/etc/default/zramswap'.")
        else:
            print("Falha ao ativar ZRAM. Verifique os logs do sistema.")
    else:
        print("Verificação do status do ZRAM incerta. Tentando ativar e habilitar o serviço 'zram-swap'...")
        result = run_command(["systemctl", "enable", "--now", "zram-swap"])
        if result is not None:
            print("ZRAM ativado e habilitado com sucesso. Reinicie para garantir o funcionamento.")
            print("Para configurar o tamanho do ZRAM, você pode editar o arquivo '/etc/default/zramswap'.")
        else:
            print("Falha ao ativar ZRAM. Verifique os logs do sistema.")


def main():
    check_root()
    
    os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
    print(f"Backups de configurações serão salvos em: {BACKUP_BASE_DIR}")

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == 1:
            optimize_swappiness()
        elif choice == 2:
            optimize_vfs_cache_pressure()
        elif choice == 3:
            disable_systemd_services()
        elif choice == 4:
            optimize_grub()
        elif choice == 5:
            enable_noatime()
        elif choice == 6:
            cleanup_apt_packages()
        elif choice == 7:
            configure_zram()
        elif choice == 0:
            print("Saindo do GhenoTweaks. Obrigado por usar!")
            break
        
        input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()