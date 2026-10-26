"""Tests de scripts/styles-calcules.py : la comparaison des relevés (sans navigateur).

    python3 -m unittest discover -s scripts/tests
"""

import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
SCRIPT = Path(__file__).resolve().parent.parent / "styles-calcules.py"
spec = importlib.util.spec_from_file_location("styles_calcules", SCRIPT)
styles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(styles)

AVANT = {"p:0": {"color": "red", "margin": "0px"}, "div:1": {"display": "block"}}


class Ecarts(unittest.TestCase):
    def test_des_releves_identiques_ne_donnent_rien(self):
        self.assertEqual(styles.ecarts(AVANT, dict(AVANT)), ({}, []))

    def test_une_propriete_changee_est_relevee_avec_ses_deux_valeurs(self):
        apres = {**AVANT, "p:0": {"color": "blue", "margin": "0px"}}
        self.assertEqual(styles.ecarts(AVANT, apres), ({"p:0": {"color": ("red", "blue")}}, []))

    def test_un_element_disparu_est_releve(self):
        self.assertEqual(styles.ecarts(AVANT, {"p:0": AVANT["p:0"]}), ({}, ["div:1"]))

    def test_une_propriete_disparue_compte_comme_un_ecart(self):
        apres = {**AVANT, "p:0": {"color": "red"}}
        self.assertEqual(styles.ecarts(AVANT, apres), ({"p:0": {"margin": ("0px", None)}}, []))


if __name__ == "__main__":
    unittest.main()
