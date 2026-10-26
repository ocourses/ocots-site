<!-- LTeX: language=fr-FR -->

# Conception : modèle de configuration d'un site de cours

Suivi : ocourses/ocots-site#1 · Issue : ocourses/ocots-site#2

Ce document fixe la forme de `site.config.js`, le contrat d'un module
d'illustration et la frontière entre le socle (`ocots-site`) et un cours. Il
précède toute extraction de code. Les décisions prises sont à la fin
([Décisions](#décisions)).

## Principes

| Principe | Application |
|----------|-------------|
| DRY | Tout ce qui est identique dans les trois sites va dans le socle : le balisage d'`illustration.html`, `trouve`, le moteur du glossaire, la version de KaTeX, le test du catalogue. |
| KISS | Une configuration est un objet JS, sans schéma externe ni étape de build. Une fonction du socle valide sa forme. |
| YAGNI | Une clé n'existe que si au moins deux cours s'en servent. Un module du socle qu'un cours n'importe pas ne demande aucun drapeau. |
| Ouvert/fermé | Un cours étend le socle (modules d'illustrations, pages à lui, feuille `cours.css`) sans en modifier un fichier. |
| Inversion de dépendance | Le cours importe le socle et lui passe sa configuration. Le socle n'importe jamais un fichier du cours : il ne connaît que le contrat d'un module d'illustration. |
| Responsabilité unique | La configuration décrit un cours. Le code du socle anime les pages. |

## Relevé (sites au 2026-10-26)

Comparaison de `automatique` (A), `calcul-differentiel-edo` (C) et
`mesure-integration` (M).

- `illustration.html` : identique dans les trois.
- `index.html` : seuls diffèrent le titre, le sous-titre, le paragraphe
  d'introduction (un seul, sans formule ni balisage, dans les trois) et l'URL
  des issues. Le paragraphe de signalement est le même texte. A ajoute un
  `<template>` pour le simulateur.
- `js/accueil.js` : C et M sont identiques, au commentaire d'en-tête près
  (59 lignes). A fait 162 lignes : schéma de la boucle fermée et galerie du
  simulateur. L'écart de A est donc propre au simulateur, pas à l'accueil.
- `js/illustration.js` : A et C ne diffèrent que par le suffixe du titre et
  la clé de préférences. M ajoute le bouton « Réinitialiser » (commit
  `791511d`, « partout »). M est la version de référence. Le contrat d'un
  module (commentaire d'en-tête) et les `outils` passés à `monte` sont
  identiques dans les trois.
- `js/parcours.js` : A injecte les exemples du simulateur ; C et M sont
  identiques.
- `trouve()` de `catalogue.js` et `appliqueGlossaire()` de `glossaire.js` :
  identiques dans les trois. Seules les données diffèrent (thèmes, termes).
  Les trois cours ont un glossaire.
- Test « catalogue : identifiants uniques, modules présents pour les
  illustrations disponibles » : le même dans les trois cours
  (`illustrations.test.js` de A et C, `catalogue.test.js` de M).
- `js/ui/katex.js` : C a un traitement de la ponctuation collée à une formule
  que M n'a pas. La version de C est retenue à l'étape « presque identiques »
  (ocots-site#5, voir `CHANGELOG.md`).
- Les sites ont trois jours (premiers commits des 23 et 24 octobre 2026) : peu
  de préférences navigateur à préserver.

## Format : module JS

`site.config.js`, à la racine de `site/`, exporte par défaut un objet. JSON est
écarté : la configuration porte une fonction (`charge`) et importe des données
JS (`themes`, `glossaire`), qu'un JSON ne peut pas exprimer.

## Clés

Chaque clé est utilisée par les trois cours : toutes sont obligatoires. Un
défaut qu'aucun cours n'emploie serait un chemin de code jamais exercé. Seule
exception, `pagesDuTheme` (décision 15). Une clé inconnue est une faute (une faute
de frappe ne passe pas en silence).

| Clé | Type | Contrainte vérifiée | Rôle |
|-----|------|---------------------|------|
| `id` | chaîne | `^[a-z0-9-]+$` | Préfixe des clés de préférences (`<id>.illustration.<page>`), nom du paquet. |
| `titre` | chaîne | non vide | Titre de l'accueil (`<titre> : explorer le cours`) et suffixe du titre de chaque page (`<page> · <titre>`). |
| `sousTitre` | chaîne | non vide | Ligne sous le titre de l'accueil. |
| `intro` | tableau de chaînes | au moins une | Paragraphes d'introduction, rendus par `rendTexte` (typographie française ; formules `$…$` permises). |
| `depotIssues` | chaîne | `^[\w.-]+/[\w.-]+$` | Cible du paragraphe de signalement, rédigé une fois dans le socle. |
| `themes` | tableau | voir ci-dessous | Le catalogue : thèmes et illustrations (même forme qu'aujourd'hui). Le socle en déduit `trouve`. |
| `glossaire` | objet | chaque entrée a `formes` (non vide), `definition`, `source` | Termes du cours. Le moteur est dans le socle. |
| `charge` | `(id) => Promise<module>` | fonction | Charge le module d'une illustration. Un `import()` relatif ne sort pas du fichier où il est écrit : c'est le cours qui le fait. |
| `pagesDuTheme` | `(theme) => [{ genre, id, titre, lien }]` | fonction, **facultative** | Pages du cours insérées dans le parcours après les illustrations du thème (précédent/suivant, retour à la carte). Seul A s'en sert, pour le simulateur (décision 15). |

Forme de `themes` (inchangée) : `[{ id, titre, source, illustrations: [{ id,
titre, resume, source, disponible }] }]`. Les identifiants d'illustration sont
uniques dans tout le catalogue.

La clé de préférences `<id>.illustration.<page>` est construite à un seul
endroit, dans le module d'illustration du socle, jamais par l'appelant.

### Clés écartées

- `modules: { glossaire, vue3d, simulateur }` : un module ES n'est chargé que
  s'il est importé. Aucun drapeau.
- `katex` : la version est une constante du socle, dans un seul fichier.
- `clePreferences` : la clé suit `id` (décision 5).
- `extensions` (un objet de crochets) : seul `pagesDuTheme` est nécessaire ; voir
  [Points d'extension](#points-dextension).

## Validation

Le socle exporte deux fonctions, et chaque cours les appelle dans un test d'une
ligne.

- `valideConfig(config)` vérifie les clés et contraintes du tableau ci-dessus,
  sans rien charger. Elle lève **une** erreur qui liste **toutes** les fautes
  (clé manquante, type erroné, format, identifiant en double), pour qu'un
  cours mal configuré se corrige en une fois.
- `verifieCours(config)` appelle `valideConfig`, puis, pour chaque
  illustration `disponible` (et elles seules), charge son module par
  `config.charge` et vérifie le contrat ci-dessous : pas de clé inconnue,
  `monte` est une fonction, chaque réglage et chaque préférence d'un essai est
  une clé connue, **du même type** que sa valeur par défaut (sinon la page
  l'ignorerait en silence) et, pour un texte, permise par `choix`, chaque terme
  de `termes` est une entrée du glossaire. Elle vérifie enfin le parcours
  (pages ajoutées par `pagesDuTheme` bien formées, sans doublon). C'est le test
  aujourd'hui recopié dans les trois cours. Un module qui ne se charge pas est
  une faute nommée, pas une exception qui masque les autres.

Le code est dans `js/config.js` ; `fautesConfig` et `fautesCours` rendent la liste
des fautes sans lever.

```js
// tests/config.test.js d'un cours
import { test } from 'node:test';
import { verifieCours } from '../socle/js/config.js';
import config from '../site.config.js';

test('le cours respecte le contrat du socle', () => verifieCours(config));
```

## Contrat d'un module d'illustration

C'est le point d'extension principal : le socle n'appelle que ce qui suit. Le
contrat est celui des trois cours aujourd'hui, inchangé.

`js/illustrations/<id>.js` exporte par défaut un objet :

| Champ | Obligatoire | Rôle |
|-------|-------------|------|
| `monte(zone, outils)` | oui | Construit l'illustration dans `zone` et renvoie `{ applique(etat) }`, appelé par un essai et par « Réinitialiser ». |
| `etat` | non | Réglages par défaut (nombres, booléens, textes), gardés dans l'URL. |
| `choix` | non | Valeurs permises des réglages et préférences textuels, par exemple `{ forme: ['propres', 'compagnon'] }`. Une autre valeur lue est remplacée par le défaut. |
| `preferences` | non | Préférences d'affichage par défaut, gardées dans le navigateur. |
| `rappel` | non | Paragraphes du cours (texte avec formules `$…$`, ou `$$…$$` seul) ; un tableau de textes devient une liste à puces. |
| `essais` | non | `[{ texte, etat?, preferences? }]` ; avec `etat`, un bouton « Essayer » applique le réglage. |
| `termes` | non | Clés du glossaire employées par la page ; leur première occurrence est soulignée, avec la définition en infobulle. |

`outils`, fourni par le socle à `monte` :

| Outil | Rôle |
|-------|------|
| `etat` | Réglages courants (lus dans l'URL). |
| `change(partiel)` | Met à jour des réglages et l'URL. |
| `preferences` | Instance de `Preferences` : `valeurs`, `change(partiel)`. |
| `rend`, `rendTexte` | Rendu KaTeX. |
| `glossaire(element, cles)` | Souligne des termes dans un texte de l'illustration. |
| `mouvementReduit` | Préférence système « animations réduites ». |
| `surTheme(f)` | Rappel au changement de thème clair/sombre. |

Le module ne touche pas au DOM à l'import : `verifieCours` le charge sous Node,
sans navigateur.

## Disposition d'un cours

```
site/
  index.html          copie de socle/modeles/index.html
  illustration.html   copie de socle/modeles/illustration.html
  site.config.js
  css/cours.css       surcouche optionnelle
  js/illustrations/   modules du cours (+ catalogue.js, glossaire.js : données)
  socle/              sous-module ocots-site (css, js communs, tests communs)
  tests/              tests propres au cours
```

Les deux gabarits sont des modèles statiques complets du socle (décision 6,
révisée) : le balisage d'aujourd'hui (en-tête, fil d'Ariane, onglets), les liens
`socle/css/*.css` puis `css/cours.css`, un `<noscript>` qui dit que la page
demande JavaScript, et un module qui importe `site.config.js` et appelle
`demarreAccueil(config)` ou `demarreIllustration(config)`. Le JavaScript ne
remplit que les textes (titres, intro, signalement) à partir de la configuration.
Le cours copie les modèles, et un test du socle, exécuté dans le cours, vérifie
que ses gabarits leur sont identiques.

## KaTeX

Le chargement de KaTeX (CSS et script) est fait par le socle avant tout
rendu, depuis le CDN, comme aujourd'hui. La version **et** l'empreinte
(`integrity`, avec `crossorigin="anonymous"`) sont écrites une seule fois, dans
le chargeur : chargement reproductible, refusé si le fichier servi change. Le
chargeur ne fait rien si `window.katex` existe déjà.

Vérifié par un essai jetable (accueil minimal, Chrome sans interface) : le
module du cours est chargé, la formule rendue.

## Points d'extension

Un cours étend le socle de trois façons, sans modifier un fichier du socle :

1. **Illustrations** : ses modules `js/illustrations/<id>.js`, atteints par
   `charge` et conformes au [contrat](#contrat-dun-module-dillustration).
2. **Feuille de style** : `css/cours.css` redéfinit les variables de
   `theme.css` ou ajoute ses règles.
3. **Pages à lui** : une page HTML du cours qui importe librement les modules du
   socle (`ui/`, `format`, `katex`). Aucun registre de pages.

4. **Pages dans le parcours** : `pagesDuTheme(theme)` insère des pages du cours
   après les illustrations d'un thème (décision 15).
5. **Greffe sur l'accueil** : l'accueil produit une section `#theme-<id>` par
   thème ; cet identifiant fait partie du contrat. Un cours qui veut ajouter un
   bloc à un thème appelle `demarreAccueil(config)`, puis le greffe dans la section.

Rien d'autre n'est défini. Le simulateur d'A utilise 3, 4 et 5 : ses pages
(`exemple.html`) dans le parcours, son schéma et sa galerie greffés sur
`#theme-commande`. Son code reste dans A, et le mot « simulateur » n'apparaît pas
dans le socle.

## Stratégie de test

Le socle est copié tel quel dans chaque cours, et ses tests y tournent
(`npm test` dans `site/`, côté enseignant comme côté étudiant). Un test du socle
ne dépend donc d'aucun fichier d'un cours, sauf par la configuration que le
cours lui passe.

| Niveau | Quoi | Où |
|--------|------|----|
| Unitaire | Fonctions pures : `format`, `ode`, `preferences`, `graduations`, `Camera.tourne`, `valideConfig` (une configuration valide, puis une fausse par cas d'erreur). | `tests/` du socle |
| Avec doublures | Faux stockage, faux DOM minimal, faux contexte 2D espion (il enregistre les appels), faux `katex`. | `tests/aides/` du socle, partagés |
| Contrat | `verifieCours(config)` : configuration et chaque module d'illustration. | appelé par chaque cours |
| Contrat JS ↔ CSS | Toute variable lue par `theme.js` et toute classe posée par le JS du socle existe dans le CSS du socle. | `tests/` du socle |
| Non-régression entre cours | Les tests de chaque cours passent avec les fichiers du socle ; le script échoue sinon. | `scripts/verifie-cours.py` (ocots-site#5) |
| Bout en bout | Chaque page d'illustration s'ouvre sans erreur de console (Chrome sans interface) ; captures avant/après pour le rendu. | script, à la migration de chaque cours |

Les doublures sont écrites à la main, sans `jsdom` ni `linkedom`, tant qu'elles
restent petites : une dépendance npm obligerait le dépôt étudiant à faire
`npm ci` avant `npm test`.

## Exemples

```js
// mesure-integration
import { themes } from './js/illustrations/catalogue.js';
import { GLOSSAIRE } from './js/illustrations/glossaire.js';

export default {
  id: 'mesure-integration',
  titre: 'Mesure et intégration',
  sousTitre: 'Mesure et intégration, première année — ENSEEIHT, Sciences du numérique',
  intro: [
    'Des illustrations interactives du poly et des TD, rangées par chapitre dans l\'ordre du cours. Chacune rappelle le résultat du cours, propose des choses à essayer et garde ses réglages dans son lien : on choisit une fonction, un paramètre, une mesure, et l\'on regarde ce que devient l\'intégrale.',
  ],
  depotIssues: 'ocourses/mesure-integration',
  themes,
  glossaire: GLOSSAIRE,
  charge: (id) => import(`./js/illustrations/${id}.js`),
};
```

`calcul-differentiel-edo` : `id: 'calcul-differentiel-edo'`, `titre: 'Calcul
différentiel et EDO'`, `sousTitre: 'Calcul différentiel et équations
différentielles ordinaires — parcours ModIA, INP-ENSEEIHT et INSA Toulouse'`,
`depotIssues: 'ocourses/calcul-differentiel-edo'`.

`automatique` : `id: 'automatique'`, `titre: 'Automatique'`, `sousTitre:
'Automatique, première année — ENSEEIHT, Sciences du numérique'`,
`depotIssues: 'ocourses/automatique'`. Le simulateur reste dans le cours
jusqu'à la décision de ocourses/ocots-site#7.

## Décisions

Toutes du 2026-10-26, sauf mention contraire. Une décision qui change est
barrée, et la nouvelle est ajoutée en dessous avec sa date.

| # | Sujet | Décision | Raison |
|---|-------|----------|--------|
| 1 | Format de la configuration | Module JS, pas JSON. | La configuration porte une fonction (`charge`) et importe des données JS. `valideConfig` et `verifieCours` tiennent lieu de schéma. |
| 2 | Sens des dépendances | Le cours importe le socle, jamais l'inverse ; `charge`, `themes` et `glossaire` sont passés au socle. | Un `import()` relatif ne sort pas de son fichier : le socle ne peut pas charger `./illustrations/<id>.js` du cours. |
| 3 | `trouve()` et moteur du glossaire | Dans le socle. | Identiques (même empreinte) dans les trois sites ; seules les données diffèrent. |
| 4 | Version de référence d'`illustration.js` | M. | Seule à avoir « Réinitialiser » (`791511d`, « partout »). Les écarts A/C/M se réduisent au suffixe du titre et à la clé de préférences, qui deviennent `titre` et `id`. Le bouton vaut pour tous les cours, sans réglage. |
| 5 | Clés de préférences | Pas de `clePreferences` : la clé suit `id`. On accepte une remise à zéro unique des préférences d'affichage d'A et M. | Sites de trois jours. `Preferences` traite déjà une entrée absente comme un retour aux défauts : aucun code de migration. À signaler dans le `CHANGELOG` de la version qui migre chaque cours. |
| 6 | Gabarits HTML | ~~Pages minimales dans le cours, balisage produit par le socle, `<noscript>` ; gabarits fournis comme modèles par le socle et vérifiés par un test.~~ | ~~Un seul exemplaire du balisage, de KaTeX et des liens CSS.~~ |
| 6 (révisée le 2026-10-26, ocots-site#7) | Gabarits HTML | Modèles **statiques complets** dans le socle (`modeles/index.html`, `modeles/illustration.html` : le balisage d'aujourd'hui, liens `socle/…`, `<noscript>`), copiés dans le cours et vérifiés par un test d'égalité ; le JavaScript ne remplit que les textes. | `illustration.html` est déjà identique dans les trois cours, `index.html` ne diffère que par quatre textes de la configuration : le modèle suffit à n'avoir qu'un exemplaire. Produire le balisage par JavaScript n'apporterait rien et serait du code à écrire et tester (KISS, YAGNI). |
| 7 | KaTeX | Chargé par le socle depuis le CDN, version et empreinte SRI dans le chargeur. Vendorisé seulement si l'usage hors ligne devient un besoin. | Aucun changement de comportement ; le chargeur unique rend la vendorisation locale le jour venu. |
| 8 | Drapeaux `modules` | Aucun. | Un module ES inutilisé n'est pas chargé. |
| 9 | Clés `intro`, `glossaire` | Obligatoires. | Les trois cours ont une intro et un glossaire. |
| 10 | Emplacement du socle | Sous-module `site/socle/`. | Proposé en ocots-site#3 (PR #11). |
| 11 | Test du catalogue | `verifieCours(config)` dans le socle. | Le même test est recopié dans les trois cours. |
| 12 | Briques d'illustration | `js/briques/` dans le socle (`commun.js`, puis `plan-trace-det`, `portraits`). | La conception réserve `js/illustrations/` aux modules du cours, qui garde son propre `commun.js` : deux fichiers de même nom et de rôles différents seraient source de confusion. |
| 13 | Code sans test autonome (`dim2`) | Écrire des tests de caractérisation avant de le reprendre. | Le code est pur : figer ses sorties actuelles sur des cas typiques est peu coûteux, et c'est le filet de la migration. |
| 15 | Simulateur | Il reste dans `automatique`. Le socle lui offre `pagesDuTheme` (seule clé facultative) et la greffe sur `#theme-<id>` de l'accueil ; le drapeau `simulateur` sort du catalogue. | Un seul cours l'emploie, il fait plus de 2 500 lignes et dépend de uPlot : c'est un domaine, pas une brique. Sans `pagesDuTheme`, A garderait une copie divergente de `parcours.js` (ocots-site#7). |

Reportées : aucune. Le simulateur et le parcours sont tranchés par la décision 15.
