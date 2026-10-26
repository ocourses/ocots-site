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
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
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


def releve(site, page, port):
    dossier = Path(tempfile.mkdtemp(prefix="styles-")) / "site"
    shutil.copytree(site, dossier, ignore=shutil.ignore_patterns("node_modules", ".git"))
    fichier = dossier / page.split("?")[0]
    fichier.write_text(fichier.read_text().replace("</body>", RELEVE + "</body>"))
    serveur = subprocess.Popen([sys.executable, "-m", "http.server", "--directory", str(dossier), str(port)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--blink-settings=preferredColorScheme=1",
                            "--window-size=1504,856", "--virtual-time-budget=12000", "--dump-dom",
                            f"http://localhost:{port}/{page}"], capture_output=True, text=True, timeout=120)
    finally:
        serveur.terminate()
        shutil.rmtree(dossier.parent, ignore_errors=True)
    m = re.search(r'<pre id="releve">(.*?)</pre>', r.stdout, re.S)
    return json.loads(html.unescape(m.group(1))) if m else {}


def main():
    avant, apres, *pages = sys.argv[1:]
    ecarts = 0
    for page in pages:
        a, b = releve(avant, page, 9701), releve(apres, page, 9702)
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
