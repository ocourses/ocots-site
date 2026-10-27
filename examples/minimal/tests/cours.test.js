// Les tests d'un cours : le contrat du socle (configuration, modules
// d'illustration, parcours) et les gabarits, copies exactes des modèles.

import { test } from 'node:test';

import { verifieCours } from '../socle/js/config.js';
import { verifieModeles } from '../socle/js/modeles.js';
import config from '../site.config.js';

test('le cours respecte le contrat du socle', () => verifieCours(config));
test('les gabarits sont ceux du socle', () => verifieModeles(new URL('../', import.meta.url)));
