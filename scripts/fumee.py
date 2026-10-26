#!/usr/bin/env python3
"""Test de fumée : une page du socle s'ouvre dans Chrome sans interface, sans erreur.

    scripts/fumee.py [PAGE ...]     # défaut : examples/minimal/index.html

Sert le dépôt avec `serve.mjs`, charge chaque page, et vérifie que le script de la
page est allé au bout (`data-ok="1"` sur `<body>`), que KaTeX a rendu une formule, et
que la console du navigateur ne contient aucune erreur. Demande le réseau (KaTeX est
chargé depuis un CDN). Code de sortie 1 au premier écart.
"""

import os
import re
import sys
from pathlib import Path

from navigateur import SOCLE, lance_chrome, servi

PAGE_PAR_DEFAUT = "examples/minimal/index.html"
ERREUR = re.compile(
    r"CONSOLE[^\n]*(Uncaught|Failed to load|net::ERR|status of 404|"
    r"SyntaxError|TypeError|ReferenceError)",
    re.I,
)
EXIGE_CHROME = os.environ.get("EXIGE_CHROME") == "1"

if EXIGE_CHROME and not Path(navigateur.chrome()).exists():
    raise RuntimeError("Chrome introuvable alors que EXIGE_CHROME=1")


def verifie(url, page):
    """Les défauts de `page`, sous forme de liste de messages (vide si tout va bien)."""
    reponse = lance_chrome(f"{url}/{page}", "--dump-dom", "--enable-logging=stderr", "--v=0")
    defauts = []
    if 'data-ok="1"' not in reponse.stdout:
        defauts.append('le script de la page n\'est pas allé au bout (pas de data-ok="1")')
    if 'class="katex"' not in reponse.stdout:
        defauts.append("aucune formule rendue par KaTeX")
    defauts += [f"console : {ligne.strip()[:160]}" for ligne in reponse.stderr.splitlines() if ERREUR.search(ligne)]
    return defauts


def main(pages):
    echec = False
    with servi(SOCLE) as url:
        for page in pages or [PAGE_PAR_DEFAUT]:
            defauts = verifie(url, page)
            print(f"{page} : {'ok' if not defauts else 'ÉCHEC'}")
            for defaut in defauts:
                print(f"   - {defaut}")
            echec = echec or bool(defauts)
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
