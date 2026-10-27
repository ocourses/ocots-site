#!/usr/bin/env python3
"""Rejoue les tests de chaque cours avec les fichiers du socle à la place de ses copies.

    scripts/verifie-cours.py

Pour chaque cours, sur une copie de son `site/` :
  1. les fichiers du socle (`js/` et `css/theme.css`, ceux que git suit) remplacent
     les copies du cours ;
  2. son `js/illustrations/commun.js` devient une façade : elle réexporte les briques
     du socle et garde le code propre au cours (`propre-aux-cours.json`) ;
  3. `node --test` est lancé avant et après.

Le script échoue (code 1) si un test réussi avant manque ou échoue après : il compare
les noms des tests, pas seulement leur nombre. Chemins des cours : COURS
(défaut ~/Courses), ou SITE_AUTOMATIQUE, SITE_CALCUL, SITE_MESURE.

Un bloc propre au cours se termine par une accolade fermante en colonne 0 (`}` seul sur
sa ligne), ou tient en une ligne terminée par `;` : c'est ce que le script sait extraire.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOCLE = Path(__file__).resolve().parent.parent
RACINE = Path(os.environ.get("COURS", Path.home() / "Courses"))
SITES = {
    "automatique": os.environ.get("SITE_AUTOMATIQUE", RACINE / "automatique/automatique-enseignants/site"),
    "calcul": os.environ.get("SITE_CALCUL", RACINE / "calcul_differentiel_edo/calcul-differentiel-edo-enseignants/site"),
    "mesure": os.environ.get("SITE_MESURE", RACINE / "mesure_et_integration/integration/mesure-integration-enseignants/site"),
}
PROPRE = json.loads((SOCLE / "scripts/propre-aux-cours.json").read_text())


# Fichiers du socle qui ne remplacent pas encore ceux des cours : la couche de
# configuration (ocots-site#7) prend ses données en argument, et chaque cours
# l'adopte à sa migration. Les poser ici mesurerait la migration, pas la fusion.
A_LA_MIGRATION = {"js/config.js", "js/catalogue.js", "js/parcours.js"}


def fichiers_du_socle():
    suivis = subprocess.run(["git", "-C", SOCLE, "ls-files", "js", "css/theme.css"], capture_output=True, text=True, check=True)
    return [f for f in suivis.stdout.split() if f not in A_LA_MIGRATION]


def bloc(source, nom):
    """Commentaires qui précèdent et déclaration de `nom` (fonction ou constante)."""
    debut = re.search(rf"((?:^//[^\n]*\n)*)^(?:export )?(?:function|const) {nom}\b[^\n]*\n", source, re.M)
    if not debut:
        raise SystemExit(f"bloc introuvable dans commun.js du cours : {nom}")
    if debut.group(0).rstrip().endswith(";"):
        return source[debut.start():debut.end()]
    fin = source.index("\n}\n", debut.end()) + 3
    return source[debut.start():fin]


def facade(cours, original):
    propre = PROPRE[cours]
    lignes = ["export * from '../briques/commun.js';", *propre["imports"]]
    if propre["briques"]:
        lignes.append(f"import {{ {', '.join(propre['briques'])} }} from '../briques/commun.js';")
    blocs = "\n".join(bloc(original, nom) for nom in propre["blocs"])
    return "\n".join(lignes) + "\n\n" + blocs


def tests_reussis(site):
    """(noms des tests réussis, noms des tests en échec) d'un `node --test`."""
    sortie = subprocess.run(["node", "--test", "--test-reporter=tap"], cwd=site, capture_output=True, text=True).stdout
    reussis = set(re.findall(r"^\s*ok \d+ - (.*?)(?: # .*)?$", sortie, re.M))
    echecs = set(re.findall(r"^\s*not ok \d+ - (.*?)(?: # .*)?$", sortie, re.M))
    return reussis, echecs


def verifie(cours, site):
    site = Path(site)
    avant, echecs_avant = tests_reussis(site)
    with tempfile.TemporaryDirectory(prefix=f"verifie-{cours}-") as dossier:
        copie = Path(dossier) / "site"
        shutil.copytree(site, copie, ignore=shutil.ignore_patterns("node_modules", ".git"))
        original = (site / "js/illustrations/commun.js").read_text()
        for fichier in fichiers_du_socle():
            cible = copie / fichier
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOCLE / fichier, cible)
        (copie / "js/illustrations/commun.js").write_text(facade(cours, original))
        apres, echecs_apres = tests_reussis(copie)
    manquants = sorted(avant - apres)
    nouveaux_echecs = sorted(echecs_apres - echecs_avant)
    print(f"{cours} : {len(avant)} tests avant, {len(apres)} après, {len(manquants)} manquant(s), {len(nouveaux_echecs)} nouvel(aux) échec(s)")
    for nom in sorted(set(manquants) | set(nouveaux_echecs)):
        print(f"   - {nom}")
    return not manquants and not nouveaux_echecs


def main():
    resultats = [verifie(cours, site) for cours, site in SITES.items()]
    sys.exit(0 if all(resultats) else 1)


if __name__ == "__main__":
    main()
