"""Tests de scripts/site-apres.py : liens remplacés, reste du cours calculé, pages posées.

    python3 -m unittest discover -s scripts/tests
"""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "site-apres.py"
spec = importlib.util.spec_from_file_location("site_apres", SCRIPT)
site_apres = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_apres)

PAGE = """<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
    <link rel="stylesheet" href="css/theme.css" />
    <link rel="stylesheet" href="css/style.css" />
</head><body><p class="propre">x</p></body>
"""


class Relie(unittest.TestCase):
    def test_les_feuilles_du_socle_puis_celle_du_cours_dans_l_ordre(self):
        lignes = site_apres.relie(PAGE).splitlines()
        self.assertEqual(lignes[1:5], [
            '    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />',
            '    <link rel="stylesheet" href="socle/css/theme.css" />',
            '    <link rel="stylesheet" href="socle/css/style.css" />',
            '    <link rel="stylesheet" href="css/cours.css" />',
        ])

    def test_un_lien_de_forme_inattendue_est_signale(self):
        with self.assertRaisesRegex(ValueError, "css/style.css"):
            site_apres.relie('<link href="css/style.css" rel="stylesheet">')


class Construit(unittest.TestCase):
    def test_un_site_avec_le_socle_et_son_reste(self):
        with tempfile.TemporaryDirectory() as dossier:
            site = Path(dossier) / "site"
            (site / "css").mkdir(parents=True)
            (site / "index.html").write_text(PAGE)
            (site / "css/theme.css").write_text(":root {}\n")
            (site / "css/style.css").write_text(".propre {\n  color: var(--texte);\n}\n")
            sortie = site_apres.construit(site, Path(dossier) / "apres")
            self.assertIn('href="css/cours.css"', (sortie / "index.html").read_text())
            self.assertIn(".propre {", (sortie / "css/cours.css").read_text())
            self.assertTrue((sortie / "socle/css/style.css").exists())
            self.assertFalse((sortie / "css/style.css").exists())
            self.assertFalse((sortie / "css/theme.css").exists())
            # Le site d'origine n'est pas touché.
            self.assertTrue((site / "css/style.css").exists())


class PosePages(unittest.TestCase):
    """Sur une copie du cours minimal (sans son lien socle/) ; demande Node."""

    def cours(self, dossier):
        sortie = Path(dossier) / "cours"
        shutil.copytree(site_apres.SOCLE / "examples/minimal", sortie, ignore=shutil.ignore_patterns("socle", "*.html"))
        return sortie

    def test_modeles_js_du_socle_et_configuration_verifiee(self):
        with tempfile.TemporaryDirectory() as dossier:
            sortie = self.cours(dossier)
            config = Path(dossier) / "cours.config.js"
            shutil.move(sortie / "site.config.js", config)
            site_apres.pose_pages(sortie, config, ["illustration.html"])
            self.assertEqual((sortie / "site.config.js").read_text(), config.read_text())
            self.assertEqual((sortie / "illustration.html").read_text(), (site_apres.SOCLE / "modeles/illustration.html").read_text())
            self.assertFalse((sortie / "index.html").exists())
            self.assertTrue((sortie / "socle/js/illustration.js").exists())
            self.assertTrue((sortie / "socle/modeles/index.html").exists())

    def test_une_configuration_fausse_arrete(self):
        with tempfile.TemporaryDirectory() as dossier:
            sortie = self.cours(dossier)
            fausse = Path(dossier) / "faux.config.js"
            fausse.write_text((sortie / "site.config.js").read_text().replace("titre: 'Cours minimal'", "titre: ''"))
            with self.assertRaisesRegex(ValueError, r"configuration\.titre"):
                site_apres.pose_pages(sortie, fausse)


if __name__ == "__main__":
    unittest.main()
