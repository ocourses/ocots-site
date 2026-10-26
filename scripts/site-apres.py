#!/usr/bin/env python3
"""Le site d'un cours avec le CSS du socle, tel que la migration le posera.

    scripts/site-apres.py SITE SORTIE

Copie SITE dans SORTIE (qui ne doit pas exister), y pose les feuilles du socle
(`socle/css/`), calcule son `css/cours.css` (`residu-css.py --site`) et fait lier
à chaque page `socle/css/theme.css`, `socle/css/style.css` puis `css/cours.css`,
à la place de `css/theme.css` et `css/style.css`, qui sont retirées : une page
oubliée n'aurait plus de style, au lieu de garder l'ancien en silence.

C'est le site « après » que comparent `styles-calcules.py` et `captures.py`.
Seul le CSS change : le JavaScript reste celui du cours.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

SOCLE = Path(__file__).resolve().parent.parent
LIENS = {
    "css/theme.css": ["socle/css/theme.css"],
    "css/style.css": ["socle/css/style.css", "css/cours.css"],
}
LIEN = re.compile(r'^([ \t]*<link rel="stylesheet" href=")(css/(?:theme|style)\.css)("\s*/?>)$', re.M)


def relie(html):
    """Remplace les liens vers les feuilles du cours par ceux du socle et de `cours.css`."""
    nouveau = LIEN.sub(lambda m: "\n".join(f"{m.group(1)}{cible}{m.group(3)}" for cible in LIENS[m.group(2)]), html)
    restes = [ancien for ancien in LIENS if f'href="{ancien}"' in nouveau]
    if restes:
        raise ValueError(f"lien non remplacé (forme inattendue) : {', '.join(restes)}")
    return nouveau


def construit(site, sortie):
    site, sortie = Path(site).resolve(), Path(sortie)
    shutil.copytree(site, sortie, ignore=shutil.ignore_patterns("node_modules", ".git"))
    shutil.copytree(SOCLE / "css", sortie / "socle/css")
    reste = subprocess.run([sys.executable, str(SOCLE / "scripts/residu-css.py"), str(site / "css/style.css"), "--site", str(site)],
                           capture_output=True, text=True, check=True)
    (sortie / "css/cours.css").write_text(reste.stdout)
    for page in sortie.glob("*.html"):
        page.write_text(relie(page.read_text()))
    for ancien in LIENS:
        (sortie / ancien).unlink()
    return sortie


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(construit(*sys.argv[1:]))


if __name__ == "__main__":
    main()
