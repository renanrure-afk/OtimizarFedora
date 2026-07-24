# Otimizar Fedora Linux — Checklist final de submissão ao Flathub

Este pacote já está com TUDO que dava pra deixar pronto:

- [x] App ID correto: `io.github.renanrure_afk.OtimizarFedora`
      (seu usuário tem hífen, e ID Flatpak não aceita hífen — a regra
      do Flathub é trocar por underscore, e é exatamente o que está feito)
- [x] Runtime GNOME 50 (versão suportada em 2026 — confirme com
      `flatpak remote-info flathub org.gnome.Platform` se quiser)
- [x] Manifesto, .desktop, metainfo com traduções PT-BR
- [x] Ícone 3RS em 256/128/64, quadrado, fundo transparente
- [x] LICENSE (MIT), README.md público, .gitignore
- [x] Código adaptado pra sandbox (flatpak-spawn --host)

## O que falta — e só você pode fazer

### 1. Testar o build local (você já está no meio disso)

```bash
flatpak install -y flathub org.gnome.Platform//50 org.gnome.Sdk//50
flatpak run org.flatpak.Builder --force-clean --user --install \
  build-dir io.github.renanrure_afk.OtimizarFedora.yml
flatpak run io.github.renanrure_afk.OtimizarFedora
```

### 2. Screenshot (obrigatório)

Com o app aberto e autenticado, rode "Bateria e Espaço" (rápido, enche
o log com conteúdo real) e capture a janela. Salve como:

```
screenshots/principal.png
```

O metainfo já aponta pra URL certa desse arquivo no seu GitHub.

### 3. Criar o repositório PÚBLICO no GitHub

Nome sugerido: `otimizar-fedora` (as URLs no metainfo já apontam pra ele).
Seus repos atuais são todos privados — este precisa ser público, porque
o Flathub e os usuários vão acessar o código e o screenshot por lá.

```bash
cd otimizar-fedora
git init
git add .
git commit -m "Versão inicial do Otimizar Fedora Linux"
git branch -M main
git remote add origin https://github.com/renanrure-afk/otimizar-fedora.git
git push -u origin main
```

### 4. Rodar o linter

```bash
flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
  manifest io.github.renanrure_afk.OtimizarFedora.yml

flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
  appstream io.github.renanrure_afk.OtimizarFedora.metainfo.xml
```

O linter VAI acusar a permissão `--talk-name=org.freedesktop.Flatpak`.
Não é bug: é a permissão que deixa o app rodar dnf/fwupdmgr no sistema.
Sem ela o app não faz nada. Guarde a saída do linter pra submissão.

### 5. Submeter

1. Faça fork de https://github.com/flathub/flathub
2. Crie uma branch A PARTIR da branch `new-pr` (não da master)
3. Copie APENAS o arquivo `io.github.renanrure_afk.OtimizarFedora.yml`
   pra raiz do fork — mas ATENÇÃO: pra submissão, o manifesto precisa
   apontar pro seu repositório público em vez de `type: dir`. Troque a
   seção `sources` do manifesto por:

   ```yaml
   sources:
     - type: git
       url: https://github.com/renanrure-afk/otimizar-fedora.git
       tag: v1.0.0
       commit: COLE_AQUI_O_HASH_DO_COMMIT_DA_TAG
   ```

   E crie a tag no seu repo antes:

   ```bash
   git tag v1.0.0 && git push origin v1.0.0
   git rev-parse v1.0.0   # esse é o hash pra colar no manifesto
   ```

4. Abra o Pull Request contra a branch `new-pr`
5. No texto do PR, se declare como desenvolvedor do app e JUSTIFIQUE
   a permissão de host. Sugestão de justificativa (em inglês, que é o
   idioma da revisão):

   > This app is a system maintenance tool for Fedora. Its core purpose
   > is running host-level maintenance (dnf, fwupdmgr, fstrim) with a
   > single polkit authentication. The org.freedesktop.Flatpak permission
   > is required for flatpak-spawn --host; the app runs only a fixed,
   > hardcoded allowlist of commands (see manutencao_helper.sh) and
   > nothing else.

## Expectativa realista

A revisão pode recusar por causa do escape de sandbox e por o app ser
específico de uma distro. Se isso acontecer, o caminho natural é o COPR
(repositório comunitário do Fedora), onde esse tipo de ferramenta é
bem-vinda sem nenhuma dessas restrições. O código já está pronto — o
empacotamento RPM pro COPR é um passo curto a partir daqui.
