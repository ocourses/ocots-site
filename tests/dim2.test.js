// Caractérisation de js/core/dim2.js : les cas du TD1, spectre, nature,
// exponentielle et directions propres. Ces tests figent l'API avant la migration
// des deux cours qui la consomment.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { CAS_TD1, applique, directionsPropres, exponentielle, matrice, nature, spectre } from '../js/core/dim2.js';

const proche = (a, b, tol = 1e-9) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);
const procheMatrice = (A, B, tol = 1e-9) => A.forEach((ligne, i) => ligne.forEach((v, j) => proche(v, B[i][j], tol)));

test('CAS_TD1 : les onze cas sont présents et distincts', () => {
  assert.equal(CAS_TD1.length, 11);
  assert.deepEqual(new Set(CAS_TD1.map((c) => c.cas)).size, 11);
  assert.deepEqual(CAS_TD1.map((c) => c.cas), ['P₁', 'P₂', 'P₃', 'P₄', 'P₅', 'P₆', 'P₇', 'P₈', 'P₉', 'P₁₀', 'P₁₁']);
});

test('matrice : formes propres et compagnon ont la trace et le déterminant demandés', () => {
  for (const [tr, det] of [[-3, 2], [3, 2], [0, -1], [-2, 4], [0, 3]]) {
    for (const forme of ['propres', 'compagnon']) {
      const A = matrice(tr, det, forme);
      proche(A[0][0] + A[1][1], tr);
      proche(A[0][0] * A[1][1] - A[0][1] * A[1][0], det);
    }
  }
  assert.deepEqual(matrice(3, 2, 'compagnon'), [[0, 1], [-2, 3]]);
  procheMatrice(matrice(-2, 1), [[-1, 1], [0, -1]]);
  procheMatrice(matrice(0, 3), [[0, Math.sqrt(3)], [-Math.sqrt(3), 0]]);
});

test('spectre : réels distincts, double et complexes conjuguées', () => {
  assert.deepEqual(spectre(-3, 2).valeurs, [{ re: -2, im: 0 }, { re: -1, im: 0 }]);
  assert.equal(spectre(-3, 2).reelles, true);
  assert.deepEqual(spectre(0, 3).valeurs, [{ re: 0, im: Math.sqrt(3) }, { re: 0, im: -Math.sqrt(3) }]);
  assert.equal(spectre(0, 3).reelles, false);
  assert.deepEqual(spectre(0, 0).valeurs, [{ re: 0, im: 0 }, { re: 0, im: 0 }]);
});

test('nature : les onze cas du TD1 gardent leur classification', () => {
  const attendus = Object.fromEntries(CAS_TD1.map(({ tr, det, cas }) => [cas, nature(tr, det)]));
  assert.deepEqual(Object.fromEntries(Object.entries(attendus).map(([cas, n]) => [cas, n.cas])), Object.fromEntries(CAS_TD1.map(({ cas }) => [cas, cas])));
  assert.equal(attendus['P₁'].stabilite, 'asymptotiquement stable');
  assert.equal(attendus['P₈'].stabilite, 'stable');
  assert.equal(attendus['P₃'].stabilite, 'instable');
});

test('exponentielle : t=0 donne I et les cas diagonaux sont exacts', () => {
  const A = [[-2, 0], [0, 3]];
  procheMatrice(exponentielle(A, 0), [[1, 0], [0, 1]]);
  procheMatrice(exponentielle(A, 0.5), [[Math.exp(-1), 0], [0, Math.exp(1.5)]], 1e-8);
});

test('exponentielle : nilpotente et rotation', () => {
  procheMatrice(exponentielle([[0, 1], [0, 0]], 2), [[1, 2], [0, 1]]);
  procheMatrice(exponentielle([[0, 1], [-1, 0]], Math.PI / 2), [[0, 1], [-1, 0]], 1e-8);
});

test('exponentielle : e^(tA) applique les compositions attendues', () => {
  const A = [[-1, 2], [0, -1]];
  const E = exponentielle(A, 0.3);
  const x = applique(E, [2, -1]);
  proche(x[0], Math.exp(-0.3) * (2 - 0.6), 1e-8);
  proche(x[1], -Math.exp(-0.3), 1e-8);
});

test('directionsPropres : deux directions, une direction de Jordan, aucun complexe', () => {
  assert.equal(directionsPropres([[1, 0], [0, 2]]).length, 2);
  assert.equal(directionsPropres([[1, 1], [0, 1]]).length, 1);
  assert.deepEqual(directionsPropres([[0, -1], [1, 0]]), []);
  for (const { lambda, v } of directionsPropres([[1, 0], [0, 2]])) {
    const Av = applique([[1, 0], [0, 2]], v);
    proche(Av[0], lambda * v[0]);
    proche(Av[1], lambda * v[1]);
  }
});
