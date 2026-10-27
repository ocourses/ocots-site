// Configuration du cours minimal : un vrai petit cours qui consomme le socle comme
// le fera chaque cours (socle/ est ici un lien vers la racine du dépôt, à la place
// du sous-module). Clés : docs/conception.md.

import { themes } from './js/illustrations/catalogue.js';
import { GLOSSAIRE } from './js/illustrations/glossaire.js';

export default {
  id: 'cours-minimal',
  titre: 'Cours minimal',
  sousTitre: 'Exemple du socle ocots-site — deux illustrations',
  intro: ['Un cours réduit à deux illustrations, pour éprouver le socle : une droite $y = a x$ et une somme de Riemann.'],
  depotIssues: 'ocourses/ocots-site',
  themes,
  glossaire: GLOSSAIRE,
  charge: (id) => import(`./js/illustrations/${id}.js`),
};
