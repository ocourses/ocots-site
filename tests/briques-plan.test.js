// Briques extraites avec dim2 : fonctions pures de plan-trace-det et import du
// moteur de portraits. Le rendu reste couvert par les tests des deux cours.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { aimante, borneLe, pointDuPlan, PLACEMENT } from '../js/briques/plan-trace-det.js';
import { Particules, orbitesDuPortrait } from '../js/briques/portraits.js';

const proche = (a, b, tol = 1e-9) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);

test('plan-trace-det : aimantation sur les axes et la parabole', () => {
  assert.deepEqual(aimante(0.01, 1, 0.1, 0.1), [0, 1]);
  assert.deepEqual(aimante(2, 1.01, 0.1, 0.1), [2, 1]);
  assert.deepEqual(aimante(2, 1.04, 0.1, 0.1), [2, 1]);
  assert.deepEqual(aimante(2, 1.3, 0.1, 0.1), [2, 1.3]);
});

test('plan-trace-det : point arrondi et borne dans le rectangle autorisé', () => {
  assert.deepEqual(pointDuPlan(1.23456, 0.98765, 0, 0), { tr: 1.235, det: 0.988 });
  const p = pointDuPlan(2.001, 1.001, 0.1, 0.1);
  proche(p.det, p.tr * p.tr / 4);
  assert.deepEqual(borneLe({ tr: 8, det: -4 }, { tr: [-2, 3], det: [0, 5] }), { tr: 3, det: 0 });
  assert.equal(PLACEMENT['P₁'].cote, 'bas-droite');
});

test('portraits : les orbites du centre restent dans le cadre', () => {
  const orbites = orbitesDuPortrait([[0, -1], [1, 0]], { x: [-2, 2], y: [-2, 2] }, { departs: 8 });
  assert.ok(orbites.length > 0);
  for (const orbite of orbites) for (const [x, y] of orbite) {
    assert.ok(x >= -2 && x <= 2 && y >= -2 && y <= 2);
  }
});

test('portraits : la classe Particules est exportée par la brique', () => {
  assert.equal(typeof Particules, 'function');
});
