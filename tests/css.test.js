// Feuilles du socle : aucune couleur en dur hors de theme.css (la charte), et
// `style.css` n'importe que des fichiers qui existent. Le calcul du reste d'un
// cours (scripts/residu-css.py) est vérifié sur une feuille de contrôle.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const css = new URL('../css/', import.meta.url).pathname;
const sansCommentaires = (t) => t.replace(/\/\*[\s\S]*?\*\//g, '');

test('aucune couleur en dur dans les composants', () => {
  const COULEUR = /#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla)\(/;
  for (const f of readdirSync(css).filter((f) => f.endsWith('.css') && f !== 'theme.css')) {
    const fautes = sansCommentaires(readFileSync(join(css, f), 'utf8'))
      .split('\n')
      .filter((l) => COULEUR.test(l));
    assert.deepEqual(fautes, [], `${f} : couleur en dur`);
  }
});

test('style.css importe des fichiers qui existent', () => {
  const imports = [...readFileSync(join(css, 'style.css'), 'utf8').matchAll(/@import url\('\.\/([^']+)'\)/g)].map((m) => m[1]);
  assert.ok(imports.length > 0);
  for (const f of imports) assert.ok(existsSync(join(css, f)), f);
});

test('residu-css : garde ce que le socle n’a pas, ignore un « ; » dans un commentaire', () => {
  const dossier = mkdtempSync(join(tmpdir(), 'residu-'));
  const cours = join(dossier, 'style.css');
  const socle = readFileSync(join(css, 'base.css'), 'utf8');
  const premiere = socle.slice(socle.indexOf('body {'), socle.indexOf('}', socle.indexOf('body {')) + 1);
  writeFileSync(
    cours,
    `${premiere}\n\n/* Propre au cours ; avec un point-virgule. */\n\n.propre-au-cours-xyz {\n  color: var(--texte);\n}\n`,
  );
  const sortie = execFileSync('python3', [new URL('../scripts/residu-css.py', import.meta.url).pathname, cours], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  });
  assert.match(sortie, /^\/\* Propre au cours ; avec un point-virgule\. \*\/\s*\.propre-au-cours-xyz \{/);
  assert.doesNotMatch(sortie, /body \{/);
});
