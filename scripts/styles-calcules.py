#!/usr/bin/env python3
"""Compare les styles calculés de chaque élément des pages, avant et après.

    scripts/styles-calcules.py SITE_AVANT SITE_APRES [PAGE ...] [--tailles 1504x856 390x844 1504x600]
    scripts/styles-calcules.py ~/…/site /tmp/site-apres 'illustration.html?id=picard'

Plus fiable qu'une capture pour une page animée : une capture diffère d'une prise
à l'autre quand un canevas se redessine, pas les styles calculés. Chrome sans
interface charge la page, un script ajouté au HTML relève getComputedStyle de
chaque élément, et l'on compare. Sans PAGE : toutes les pages de SITE_AVANT
(celles de captures.py). Chaque taille (par défaut 1504 × 856) est une fenêtre :
390x844 pour un téléphone, 1504x600 pour une fenêtre basse, où jouent les règles
de petit écran, de hauteur et `:has`. Code de sortie 1 s'il y a un écart.
SITE_APRES se construit avec site-apres.py.
"""

import argparse
import concurrent.futures
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from captures import pages
from navigateur import lance_chrome, servi, taille

RELEVE = """<script>
window.addEventListener('load', () => setTimeout(() => {
  const sortie = {};
  // <noscript> n'est pas rendu quand JavaScript tourne : ni relevé, ni compté
  // dans le rang de ses voisins (un modèle en ajoute un sans rien déplacer).
  const rendus = (parent) => [...parent.children].filter((x) => !['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(x.tagName));
  document.querySelectorAll('body *').forEach((e) => {
    if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(e.tagName) || e.closest('noscript')) return;
    const chemin = [];
    for (let n = e; n && n !== document.body; n = n.parentNode) {
      const c = typeof n.className === 'string' && n.className.trim() ? '.' + n.className.trim().split(/\\s+/).join('.') : '';
      chemin.unshift(n.tagName.toLowerCase() + c + ':' + rendus(n.parentNode).indexOf(n));
    }
    const cs = getComputedStyle(e);
    sortie[chemin.join('>')] = Object.fromEntries([...cs].map((k) => [k, cs.getPropertyValue(k)]));
  });
  const pre = document.createElement('pre');
  pre.id = 'releve';
  pre.textContent = JSON.stringify(sortie);
  document.body.appendChild(pre);
}, 3000));
</script>"""


def releves(site, liste, tailles):
    """{(page, taille) : {chemin d'élément : {propriété : valeur}}} ; {} si la page n'a rien rendu."""
    with tempfile.TemporaryDirectory(prefix="styles-") as dossier:
        copie = Path(dossier) / "site"
        shutil.copytree(site, copie, ignore=shutil.ignore_patterns("node_modules", ".git"))
        for page in copie.glob("*.html"):
            page.write_text(page.read_text().replace("</body>", RELEVE + "</body>"))

        def un(cle):
            page, (largeur, hauteur) = cle
            try:
                sortie = lance_chrome(f"{url}/{page}", "--dump-dom", largeur=largeur, hauteur=hauteur, delai=120).stdout
            except subprocess.TimeoutExpired:
                return cle, {}    # signalée comme page vide
            m = re.search(r'<pre id="releve">(.*?)</pre>', sortie, re.S)
            return cle, json.loads(html.unescape(m.group(1))) if m else {}

        cles = [(page, t) for page in liste for t in tailles]
        with servi(copie) as url:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                resultats = dict(pool.map(un, cles))
            # Sous la charge de quatre Chrome, une page peut ne rien rendre à temps :
            # elle est relancée seule, une fois, avant d'être signalée vide.
            for cle in [c for c, r in resultats.items() if not r]:
                resultats[cle] = un(cle)[1]
            return resultats


def ecarts(avant, apres):
    """(éléments aux styles différents {chemin : {propriété : (avant, après)}}, éléments absents après)."""
    diff = {k: {p: (v, apres[k].get(p)) for p, v in props.items() if v != apres[k].get(p)} for k, props in avant.items() if k in apres}
    return {k: v for k, v in diff.items() if v}, [k for k in avant if k not in apres]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("avant")
    p.add_argument("apres")
    p.add_argument("pages", nargs="*")
    p.add_argument("--tailles", nargs="+", default=["1504x856"], metavar="LARGEURxHAUTEUR")
    args = p.parse_args()
    tailles = [taille(t) for t in args.tailles]
    liste = args.pages or [chemin for _, chemin in pages(Path(args.avant))]
    a, b = releves(args.avant, liste, tailles), releves(args.apres, liste, tailles)
    signales = 0
    for cle in sorted(a):
        page, (largeur, hauteur) = cle
        diff, manque = ecarts(a[cle], b[cle])
        vide = not a[cle] or not b[cle]
        if diff or manque or vide:
            signales += 1
        etat = "page vide" if vide else f"{len(a[cle])} éléments, {len(diff)} aux styles différents, {len(manque)} absents après"
        print(f"{largeur}x{hauteur} {page} : {etat}")
        for k, v in list(diff.items())[:8]:
            print(f"   {k[-100:]}")
            for prop, (x, y) in list(v.items())[:4]:
                print(f"      {prop}: {x} -> {y}")
    print(f"{len(a) - signales}/{len(a)} pages × tailles sans écart de style")
    sys.exit(1 if signales else 0)


if __name__ == "__main__":
    main()
