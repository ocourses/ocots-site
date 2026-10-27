"""Tests de .github/scripts/notes-de-version : la section du CHANGELOG qui devient les notes de release.

    python3 -m unittest discover -s scripts/tests
"""

import importlib.machinery
import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / ".github/scripts/notes-de-version"
chargeur = importlib.machinery.SourceFileLoader("notes_de_version", str(SCRIPT))
spec = importlib.util.spec_from_loader("notes_de_version", chargeur)
notes = importlib.util.module_from_spec(spec)
chargeur.exec_module(notes)

CHANGELOG = """# Journal

---

## Non publié

- à venir

---

## v0.2.0 — 2026-11-01

### Fichiers

- un
- deux

---

## v0.1.0 — 2026-10-30

- premier
"""


class Section(unittest.TestCase):
    def test_la_section_d_une_version_sans_le_reste(self):
        self.assertEqual(notes.section(CHANGELOG, "v0.2.0"), "### Fichiers\n\n- un\n- deux")

    def test_la_derniere_section_va_jusqu_a_la_fin(self):
        self.assertEqual(notes.section(CHANGELOG, "v0.1.0"), "- premier")

    def test_une_version_absente_n_a_pas_de_section(self):
        self.assertIsNone(notes.section(CHANGELOG, "v0.3.0"))

    def test_v0_2_ne_prend_pas_v0_20(self):
        self.assertIsNone(notes.section(CHANGELOG.replace("v0.2.0", "v0.20.0"), "v0.2"))

    def test_une_preversion_au_dessus_ne_remplace_pas_la_version(self):
        changelog = CHANGELOG.replace(
            "## v0.2.0 — 2026-11-01",
            "## v0.2.0-rc1 — 2026-11-01\n\n- préversion\n\n---\n\n## v0.2.0 — 2026-11-01",
        )
        self.assertEqual(notes.section(changelog, "v0.2.0"), "### Fichiers\n\n- un\n- deux")


class Main(unittest.TestCase):
    """Le script lancé dans un dépôt : son code de sortie selon le CHANGELOG.md du tag."""

    def lance(self, changelog, version):
        with tempfile.TemporaryDirectory() as dossier:
            Path(dossier, "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            avant = os.getcwd()
            os.chdir(dossier)
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    return notes.main([version])
            finally:
                os.chdir(avant)

    def test_publie_quand_non_publie_est_vide(self):
        vide = CHANGELOG.replace("- à venir\n\n", "")
        self.assertEqual(self.lance(vide, "v0.2.0"), 0)

    def test_refuse_un_tag_qui_porte_des_changements_non_publies(self):
        self.assertEqual(self.lance(CHANGELOG, "v0.2.0"), 1)

    def test_refuse_une_version_sans_section(self):
        vide = CHANGELOG.replace("- à venir\n\n", "")
        self.assertEqual(self.lance(vide, "v0.3.0"), 1)


if __name__ == "__main__":
    unittest.main()
