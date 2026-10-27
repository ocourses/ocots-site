"""Tests de scripts/residu-css.py. Un outil Python se teste en Python, à côté de lui :
`tests/` du socle ne teste que ce qui est publié (et `scripts/` ne l'est pas).

    python3 -m unittest discover -s scripts/tests
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "residu-css.py"
spec = importlib.util.spec_from_file_location("residu_css", SCRIPT)
residu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(residu)

# Le bloc `body` tel que le socle l'écrit : un cours qui le reprend à l'identique n'a rien à garder.
BODY_DU_SOCLE = next(brut for brut, tete, _, _ in residu.blocs(residu.texte_socle()) if tete == "body").strip() + "\n"


def lance(css, *options):
    with tempfile.TemporaryDirectory() as dossier:
        feuille = Path(dossier) / "style.css"
        feuille.write_text(css)
        return subprocess.run([sys.executable, str(SCRIPT), str(feuille), *options], capture_output=True, text=True).stdout


class Analyse(unittest.TestCase):
    def test_virgules_hors_parentheses(self):
        self.assertEqual(residu.virgules("a, b:is(.c, .d), e"), ["a", " b:is(.c, .d)", " e"])

    def test_un_point_virgule_dans_un_commentaire_ne_termine_rien(self):
        blocs = residu.blocs("/* un ; piège */\n.a { color: red; }\n")
        self.assertEqual([tete for _, tete, _, _ in blocs], [".a"])

    def test_media_garde_ses_sous_blocs(self):
        _, tete, regles, sous = residu.blocs("@media (min-width: 1px) { .a { margin: 0; } .b { margin: 1px; } }")[0]
        self.assertTrue(tete.startswith("@media"))
        self.assertEqual(len(sous), 2)
        self.assertEqual(len(regles), 2)

    def test_proprietes_par_selecteur(self):
        self.assertEqual(residu.proprietes(".a { margin: 0; color: red; } .a { padding: 0; }"), {("", ".a"): {"margin", "color", "padding"}})


class Reste(unittest.TestCase):
    def test_un_bloc_du_socle_est_omis_un_bloc_propre_est_garde(self):
        sortie = lance(BODY_DU_SOCLE + "\n.propre-au-cours-xyz {\n  color: var(--texte);\n}\n")
        self.assertIn(".propre-au-cours-xyz", sortie)
        self.assertNotIn("body {", sortie)

    def test_un_commentaire_avec_point_virgule_ne_fait_pas_perdre_la_regle_suivante(self):
        sortie = lance("/* Propre au cours ; suite. */\n\n.propre-au-cours-xyz {\n  color: var(--texte);\n}\n")
        self.assertRegex(sortie, r"^/\* Propre au cours ; suite\. \*/\s*\.propre-au-cours-xyz \{")

    def test_d_un_bloc_garde_les_selecteurs_du_socle_sont_retires(self):
        sortie = lance("@media (max-width: 700px) {\n  /* Une colonne. */\n  .propre-au-cours-xyz,\n  .grille-2 {\n"
                       "    grid-template-columns: minmax(0, 1fr);\n  }\n}\n")
        self.assertIn("  /* Une colonne. */\n  .propre-au-cours-xyz {\n    grid-template-columns", sortie)
        self.assertNotIn(".grille-2", sortie)

    def test_une_regle_aux_declarations_differentes_est_gardee(self):
        sortie = lance("body {\n  margin: 5px;\n}\n")
        self.assertIn("margin: 5px", sortie)

    def test_les_proprietes_du_socle_que_le_cours_ne_regle_pas_sont_remises_a_revert(self):
        sortie = lance("body {\n  margin: 5px;\n}\n")
        socle = residu.proprietes(residu.texte_socle())[("", "body")]
        self.assertIn("revert", sortie)
        for propriete in socle - {"margin"}:
            self.assertIn(f"{propriete}: revert", sortie)

    def test_un_selecteur_absent_du_cours_est_une_nouveaute_non_neutralisee(self):
        nouveautes = lance("body {\n  margin: 0;\n}\n", "--nouveautes").splitlines()
        self.assertIn(".carte-onglets [role='tabpanel'] > h2", nouveautes)
        self.assertNotIn("body", nouveautes)

    def test_le_css_mort_est_ecarte_avec_un_site(self):
        with tempfile.TemporaryDirectory() as site:
            (Path(site) / "index.html").write_text('<div class="vivant"></div>')
            css = ".vivant { color: red; }\n.mort-xyz { color: red; }\n"
            feuille = Path(site) / "style.css"
            feuille.write_text(css)
            sortie = subprocess.run([sys.executable, str(SCRIPT), str(feuille), "--site", site], capture_output=True, text=True).stdout
        self.assertIn(".vivant", sortie)
        self.assertNotIn(".mort-xyz", sortie)


if __name__ == "__main__":
    unittest.main()
