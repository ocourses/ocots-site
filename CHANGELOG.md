<!-- LTeX: language=fr-FR -->

# Journal des versions

Un cours **épingle une version** de ce dépôt (sous-module `site/socle/`).

---

## Non publié

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
| `js/ui/vue3d.js` | C | **A** : `zmin` (défaut 0, les valeurs sous 0 sont ramenées à 0), `facettes`, `dessineFacettes`, `surfaces` ; `surface(f, options)` s'utilise comme avant. À vérifier sur la surface de Lyapunov. |
| `js/illustrations/commun.js` | A + C + M, moins le propre à un cours | **A, C, M** : `boutonAide` (bulle d'aide d'une carte), `reinitialise()` du zoom. **A, C** : la zone d'un verdict réserve deux lignes (`.zone-verdict`, seulement dans M aujourd'hui, voir CSS). |
| `js/core/ode.js` | A (= C) | Aucun. |

### Restent dans le cours (un seul usage)

- `automatique` : `simule` (RK4 sur une trajectoire, importe `core/ode.js`). `calcul-differentiel-edo` en a une copie sans appelant : à supprimer.
- `calcul-differentiel-edo` : `champsPoint` (deux champs pour un point glissé).
- `mesure-integration` : `choisitIndice`, `echelleLog`, `axesLog`, `choixEchelle`.

### Reporté

- `js/illustration.js` : relève de la configuration (#7).
- `js/core/dim2.js`, `js/illustrations/{plan-trace-det,portraits}.js` : sans test autonome (`dim2`), ou dépendants de la décision sur les briques d'illustration.
- `illustration.html` : voir la conception.
