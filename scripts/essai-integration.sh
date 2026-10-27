#!/bin/sh
# Essai de bout en bout, en local, de l'intégration du socle comme sous-module :
#   dépôt enseignant (site/socle = sous-module) -> publier-etudiant -> dépôt
#   étudiant -> site servi et testé comme le fait GitHub Pages.
# Vérifie aussi qu'une montée de version du socle ne change que le gitlink du
# dépôt enseignant, et qu'un clone sans sous-module initialisé échoue avec un
# message clair, au test comme à la publication.
# Chaque vérification échoue d'elle-même : le script sort en erreur au premier écart.
#
# Le socle monté ici est factice (quelques fichiers écrits ci-dessous) : il
# éprouve le mécanisme, pas le contenu du dépôt. L'étape 6 charge KaTeX depuis
# jsDelivr : elle demande le réseau.
#
# Usage : scripts/essai-integration.sh [chemin/vers/ocots-publication]
# Prérequis : git, python3, node 22+, npm, curl, publier-etudiant >= 1.2.0.
# Facultatif : Chrome ou Chromium (CHROME=… pour le désigner), sinon l'étape 6
# est ignorée. PORT=… change le port du serveur (8765 par défaut).
set -eu

# publier-etudiant commite lui-même : une identité, si le poste (ou la CI) n'en a pas.
export GIT_AUTHOR_NAME=${GIT_AUTHOR_NAME:-essai} GIT_AUTHOR_EMAIL=${GIT_AUTHOR_EMAIL:-essai@essai}
export GIT_COMMITTER_NAME=${GIT_COMMITTER_NAME:-essai} GIT_COMMITTER_EMAIL=${GIT_COMMITTER_EMAIL:-essai@essai}

PUBLICATION=${1:-$(dirname "$0")/../../ocots-publication}
PE="$PUBLICATION/bin/publier-etudiant"
[ -f "$PE" ] || { echo "publier-etudiant introuvable : $PE (passer le chemin d'ocots-publication en argument)" >&2; exit 1; }
if [ -z "${CHROME:-}" ]; then
  for c in google-chrome chromium chromium-browser; do
    CHROME=$(command -v "$c" || true)
    [ -n "$CHROME" ] && break
  done
  [ -n "$CHROME" ] || CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
fi
PORT=${PORT:-8765}
tmp=$(mktemp -d "${TMPDIR:-/tmp}/essai-socle.XXXXXX")
serveur=
nettoie() {
  if [ -n "$serveur" ]; then kill "$serveur" 2>/dev/null; wait "$serveur" 2>/dev/null || true; fi
  rm -rf "$tmp"
}
trap nettoie EXIT

g() { dir=$1; shift; git -C "$dir" -c user.name=essai -c user.email=essai@essai -c protocol.file.allow=always "$@"; }
etape() { printf '\n== %s\n' "$*"; }
echoue() { echo "ÉCHEC : $*" >&2; exit 1; }

version=$(python3 "$PE" --version | awk '{print $NF}')
python3 - "$version" <<'EOF'
import sys
v = tuple(int(x) for x in sys.argv[1].split("."))
sys.exit(0 if v >= (1, 2, 0) else "publier-etudiant >= 1.2.0 requis")
EOF
echo "publier-etudiant $version"

etape "1. Le socle factice : css, js, tests, et des outils à ne pas publier (tag v0.1.0)"
socle=$tmp/socle
mkdir -p "$socle/css" "$socle/js" "$socle/tests" "$socle/scripts" "$socle/docs" \
  "$socle/examples/minimal" "$socle/modeles" "$socle/.github/workflows"
git init -q -b main "$socle"
printf '{"private":true,"type":"module","scripts":{"test":"node --test"}}\n' > "$socle/package.json"
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
echo "outil du socle" > "$socle/scripts/outil.sh"
echo "note du socle" > "$socle/docs/note.md"
echo "exemple du socle" > "$socle/examples/minimal/index.html"
echo "modèle du socle" > "$socle/modeles/site.yml"
echo "workflow du socle" > "$socle/.github/workflows/site.yml"
g "$socle" add -A && g "$socle" commit -q -m "socle v0.1.0" && g "$socle" tag v0.1.0

etape "2. Dépôt enseignant : site/ avec le socle en sous-module"
ens=$tmp/ens
mkdir -p "$ens/site/js" "$ens/site/scripts"
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
# Un dossier scripts/ du cours lui-même : il doit, lui, être publié.
echo "outil du cours" > "$ens/site/scripts/outil.sh"
# Garde recommandée dans le package.json d'un cours (README) : sans sous-module
# initialisé, npm test le dit au lieu d'échouer sur un module introuvable.
cat > "$ens/site/package.json" <<'EOF'
{"private":true,"type":"module","scripts":{"pretest":"test -f socle/package.json || { echo 'Socle absent : git submodule update --init' >&2; exit 1; }","test":"node --test"}}
EOF
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
exclure = ["node_modules", ".DS_Store", "socle/scripts/*", "socle/docs/*",
  "socle/examples/*", "socle/.github/*"]
