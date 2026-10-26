"""Tests de scripts/site-apres.py : liens remplacés, reste du cours calculé.

    python3 -m unittest discover -s scripts/tests
"""

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
