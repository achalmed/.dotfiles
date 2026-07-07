# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A personal dotfiles repository for Arch Linux and Kubuntu, managed by a custom bash tool ("dotfiles-manager", v3). Config files live here as packages (one directory per app: `kde/`, `shell/`, `konsole/`, `meta/`, etc.) and are symlinked into `$HOME`, so edits made through the symlinks show up directly as changes in this repo. Documentation, comments, log messages, and commands are in Spanish.

Core philosophy ("principio de mínima captura"): only files representing manual personalization are versioned — never caches, MRU lists, window geometry, session state, databases, machine IDs, or credentials. The v3 audit deliberately dropped state-dominated files (`digikamrc`, `krusaderrc`, `okularrc`, Zotero `prefs.js`, LibreOffice `registrymodifications.xcu`, `plasma-org.kde.plasma.desktop-appletsrc`, `plasmashellrc`); they were restored as real files in `$HOME` and must not be re-adopted. The README's "Exclusiones deliberadas" section is the authoritative list.

## Commands

There is no build, lint, or test suite. The tool is `main.sh` (run from the repo root, or via the `dotfiles` alias):

```bash
./main.sh                          # interactive menu
./main.sh instalar                 # create symlinks repo → $HOME
./main.sh adoptar -p meta          # move configs $HOME → repo, then symlink
./main.sh actualizar               # re-apply symlinks
./main.sh eliminar                 # remove symlinks (repo untouched)
./main.sh sync-push                # sensitive-data scan + commit + push
./main.sh sync-pull                # pull + re-link
./main.sh estado                   # symlink + git status
./main.sh backup                   # tarball backup into .backups/
./main.sh seguridad                # scan all tracked files for credentials
./main.sh instalar-deps            # install deps per distro (pacman/apt)
```

Global options: `-p, --packages a,b,c` (limit to specific packages; names are validated against `STOW_PACKAGES`), `-n, --dry-run`, `-v, --verbose`, `-f, --force` (replace without prompting), `--no-backup`.

Non-interactive use is safe: prompts fall back to the safe default (skip / don't delete) when no TTY is available, and `sync-push` auto-generates a commit message. Still prefer passing `-p` and `--dry-run` first when scripting.

## Architecture

`main.sh` is a thin orchestrator: it sources modules in dependency order, parses args, and dispatches to a handler function (invoked inside an `if` so failures are reported instead of killed by `set -e`). All logic lives in `lib/`:

- `config.sh` — all constants: distro detection (pacman vs apt), `STOW_PACKAGES` (canonical package list), `PACKAGE_FILES` (explicit file map), `SENSITIVE_PATTERNS` + `SENSITIVE_SCAN_ALLOWLIST`. Loaded first; everything else depends on it. `DOTFILES_DIR` derives from `$HOME` (overridable via env var).
- `lib/logger.sh` — leveled logging to console and `.logs/dotfiles-YYYY-MM-DD.log`
- `lib/validator.sh` — pre-flight checks; `validate_no_sensitive_data` scans **all** tracked + untracked-unignored files with key=value-style regexes
- `lib/cli.sh` — argument parsing (validates `-p` values), interactive menu, confirmations
- `lib/stow_ops.sh` — adoptar/instalar/actualizar/eliminar; `_read_choice` helper gives TTY-safe prompts
- `lib/git_ops.sh` — sync-push/sync-pull/status
- `lib/tools.sh` — surgical backups (keeps last 15 in `.backups/`), dependency install

Key design decisions:

1. **File selection is explicit, not automatic.** The `PACKAGE_FILES` map in `config.sh` decides exactly which files each package manages (`PACKAGE_FILES["kate"]=".config/katerc|..."`, `|`-separated, paths relative to `$HOME`; entries may be directories, managed as directory symlinks). Anything not listed is never touched.
2. **GNU Stow is NOT invoked.** Symlinks are created directly with `ln -sfn`, file by file. The package layout remains 100% stow-compatible (paths relative to `$HOME` inside each package dir), so `stow <pkg>` would also work, but the manager gives file-level control. Don't reintroduce a hard stow dependency.
3. `sync-push` refuses to push if the sensitive-data scan finds matches; reviewed false positives go in `SENSITIVE_SCAN_ALLOWLIST`.

## Packages

`git`, `shell` (zsh + starship at XDG path `.config/starship.toml`), `kde` (preference-dominated files only), `konsole` (konsolerc + profiles in `.local/share/konsole/`), `positron`, `obsidian` (vault config; vault = `~/Documents`), `meta` (vault work resources in `~/Documents/meta`: templater/quickadd/dataview scripts, dashboards — managed as directory symlinks; `attachments/`, `archivo/`, `.claude/` deliberately excluded), `calibre`, `kate`, `texstudio`, `okular` (`okularpartrc` only), `rstudio`, `xournalpp`, `koreader`.

## Adding a new package

1. Add the package name to `STOW_PACKAGES` in `config.sh`
2. Add its file list to `PACKAGE_FILES` — only user-preference files, never cache/state/credentials; watch a candidate file with `git diff` for a few days if unsure whether it churns
3. Run `./main.sh adoptar -p <pkg>` (config exists in `$HOME`) or `./main.sh instalar -p <pkg>` (config exists in repo)

## Conventions and gotchas

- Scripts use `set -euo pipefail` and are shellcheck-annotated (`# shellcheck source=...`); keep both when editing. Bash 4+ required (associative arrays).
- Do not `source /etc/os-release` — its variables (VERSION, NAME, ID) collide with the repo's readonly constants; `config.sh` greps the ID field instead.
- Hybrid files with accepted minor churn: `kdeglobals`, `kwinrc`, `konsolerc`, `texstudio.ini` (preferences dominate; small diffs after app use are normal).
- The Obsidian vault is `~/Documents` itself; `obsidian` and `meta` packages assume that path.
- starship config is versioned but inactive: `.zshrc` uses Oh My Zsh and doesn't init starship.
- `.backups/` and `.logs/` are auto-managed by the tool; don't edit or commit them.
- Historical note: old commits contain digiKam's encoded DB password (file no longer tracked). Rewriting history requires the user's explicit decision.
- Commit messages follow conventional-commit style with Spanish descriptions, e.g. `feat(config): add explicit file mapping for all stow packages`.
