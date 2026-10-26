"""Tests de scripts/fumee.py : détection des erreurs de console, et page défaillante.

    python3 -m unittest discover -s scripts/tests

La partie qui lance Chrome est sautée, avec sa raison, s'il est introuvable ; la CI
du socle l'a.
"""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import navigateur  # noqa: E402

spec = importlib.util.spec_from_file_location("fumee", Path(__file__).resolve().parent.parent / "fumee.py")
fumee = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fumee)

CHROME_ABSENT = not Path(navigateur.chrome()).exists()


class Console(unittest.TestCase):
    def test_une_erreur_de_la_console_est_reconnue(self):
        ligne = '[1:2:1026/231321:INFO:CONSOLE:7] "Uncaught TypeError: x is null", source: http://localhost/p.js (7)'
        self.assertTrue(fumee.ERREUR.search(ligne))

    def test_un_message_ordinaire_ne_l_est_pas(self):
        self.assertFalse(fumee.ERREUR.search('[1:2:1026/231321:INFO:CONSOLE:7] "chargé", source: http://localhost/p.js (7)'))
        self.assertFalse(fumee.ERREUR.search("[1:2:1026/231321:ERROR:gpu_process_host.cc:1] GPU"))


@unittest.skipIf(CHROME_ABSENT, "Chrome introuvable (variable CHROME)")
class Page(unittest.TestCase):
    def defauts(self, html):
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "p.html").write_text(html)
            with navigateur.servi(dossier) as url:
                return fumee.verifie(url, "p.html")

    def test_une_page_vide_echoue(self):
        defauts = self.defauts("<!doctype html><body></body>")
        self.assertTrue(any("data-ok" in d for d in defauts))
        self.assertTrue(any("KaTeX" in d for d in defauts))

    def test_une_erreur_de_script_est_rapportee(self):
        defauts = self.defauts("<!doctype html><body><script>null.boom</script></body>")
        self.assertTrue(any(d.startswith("console") for d in defauts))


if __name__ == "__main__":
    unittest.main()
