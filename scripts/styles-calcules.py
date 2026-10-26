#!/usr/bin/env python3
"""Compare les styles calculés de chaque élément d'une page, avant et après.

    scripts/styles-calcules.py SITE_AVANT SITE_APRES PAGE [PAGE ...]
    scripts/styles-calcules.py ~/…/site /tmp/site-apres 'illustration.html?id=picard'

Plus fiable qu'une capture pour une page animée : une capture diffère d'une prise
à l'autre quand un canevas se redessine, pas les styles calculés. Chrome sans
interface charge la page, un script ajouté au HTML relève getComputedStyle de
chaque élément, et l'on compare. Code de sortie 1 s'il y a un écart.
"""

import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from navigateur import lance_chrome, servi
RELEVE = """<script>
window.addEventListener('load', () => setTimeout(() => {
  const sortie = {};
  document.querySelectorAll('body *').forEach((e) => {
    if (['SCRIPT', 'STYLE'].includes(e.tagName)) return;
    const chemin = [];
    for (let n = e; n && n !== document.body; n = n.parentNode) {
      const c = typeof n.className === 'string' && n.className.trim() ? '.' + n.className.trim().split(/\\s+/).join('.') : '';
      chemin.unshift(n.tagName.toLowerCase() + c + ':' + [...n.parentNode.children].indexOf(n));
    }
    const cs = getComputedStyle(e);
    sortie[chemin.join('>')] = Object.fromEntries([...cs].map((k) => [k, cs.getPropertyValue(k)]));
  });
  const pre = document.createElement('pre');
  pre.id = 'releve';
  pre.textContent = JSON.stringify(sortie);
  document.body.appendChild(pre);
}, 3000));
</script>"""


def releve(site, page):
    with tempfile.TemporaryDirectory(prefix="styles-") as dossier:
        copie = Path(dossier) / "site"
        shutil.copytree(site, copie, ignore=shutil.ignore_patterns("node_modules", ".git"))
        fichier = copie / page.split("?")[0]
        fichier.write_text(fichier.read_text().replace("</body>", RELEVE + "</body>"))
        with servi(copie) as url:
            sortie = lance_chrome(f"{url}/{page}", "--dump-dom", delai=120).stdout
    m = re.search(r'<pre id="releve">(.*?)</pre>', sortie, re.S)
    return json.loads(html.unescape(m.group(1))) if m else {}


def main():
    avant, apres, *pages = sys.argv[1:]
    ecarts = 0
    for page in pages:
        a, b = releve(avant, page), releve(apres, page)
        diff = {k: {p: (a[k][p], b[k].get(p)) for p in a[k] if a[k][p] != b[k].get(p)} for k in a if k in b}
        diff = {k: v for k, v in diff.items() if v}
        manque = [k for k in a if k not in b]
        print(f"{page} : {len(a)} éléments, {len(diff)} aux styles différents, {len(manque)} absents après")
        for k, v in list(diff.items())[:8]:
            print(f"   {k[-100:]}")
            for p, (x, y) in list(v.items())[:4]:
                print(f"      {p}: {x} -> {y}")
        ecarts += len(diff) + len(manque) + (not a)
    sys.exit(1 if ecarts else 0)


if __name__ == "__main__":
    main()
