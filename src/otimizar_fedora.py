#!/usr/bin/env python3
# ─────────────────────────────────────────────────────
#  Otimizar Fedora Linux - App gráfico (GTK4)
#  Empacotado como Flatpak.
#
#  Dentro da sandbox Flatpak, todos os comandos de
#  sistema rodam no host via `flatpak-spawn --host`.
#  Fora do Flatpak, roda direto (modo desenvolvimento).
# ─────────────────────────────────────────────────────

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio, Pango

import os
import subprocess
import threading

APP_ID = "io.github.renanrure_afk.OtimizarFedora"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(APP_DIR, "manutencao_helper.sh")

# Detecta se está rodando dentro de uma sandbox Flatpak
DENTRO_FLATPAK = os.path.exists("/.flatpak-info")


def _no_host(args):
    """Prefixa o comando com flatpak-spawn --host quando
    estamos dentro da sandbox. Fora dela, retorna como está."""
    if DENTRO_FLATPAK:
        return ["flatpak-spawn", "--host"] + args
    return args


class JanelaPrincipal(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Otimizar Fedora Linux")
        self.set_default_size(760, 620)

        self.helper = None          # processo root (pkexec no host)
        self.ocupado = False
        self.botoes = []

        # ── Layout geral ──
        raiz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(raiz)

        header = Gtk.HeaderBar()
        self.set_titlebar(header)

        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(22, 22)
        header.pack_end(self.spinner)

        self.status = Gtk.Label(label="Autenticando...")
        self.status.add_css_class("dim-label")
        header.pack_start(self.status)

        conteudo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        conteudo.set_margin_top(12)
        conteudo.set_margin_bottom(12)
        conteudo.set_margin_start(12)
        conteudo.set_margin_end(12)
        conteudo.set_vexpand(True)
        raiz.append(conteudo)

        # ── Coluna de botões ──
        col_botoes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        col_botoes.set_size_request(260, -1)
        conteudo.append(col_botoes)

        self._secao(col_botoes, "ATUALIZAR")
        self._botao(col_botoes, "🔄  Atualizar Sistema", self.acao_atualizar)
        self._botao(col_botoes, "💾  Verificar Firmware", self.acao_firmware)

        self._secao(col_botoes, "LIMPAR")
        self._botao(col_botoes, "🧹  Limpeza Segura", self.acao_limpeza)
        self._botao(col_botoes, "🗑️  Remover Kernels Antigos", self.acao_kernels)
        self._botao(col_botoes, "⚡  Otimizar SSD (TRIM)", self.acao_trim)

        self._secao(col_botoes, "DIAGNOSTICAR")
        self._botao(col_botoes, "🩺  Saúde do SSD (SMART)", self.acao_smart)
        self._botao(col_botoes, "🔋  Bateria e Espaço", self.acao_bateria)

        self._secao(col_botoes, "")
        btn_tudo = self._botao(col_botoes, "🚀  Executar Tudo", self.acao_tudo)
        btn_tudo.add_css_class("suggested-action")

        # ── Área de log ──
        frame = Gtk.Frame()
        frame.set_hexpand(True)
        conteudo.append(frame)

        scroll = Gtk.ScrolledWindow()
        frame.set_child(scroll)

        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.set_monospace(True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_view.set_left_margin(10)
        self.log_view.set_right_margin(10)
        self.log_view.set_top_margin(8)
        self.log_buffer = self.log_view.get_buffer()
        scroll.set_child(self.log_view)

        self._travar_botoes(True)
        self.log("Bem-vindo! Autentique-se para começar.\n")

        threading.Thread(target=self._iniciar_helper, daemon=True).start()

    # ───────── UI helpers ─────────

    def _secao(self, box, titulo):
        if titulo:
            lbl = Gtk.Label(label=titulo, xalign=0)
            lbl.add_css_class("dim-label")
            lbl.set_margin_top(8)
            box.append(lbl)
        else:
            box.append(Gtk.Separator(margin_top=8, margin_bottom=4))

    def _botao(self, box, texto, callback):
        btn = Gtk.Button(label=texto)
        btn.set_halign(Gtk.Align.FILL)
        child = btn.get_child()
        if isinstance(child, Gtk.Label):
            child.set_xalign(0)
        btn.connect("clicked", lambda *_: callback())
        box.append(btn)
        self.botoes.append(btn)
        return btn

    def _travar_botoes(self, travar):
        for b in self.botoes:
            b.set_sensitive(not travar)

    def log(self, texto):
        def _add():
            fim = self.log_buffer.get_end_iter()
            self.log_buffer.insert(fim, texto)
            mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
            self.log_view.scroll_mark_onscreen(mark)
            return False
        GLib.idle_add(_add)

    def _set_status(self, texto, girando):
        def _upd():
            self.status.set_label(texto)
            if girando:
                self.spinner.start()
            else:
                self.spinner.stop()
            return False
        GLib.idle_add(_upd)

    # ───────── Helper root (pkexec no host) ─────────

    def _iniciar_helper(self):
        """Abre o helper como root NO HOST. Como o host não
        enxerga arquivos dentro da sandbox, o conteúdo do
        script é passado inteiro via `bash -c`."""
        self._set_status("Aguardando digital/senha...", True)
        try:
            with open(HELPER, "r", encoding="utf-8") as f:
                script = f.read()

            self.helper = subprocess.Popen(
                _no_host(["pkexec", "/bin/bash", "-c", script]),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for linha in self.helper.stdout:
                if "__PRONTO__" in linha:
                    break
            if self.helper.poll() is not None:
                raise RuntimeError("Autenticação cancelada ou negada.")
            self._set_status("Autenticado ✔", False)
            self.log("Autenticado com sucesso. Escolha uma opção.\n\n")
            GLib.idle_add(self._travar_botoes, False)
        except Exception as e:
            self._set_status("Falha na autenticação", False)
            self.log(f"\n✘ {e}\nFeche e abra o app para tentar de novo.\n")

    def _rodar_root(self, comandos, titulo, ao_final=None):
        """Envia comandos pré-definidos ao helper root e
        transmite a saída para o log em tempo real."""
        if self.ocupado or not self.helper:
            return
        self.ocupado = True
        GLib.idle_add(self._travar_botoes, True)
        self._set_status(f"Executando: {titulo}...", True)
        self.log(f"\n═══ {titulo} ═══\n")

        def _worker():
            try:
                for cmd in comandos:
                    self.helper.stdin.write(cmd + "\n")
                    self.helper.stdin.flush()
                    for linha in self.helper.stdout:
                        if linha.startswith("__FIM__"):
                            codigo = linha.strip().split(":")[-1]
                            if codigo == "0":
                                self.log("✔ Etapa concluída.\n")
                            else:
                                self.log(f"⚠ Etapa terminou com código {codigo}.\n")
                            break
                        self.log(linha)
            except Exception as e:
                self.log(f"✘ Erro: {e}\n")
            finally:
                self.ocupado = False
                self._set_status("Pronto", False)
                GLib.idle_add(self._travar_botoes, False)
                if ao_final:
                    ao_final()

        threading.Thread(target=_worker, daemon=True).start()

    def _rodar_usuario(self, args, titulo, ao_final=None):
        """Roda comandos como usuário comum, no host."""
        if self.ocupado:
            return
        self.ocupado = True
        GLib.idle_add(self._travar_botoes, True)
        self._set_status(f"Executando: {titulo}...", True)
        self.log(f"\n═══ {titulo} ═══\n")

        def _worker():
            try:
                p = subprocess.Popen(
                    _no_host(args), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, bufsize=1,
                )
                for linha in p.stdout:
                    self.log(linha)
                p.wait()
                self.log("✔ Concluído.\n" if p.returncode == 0
                         else f"⚠ Terminou com código {p.returncode}.\n")
            except FileNotFoundError:
                self.log("⚠ Comando não encontrado. Pulando.\n")
            except Exception as e:
                self.log(f"✘ Erro: {e}\n")
            finally:
                self.ocupado = False
                self._set_status("Pronto", False)
                GLib.idle_add(self._travar_botoes, False)
                if ao_final:
                    ao_final()

        threading.Thread(target=_worker, daemon=True).start()

    # ───────── Ações ─────────

    def acao_atualizar(self):
        def depois_dnf():
            self._rodar_usuario(["flatpak", "update", "-y"],
                                "Atualizar Flatpaks",
                                ao_final=lambda: self._rodar_root(
                                    ["verificar_reboot"], "Verificar Reinicialização"))
        self._rodar_root(["atualizar_dnf"], "Atualizar Sistema (DNF)",
                         ao_final=depois_dnf)

    def acao_firmware(self):
        self._rodar_root(["atualizar_firmware"], "Verificar Firmware")

    def acao_limpeza(self):
        def depois():
            self._rodar_usuario(["flatpak", "uninstall", "--unused", "-y"],
                                "Limpar Flatpaks órfãos")
        self._rodar_root(["limpeza"], "Limpeza Segura", ao_final=depois)

    def acao_kernels(self):
        dialog = Gtk.AlertDialog()
        dialog.set_message("Remover kernels antigos?")
        dialog.set_detail("O kernel atual e o anterior serão mantidos como segurança.")
        dialog.set_buttons(["Cancelar", "Remover"])
        dialog.set_cancel_button(0)
        dialog.set_default_button(1)

        def resposta(dlg, resultado):
            try:
                if dlg.choose_finish(resultado) == 1:
                    self._rodar_root(["remover_kernels"], "Remover Kernels Antigos")
            except Exception:
                pass
        dialog.choose(self, None, resposta)

    def acao_trim(self):
        self._rodar_root(["trim"], "Otimizar SSD (TRIM)")

    def acao_smart(self):
        self._rodar_root(["smart"], "Saúde do SSD")

    def acao_bateria(self):
        script = r'''
BAT=$(ls /sys/class/power_supply/ 2>/dev/null | grep -m1 BAT)
if [ -n "$BAT" ]; then
  A=$(cat /sys/class/power_supply/$BAT/energy_full 2>/dev/null)
  D=$(cat /sys/class/power_supply/$BAT/energy_full_design 2>/dev/null)
  [ -n "$A" ] && [ -n "$D" ] && echo "Saude da bateria: $(( A * 100 / D ))% da capacidade original"
  C=$(cat /sys/class/power_supply/$BAT/cycle_count 2>/dev/null)
  [ -n "$C" ] && echo "Ciclos de carga: $C"
fi
echo ""
echo "Espaco em disco:"
df -h / /home 2>/dev/null | grep -v tmpfs
'''
        self._rodar_usuario(["bash", "-c", script], "Bateria e Espaço")

    def acao_tudo(self):
        def p4():
            self._rodar_root(["trim", "verificar_reboot"], "TRIM + Reinicialização",
                             ao_final=lambda: self.log("\n🚀 Manutenção completa finalizada!\n"))
        def p3():
            self._rodar_usuario(["flatpak", "uninstall", "--unused", "-y"],
                                "Limpar Flatpaks órfãos", ao_final=p4)
        def p2():
            self._rodar_root(["atualizar_firmware", "limpeza"],
                             "Firmware + Limpeza", ao_final=p3)
        def p1():
            self._rodar_usuario(["flatpak", "update", "-y"],
                                "Atualizar Flatpaks", ao_final=p2)
        self._rodar_root(["atualizar_dnf"], "Atualizar Sistema (DNF)", ao_final=p1)

    def do_close_request(self):
        try:
            if self.helper and self.helper.poll() is None:
                self.helper.stdin.write("sair\n")
                self.helper.stdin.flush()
        except Exception:
            pass
        return False


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.get_active_window()
        if not win:
            win = JanelaPrincipal(self)
        win.present()


if __name__ == "__main__":
    App().run(None)
