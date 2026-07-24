# Otimizar Fedora Linux

One-click system maintenance for Fedora Linux. Update packages and firmware,
clean caches and old kernels, run SSD TRIM, and check disk health and battery
status — all from a single GTK4 window. Authenticate once (fingerprint or
password) and run everything.

Manutenção do sistema Fedora em um clique. Atualize pacotes e firmware,
limpe caches e kernels antigos, rode o TRIM do SSD e verifique a saúde do
disco e da bateria em uma única janela GTK4.

## Features / Funcionalidades

- System updates via DNF + Flatpak updates
- Firmware updates (fwupd)
- Safe cleanup: package cache, orphan packages, old journals, unused Flatpaks
- Old kernel removal (keeps current + previous)
- SSD TRIM
- SMART disk health, battery health and disk space report
- "Run everything" one-click full maintenance

## Install / Instalação

Flatpak (local build):

```bash
flatpak install -y flathub org.gnome.Platform//50 org.gnome.Sdk//50
flatpak run org.flatpak.Builder --force-clean --user --install \
  build-dir io.github.renanrure_afk.OtimizarFedora.yml
flatpak run io.github.renanrure_afk.OtimizarFedora
```

## Requirements / Requisitos

- Fedora Linux (uses dnf)
- polkit (authentication dialog)

## License / Licença

MIT — see [LICENSE](LICENSE).

## Ownership / Titularidade

Developed and maintained by **3R Serviços Digitais** (CNPJ 40.518.650/0001-48).
The **3RS** logo is a registered trademark (INPI Brazil, process 935411313,
registration in force until 2036). Source code is MIT-licensed; the brand
and logo are not — see the trademark notice in [LICENSE](LICENSE).

Desenvolvido e mantido pela **3R Serviços Digitais**. O logo **3RS** é marca
registrada no INPI (processo 935411313, registro em vigor até 2036). O código
é livre sob MIT; a marca e o logo não — veja o aviso no arquivo LICENSE.
