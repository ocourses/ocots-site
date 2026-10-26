// Formats d'affichage : nombres, polynômes, vecteurs, nombres à largeur fixe
// (la place réservée dépend de ce que la grandeur peut devenir, pas d'un défaut).

import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  chiffresEntiers,
  latexIntervalle,
  latexNombreFinal,
  latexNombreFixe,
  latexPositifFixe,
  latexScientifique,
  latexVecteur,
  nombreCourt,
  polynomeLatex,
  separateur,
} from '../js/ui/format.js';

test('nombreCourt : 4 chiffres, virgule française, notation scientifique aux extrêmes', () => {
  assert.equal(nombreCourt(0), '0');
  assert.equal(nombreCourt(0.0021), '0,0021');
  assert.equal(nombreCourt(-12.3456789), '−12,35');
  assert.equal(nombreCourt(2.34e-5), '2,34e-5');
  assert.equal(nombreCourt(-2.5e-7), '−2,5e-7');
  assert.equal(nombreCourt(123456), '1,235e5');
  assert.equal(nombreCourt(NaN), '—');
});

test('polynomeLatex : signes, coefficients unitaires et termes nuls', () => {
  assert.equal(polynomeLatex([1, 5, 10.2]), '\\lambda^{2} + 5\\lambda + 10{,}2');
  assert.equal(polynomeLatex([1, 0, -3]), '\\lambda^{2} - 3');
  assert.equal(polynomeLatex([1, 0, 0, 0, 1]), '\\lambda^{4} + 1');
  assert.equal(polynomeLatex([1, -1]), '\\lambda - 1');
});

test('latexVecteur : un scalaire sans parenthèses, un vecteur séparé par « ; »', () => {
  assert.equal(latexVecteur([7.04]), '7{,}04');
  assert.equal(latexVecteur([0.8, 0]), '\\left(0{,}8\\ ;\\ 0\\right)');
});

test('nombres fixes : une grandeur positive ne réserve ni signe ni chiffre inutile', () => {
  // Pas de place pour le signe, pas de chiffre de plus devant 2,772.
  assert.equal(latexPositifFixe(2.772), '2{,}772');
  // Une grandeur signée garde la place du signe quand elle est positive.
  assert.equal(latexNombreFixe(2.772, 3), '\\phantom{-}2{,}772');
  assert.equal(latexNombreFixe(-2.772, 3), '-2{,}772');
  // Une grandeur qui peut passer 10 réserve le chiffre demandé, pas davantage.
  assert.equal(latexPositifFixe(2.772, 3, 2), '\\phantom{0}2{,}772');
  assert.equal(latexPositifFixe(13.437, 3, 2), '13{,}437');
  // Zéro négatif arrondi : jamais « −0,00 ».
  assert.equal(latexNombreFixe(-0.0001, 2), '\\phantom{-}0{,}00');
});

test('nombres fixes : le chiffre réservé suit le plus grand nombre atteignable', () => {
  assert.deepEqual([0.4, 9.99, 10, 21.3, 150].map(chiffresEntiers), [1, 1, 2, 2, 3]);
});

test('nombres fixes : +∞ garde la largeur d’un nombre fini', () => {
  assert.equal(latexPositifFixe(Infinity, 3, 1), '\\phantom{000}+\\infty');
});

test('nombres fixes : en fin de phrase, le signe n’est écrit que s’il est négatif', () => {
  assert.equal(latexNombreFinal(0.7854, 4), '0{,}7854');
  assert.equal(latexNombreFinal(-0.7854, 4), '-0{,}7854');
  assert.equal(latexNombreFinal(-0.00001, 3), '0{,}000');
});

test('séparateur : la virgule pour des entiers, le point-virgule dès qu’un décimal s’écrit', () => {
  assert.equal(separateur([0, 1]), ',\\ ');
  assert.equal(separateur([1.5, 2]), '\\,;\\ ');
  assert.equal(separateur([1.0004, 2], 3), ',\\ ');
  assert.equal(latexIntervalle(0, 6), '[0,\\ 6]');
  assert.equal(latexIntervalle(1.5, 2.5, { chiffres: 2 }), '[1{,}5\\,;\\ 2{,}5]');
});

test('latexScientifique : notation scientifique aux extrêmes, nombre ordinaire sinon', () => {
  assert.equal(latexScientifique(0.00001234, 3), '1{,}23 \\cdot 10^{-5}');
  assert.equal(latexScientifique(12345678, 3), '1{,}23 \\cdot 10^{7}');
  assert.equal(latexScientifique(2.5, 3), '2{,}5');
  assert.equal(latexScientifique(Infinity), '+\\infty');
});
