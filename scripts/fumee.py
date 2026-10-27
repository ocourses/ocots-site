#!/usr/bin/env python3
"""Test de fumée : une page du socle s'ouvre dans Chrome sans interface, sans erreur.

    scripts/fumee.py [--racine DOSSIER] [PAGE ...]

Sert DOSSIER (par défaut le dépôt) avec `serve.mjs`, charge chaque page (par défaut
l'accueil et les illustrations du cours minimal), et vérifie que la page a démarré
(`data-ok="1"` sur `<body>`, posé par les pages du socle une fois KaTeX chargé) et
que la console du navigateur ne contient aucune erreur. Demande le réseau (KaTeX
est chargé depuis un CDN). Code de sortie 1 s'il y a un écart.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from navigateur import SOCLE, chrome, lance_chrome, servi

PAGES_PAR_DEFAUT = [
    "examples/minimal/index.html",
    "examples/minimal/illustration.html?id=droite",
    "examples/minimal/illustration.html?id=aire",
    "examples/minimal/illustration.html?id=inconnue",
]
ERREUR = re.compile(
    r"CONSOLE[^\n]*(Uncaught|Failed to load|net::ERR|status of 404|"
    r"SyntaxError|TypeError|ReferenceError)",
    re.I,
)
EXIGE_CHROME = os.environ.get("EXIGE_CHROME") == "1"

if EXIGE_CHROME and not Path(chrome()).exists():
    raise RuntimeError("Chrome introuvable alors que EXIGE_CHROME=1")


def verifie(url, page):
    """Les défauts de `page`, sous forme de liste de messages (vide si tout va bien)."""
    reponse = lance_chrome(f"{url}/{page}", "--dump-dom", "--enable-logging=stderr", "--v=0")
    defauts = []
    if 'data-ok="1"' not in reponse.stdout:
        defauts.append('la page n\'a pas démarré (pas de data-ok="1")')
    defauts += [f"console : {ligne.strip()[:160]}" for ligne in reponse.stderr.splitlines() if ERREUR.search(ligne)]
    return defauts


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--racine", default=SOCLE, type=Path, help="dossier servi (défaut : le dépôt)")
    p.add_argument("pages", nargs="*", default=PAGES_PAR_DEFAUT)
    args = p.parse_args()
    echec = False
    with servi(args.racine) as url:
        for page in args.pages:
            defauts = verifie(url, page)
            print(f"{page} : {'ok' if not defauts else 'ÉCHEC'}")
            for defaut in defauts:
                print(f"   - {defaut}")
            echec = echec or bool(defauts)
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
