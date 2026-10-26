<!-- LTeX: language=fr-FR -->

# CSS : socle et surcouche par cours

Suivi : ocourses/ocots-site#1 · Issue : ocourses/ocots-site#6

## Relevé (feuilles `css/style.css` au 2026-10-26)

| Cours | Lignes | Règles (contexte + sélecteur) |
|-------|--------|-------------------------------|
| automatique (A) | 2303 | 389 |
| calcul-differentiel-edo (C) | 2422 | 413 |
| mesure-integration (M) | 1227 | 194 |

- **A est un sous-ensemble de C**, règle pour règle : aucune règle d'A n'est absente de C.
  `theme.css` est identique dans les trois.
- 168 règles sont identiques dans les trois sites ; 215 le sont dans A et C seulement.
- Sur ces 215, environ 120 ne servent qu'au simulateur d'A (`.app`, `.console`,
  `.mesures`, `#plan`, `#schema`…) : C les embarque sans les employer (CSS mort).
- 6 règles partagées ont des déclarations différentes (`.entete-actions`, `a.bouton-lien`,
  `.verdict`, `.legende-courbes`, `.barre-legende`, `.texte-fixe`) : M a la version récente.
- M se présente lui-même (en-tête de sa dernière section) comme la feuille d'A sans les règles
  du simulateur, plus une section « Mesure et intégration » de règles propres.

## Choix : M sert de socle

`css/style.css` du socle est la feuille de M **sans sa section propre au cours**, coupée en
composants aux bannières qu'elle contient déjà. La concaténation des composants redonne les
970 lignes d'origine (hors lignes vides) : aucune règle n'est réécrite.

| Fichier | Contenu |
|---------|---------|
| `base.css` | remise à zéro, corps, titres, liens |
| `entete.css` | en-tête, fil d'Ariane, boutons d'en-tête |
| `onglets.css` | boîtes à onglets |
| `champs.css` | curseurs, saisies, cases, choix |
| `petit-ecran.css` | adaptations de petit écran |
| `catalogue.css` | cartes du catalogue |
| `illustration.css` | gabarit des pages d'illustration (le plus gros) |
| `accueil.css` | carte du cours |
| `infobulle.css` | infobulles, bloc repliable, zoom, bouton « i » |
| `style.css` | les `@import` ci-dessus, dans l'ordre de la cascade |

Un cours lie `socle/css/theme.css`, `socle/css/style.css`, puis son `css/cours.css`.

## `css/cours.css` : le reste, calculé

`scripts/residu-css.py STYLE.css [--site DOSSIER]` produit, pour un cours, la feuille à garder :

1. les blocs que le socle ne contient pas à l'identique, dans leur ordre d'origine
   (règles propres, et règles dont les déclarations diffèrent : elles passent après le socle) ;
2. avec `--site`, sans les blocs dont aucun sélecteur ne peut servir (classe ou identifiant que
   ni le HTML ni les chaînes JavaScript du site n'emploient) : listés comme « morts » ;
3. en fin de feuille, `revert` pour les propriétés que le socle règle sur un sélecteur du
   cours sans que le cours les règle : le cours garde son apparence.

`--nouveautes` liste à part les règles du socle dont le sélecteur n'existe pas dans le cours :
c'est le comportement que le cours **gagne**, à relire avant de migrer.

Résultat : M 9 blocs (66 lignes), C 74 blocs (le reste du simulateur y est écarté : 147 blocs
morts), A 193 blocs (le simulateur ; 5 blocs morts).

### Règles que le socle ajoute à A et C

`.carte-onglets [role='tabpanel'] > h2` (le titre du panneau, redondant avec l'onglet, est masqué),
`.entete-barre > div:first-child`, `.rappel .katex-display`, `.rappel p:has(> .katex-display)`,
`.zone-verdict`, `.hauteur-fixe` (deux règles de média), `button.bouton-lien` (et `:hover`),
`canvas.toile + :is(.bloc-maths, .texte-fixe, .barre-legende, .note)`. Elles viennent de M.

## Vérification visuelle

`scripts/captures.py` prend une capture de chaque page (accueil, illustrations et exemples
disponibles) à 1504 × 856, thème clair forcé, avant et après, et compte les pixels différents
au-delà du bruit mesuré entre deux prises de la référence.

Résultats (22, 19 et 19 pages) :

| Cours | Socle complet | Socle sans les règles nouvelles pour le cours |
|-------|---------------|-----------------------------------------------|
| M | **22 / 22** identiques | (sans objet : il les a toutes) |
| C | 1 / 19 | **18 / 19** (reste : `pendule`, 1 114 px, animation) |
| A | 5 / 19 | **13 / 19** (restent : 4 exemples du simulateur et `lyapunov`, de l'ordre du bruit ; `pendule-amorti`, voir ci-dessous) |

- **M reproduit exactement l'existant** : le socle plus son `cours.css` redonnent les pages
  pixel pour pixel. C'est la preuve que le découpage et le calcul du reste ne perdent rien.
- **« Socle complet » diffère pour A et C**, comme prévu : c'est l'effet des règles que M leur
  apporte (titre de panneau masqué, formules du rappel resserrées…). La colonne de droite
  neutralise ces seules règles (copie du socle sans elles) pour isoler le reste : les pages
  d'A et C redeviennent identiques, à quelques animations près.
- **`pendule-amorti` (A), 12 419 px, stable d'une prise à l'autre** : `scripts/styles-calcules.py`
  montre pourtant des styles calculés **identiques** pour chaque élément (comme pour `lyapunov`, le
  segway, `picard`, les accueils d'A et de C). La différence vient donc du dessin d'un canevas
  (moment du dessin, avec le chargement par `@import`), pas de la feuille de style. À rejouer à la
  migration d'A, dans un navigateur.
- Deux défauts trouvés et corrigés grâce à ces vérifications : un « ; » dans un commentaire CSS
  faisait perdre la règle qui suivait ; `unset` écrasait le `cursor: pointer` des liens (le
  navigateur le donne aux `a`), d'où `revert`.

## Limites

- Fenêtre unique : 1504 × 856. Les conditions fines (`:has`, hauteur de fenêtre, mobile) ne
  sont pas rejouées ; à faire à la migration de chaque cours.
- L'élagage du CSS mort lit des chaînes littérales : un nom de classe construit autrement serait
  jugé mort à tort. La liste des blocs écartés est affichée pour relecture.
- Le CSS mort restant est conservé quand un seul de ses sélecteurs peut servir.
- La remise à `revert` suppose qu'aucune autre règle du cours ne règle la même propriété sur le
  même élément.
- Les captures contiennent un peu de bruit (animations, particules) : une page est signalée
  au-delà de ce bruit plus 20 pixels.
