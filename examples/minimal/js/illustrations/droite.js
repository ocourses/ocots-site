// La droite y = a x : un réglage numérique (la pente), gardé dans l'URL.

import { carte, paragraphe, toile } from '../../socle/js/briques/commun.js';
import { Repere } from '../../socle/js/ui/repere.js';

export default {
  rappel: ['La droite $y = a x$ passe par l’origine ; sa pente $a$ dit de combien $y$ monte quand $x$ augmente de $1$.'],
  essais: [
    { texte: 'Doubler la pente : $a = 2$.', etat: { a: 2 } },
    { texte: 'Une pente négative : $a = -1$, la droite descend.', etat: { a: -1 } },
  ],
  etat: { a: 1 },
  termes: ['pente'],
  monte(zone, outils) {
    const c = carte(zone, 'La droite $y = a x$');
    const note = paragraphe(c, '');
    const canevas = toile(c, '1 / 1', () => dessine());
    const repere = new Repere(canevas, { x: [-2, 2], y: [-2, 2], egal: true });
    function dessine() {
      const { a } = outils.etat;
      outils.rendTexte(note, `Pente : $a = ${a}$.`);
      if (!repere.prepare()) return;
      repere.axes({ noms: ['x', 'y'] });
      repere.trace([[-2, -2 * a], [2, 2 * a]]);
    }
    dessine();
    return { applique: dessine };
  },
};
