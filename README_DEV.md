# Dév – Lint, Hooks & Workflow

## Prérequis
- Python 3.10+
- (Optionnel) PHP si des fichiers `.php` existent (php-cs-fixer / phpstan)
- Godot 4.x (édition du projet) — le lint GDScript tourne en CLI
- Outils installés via `requirements-dev.txt` (gdtoolkit, ruff, mypy, editorconfig-checker)

## Setup (Linux/macOS)
    pip install -r requirements-dev.txt
    pre-commit install

## Setup (Windows PowerShell)
    pip install -r requirements-dev.txt
    pre-commit install
    git config --global core.autocrlf false   # recommandé (EOL = LF)

## Lancer le lint en local
- Linux/macOS : ./tools/lint.sh
- Windows      : .\tools\lint.ps1
Le hook pre-commit exécute aussi tools/lint.py automatiquement à chaque commit.

## Outils utilisés
- GDScript : gdformat, gdlint
- Python   : ruff (format + lint), mypy
- Shell    : shfmt, shellcheck
- EditorConfig : editorconfig-checker (avec exclusion des caches)
Notes:
- Tous les outils Python sont fournis via requirements-dev.txt
- Linux (optionnel) : sudo apt-get update && sudo apt-get install -y shellcheck shfmt

## Conventions de branches & MR
- Développer sur des branches : `CODE`_`BreveExplication`
- Convention des commits : Feat[`CODE`]: `Explications` ou Fix[`CODE`]: `Explications`...
- MR vers preprod (QA), puis MR vers prod pour release
- Push direct interdit sur preprod/prod (branches protégées)
- CI GitLab : pipeline obligatoire et “vert” avant merge
- Discussions de MR résolues avant merge
- Templates de MR :
  - GitLab : .gitlab/merge_request_templates/Feature.md ou Hotfix.md
  - Choisir le template dans “Choose a template” lors de la création de la MR

## Fins de ligne & format
Le repo force LF + newline final.
- Si EditorConfig remonte des erreurs :
  - Dans VS Code, change CRLF -> LF (en bas à droite) et ré-enregistre
  - Renormaliser une fois si besoin :
        git add --renormalize .
        git commit -m "Normalize line endings to LF"
- Fichiers de config présents :
  - .editorconfig (end_of_line=lf, insert_final_newline=true, etc.)
  - .gitattributes (* text=auto eol=lf ; binaires en binary)
  - .ecrc (exclusions editorconfig-checker pour caches : .mypy_cache, .ruff_cache, .godot, .import, etc.)

## Mirroring GitLab -> GitHub
- GitHub sert de miroir “lecture seule” pour l’équipe (pushs humains interdits)
- Les pushes sont faits automatiquement par GitLab (push mirroring via PAT)
- En cas d’urgence (GitLab indisponible) : suivre la procédure “break glass”

## Commandes utiles
    pre-commit run --all-files
    ruff check . --fix
    mypy .

## Notes techniques
- pre-commit appelle le lint avec “python -X utf8 tools/lint.py” (UTF-8 forcé, compat Windows)
- tools/lint.py ignore les caches (mypy/ruff/godot/import) pour editorconfig-checker
- La CI GitLab vérifie tools/lint.py et bloque le merge si KO
