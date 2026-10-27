"""Copie d'un site de cours, partagée par les outils qui le rejouent ailleurs."""

import shutil

IGNORES = shutil.ignore_patterns("node_modules", ".git")


def copie_site(site, cible):
    """Copie `site` dans `cible`, sans `node_modules` ni `.git`. Les liens symboliques
    restent des liens : celui du cours minimal du socle (`examples/minimal/socle`,
    vers la racine du socle) boucle sinon, dès que le socle est un sous-module du cours."""
    shutil.copytree(site, cible, symlinks=True, ignore=IGNORES)
