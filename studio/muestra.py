"""muestra.py — un repo de dotfiles y un HOME inventados para las capturas y para probar la ventana sin tocar nada real.

`crear(carpeta)` copia el gestor (main.sh, config.sh, lib/, docs/, README.md, .gitignore) a `<carpeta>/dotfiles` y deja
cada estado a la vista con el mapa real de config.sh:

- enlazados: git, konsole, vim, nvim y kde (con `kdeglobals`, híbrido, reescrito por «Plasma» y sin confirmar);
- texstudio enlazado, con `texstudio.ini` (híbrido con filtro clean) también reescrito;
- shell: `.zshrc` real en HOME distinto del repo (conflicto; con un token falso que la comparación oculta) y
  `starship.toml` sin enlazar;
- calibre: archivos reales en HOME (la aplicación sustituye el enlace);
- kate: solo en HOME (adoptar lo lleva al repo); okular: solo en el repo (instalar);
- el resto, sin configuración;
- para el escáner: una contraseña en la URL de un remoto de `.gitconfig` y un `.env` nuevo con un token de Slack falso.

Devuelve (repo, casa). Ningún dato es de la máquina: todo es texto de ejemplo.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REPO_REAL = AQUI.parent
ENTORNO_GIT = {"GIT_AUTHOR_NAME": "Muestra", "GIT_AUTHOR_EMAIL": "muestra@ejemplo.org", "GIT_COMMITTER_NAME": "Muestra",
               "GIT_COMMITTER_EMAIL": "muestra@ejemplo.org", "GIT_CONFIG_GLOBAL": "/dev/null"}
TOKEN_FALSO = "gh" + "p_" + "Mu3str4" * 6        # partido: escrito entero, el escáner del repo lo encontraría aquí

CONTENIDO = {
    ".gitconfig": "[user]\n\tname = Persona de Muestra\n\temail = muestra@ejemplo.org\n[init]\n\tdefaultBranch = main\n[pull]\n\trebase = true\n",
    ".zshrc": "# zsh de muestra\nexport EDITOR=kate\nalias ll='ls -lh'\nalias gs='git status'\nplugins=(git)\n",
    ".config/starship.toml": "add_newline = false\n\n[character]\nsuccess_symbol = \"[›](bold green)\"\n",
    ".vimrc": "set number\nset expandtab\nset shiftwidth=4\ncolorscheme lliphi\n",
    ".config/nvim/init.lua": "vim.opt.number = true\nvim.opt.expandtab = true\nvim.cmd.colorscheme('lliphi')\n",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env={**os.environ, **ENTORNO_GIT})


def _escribir(p: Path, texto: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")


def _texto(rel: str, paquete: str) -> str:
    if rel in CONTENIDO:
        return CONTENIDO[rel]
    nombre = Path(rel).name
    if nombre == "kdeglobals":
        return "[General]\nColorScheme=LliphiOscuro\nfont=Inter,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1\n\n[KDE]\nSingleClick=false\nwidgetStyle=kvantum\n"
    if nombre == "texstudio.ini":
        return "[General]\nEditor\\Font%20Family=JetBrains Mono\nEditor\\Font%20Size=11\nTools\\Commands\\latexmk=latexmk -lualatex %\n"
    if nombre.endswith((".json", ".js")):
        return '{\n  "editor.fontFamily": "JetBrains Mono",\n  "editor.tabSize": 4,\n  "workbench.colorTheme": "Lliphi"\n}\n'
    if nombre.endswith(".service"):
        return "[Unit]\nDescription=Unidad de muestra\n\n[Service]\nType=oneshot\nExecStart=/usr/bin/true\n\n[Install]\nWantedBy=default.target\n"
    return f"# {paquete}: {rel} (muestra)\n[General]\nTema=Lliphi\nIdioma=es\n"


def crear(carpeta: Path) -> tuple[Path, Path]:
    repo, casa = carpeta / "dotfiles", carpeta / "casa"
    repo.mkdir(parents=True, exist_ok=True)
    casa.mkdir(parents=True, exist_ok=True)
    for n in ("main.sh", "config.sh", ".gitignore", "README.md"):
        shutil.copy2(REPO_REAL / n, repo / n)
    shutil.copytree(REPO_REAL / "lib", repo / "lib", dirs_exist_ok=True)
    shutil.copytree(REPO_REAL / "docs", repo / "docs", dirs_exist_ok=True, ignore=shutil.ignore_patterns("figuras"))

    import sys
    sys.path.insert(0, str(AQUI))
    from dotfiles_app import estado as est
    mapa = est.mapa(repo)

    enlazados = ("git", "konsole", "vim", "nvim", "kde", "texstudio")
    for paquete, rels in mapa.items():
        for rel in rels:
            if rel.endswith("/"):
                continue
            en_repo, en_casa = repo / paquete / rel, casa / rel
            if paquete in enlazados:
                _escribir(en_repo, _texto(rel, paquete))
                en_casa.parent.mkdir(parents=True, exist_ok=True)
                en_casa.symlink_to(en_repo)
            elif paquete == "shell":
                _escribir(en_repo, _texto(rel, paquete))
                if rel == ".zshrc":
                    _escribir(en_casa, _texto(rel, paquete).replace("alias gs='git status'\n", "alias gs='git status -sb'\nalias k=kate\n")
                              + f"export GITHUB_TOKEN={TOKEN_FALSO}\n")
            elif paquete == "calibre":
                _escribir(en_repo, _texto(rel, paquete))
                _escribir(en_casa, _texto(rel, paquete).replace("Idioma=es", "Idioma=es\nUltimaBiblioteca=Biblioteca de muestra"))
            elif paquete == "kate":
                _escribir(en_casa, _texto(rel, paquete))
            elif paquete == "okular":
                _escribir(en_repo, _texto(rel, paquete))
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "filter.texstudio-ini.clean", "bash lib/filtros/texstudio_ini.sh")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "muestra: estado inicial")
    # lo que las aplicaciones reescribieron desde el último commit (los híbridos, a la vista en Cambios)
    for paquete, rels in mapa.items():
        for rel in rels:
            nombre = Path(rel).name
            p = repo / paquete / rel
            if nombre == "kdeglobals" and p.is_file():
                p.write_text(p.read_text(encoding="utf-8").replace("SingleClick=false", "SingleClick=true")
                             + "\n[KFileDialog Settings]\nRecent Files=muestra.pdf\n", encoding="utf-8")
            if nombre == "texstudio.ini" and p.is_file():
                p.write_text(p.read_text(encoding="utf-8").replace("Font%20Size=11", "Font%20Size=12"), encoding="utf-8")
    p = repo / "git" / ".gitconfig"
    p.write_text(p.read_text(encoding="utf-8") + "[merge]\n\tconflictstyle = zdiff3\n"
                 + "[remote \"espejo\"]\n\turl = https://" + "persona:" + "Muestra2026" + "@git.ejemplo.org/dotfiles.git\n", encoding="utf-8")
    # lo que el escáner debe ver antes de confirmar: una contraseña en una URL (arriba) y un .env nuevo sin ignorar
    _escribir(repo / "shell" / ".config" / "servicio.env", "SERVICIO_URL=https://ejemplo.org\nSERVICIO_TOKEN=" + "xo" + "xb-" + "1234567890-muestra\n")
    return repo, casa


if __name__ == "__main__":
    import sys
    print(crear(Path(sys.argv[1])))