EOF
g "$ens" add -A && g "$ens" commit -q -m "cours"
echo "gitlink : $(g "$ens" ls-files --stage site/socle)"

etape "3. Clone enseignant sans sous-module : npm test le dit"
git clone -q "$ens" "$tmp/ens-clone"
if (cd "$tmp/ens-clone/site" && npm test >"$tmp/garde.log" 2>&1); then
  echoue "npm test passe alors que le socle n'est pas initialisé"
fi
grep -q "Socle absent : git submodule update --init" "$tmp/garde.log" || { cat "$tmp/garde.log"; echoue "message de la garde absent"; }
echo "ok : « Socle absent : git submodule update --init »"

etape "4. Dépôt étudiant (vide, avec origine)"
git init -q --bare -b main "$tmp/origin.git"
git clone -q "$tmp/origin.git" "$tmp/etu"
echo accueil > "$tmp/etu/README.md"
g "$tmp/etu" add -A && g "$tmp/etu" commit -q -m init && g "$tmp/etu" push -q origin HEAD:main

etape "5. Publier depuis le clone sans sous-module est refusé (sinon le miroir viderait site/socle/)"
if python3 "$PE" --config "$tmp/ens-clone/publication.toml" simuler >"$tmp/refus.log" 2>&1; then
  echoue "publier-etudiant accepte un sous-module non initialisé"
fi
grep -q "sous-module non initialisé" "$tmp/refus.log" || { cat "$tmp/refus.log"; echoue "refus sans le message attendu"; }
echo "ok : « sous-module non initialisé »"

etape "6. publier-etudiant simuler puis preparer"
python3 "$PE" --config "$ens/publication.toml" simuler | sed -n 1,12p
python3 "$PE" --config "$ens/publication.toml" preparer >/dev/null
etu=$tmp/etu-publication
for f in site/socle/package.json site/socle/js/accueil.js site/socle/css/theme.css site/socle/tests/socle.test.js \
  site/socle/modeles/site.yml site/index.html site/scripts/outil.sh; do
  test -f "$etu/$f" || echoue "manque côté étudiant : $f"
  echo "présent côté étudiant : $f"
done
for f in site/socle/.git .gitmodules site/socle/scripts site/socle/docs \
  site/socle/examples site/socle/.github; do
  test ! -e "$etu/$f" || echoue "publié à tort côté étudiant : $f"
  echo "absent côté étudiant : $f"
done

etape "7. Tests du dépôt étudiant (comme .github/workflows/site.yml : npm test dans site/)"
(cd "$etu/site" && npm test >"$tmp/tests.log" 2>&1) || { cat "$tmp/tests.log"; echoue "npm test côté étudiant"; }
grep -E "(tests|pass|fail) [0-9]+" "$tmp/tests.log"

etape "8. Site servi depuis le dépôt étudiant, vérifié dans un navigateur"
if [ -x "$CHROME" ]; then
  python3 -m http.server --directory "$etu/site" "$PORT" >/dev/null 2>&1 &
  serveur=$!
  i=0
  until curl -sf "http://localhost:$PORT/index.html" >/dev/null 2>&1; do
    kill -0 "$serveur" 2>/dev/null || echoue "le serveur n'a pas démarré (port $PORT occupé ? PORT=… pour en changer)"
    i=$((i + 1))
    [ "$i" -lt 50 ] || echoue "le serveur ne répond pas sur le port $PORT"
    sleep 0.1
  done
  dom=$("$CHROME" --headless=new --disable-gpu --virtual-time-budget=8000 --dump-dom "http://localhost:$PORT/index.html" 2>/dev/null)
  for motif in 'data-ok="1"' 'class="katex"' 'module du cours charge' 'Cours démo : explorer le cours'; do
    printf '%s' "$dom" | grep -q "$motif" || echoue "absent de la page : $motif"
    echo "ok : $motif"
  done
else
  echo "Chrome introuvable ($CHROME) : étape ignorée"
fi

etape "9. Montée de version du socle (v0.2.0 : un fichier modifié, un ajouté)"
echo "/* v0.2 */" >> "$socle/css/theme.css"
echo "export const nouveau = 1;" > "$socle/js/nouveau.js"
g "$socle" add -A && g "$socle" commit -q -m "socle v0.2.0" && g "$socle" tag v0.2.0
g "$ens/site/socle" fetch -q --tags origin
g "$ens/site/socle" checkout -q v0.2.0
g "$ens" add site/socle
[ "$(g "$ens" diff --cached --name-only)" = "site/socle" ] || echoue "la montée de version touche autre chose que le gitlink"
echo "ok : seul le gitlink change côté enseignant ; une copie vendorisée y ajouterait :"
g "$ens/site/socle" diff --stat v0.1.0 v0.2.0 | sed 's/^/  /'
g "$ens" commit -q -m "socle v0.2.0"

printf '\nEssai terminé : sous-module viable de bout en bout.\n'
