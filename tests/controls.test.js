// Pas ▲ ▼ ↑ ↓ d'une boîte de saisie (ajoutePas) : bornes fixes, bornes qui
// changent après coup, lecture personnalisée. Un faux élément remplace le DOM.

import { test } from 'node:test';
import assert from 'node:assert/strict';

class Faux {
  constructor() {
    this.value = '';
    this.ecouteurs = {};
    this.evenements = 0;
  }
  setAttribute() {}
  getAttribute() {
    return null;
  }
  append() {}
  appendChild() {}
  replaceWith() {}
  addEventListener(nom, f) {
    this.ecouteurs[nom] = f;
  }
  dispatchEvent() {
    this.evenements++;
  }
  appuie(key, extra = {}) {
    this.ecouteurs.keydown({ key, preventDefault() {}, ...extra });
  }
}

globalThis.document = { createElement: () => new Faux() };
const { ajoutePas } = await import('../js/ui/controls.js');

test('ajoutePas : un pas par flèche, borné par min et max', () => {
  const saisie = new Faux();
  saisie.value = '0,9';
  ajoutePas(saisie, { pas: 0.1, min: 0, max: 1 });
  saisie.appuie('ArrowUp');
  assert.equal(saisie.value, '1');
  saisie.appuie('ArrowUp');
  assert.equal(saisie.value, '1');
  saisie.appuie('PageDown');
  assert.equal(saisie.value, '0');
  assert.equal(saisie.evenements, 3);
});

test('ajoutePas : les bornes d’un objet `limites` sont relues à chaque pas', () => {
  const saisie = new Faux();
  saisie.value = '5';
  const limites = { min: 0, max: 5 };
  ajoutePas(saisie, { pas: 1, limites });
  saisie.appuie('ArrowUp');
  assert.equal(saisie.value, '5');
  limites.max = 8;
  saisie.appuie('ArrowUp');
  assert.equal(saisie.value, '6');
});

test('ajoutePas : `max` modifié dans l’objet d’options est relu', () => {
  const saisie = new Faux();
  saisie.value = '3';
  const options = { pas: 1, min: 0, max: 3 };
  ajoutePas(saisie, options);
  options.max = 4;
  saisie.appuie('ArrowUp');
  assert.equal(saisie.value, '4');
});

test('ajoutePas : `lis` lit la valeur écrite (ici une fraction)', () => {
  const saisie = new Faux();
  saisie.value = '1/2';
  const lis = (t) => (t.includes('/') ? Number(t.split('/')[0]) / Number(t.split('/')[1]) : Number(t));
  ajoutePas(saisie, { pas: 0.25, lis });
  saisie.appuie('ArrowUp');
  assert.equal(saisie.value, '0,75');
});
