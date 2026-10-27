// Le test d'un cours : il importe le socle par un chemin relatif et lance un test
// qui lui est propre. `npm test` dans le dossier du cours ne lance que ceci.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { latexNombre } from '../../../js/ui/format.js';

test('le cours importe le socle', () => {
  assert.equal(latexNombre(2.5), '2{,}5');
});
