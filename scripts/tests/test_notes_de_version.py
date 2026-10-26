"""Tests de .github/scripts/notes-de-version : la section du CHANGELOG qui devient les notes de release.

    python3 -m unittest discover -s scripts/tests
"""

import importlib.machinery
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
