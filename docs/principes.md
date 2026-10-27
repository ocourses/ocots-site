<!-- LTeX: language=fr-FR -->

# Principes du socle

Suivi : ocourses/ocots-site#1

Les principes qui ont guidé la conception et les relectures du socle (PR #10 à
#23), chacun avec la règle qui en découle et la façon dont elle est vérifiée
aujourd'hui. Une question de conception se tranche en citant un principe, pas
une préférence.

C'est aussi la matière des futures règles `WEB` (ocots-conventions#40) et de leur
outillage (ocots-lint#78). La colonne « Vérifiée par » indique ce qui est déjà
automatique, ce qui relève encore de la relecture, et ce qu'un lint pourrait
prendre en charge.

## Conception

| # | Principe | Règle | Vérifiée par |
|---|----------|-------|--------------|
| C1 | Inversion de dépendance | Le socle n'importe jamais un fichier d'un cours ; le cours lui passe ses données (`site.config.js` : `themes`, `glossaire`, `charge`). | Relecture ; lint possible : aucun import de `js/` du socle ne sort du socle. |
| C2 | YAGNI | Une clé, une brique ou un point d'extension n'entre dans le socle que si deux cours s'en servent. Une exception est une décision écrite (décision 15). | Relecture, tableau des décisions. |
| C3 | Interface publique minimale | Chaque export documenté est une interface publique qui engage la version (décision 14) ; on n'exporte que ce dont un cours a besoin. | Relecture ; lint possible : un export sans usage hors de son fichier ni test qui le cite. |
| C4 | Responsabilité unique | Un module fait une chose, un dossier un rôle : `core/` calcule sans DOM, `ui/` fournit des composants, `briques/` dessine et réagit pour les illustrations, les pages (`accueil.js`, `illustration.js`) démarrent les gabarits, `config.js` valide. | Relecture ; lint possible : `core/` n'importe ni `ui/` ni `briques/`. |
| C5 | Ouvert/fermé | Un cours étend le socle par les points d'extension listés dans la conception, sans modifier un fichier du socle. Pas de mécanisme à un seul usage. | `verifieModeles` (gabarits identiques aux modèles), relecture. |
| C6 | Échouer tôt, et en une fois | Une clé inconnue est une faute ; un module qui ne se charge pas est une faute nommée ; toutes les fautes sont listées dans une seule erreur. | `verifieCours`, `valideConfig`, appelés au démarrage des pages et dans un test du cours. |
| C7 | Une valeur, un seul endroit | Version et empreintes de KaTeX, clé de préférences `<id>.illustration.<page>`, balisage des gabarits : écrits une fois. Une constante publique est figée (`Object.freeze`). | Tests (`KATEX` figé, `verifieModeles`). |
| C8 | Données en argument | Les fonctions du socle reçoivent leurs données (`trouve(themes, id)`, `parcours(config)`) au lieu de les importer : elles se testent sans le cours. | Tests avec un cours factice (`tests/aides/cours.js`). |
| C9 | Pas d'effet à l'import | Un module (d'illustration, du socle) ne touche pas au DOM quand on l'importe : il se charge sous Node. | `verifieCours` charge chaque module sous Node. |
| C10 | Observabilité | Une page signale qu'elle est prête (`data-ok="1"`), pour la fumée, les captures et les styles calculés. | `scripts/fumee.py`. |

## Tests

| # | Principe | Règle | Vérifiée par |
|---|----------|-------|--------------|
| T1 | Tester ce qui est publié | `tests/` ne teste que le code chargé par le navigateur, et tourne aussi côté étudiant ; les outils de `scripts/` se testent en Python, à côté d'eux. | Relecture ; CI (`npm test`, `npm run test:outils`), essai d'intégration. |
| T2 | Un test publié trouve ses données | Ce qu'un test publié lit (par exemple `socle/modeles/`) n'est pas exclu de la publication étudiante. | Essai d'intégration (présence côté étudiant, puis `npm test`). |
| T3 | Pas de dépendance pour tester | Doublures écrites à la main et partagées (`tests/aides/`), `node --test` seul : le dépôt étudiant n'a pas de `npm ci` à faire. | `package.json` sans dépendance. |
| T4 | Une doublure ne ment pas | Ce qu'une doublure ne sait pas faire lève une erreur (sélecteur non pris en charge, entité HTML) au lieu de renvoyer un résultat faux. | Tests du faux DOM. |
| T5 | Tester les vrais artefacts | Les tests des pages chargent les vrais modèles ; le contrat JS ↔ CSS lit les vrais fichiers. Une copie de fixture divergerait en silence. | `tests/aides/page.js`, `tests/contrat-css.test.js`. |
| T6 | Caractériser avant de déplacer | Avant de reprendre du code sans test, figer sa sortie complète sur des cas typiques et de part et d'autre de chaque frontière (décision 13). | Tests de `dim2`, du plan et des portraits. |
| T7 | Mesurer la valeur d'un test | Une mutation du code doit faire échouer un test ; on en essaie quelques-unes sur chaque nouveau code. | Relecture (mutations listées dans les PR). |
| T8 | Non-régression mesurée | Comparer les styles calculés aux trois tailles plutôt que des captures au pixel (un canevas n'est pas reproductible) ; comparer à une référence qui isole le changement mesuré. | `scripts/styles-calcules.py`, `scripts/site-apres.py`. |
| T9 | Non-régression par substitution | Les tests de chaque cours tournent avec le code du socle à la place de leurs copies (façades). | `scripts/verifie-cours.py`. |
| T10 | Un test, un sujet | Un fichier de test par module ; chaque cas abîme le cours factice d'une seule façon et attend une seule faute. | Relecture. |

## Écriture et suivi

| # | Principe | Règle | Vérifiée par |
|---|----------|-------|--------------|
| E1 | Le README décrit l'état | Un README ou un commentaire de code décrit le dépôt tel qu'il est, jamais une PR (« cette PR… »). | Relecture ; lint possible (motifs « cette PR », « TODO » sans issue). |
| E2 | Un changement visible est annoncé | Le `CHANGELOG` donne, cours par cours, chaque changement de comportement visible et la migration qu'il demande. | Relecture. |
| E3 | Les décisions sont versionnées | Une décision est une ligne du tableau de la conception ; une décision qui change est barrée, et la nouvelle ajoutée avec sa date. | Relecture. |
| E4 | Une règle vérifiable est outillée | Ce qui se vérifie automatiquement devient un test ou un lint, pas une consigne. | Ce document (colonne « Vérifiée par »). |
| E5 | Le suivi public reste public | Les dépôts `*-enseignants` sont privés : le suivi public n'en cite que les titres et les numéros. | Relecture. |
| E6 | Typographie française | Textes affichés : espace insécable avant `:;!?»` et après `«`, ponctuation collée à une formule (`typographie`, `rendTexte`) ; apostrophe typographique `’` dans les données (aujourd'hui mêlée à `'` selon les cours). | Code pour les espaces ; relecture pour l'apostrophe ; lint possible sur les textes du catalogue et des modules. |
