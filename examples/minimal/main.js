// Un « cours » minimal : il importe les briques du socle et dessine une carte avec une
// formule et un repère. Dans un vrai cours, les imports pointent vers `./socle/js/…`.

import { carte, paragraphe, toile } from '../../js/briques/commun.js';
import { Repere } from '../../js/ui/repere.js';

const page = document.getElementById('page');
const c = carte(page, 'Une carte du socle');
paragraphe(c, 'Une formule dans un texte : $\\int_E f\\,d\\mu$, suivie d’une virgule.');
const canevas = toile(c, '2 / 1');
canevas.style.width = '100%';

const repere = new Repere(canevas, { x: [0, 4], y: [0, 2] });
if (repere.prepare()) {
  repere.axes({ noms: ['x', 'y'] });
  repere.trace([[0, 0], [2, 1], [4, 0.5]]);
}
document.body.dataset.ok = '1';
