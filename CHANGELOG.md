<!-- LTeX: language=fr-FR -->

# Journal des versions

Un cours **épingle une version** de ce dépôt (sous-module `site/socle/`).

---

## Non publié

### Chargement de KaTeX (ocots-site#7)

`chargeKatex()` dans `js/ui/katex.js` : KaTeX 0.16.11 (version inchangée)
depuis jsDelivr, avec empreintes SRI. **Migration** : les pages du cours
retirent leurs deux balises KaTeX (`<link>` et `<script>`) ; le démarrage des
pages du socle (étape suivante de ocots-site#7) attend `chargeKatex()` avant
tout rendu. Une page à soi (exemple.html d'A) l'appelle elle-même :
`await chargeKatex()`.

### Fichiers repris (étape 1)

`css/theme.css`, `js/ui/{onglets,preferences,infobulle,theme}.js`, `serve.mjs` :
identiques dans les trois cours, aucun changement de comportement.

### Fichiers fusionnés (étape 2)

Sens de la fusion : union des améliorations, après lecture des écarts.

| Fichier | Source retenue | Changements de comportement |
|---------|----------------|-----------------------------|
| `js/ui/katex.js` | C | **A, M** : la ponctuation qui suit une formule (`,` `.` `)` ` :`) reste collée à elle dans un `<span class="insecable">`. Demande la règle CSS `.insecable` (seulement dans C aujourd'hui, voir CSS). |
| `js/ui/repere.js` | M (A = C) | **A, C** : `axes()` accepte `ordonnees` et `dans` (défauts : comportement d'avant) ; une graduation trop proche du bord droit est alignée sur le bord au lieu d'être coupée. |
| `js/ui/format.js` | A + C + M | Ajouts seulement : `latexScientifique` (C) ; `chiffresEntiers`, `latexPositifFixe`, `latexNombreFinal`, `separateur`, `latexIntervalle` (M). |
| `js/ui/controls.js` | A + C + M | **A, M** : le nom accessible d'une étiquette KaTeX n'inclut plus la source LaTeX répétée. `ajoutePas` : option `lis` (C), bornes relues à chaque pas par `limites` (C) ou `min`/`max` (M). `champ` : `bornes(min, max)` (C) et `fixeMax(max)` (M). |
| `js/ui/camera3d.js` | A (= C) | Commentaire seul. |
| `js/ui/vue3d.js` | C | **A** : `zmin` (défaut 0, les valeurs sous 0 sont ramenées à 0), `facettes`, `dessineFacettes`, `surfaces` ; `surface(f, options)` s'utilise comme avant. Sans effet pour A : son seul usage, la surface de Lyapunov, trace des fonctions positives (l'ancienne projection supposait déjà [0, zmax]). Un domaine vide (`zmax ≤ zmin`) lève une `RangeError` au lieu de dessiner `NaN`. |
| `js/briques/` (`commun.js` d'avant) | A + C + M, moins le propre à un cours | Rangé dans `js/briques/` et découpé : `cartes.js`, `contenu.js`, `toile.js`, `interaction.js`, réunis par `commun.js` (`export *`). **A, C, M** : `boutonAide` (bulle d'aide d'une carte), `reinitialise()` du zoom, identifiant de `repliable` déterministe (`repliable-1`…). **Migration** : `paragraphe(parent, texte, 'verdict')` devient `verdict(parent, texte)` (zone de deux lignes `.zone-verdict`, seulement dans M aujourd'hui, voir CSS) : 3 appels dans A, 32 dans M, aucun dans C. |
| `js/ui/canevas.js` | nouveau | `ajusteCanevas`, extrait de `Repere.prepare` et `Vue3D.prepare` qui le dupliquaient. `graduations` renvoie `[]` pour un intervalle vide ou à l'envers (elle bouclait sur `NaN`). |
| `js/core/ode.js` | A (= C) | Aucun. |

### CSS (étape « CSS »)

`css/style.css` : la feuille de `mesure-integration` sans sa section propre, en neuf composants
(`base`, `entete`, `onglets`, `champs`, `petit-ecran`, `catalogue`, `illustration`, `accueil`,
`infobulle`) importés dans l'ordre d'origine. Chaque cours ajoute son `css/cours.css`
(`scripts/residu-css.py`). Détail : `docs/css.md`.

**A, C** : règles venues de M, absentes jusqu'ici : titre masqué dans les panneaux d'onglets,
formules centrées du rappel resserrées, `.zone-verdict` et `.hauteur-fixe`, `button.bouton-lien`,
espacement sous un canevas, `.entete-barre > div:first-child`. Les six règles qui divergeaient
(`.entete-actions`, `a.bouton-lien`, `.verdict`, `.legende-courbes`, `.barre-legende`,
`.texte-fixe`) gardent leur forme actuelle dans le `cours.css` d'A et C.

### Configuration et parcours (ocots-site#7)

Ajouts : `js/config.js` (`valideConfig`, `verifieCours`), `js/catalogue.js` (`trouve`, `disponibles`),
`js/parcours.js`. **Migration de chaque cours** :

- `trouve` et le parcours prennent leurs données en argument : `trouve(config.themes, id)`,
  `installeNavigation(parcours(config), genre, id)` (le `parcours.js` du cours disparaît) ;
- le test « catalogue : identifiants uniques, modules présents… » du cours est remplacé par
  `verifieCours(config)`, plus strict : une clé inconnue, ou un essai dont un réglage ou une préférence
  n'a pas le type de sa valeur par défaut, est une faute. Les trois cours passent tels quels ;
- **A** : le drapeau `simulateur: true` sort du catalogue (clé inconnue) ; ses pages d'exemples passent
  par `pagesDuTheme` dans `site.config.js`, et `app.js` appelle
  `installeNavigation(parcours(config), 'exemple', id)`.

### Pages (ocots-site#7)

Ajouts : `modeles/index.html`, `modeles/illustration.html` (gabarits complets, liens `socle/css/…`
puis `css/cours.css`, `<noscript>`, sans balise KaTeX) ; `js/accueil.js` (`demarreAccueil`),
`js/illustration.js` (`demarreIllustration`, `lisEtat`, `versRecherche`), `js/glossaire.js`
(`appliqueGlossaire(glossaire, racine, cles)`), `js/modeles.js` (`verifieModeles`).
Changements de comportement :

- **A, C** : « ↺ Réinitialiser » sur toute page qui a des réglages (décision 4, comme M) ;
- **A, C, M** : préférences sous `<id>.illustration.<page>` (`automatique.`, `calcul-differentiel-edo.`,
  `mesure-integration.`) : les préférences d'affichage d'A et M repartent des défauts, une fois
  (décision 5) ;
- **A, C, M** : le titre de l'accueil suit la typographie française (espace insécable avant « : ») ;
  le premier changement de réglage est écrit dans l'URL tout de suite, même dans les 200 premières
  millisecondes de la page.

**Migration de chaque cours** :

- copier les deux modèles à la racine de `site/` ; ajouter le test
  `verifieModeles(new URL('../', import.meta.url))` ;
- supprimer `js/accueil.js`, `js/illustration.js`, `js/parcours.js`, `trouve` et `appliqueGlossaire`
  (le glossaire du cours ne garde que ses données) ; les tests de `lisEtat` et `versRecherche` (M)
  passent dans le socle ;
- **A** : garde son `index.html` (le modèle, plus le `<template>` du schéma et un module qui greffe le
  schéma et la galerie sur `#theme-commande` après `await demarreAccueil(config)`) et vérifie
  seulement `['illustration.html']`.

### Restent dans le cours (un seul usage)

Ils vivent dans le `js/illustrations/commun.js` **du cours**, devenu une façade (`export * from '../briques/commun.js'` suivi du code propre) : les modules d'illustration gardent `import … from './commun.js'`. `scripts/propre-aux-cours.json` liste ce code, et `scripts/verifie-cours.py` génère cette façade.

- `automatique` : `simule` (RK4 sur une trajectoire, importe `core/ode.js`). `calcul-differentiel-edo` en a une copie sans appelant : à supprimer.
- `calcul-differentiel-edo` : `champsPoint` (deux champs pour un point glissé).
- `mesure-integration` : `choisitIndice`, `echelleLog`, `axesLog`, `choixEchelle`.

### Reporté

- `js/core/dim2.js`, `js/illustrations/{plan-trace-det,portraits}.js` : sans test autonome (`dim2`), ou dépendants de la décision sur les briques d'illustration.
