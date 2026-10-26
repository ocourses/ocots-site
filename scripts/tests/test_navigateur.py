"""Tests de scripts/navigateur.py : choix de Chrome, serveur du socle sur un port libre.

    python3 -m unittest discover -s scripts/tests
"""

import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import navigateur  # noqa: E402


class Chrome(unittest.TestCase):
    def test_la_variable_chrome_l_emporte(self):
        with mock.patch.dict(os.environ, {"CHROME": "/x/chrome"}):
            self.assertEqual(navigateur.chrome(), "/x/chrome")

    def test_a_defaut_un_navigateur_du_path_puis_macos(self):
        with mock.patch.dict(os.environ, clear=True), mock.patch("shutil.which", side_effect=lambda n: "/usr/bin/chromium" if n == "chromium" else None):
            self.assertEqual(navigateur.chrome(), "/usr/bin/chromium")
        with mock.patch.dict(os.environ, clear=True), mock.patch("shutil.which", return_value=None):
            self.assertEqual(navigateur.chrome(), navigateur.CHROME_MACOS)


class Serveur(unittest.TestCase):
    def test_sert_un_dossier_sans_cache_sur_un_port_libre(self):
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "index.html").write_text("<p>bonjour</p>")
            with navigateur.servi(dossier) as url:
                reponse = urllib.request.urlopen(f"{url}/index.html")
                self.assertEqual(reponse.read(), b"<p>bonjour</p>")
                self.assertEqual(reponse.headers["Cache-Control"], "no-store")

    def test_un_fichier_absent_est_une_404(self):
        with tempfile.TemporaryDirectory() as dossier, navigateur.servi(dossier) as url:
            with self.assertRaises(urllib.error.HTTPError) as erreur:
                urllib.request.urlopen(f"{url}/absent.html")
            self.assertEqual(erreur.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
