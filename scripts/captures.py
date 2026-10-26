#!/usr/bin/env python3
"""Captures d'écran des pages d'un site et comparaison avant/après.

    scripts/captures.py prendre DOSSIER_SITE SORTIE [--tailles 1504x856 390x844 1504x600]
    scripts/captures.py comparer REFERENCE REFERENCE_BIS APRES

`prendre` sert le site, découvre ses pages (l'accueil, les illustrations et
les exemples disponibles de leurs catalogues) et enregistre une capture PNG
de chacune avec Chrome sans interface, à chaque taille demandée (par défaut
1504 × 856, la fenêtre de référence des conventions ; avec plusieurs tailles, un
sous-dossier `LARGEURxHAUTEUR` par taille : 390x844 pour un téléphone, 1504x600
pour une fenêtre basse). `comparer` donne, par page, le nombre
de pixels qui diffèrent entre REFERENCE et APRES ; REFERENCE_BIS, une seconde
prise de la même référence, mesure le bruit (animations, particules) : une page
n'est signalée que si elle diffère plus d'APRES que de REFERENCE_BIS (plus
20 pixels de tolérance). Le thème clair est forcé : la capture ne dépend pas du
réglage d'apparence du système.

Prérequis : Chrome (voir navigateur.py), ImageMagick (`compare`), Node, accès à
Internet (KaTeX est chargé depuis un CDN).
"""

import argparse
import concurrent.futures
import re
import subprocess
import sys
from pathlib import Path

from navigateur import lance_chrome, servi, taille

TOLERANCE = 20   # pixels : l'anticrénelage d'un bord n'est pas un écart


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
    tailles = [taille(t) for t in args.tailles]

    def une(url, dossier, page, dimensions):
        nom, chemin = page
        fichier = dossier / f"{nom}.png"
        try:    # lance_chrome relance déjà un Chrome bloqué
            lance_chrome(f"{url}/{chemin}", f"--screenshot={fichier}", largeur=dimensions[0], hauteur=dimensions[1])
        except subprocess.TimeoutExpired:
            pass
        return nom, fichier.exists()

    manque = []
    with servi(site) as url, concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for dimensions in tailles:
            dossier = sortie / f"{dimensions[0]}x{dimensions[1]}" if len(tailles) > 1 else sortie
            dossier.mkdir(parents=True, exist_ok=True)
            resultats = pool.map(lambda page: une(url, dossier, page, dimensions), pages(site))
            manque += [f"{dossier.name}/{nom}" for nom, ok in resultats if not ok]
    total = len(pages(site)) * len(tailles) - len(manque)
    print(f"{total} captures dans {sortie}" + (f" ; manquantes : {manque}" if manque else ""))


def ecart(a, b):
    r = subprocess.run(["compare", "-metric", "AE", "-fuzz", "1%", str(a), str(b), "null:"], capture_output=True, text=True)
    m = re.match(r"[\d.]+(?:e[+-]?\d+)?", r.stderr.strip())
    return round(float(m.group(0))) if m else -1


def comparer(args):
    ref, bis, apres = (Path(p) for p in (args.reference, args.reference_bis, args.apres))
    signales = 0
    captures = sorted(ref.rglob("*.png"))
    for png in captures:
        relatif = png.relative_to(ref)
        autre, bruit = apres / relatif, ecart(png, bis / relatif)
        d = ecart(png, autre) if autre.exists() else -1
        if d < 0 or d > bruit + TOLERANCE:
            signales += 1
            print(f"{relatif.with_suffix('').as_posix():50s} écart {d:8d} px (bruit {bruit})")
    print(f"{len(captures) - signales}/{len(captures)} pages sans écart au-delà du bruit")
    sys.exit(1 if signales else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(required=True)
    a = sub.add_parser("prendre")
    a.add_argument("site")
    a.add_argument("sortie")
    a.add_argument("--tailles", nargs="+", default=["1504x856"], metavar="LARGEURxHAUTEUR")
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
