<!-- LTeX: language=fr-FR -->

# `ocots-site` : socle commun des sites interactifs des cours

Code, styles et gabarits partagés par les sites d'illustrations interactives des
cours (`automatique`, `calcul-differentiel-edo`, `mesure-integration`). Un cours
déclare ce qui le distingue dans `site.config.js` et étend le socle sans le forker.

Suivi du chantier : [#1](https://github.com/ocourses/ocots-site/issues/1).
Conception : [`docs/conception.md`](docs/conception.md).

## Intégrer le socle dans un cours

Option retenue : **sous-module épinglé sur un tag**, dans `site/socle/`. Une
copie vendorisée a le même effet côté étudiant, mais fait apparaître chaque
fichier changé dans les diffs du dépôt enseignant ; le sous-module n'y laisse
qu'une ligne (le gitlink).

```bash
git submodule add https://github.com/ocourses/ocots-site site/socle
git -C site/socle checkout vX.Y.Z
git add site/socle .gitmodules && git commit -m "feat(site): ajoute le socle ocots-site vX.Y.Z"
```

- **URL en HTTPS**, pas en SSH (le dépôt est public) : une CI ou un clone sans
  clé n'a rien à configurer.
- **Chemins** : les gabarits du cours importent `./socle/js/...` et lient
  `socle/css/...`. `serve.mjs` (du socle) et `node --test` (lancé dans `site/`)
  résolvent donc le socle comme le navigateur. Après un clone :
  `git submodule update --init`.
- **Garde** : dans le `package.json` du cours, un `pretest` dit clairement que
  le sous-module n'est pas initialisé, au lieu d'une erreur de module
  introuvable (une CI qui clone sans `submodules:` tombe sur ce cas) :

  ```json
  "pretest": "test -f socle/package.json || { echo 'Socle absent : git submodule update --init' >&2; exit 1; }"
  ```

- **Publication** : `ocots-publication` ≥ v1.2.0 copie les fichiers du
  sous-module dans le dépôt étudiant (ni `.git` ni `.gitmodules` ne sont
  copiés) ; le workflow du dépôt étudiant n'initialise donc rien. Chaque cours
  épingle son sous-module `publication/` à v1.2.0 ou plus. Les outils et la
  documentation du socle ne servent pas à l'étudiant : les exclure dans
  `publication.toml`, par leur chemin (un motif nu comme `scripts` exclurait
  aussi les dossiers du cours qui portent ce nom) :

  ```toml
  exclure = ["node_modules", ".DS_Store", "socle/scripts/*", "socle/docs/*"]
  ```

- **Tests** : `npm test` dans `site/` exécute aussi les tests du socle, qui
  sont publiés avec lui et tournent donc côté étudiant. Un test du socle ne
  doit dépendre d'aucun fichier du cours.
- **Montée de version** : `git -C site/socle checkout vX.Y.Z`, puis commit du
  gitlink, puis publication.

### Vérifier la chaîne

```bash
scripts/essai-integration.sh [chemin/vers/ocots-publication]
```

Le script monte, dans un répertoire temporaire, un socle factice, un dépôt
enseignant, un dépôt étudiant et son origine. Il vérifie, et échoue au premier
écart :

1. qu'un clone enseignant sans sous-module initialisé fait échouer `npm test`
   avec le message de la garde ;
   et que `publier-etudiant` refuse d'en publier (« sous-module non
   initialisé ») : sinon, le miroir viderait `site/socle/` du dépôt étudiant ;
2. que `publier-etudiant` copie les fichiers du sous-module, sans `.git`, sans
   `.gitmodules` ni les dossiers exclus du socle, mais avec les dossiers du
   cours de même nom ;
3. que `npm test` passe dans le dépôt étudiant ;
4. que le site servi s'affiche dans Chrome sans interface (module du cours
   chargé, KaTeX rendu ; étape ignorée sans Chrome, et qui demande le réseau) ;
5. qu'une montée de version du socle ne change que le gitlink du dépôt
   enseignant.

Rien ne touche GitHub. Le script ne couvre pas le déploiement GitHub Pages
lui-même : `site.yml` du dépôt étudiant publie `site/` tel quel
(`upload-pages-artifact`, `path: site`), sans sous-module à initialiser.

## Contenu du socle

Fichiers identiques dans les trois sites, repris tels quels (octet pour octet) :

- `css/theme.css` : la charte, en variables CSS ;
- `js/ui/{onglets,preferences,infobulle,theme}.js` ;
- `serve.mjs` : serveur de développement sans cache, qui sert le dossier courant.
  Dans un cours : `"serve": "node socle/serve.mjs"` (lancé depuis `site/`) ;
- `tests/preferences.test.js`.

Tests ajoutés au socle (les cours n'en avaient pas) :

- `tests/onglets.test.js`, `tests/infobulle.test.js` : onglet initial, clavier,
  mot souligné, ouverture et fermeture de la bulle ;
- `tests/theme.test.js` : contrat entre `theme.js` et `theme.css` (chaque
  variable lue est définie en clair et en sombre) ;
- `tests/aides/faux-dom.js` : faux DOM minimal, partagé par les tests, sans
  dépendance npm (les tests tournent aussi dans le dépôt étudiant).

Tests du socle seul : `npm test` (Node 22 ou plus). Serveur de développement :
`npm run serve`.

**`tests/` ne teste que ce qui est publié** (le code chargé par le navigateur) : il tourne aussi côté
étudiant, où `socle/scripts/*` est exclu de la publication. Les outils de `scripts/` se testent avec
les outils, en Python, à côté d'eux : `npm run test:outils`.

Fichiers fusionnés après divergence (voir `CHANGELOG.md`, par fichier et par cours) :
`js/ui/{katex,repere,format,controls,camera3d,vue3d}.js`,
`js/briques/` (cartes, contenu, canevas, interaction), `js/core/ode.js`.

Vérifier qu'une fusion ne casse aucun cours :

```bash
scripts/verifie-cours.py     # COURS=~/Courses par défaut ; code de sortie 1 en cas de régression
```

Le script pose les fichiers du socle sur une copie de chaque `site/`, remplace son
`commun.js` par une façade (briques du socle + code propre au cours, listé dans
`scripts/propre-aux-cours.json`), et rejoue les tests du cours. Il compare les **noms**
des tests réussis avant et après : un test manquant ou en échec fait échouer le script.

## CSS

Le socle fournit `css/theme.css` (la charte, en variables) et `css/style.css` (les composants).
Un cours lie `socle/css/theme.css`, `socle/css/style.css`, puis `css/cours.css` pour ce qui lui est
propre. Voir `docs/css.md`.

```bash
scripts/residu-css.py STYLE_DU_COURS.css --site DOSSIER_SITE > cours.css   # le reste d'un cours
scripts/residu-css.py STYLE_DU_COURS.css --nouveautes                       # ce que le socle lui apporte
scripts/site-apres.py DOSSIER_SITE SORTIE                                    # le cours avec le CSS du socle
scripts/captures.py prendre DOSSIER_SITE SORTIE [--tailles 1504x856 390x844]   # captures avant/après
scripts/captures.py comparer REFERENCE REFERENCE_BIS APRES
scripts/styles-calcules.py SITE_AVANT SITE_APRES [PAGE ...] [--tailles 1504x856 390x844 1504x600]   # le critère fiable
```

Les scripts de vérification partagent `scripts/navigateur.py` : Chrome sans interface (variable `CHROME`, sinon
`google-chrome`, `chromium`, puis le chemin de macOS) et `serve.mjs` du socle, sur un port libre et sans cache.
