// Gestes à la souris : bouton gauche pour l'objet, bouton droit (ou Maj) pour
// la vue, sur un graphe zoomable (2D) et sur une caméra 3D.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { fauxCanevas } from './aides/faux-canevas.js';
import { el, evenement, installeDom, installeStyleCalcule } from './aides/faux-dom.js';

installeDom();
installeStyleCalcule();
const { boutonVue, glisse, zoomable } = await import('../js/briques/interaction.js');
const { Repere } = await import('../js/ui/repere.js');
const { Camera } = await import('../js/ui/camera3d.js');

const GAUCHE = { button: 0, shiftKey: false };
const DROIT = { button: 2, shiftKey: false };
const MAJ = { button: 0, shiftKey: true };

function appui(canevas, bouton, depart, arrivee) {
  canevas.dispatchEvent(evenement('pointerdown', { ...bouton, pointerId: 1, clientX: depart[0], clientY: depart[1] }));
  canevas.dispatchEvent(evenement('pointermove', { clientX: arrivee[0], clientY: arrivee[1] }));
  canevas.dispatchEvent(evenement('pointerup', {}));
}

test('boutonVue : bouton droit ou Maj, pas le bouton gauche seul', () => {
  assert.equal(boutonVue(GAUCHE), false);
  assert.equal(boutonVue(DROIT), true);
  assert.equal(boutonVue(MAJ), true);
});

test('glisse : `prend` reçoit l’événement, pour filtrer le bouton', () => {
  const canevas = fauxCanevas();
  const rep = new Repere(canevas, { x: [0, 10], y: [0, 4] });
  assert.ok(rep.prepare());
  const recus = [];
  glisse(canevas, rep, { prend: (x, y, ev) => !boutonVue(ev), deplace: (x) => recus.push(x) });
  appui(canevas, DROIT, [100, 100], [200, 100]);
  assert.equal(recus.length, 0);
  appui(canevas, GAUCHE, [100, 100], [200, 100]);
  assert.equal(recus.length, 2);
});

test('zoomable, deplacer: "droit" : le droit déplace la vue, le gauche reste à la figure', () => {
  const canevas = fauxCanevas();
  const rep = new Repere(canevas, { x: [0, 10], y: [0, 4] });
  const barre = el('div');
  const zoom = zoomable(canevas, rep, { barre, auto: () => ({ x: [0, 10], y: [0, 4] }), redessine: () => {}, deplacer: 'droit' });
  assert.ok(rep.prepare());
  const reglages = [];
  glisse(canevas, rep, { prend: (x, y, ev) => !boutonVue(ev), deplace: (x) => reglages.push(x) });

  appui(canevas, GAUCHE, [100, 100], [200, 100]);
  assert.deepEqual(zoom.cadre().x, [0, 10]);
  assert.equal(reglages.length, 2);

  for (const bouton of [DROIT, MAJ]) {
    zoom.reinitialise();
    appui(canevas, bouton, [100, 100], [200, 100]);
    assert.ok(zoom.cadre().x[0] < 0, 'la vue suit le pointeur vers la droite');
  }
  assert.equal(reglages.length, 2);
  assert.match(barre.children[0].innerHTML, /clic droit : déplacer/);

  const menu = evenement('contextmenu', {});
  canevas.dispatchEvent(menu);
  assert.ok(menu.defaultPrevented);
});

test('Camera.attache, tourne: boutonVue : le bouton gauche ne fait pas tourner', () => {
  const canevas = fauxCanevas();
  const c = new Camera({ azimut: 0, elevation: 0.5 }).attache(canevas, () => {}, { tourne: boutonVue });
  appui(canevas, GAUCHE, [0, 0], [100, 0]);
  assert.equal(c.azimut, 0);
  appui(canevas, DROIT, [0, 0], [100, 0]);
  assert.ok(Math.abs(c.azimut - 1) < 1e-12);
});
