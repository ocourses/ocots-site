// Somme de Riemann de x ↦ x² sur [0, 1] : un réglage numérique (n), un réglage
// textuel borné par `choix` (le point de chaque rectangle) et une préférence
// d'affichage (la courbe), gardée dans le navigateur.

import { carte, choixRadios, paragraphe, toile } from '../../socle/js/briques/commun.js';
import { Repere } from '../../socle/js/ui/repere.js';

const f = (x) => x * x;

export default {
  rappel: ['Une somme de Riemann approche $\\int_0^1 f$ par des rectangles de largeur $h = 1/n$ :', '$$\\sum_{k=0}^{n-1} f(x_k)\\,h \\to \\int_0^1 x^2\\,dx = \\frac{1}{3}$$'],
  essais: [
    { texte: 'Plus de rectangles : $n = 32$.', etat: { n: 32 } },
    { texte: 'Le point de droite, sans la courbe.', etat: { point: 'droite' }, preferences: { courbe: false } },
  ],
  etat: { n: 4, point: 'gauche' },
  choix: { point: ['gauche', 'droite'] },
  preferences: { courbe: true },
  termes: ['somme de Riemann'],
  monte(zone, outils) {
    const c = carte(zone, 'Rectangles sous $x^2$');
    const radios = choixRadios(c, {
      nom: 'point',
      options: [
        { valeur: 'gauche', texte: 'point de gauche' },
        { valeur: 'droite', texte: 'point de droite' },
      ],
      change: (point) => {
        outils.change({ point });
        dessine();
      },
    });
    const note = paragraphe(c, '');
    const canevas = toile(c, '4 / 3', () => dessine());
    const repere = new Repere(canevas, { x: [0, 1], y: [0, 1] });
    function dessine() {
      const { n, point } = outils.etat;
      radios.fixe(point);
      const h = 1 / n;
      const xs = Array.from({ length: n }, (_, k) => (point === 'gauche' ? k : k + 1) * h);
      const somme = xs.reduce((s, x) => s + f(x) * h, 0);
      outils.rendTexte(note, `Avec $n = ${n}$ : somme $\\approx ${somme.toFixed(4).replace('.', '{,}')}$.`);
      if (!repere.prepare()) return;
      repere.axes({ noms: ['x', 'y'] });
      xs.forEach((x, k) => repere.trace([[k * h, 0], [k * h, f(x)], [(k + 1) * h, f(x)], [(k + 1) * h, 0]], { largeur: 1 }));
      if (outils.preferences.valeurs.courbe) repere.trace(Array.from({ length: 51 }, (_, i) => [i / 50, f(i / 50)]));
    }
    dessine();
    return { applique: dessine };
  },
};
