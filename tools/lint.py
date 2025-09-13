import os
import sys
import subprocess
import shutil
import pathlib
from typing import Iterable, List

INCLUDE_DIRS = ["."]
SKIP_DIRS = {
    ".git",
    "node_modules",
    "vendor",
    ".venv",
    "__pycache__",
    ".import",
    ".vscode",
    ".idea",
    ".godot",
    ".mypy_cache",
    ".ruff_cache",
}

PHP_EXT = {".php"}
PY_EXT = {".py"}
SH_EXT = {".sh", ".bash"}
GD_EXT = {".gd"}


# ---------- helpers ----------
def which(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: List[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)


def collect(exts: Iterable[str]) -> List[str]:
    out: List[str] = []
    for base in INCLUDE_DIRS:
        for root, _, files in os.walk(base):
            if any(skip in root for skip in SKIP_DIRS):
                continue
            for n in files:
                p = pathlib.Path(n)
                if p.suffix.lower() in exts:
                    out.append(os.path.join(root, n))
    return out


def hint_install(tool: str) -> str:
    if tool in ("gdformat", "gdlint"):
        return "Install: pip install -r requirements-dev.txt  (needs gdtoolkit==4.*)"
    if tool == "ruff":
        return "Install: pip install -r requirements-dev.txt"
    if tool == "mypy":
        return "Install: pip install -r requirements-dev.txt"
    if tool == "php-cs-fixer":
        return "Install: composer global require friendsofphp/php-cs-fixer  (ensure it's on PATH)"
    if tool == "phpstan":
        return "Install: composer require --dev phpstan/phpstan"
    if tool == "shfmt":
        return "Install: see https://github.com/mvdan/sh#shfmt"
    if tool == "shellcheck":
        return "Install: see https://www.shellcheck.net/#installing"
    if tool == "editorconfig-checker":
        return "Install: pip install -r requirements-dev.txt"
    return "Install the tool and ensure it’s available on PATH."


def section(title: str):
    print("\n" + "=" * max(8, len(title)))
    print(title)
    print("=" * max(8, len(title)))


def info(msg: str):
    print(f"[i] {msg}")


def warn(msg: str):
    print(f"[!] {msg}")


def ok(msg: str):
    print(f"[✓] {msg}")


# ---------- main ----------
def main():
    rc = 0
    totals = []

    # --- GDScript ---
    section("GDScript (.gd)")
    gd_files = collect(GD_EXT)
    if not gd_files:
        info("Aucun fichier .gd détecté — section ignorée.")
    else:
        ok(f"{len(gd_files)} fichier(s) .gd détecté(s).")
        if which("gdformat"):
            rc |= run(["gdformat", "--line-length", "100"] + gd_files)
        else:
            warn("gdformat introuvable. " + hint_install("gdformat"))
        if which("gdlint"):
            rc |= run(["gdlint"] + gd_files)
        else:
            warn("gdlint introuvable. " + hint_install("gdlint"))
    totals.append(("GDScript", len(gd_files)))

    # --- PHP ---
    section("PHP (.php)")
    php_files = collect(PHP_EXT)
    if not php_files:
        info("Aucun fichier .php détecté — section ignorée.")
    else:
        ok(f"{len(php_files)} fichier(s) .php détecté(s).")
        if which("php"):
            if which("php-cs-fixer"):
                rc |= run(["php-cs-fixer", "fix", "--allow-risky=yes", "--quiet"])
            else:
                warn("php-cs-fixer introuvable. " + hint_install("php-cs-fixer"))
            if which("phpstan"):
                rc |= run(["phpstan", "analyse", "--no-progress", "--memory-limit=1G"])
            else:
                info(
                    "phpstan non installé (analyse statique ignorée). "
                    + hint_install("phpstan")
                )
        else:
            warn("PHP introuvable sur le PATH, section PHP ignorée.")
    totals.append(("PHP", len(php_files)))

    # --- Python ---
    section("Python (.py)")
    py_files = collect(PY_EXT)
    if not py_files:
        info("Aucun fichier .py détecté — section ignorée.")
    else:
        ok(f"{len(py_files)} fichier(s) .py détecté(s).")
        if which("ruff"):
            rc |= run(["ruff", "format", "."])
            rc |= run(["ruff", "check", ".", "--fix"])
        else:
            warn("ruff introuvable. " + hint_install("ruff"))
        if which("mypy"):
            rc |= run(["mypy", "."])
        else:
            info("mypy non installé (typing check ignoré). " + hint_install("mypy"))
    totals.append(("Python", len(py_files)))

    # --- Shell ---
    section("Shell (.sh/.bash)")
    sh_files = collect(SH_EXT)
    if not sh_files:
        info("Aucun script shell détecté — section ignorée.")
    else:
        ok(f"{len(sh_files)} script(s) shell détecté(s).")
        if which("shfmt"):
            rc |= run(["shfmt", "-w"] + sh_files)
        else:
            info(
                "shfmt non installé (formatage shell ignoré). " + hint_install("shfmt")
            )
        if which("shellcheck"):
            rc |= run(["shellcheck"] + sh_files)
        else:
            info(
                "shellcheck non installé (lint shell ignoré). "
                + hint_install("shellcheck")
            )
    totals.append(("Shell", len(sh_files)))

    # --- EditorConfig checker ---
    section("EditorConfig")
    ec_bin = (
        "editorconfig-checker"
        if which("editorconfig-checker")
        else ("ec" if which("ec") else None)
    )
    if ec_bin:
        rc |= run([ec_bin])
    else:
        info("editorconfig-checker non installé (pip install editorconfig-checker).")

    # --- Summary ---
    section("Résumé")
    for name, count in totals:
        print(f"- {name}: {count} fichier(s) pris en compte")
    if rc == 0:
        ok("Lint terminé sans erreur.")
    else:
        warn(f"Lint terminé avec code de sortie {rc} (voir messages ci-dessus).")

    sys.exit(rc)


if __name__ == "__main__":
    main()
