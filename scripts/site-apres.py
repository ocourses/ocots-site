#!/usr/bin/env python3
"""Le site d'un cours avec le CSS du socle, tel que la migration le posera.

    scripts/site-apres.py SITE SORTIE [--pages CONFIG [--modeles PAGE ...]]

Copie SITE dans SORTIE (qui ne doit pas exister), y pose les feuilles du socle
(`socle/css/`), calcule son `css/cours.css` (`residu-css.py --site`) et fait lier
à chaque page `socle/css/theme.css`, `socle/css/style.css` puis `css/cours.css`,
à la place de `css/theme.css` et `css/style.css`, qui sont retirées : une page
oubliée n'aurait plus de style, au lieu de garder l'ancien en silence.

Avec `--pages CONFIG`, les pages aussi : le JavaScript du socle (`socle/js/`) et
ses modèles (`socle/modeles/`) sont posés, CONFIG devient `site.config.js`, et
chaque page de `--modeles` (par défaut les deux gabarits) est remplacée par son
modèle. La configuration est vérifiée par `verifieCours` (Node) : une faute arrête
le script. Le reste du JavaScript du cours (modules d'illustration, pages à lui)
ne change pas. Configurations des trois cours : scripts/configs/.

C'est le site « après » que comparent `styles-calcules.py` et `captures.py`.
"""

import argparse
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


MODELES = ["index.html", "illustration.html"]
VERIFIE = """
import {{ verifieCours }} from {config!r};
import config from {site!r};
await verifieCours(config);
"""


def pose_pages(sortie, config, modeles=MODELES):
    """Pose le JavaScript et les modèles du socle, la configuration et les gabarits ; vérifie la configuration."""
    shutil.copytree(SOCLE / "js", sortie / "socle/js")
    shutil.copytree(SOCLE / "modeles", sortie / "socle/modeles")
    shutil.copy(config, sortie / "site.config.js")
    for page in modeles:
        shutil.copy(SOCLE / "modeles" / page, sortie / page)
    script = VERIFIE.format(config=(sortie / "socle/js/config.js").resolve().as_uri(), site=(sortie / "site.config.js").resolve().as_uri())
    verifie = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True)
    if verifie.returncode:
        raise ValueError(f"configuration refusée par verifieCours :\n{verifie.stderr.strip()}")


def construit(site, sortie, config=None, modeles=MODELES):
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
    if config:
        pose_pages(sortie, Path(config), modeles)
    return sortie


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("site")
    p.add_argument("sortie")
    p.add_argument("--pages", metavar="CONFIG", help="site.config.js à poser avec les pages du socle")
    p.add_argument("--modeles", nargs="+", default=MODELES, metavar="PAGE", help="gabarits remplacés par leur modèle")
    args = p.parse_args()
    print(construit(args.site, args.sortie, args.pages, args.modeles))


if __name__ == "__main__":
    main()
