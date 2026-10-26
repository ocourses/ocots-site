<!-- LTeX: language=fr-FR -->

# Conception : modèle de configuration d'un site de cours

Suivi : ocourses/ocots-site#1 · Issue : ocourses/ocots-site#2

Ce document fixe la forme de `site.config.js` et la frontière entre le socle
(`ocots-site`) et un cours. Il précède toute extraction de code.

## Principes

| Principe | Application |
|----------|-------------|
| DRY | Tout ce qui est identique dans les trois sites va dans le socle : `illustration.html`, `trouve`, le moteur du glossaire, la version de KaTeX. |
| KISS | Une configuration est un objet JS, sans schéma externe ni étape de build. Un test valide sa forme. |
| YAGNI | Une clé n'existe que si au moins deux cours s'en servent. Un module du socle qu'un cours n'importe pas ne demande aucun drapeau. |
| Ouvert/fermé | Un cours étend le socle (modules d'illustrations, pages à lui, feuille `cours.css`) sans en modifier un fichier. |
| Inversion de dépendance | Le cours importe le socle et lui passe sa configuration. Le socle n'importe jamais un fichier du cours. |
| Responsabilité unique | La configuration décrit un cours. Le code du socle anime les pages. |

## Relevé (sites au 2026-10-26)

Comparaison de `automatique` (A), `calcul-differentiel-edo` (C) et
`mesure-integration` (M).

- `illustration.html` : identique dans les trois.
- `index.html` : seuls diffèrent le titre, le sous-titre, le paragraphe
  d'introduction et l'URL des issues. Le paragraphe de signalement est le même
  texte. A ajoute un `<template>` pour le simulateur.
- `js/accueil.js` : C et M sont identiques, au commentaire d'en-tête près
  (59 lignes). A fait 162 lignes : schéma de la boucle fermée et galerie du
  simulateur. L'écart de A est donc propre au simulateur, pas à l'accueil.
- `js/illustration.js` : A et C ne diffèrent que par le suffixe du titre et
  la clé de préférences. M ajoute le bouton « Réinitialiser » (commit
  `791511d`, « partout »). M est la version de référence.
- `js/parcours.js` : A injecte les exemples du simulateur ; C et M sont
  identiques.
- `trouve()` de `catalogue.js` et `appliqueGlossaire()` de `glossaire.js` :
  identiques dans les trois. Seules les données diffèrent (thèmes, termes).
- `js/ui/katex.js` : C a un traitement de la ponctuation collée à une formule
  que M n'a pas. Cas pour l'étape « presque identiques » (ocots-site#5).
- Les sites ont trois jours (premiers commits des 23 et 24 octobre 2026) : peu
  de préférences navigateur à préserver.

## Format : module JS

`site.config.js`, à la racine de `site/`, exporte par défaut un objet. JSON est
écarté : la configuration porte une fonction (`charge`) et importe des données
JS (`themes`, `glossaire`), qu'un JSON ne peut pas exprimer.

## Clés

Chaque clé est utilisée par les trois cours.

| Clé | Type | Défaut | Rôle |
|-----|------|--------|------|
| `id` | chaîne, identifiant | obligatoire | Préfixe des clés de préférences (`<id>.illustration.<page>`), nom du paquet. |
| `titre` | chaîne | obligatoire | Titre de l'accueil (`<titre> : explorer le cours`) et suffixe du titre de chaque page (`<page> · <titre>`). |
| `sousTitre` | chaîne | obligatoire | Ligne sous le titre de l'accueil. |
| `intro` | tableau de chaînes | `[]` | Paragraphes d'introduction, en texte brut. |
| `depotIssues` | chaîne `org/depot` | obligatoire | Cible du paragraphe de signalement, rédigé une fois dans le socle. |
| `themes` | tableau | obligatoire | Le catalogue : thèmes et illustrations (même forme qu'aujourd'hui). Le socle en déduit `trouve`. |
| `glossaire` | objet | `{}` | Termes du cours. Le moteur est dans le socle. |
| `charge` | `(id) => Promise<module>` | obligatoire | Charge le module d'une illustration. Un `import()` relatif ne sort pas du fichier où il est écrit : c'est le cours qui le fait. |

Le socle exporte `valideConfig(config)` : elle lève une erreur claire
(clés manquantes, type erroné) et chaque cours l'appelle dans un test.

### Clés écartées

- `modules: { glossaire, vue3d, simulateur }` : un module ES n'est chargé que
  s'il est importé. Aucun drapeau.
- `katex` : la version est une constante du socle, dans un seul fichier.
- `clePreferences` : voir la question ouverte 5.
- `extensions` : un seul cours (A) en a besoin ; voir ci-dessous.

## Disposition d'un cours

```
site/
  index.html          gabarit minimal (~10 lignes)
  illustration.html   gabarit minimal
  site.config.js
  css/cours.css       surcouche optionnelle
  js/illustrations/   modules du cours (+ catalogue.js, glossaire.js : données)
  socle/              sous-module ocots-site (css, js communs, tests communs)
  tests/              tests propres au cours
```

Un gabarit HTML du cours tient en quelques lignes : liens `socle/css/*.css`,
`css/cours.css`, un module qui importe `site.config.js` et appelle
`demarreAccueil(config)` ou `demarreIllustration(config)`. Le balisage de
`illustration.html` (onglets, fil d'Ariane) est dans le socle, produit par JS.
Titres et textes de l'accueil viennent de la configuration.

Le chargement de KaTeX (CSS et script) est fait par le socle avant tout
rendu : la version n'est écrite qu'une fois. Vérifié par un essai jetable
(accueil minimal, Chrome sans interface) : le module du cours est chargé, la
formule rendue.

## Points d'extension

Un cours étend le socle de trois façons, sans modifier un fichier du socle :

1. **Illustrations** : ses modules `js/illustrations/<id>.js`, atteints par `charge`.
2. **Feuille de style** : `css/cours.css` redéfinit les variables de
   `theme.css` ou ajoute ses règles.
3. **Pages à lui** : une page HTML du cours qui importe librement les modules du
   socle (`ui/`, `format`, `katex`). Aucun registre de pages.

Rien d'autre n'est défini. Le simulateur d'A a besoin de deux choses de plus
(des pages dans le parcours, un bloc dans l'accueil) : leur forme est le sujet
de ocourses/ocots-site#7, quand le relevé de `core/` et `ui/panneaux` sera fait.
Inventer maintenant un mécanisme à un seul usage serait spéculatif.

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

## Questions ouvertes et choix

Voir le commentaire de la pull request.
