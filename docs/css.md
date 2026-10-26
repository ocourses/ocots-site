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

Décision (relecture) : **adoptées pour tous**, sans réglage. M est la version la plus récente et ce sont des
améliorations, pas des variantes ; le titre de panneau masqué l'est visuellement mais reste lu par les
lecteurs d'écran. `scripts/residu-css.py --nouveautes` en donne la liste ; elle va dans la PR de migration
de chaque cours, avec les captures avant/après, pour que l'enseignant voie ce qui change.

`.carte-onglets [role='tabpanel'] > h2` (le titre du panneau, redondant avec l'onglet, est masqué),
`.entete-barre > div:first-child`, `.rappel .katex-display`, `.rappel p:has(> .katex-display)`,
`.zone-verdict`, `.hauteur-fixe` (deux règles de média), `button.bouton-lien` (et `:hover`),
`canvas.toile + :is(.bloc-maths, .texte-fixe, .barre-legende, .note)`. Elles viennent de M. Pour A s'ajoute
`.insecable` (`white-space: nowrap`, de C), que le `katex.js` du socle a besoin de voir défini.

## Vérification visuelle

`scripts/captures.py` prend une capture de chaque page (accueil, illustrations et exemples
disponibles) à 1504 × 856, thème clair forcé, avant et après, et compte les pixels différents
au-delà du bruit mesuré entre deux prises de la référence.

Résultats (22, 19 et 19 pages ; serveur `serve.mjs` du socle, sans cache) :

| Cours | Socle complet | Socle sans les règles nouvelles pour le cours |
|-------|---------------|-----------------------------------------------|
| M | **21 / 22** (22 / 22 à d'autres prises, voir ci-dessous) | (sans objet : il les a toutes) |
| C | 1 / 19 | **17 / 19** (restent : `cauchy`, 144 px, et `pendule`, une animation) |
| A | 4 / 19 | **17 / 19** (restent : deux exemples du simulateur, animés) |

- **M reproduit l'existant** : le socle plus son `cours.css` redonnent les pages, sans écart de style
  calculé pour chaque élément des pages examinées. La page qui diffère change d'une prise à l'autre.
- **Les captures ne sont pas reproductibles à 100 %**, même sans rien changer : deux prises de la
  même feuille « après » diffèrent sur `convergence-dominee` et `etagees` (autres pages à une autre
  prise), et il en va de même avec les composants **concaténés en un seul fichier** (sans `@import`).
  Le dessin d'un canevas dépend du moment où il est redessiné (`ResizeObserver`), pas de la feuille de
  style. D'où le second critère : `scripts/styles-calcules.py`, qui compare les styles calculés
  de chaque élément et donne le même verdict à chaque fois (0 élément différent sur `picard`,
  `lyapunov`, le segway, `pendule-amorti`, `convergence-dominee` et les accueils d'A et C).
- **« Socle complet » diffère pour A et C**, comme prévu : c'est l'effet des règles que M leur
  apporte (titre de panneau masqué, formules du rappel resserrées…). La colonne de droite
  neutralise ces seules règles (copie du socle sans elles) pour isoler le reste : les pages
  d'A et C redeviennent identiques, à quelques animations près.
- Deux défauts trouvés et corrigés grâce à ces vérifications : un « ; » dans un commentaire CSS
  faisait perdre la règle qui suivait ; `unset` écrasait le `cursor: pointer` des liens (le
  navigateur le donne aux `a`), d'où `revert`.

### Trois tailles de fenêtre, styles calculés de M

`scripts/site-apres.py` construit le site « après » d'un cours, comme la migration le posera : les
feuilles du socle dans `socle/css/`, son `css/cours.css` calculé, et les liens des pages remplacés
(les anciennes feuilles sont retirées, pour qu'une page oubliée se voie). Puis :

```bash
scripts/site-apres.py SITE_M /tmp/m-apres
scripts/styles-calcules.py SITE_M /tmp/m-apres --tailles 1504x856 390x844 1504x600
```

Résultat : **66 / 66** (22 pages × 3 tailles : 1504 × 856, téléphone 390 × 844, fenêtre basse
1504 × 600), **aucun élément aux styles différents**. Les règles de petit écran, de hauteur et `:has`
du socle redonnent donc M à l'identique. Le critère détecte bien ce qu'il doit : une déclaration
ajoutée dans le `@media` de petit écran donne 1 élément différent à 390 × 844 et 0 à 1504 × 856, ce
qu'une vérification à une seule taille aurait manqué. Sous la charge de quatre Chrome en parallèle,
une page peut ne rien rendre à temps : elle est relancée seule avant d'être signalée.

## Limites

- Captures : une fenêtre de 1504 × 856. Les styles calculés de M, eux, sont vérifiés aux trois
  tailles (voir ci-dessous). A et C le seront aux trois tailles dans leur PR de migration (#428, #144),
  puisque c'est là que leur apparence change.
- L'élagage du CSS mort lit des chaînes littérales : un nom de classe construit autrement serait
  jugé mort à tort. La liste des blocs écartés est affichée pour relecture.
- Le CSS mort restant est conservé quand un seul de ses sélecteurs peut servir.
- `revert` ne revient pas à « la règle précédente du cours » mais à la valeur du **navigateur** : il
  annule donc aussi toute autre règle de l'auteur sur la même propriété et le même élément. Les styles
  calculés le contrôlent en pratique. Si un cas réel se présente, ranger le socle dans un `@layer socle` et
  neutraliser avec `revert-layer`, qui n'annule que l'apport du socle ; pas maintenant (KISS), et la
  feuille KaTeX, chargée hors couche, l'emporterait alors sur les règles du socle qui visent `.katex-display`.
- `@import` : le navigateur découvre les 9 composants en lisant `style.css` puis les demande en parallèle,
  soit un aller-retour de plus. À mesurer (Lighthouse) à la migration de #464 ; ne pas lister les 9
  `<link>` dans les gabarits : l'ordre de la cascade serait écrit à deux endroits.
- Les captures contiennent un peu de bruit (animations, particules) : une page est signalée
  au-delà de ce bruit plus 20 pixels.
