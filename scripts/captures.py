#!/usr/bin/env python3
"""Captures d'écran des pages d'un site et comparaison avant/après.

    scripts/captures.py prendre DOSSIER_SITE SORTIE [--largeur 1504 --hauteur 856]
    scripts/captures.py comparer REFERENCE REFERENCE_BIS APRES

`prendre` sert le site, découvre ses pages (l'accueil, les illustrations et
les exemples disponibles de leurs catalogues) et enregistre une capture PNG
de chacune avec Chrome sans interface. `comparer` donne, par page, le nombre
de pixels qui diffèrent entre REFERENCE et APRES ; REFERENCE_BIS, une seconde
prise de la même référence, mesure le bruit (animations, particules) : une page
n'est signalée que si elle diffère plus d'APRES que de REFERENCE_BIS (plus
20 pixels de tolérance). Le thème clair est forcé : la capture ne dépend pas du
réglage d'apparence du système.

Prérequis : Google Chrome (variable CHROME), ImageMagick (`compare`), accès à
Internet (KaTeX est chargé depuis un CDN).
"""

import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import time
from pathlib import Path

TOLERANCE = 20   # pixels : l'anticrénelage d'un bord n'est pas un écart
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def disponibles(catalogue):
    """Identifiants des entrées marquées `disponible: true`, dans l'ordre."""
    ids, dernier = [], None
    for ligne in catalogue.read_text().splitlines():
        m = re.match(r"\s*id: '([^']+)'", ligne)
        if m:
            dernier = m.group(1)
        if re.search(r"disponible: true", ligne) and dernier:
            ids.append(dernier)
    return ids


def pages(site):
    liste = [("index", "index.html")]
    cat = site / "js/illustrations/catalogue.js"
    if cat.exists():
        liste += [(f"illustration-{i}", f"illustration.html?id={i}") for i in disponibles(cat)]
    ex = site / "js/exemples/catalogue.js"
    if ex.exists():
        liste += [(f"exemple-{i}", f"exemple.html?id={i}") for i in disponibles(ex)]
    return liste


def prendre(args):
    site, sortie = Path(args.site).resolve(), Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    port = 8800 + os.getpid() % 900
    serveur = subprocess.Popen([sys.executable, "-m", "http.server", "--directory", str(site), str(port)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    def une(page):
        nom, chemin = page
        fichier = sortie / f"{nom}.png"
        for _ in range(2):    # Chrome sans interface se bloque parfois : une reprise
            try:
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                "--blink-settings=preferredColorScheme=1",
                                f"--window-size={args.largeur},{args.hauteur}", "--virtual-time-budget=12000",
                                f"--screenshot={fichier}", f"http://localhost:{port}/{chemin}"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            except subprocess.TimeoutExpired:
                continue
            if fichier.exists():
                break
        return nom, fichier.exists()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            resultats = list(pool.map(une, pages(site)))
    finally:
        serveur.terminate()
    manque = [n for n, ok in resultats if not ok]
    print(f"{len(resultats) - len(manque)} captures dans {sortie}" + (f" ; manquantes : {manque}" if manque else ""))


def ecart(a, b):
    r = subprocess.run(["compare", "-metric", "AE", "-fuzz", "1%", str(a), str(b), "null:"],
                       capture_output=True, text=True)
    m = re.match(r"[\d.]+(?:e[+-]?\d+)?", r.stderr.strip())
    return round(float(m.group(0))) if m else -1


def comparer(args):
    ref, bis, apres = (Path(p) for p in (args.reference, args.reference_bis, args.apres))
    signales = 0
    for png in sorted(ref.glob("*.png")):
        autre, bruit = apres / png.name, ecart(png, bis / png.name)
        d = ecart(png, autre) if autre.exists() else -1
        if d < 0 or d > bruit + TOLERANCE:
            signales += 1
            print(f"{png.stem:50s} écart {d:8d} px (bruit {bruit})")
    total = len(list(ref.glob("*.png")))
    print(f"{total - signales}/{total} pages sans écart au-delà du bruit")
    sys.exit(1 if signales else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(required=True)
    a = sub.add_parser("prendre")
    a.add_argument("site")
    a.add_argument("sortie")
    a.add_argument("--largeur", type=int, default=1504)
    a.add_argument("--hauteur", type=int, default=856)
    a.set_defaults(f=prendre)
    b = sub.add_parser("comparer")
    b.add_argument("reference")
    b.add_argument("reference_bis")
    b.add_argument("apres")
    b.set_defaults(f=comparer)
    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
