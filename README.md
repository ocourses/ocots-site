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
- **Publication** : `ocots-publication` ≥ v1.2.0 copie les fichiers du
  sous-module dans le dépôt étudiant (ni `.git` ni `.gitmodules` ne sont
  copiés). Le workflow du dépôt étudiant n'initialise donc rien. Les épingler
  à `publication/` ≥ v1.2.0 dans chaque cours.
- **Tests** : `npm test` dans `site/` exécute aussi les tests du socle, qui
  sont copiés avec lui. Un test du socle ne doit dépendre d'aucun fichier du cours.
- **Montée de version** : `git -C site/socle checkout vX.Y.Z`, puis commit du
  gitlink, puis publication.

### Vérifier la chaîne

```bash
scripts/essai-integration.sh [chemin/vers/ocots-publication]
```

Le script monte, dans un répertoire temporaire, un socle, un dépôt enseignant,
un dépôt étudiant et son origine, publie avec `publier-etudiant`, lance
`npm test` dans le dépôt étudiant, sert le site et le vérifie dans Chrome sans
interface (module du cours chargé, KaTeX rendu). Rien ne touche GitHub.

Il ne couvre pas le déploiement GitHub Pages lui-même : `site.yml` du dépôt
étudiant publie `site/` tel quel (`upload-pages-artifact`, `path: site`), sans
sous-module à initialiser.
