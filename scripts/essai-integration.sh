#!/bin/sh
# Essai de bout en bout, en local, de l'intégration du socle comme sous-module :
#   dépôt enseignant (site/socle = sous-module) -> publier-etudiant -> dépôt
#   étudiant -> site servi et testé comme le fait GitHub Pages.
# Mesure aussi le coût d'une montée de version : sous-module contre copie.
#
# Usage : scripts/essai-integration.sh [chemin/vers/ocots-publication]
# Prérequis : git, python3, node 22+, publier-etudiant >= 1.2.0.
# Facultatif : Google Chrome (vérification dans un navigateur).
set -eu

PUBLICATION=${1:-$(cd "$(dirname "$0")/../../ocots-publication" && pwd)}
CHROME=${CHROME:-"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}
PORT=${PORT:-8765}
PE="$PUBLICATION/bin/publier-etudiant"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/essai-socle.XXXXXX")
serveur=
nettoie() { [ -n "$serveur" ] && kill "$serveur" 2>/dev/null; rm -rf "$tmp"; }
trap nettoie EXIT

g() { dir=$1; shift; git -C "$dir" -c user.name=essai -c user.email=essai@essai -c protocol.file.allow=always "$@"; }
etape() { printf '\n== %s\n' "$*"; }

version=$(python3 "$PE" --version | awk '{print $NF}')
python3 - "$version" <<'EOF'
import sys
v = tuple(int(x) for x in sys.argv[1].split("."))
sys.exit(0 if v >= (1, 2, 0) else "publier-etudiant >= 1.2.0 requis")
EOF
echo "publier-etudiant $version"

etape "1. Le socle : un dépôt avec css, js, tests (tag v0.1.0)"
socle=$tmp/socle
mkdir -p "$socle/css" "$socle/js" "$socle/tests"
git init -q -b main "$socle"
cat > "$socle/css/theme.css" <<'EOF'
:root { --fond: #fff; }
EOF
cat > "$socle/js/katex-chargeur.js" <<'EOF'
const VERSION = '0.16.11';
const BASE = `https://cdn.jsdelivr.net/npm/katex@${VERSION}/dist`;
export function chargeKatex() {
  if (window.katex) return Promise.resolve();
  const css = document.createElement('link');
  css.rel = 'stylesheet';
  css.href = `${BASE}/katex.min.css`;
  document.head.appendChild(css);
  return new Promise((ok, ko) => {
    const s = document.createElement('script');
    s.src = `${BASE}/katex.min.js`;
    s.onload = ok;
    s.onerror = () => ko(new Error('KaTeX indisponible'));
    document.head.appendChild(s);
  });
}
EOF
cat > "$socle/js/accueil.js" <<'EOF'
import { chargeKatex } from './katex-chargeur.js';
export async function demarre(config) {
  await chargeKatex();
  document.title = `${config.titre} : explorer le cours`;
  document.getElementById('h').textContent = config.titre;
  const formule = document.createElement('span');
  window.katex.render('\\int_E f\\,d\\mu', formule);
  document.body.appendChild(formule);
  const m = await config.charge('demo');
  document.getElementById('d').textContent = m.default.texte;
}
EOF
cat > "$socle/tests/socle.test.js" <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
test('le socle a ses tests', () => assert.equal(1 + 1, 2));
EOF
g "$socle" add -A && g "$socle" commit -q -m "socle v0.1.0" && g "$socle" tag v0.1.0

etape "2. Dépôt enseignant : site/ avec le socle en sous-module"
ens=$tmp/ens
mkdir -p "$ens/site/js"
git init -q -b main "$ens"
cat > "$ens/site/index.html" <<'EOF'
<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>x</title>
<link rel="stylesheet" href="socle/css/theme.css">
<script type="module">
import config from './site.config.js';
import { demarre } from './socle/js/accueil.js';
await demarre(config);
document.body.dataset.ok = '1';
</script></head><body><h1 id="h"></h1><p id="d"></p></body></html>
EOF
echo "export default { id: 'demo', titre: 'Cours démo', charge: (id) => import(\`./js/\${id}.js\`) };" > "$ens/site/site.config.js"
echo "export default { texte: 'module du cours charge' };" > "$ens/site/js/demo.js"
printf '{"private":true,"type":"module","scripts":{"test":"node --test"}}\n' > "$ens/site/package.json"
g "$ens" submodule add -q "$socle" site/socle
g "$ens/site/socle" checkout -q v0.1.0
cat > "$ens/publication.toml" <<EOF
[depot]
chemin = "$tmp/etu"
worktree = "$tmp/etu-publication"

[[dossier]]
source = "site"
cible = "site"
miroir = true
exclure = ["node_modules", ".DS_Store"]
EOF
g "$ens" add -A && g "$ens" commit -q -m "cours"
echo "gitlink : $(g "$ens" ls-files --stage site/socle)"

etape "3. Dépôt étudiant (vide, avec origine)"
git init -q --bare -b main "$tmp/origin.git"
git clone -q "$tmp/origin.git" "$tmp/etu"
echo accueil > "$tmp/etu/README.md"
g "$tmp/etu" add -A && g "$tmp/etu" commit -q -m init && g "$tmp/etu" push -q origin HEAD:main

etape "4. publier-etudiant simuler puis preparer"
python3 "$PE" --config "$ens/publication.toml" simuler | sed -n 1,12p
python3 "$PE" --config "$ens/publication.toml" preparer >/dev/null
etu=$tmp/etu-publication
for f in site/socle/js/accueil.js site/socle/css/theme.css site/socle/tests/socle.test.js site/index.html; do
  test -f "$etu/$f" && echo "présent côté étudiant : $f" || { echo "MANQUE côté étudiant : $f"; exit 1; }
done
test ! -e "$etu/site/socle/.git" || { echo "le .git du sous-module a été copié"; exit 1; }
test ! -e "$etu/.gitmodules" || { echo ".gitmodules copié côté étudiant"; exit 1; }
echo "pas de .git ni de .gitmodules côté étudiant : le workflow Pages n'a rien à initialiser"

etape "5. Tests du dépôt étudiant (comme .github/workflows/site.yml : npm test dans site/)"
(cd "$etu/site" && node --test >"$tmp/tests.log" 2>&1) || { cat "$tmp/tests.log"; exit 1; }
grep -E "(tests|pass|fail) [0-9]+" "$tmp/tests.log"

etape "6. Site servi depuis le dépôt étudiant, vérifié dans un navigateur"
if [ -x "$CHROME" ]; then
  python3 -m http.server --directory "$etu/site" "$PORT" >/dev/null 2>&1 &
  serveur=$!
  sleep 1
  dom=$("$CHROME" --headless=new --disable-gpu --virtual-time-budget=8000 --dump-dom "http://localhost:$PORT/index.html" 2>/dev/null)
  for motif in 'data-ok="1"' 'class="katex"' 'module du cours charge' 'Cours démo : explorer le cours'; do
    printf '%s' "$dom" | grep -q "$motif" && echo "ok : $motif" || { echo "ABSENT : $motif"; exit 1; }
  done
else
  echo "Chrome introuvable ($CHROME) : étape ignorée"
fi

etape "7. Montée de version du socle (v0.2.0 : un fichier modifié, un ajouté)"
echo "/* v0.2 */" >> "$socle/css/theme.css"
echo "export const nouveau = 1;" > "$socle/js/nouveau.js"
g "$socle" add -A && g "$socle" commit -q -m "socle v0.2.0" && g "$socle" tag v0.2.0
g "$ens/site/socle" fetch -q --tags origin
g "$ens/site/socle" checkout -q v0.2.0
g "$ens" add site/socle
echo "Diff côté enseignant (sous-module) :"
g "$ens" diff --cached --stat | sed 's/^/  /'
g "$ens" commit -q -m "socle v0.2.0"
echo "Copie vendorisée : le diff du dépôt enseignant contiendrait ces fichiers, pas une ligne :"
g "$ens/site/socle" diff --stat v0.1.0 v0.2.0 | sed 's/^/  /'
echo "Côté étudiant, l'une et l'autre option donnent les mêmes fichiers ordinaires."

printf '\nEssai terminé : sous-module viable de bout en bout.\n'
