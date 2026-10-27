"""Tests de scripts/sites.py : la copie d'un site de cours.

    python3 -m unittest discover -s scripts/tests
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sites import copie_site  # noqa: E402


class Copie(unittest.TestCase):
    def test_un_lien_qui_boucle_reste_un_lien(self):
        # Le cours minimal du socle pointe vers la racine du socle : en sous-module
        # d'un cours, suivre le lien recopie le socle à l'infini.
        with tempfile.TemporaryDirectory() as d:
            site = Path(d) / "site"
            minimal = site / "socle/examples/minimal"
            minimal.mkdir(parents=True)
            (minimal / "socle").symlink_to("../..")
            (site / "index.html").write_text("<p>accueil</p>")
            copie_site(site, Path(d) / "copie")
            lien = Path(d) / "copie/socle/examples/minimal/socle"
            self.assertTrue(lien.is_symlink())
            self.assertEqual((Path(d) / "copie/index.html").read_text(), "<p>accueil</p>")

    def test_node_modules_et_git_ne_sont_pas_copies(self):
        with tempfile.TemporaryDirectory() as d:
            site = Path(d) / "site"
            for nom in ("node_modules/x", ".git/HEAD", "js/a.js"):
                (site / nom).parent.mkdir(parents=True, exist_ok=True)
                (site / nom).write_text("")
            copie_site(site, Path(d) / "copie")
            self.assertEqual(sorted(p.name for p in (Path(d) / "copie").iterdir()), ["js"])


if __name__ == "__main__":
    unittest.main()
