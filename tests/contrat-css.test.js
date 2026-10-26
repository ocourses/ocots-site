// Contrat JS ↔ CSS : toute classe que le JavaScript du socle pose sur un élément
// est définie dans les feuilles du socle. Marqué `todo` tant que le CSS des
// composants n'est pas dans le socle (#6) : le test échoue alors sans faire
// échouer la suite ; ce sera le critère de fin de #6.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const racine = new URL('../', import.meta.url).pathname;
const lis = (dossier, motif) =>
  readdirSync(join(racine, dossier), { recursive: true })
    .filter((f) => motif.test(f))
    .map((f) => readFileSync(join(racine, dossier, f), 'utf8'));

const POSEES = [/className = '([^'$`]+)'/g, /classList\.(?:add|toggle)\('([^'$`]+)'/g];
const classesPosees = () => {
  const noms = new Set();
  for (const source of lis('js', /\.js$/)) {
    for (const motif of POSEES) for (const m of source.matchAll(motif)) m[1].split(/\s+/).filter(Boolean).forEach((n) => noms.add(n));
  }
  return noms;
};

test('contrat JS ↔ CSS : chaque classe posée par le socle est définie dans css/', { todo: 'le CSS des composants arrive avec #6' }, () => {
  const css = lis('css', /\.css$/).join('\n');
  const manquantes = [...classesPosees()].filter((n) => !new RegExp(`\\.${n}(?![\\w-])`).test(css)).sort();
  assert.deepEqual(manquantes, []);
});

test('contrat JS ↔ CSS : le relevé des classes posées n’est pas vide', () => {
  assert.ok(classesPosees().size > 10);
});
