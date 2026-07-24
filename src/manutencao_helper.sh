#!/bin/bash
# ─────────────────────────────────────────────────────
# Helper privilegiado do app Manutenção Fedora
# É iniciado via pkexec (pede digital/senha UMA vez)
# e fica aguardando comandos pré-definidos do app.
# Só executa ações da lista abaixo. Nada além disso.
# ─────────────────────────────────────────────────────

echo "__PRONTO__"

while IFS= read -r cmd; do
    case "$cmd" in
        atualizar_dnf)
            dnf upgrade --refresh -y
            ;;
        atualizar_firmware)
            fwupdmgr refresh --force
            fwupdmgr update -y
            ;;
        limpeza)
            dnf clean all
            dnf autoremove -y
            journalctl --vacuum-time=2w
            ;;
        remover_kernels)
            dnf remove --oldinstallonly -y
            ;;
        trim)
            fstrim -av
            ;;
        verificar_reboot)
            if dnf needs-restarting -r > /dev/null 2>&1; then
                echo "Nenhuma reinicializacao necessaria."
            else
                echo "ATENCAO: o sistema precisa ser REINICIADO para aplicar atualizacoes."
            fi
            ;;
        smart)
            DISCO=$(lsblk -dno NAME,TYPE | awk '$2=="disk"{print "/dev/"$1; exit}')
            if command -v smartctl > /dev/null 2>&1; then
                smartctl -H "$DISCO" | grep -iE "result|overall"
                smartctl -a "$DISCO" 2>/dev/null | grep -iE "percentage used|temperature:|power on hours" | head -5
            else
                echo "smartctl nao instalado (sudo dnf install smartmontools)"
            fi
            ;;
        sair)
            exit 0
            ;;
        *)
            echo "Comando nao reconhecido: $cmd"
            ;;
    esac
    echo "__FIM__:$?"
done
