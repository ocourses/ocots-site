#!/usr/bin/env python3
"""Rejoue les tests de chaque cours avec les fichiers du socle posés à la place de
ses copies, pour vérifier qu'une fusion (étape 2) ne casse rien.

Le code propre à un cours, laissé hors du socle (par exemple `simule`), est
remis dans son `commun.js`, comme le fera la migration. Chemins : COURS
(défaut ~/Courses) ou SITE_AUTOMATIQUE, SITE_CALCUL, SITE_MESURE.
"""
import os, re, shutil, subprocess, tempfile
SOC=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RACINE = os.environ.get('COURS', os.path.expanduser('~/Courses'))
SITES = {
    'automatique': os.environ.get('SITE_AUTOMATIQUE', RACINE + '/automatique/automatique-enseignants/site'),
    'calcul': os.environ.get('SITE_CALCUL', RACINE + '/calcul_differentiel_edo/calcul-differentiel-edo-enseignants/site'),
    'mesure': os.environ.get('SITE_MESURE', RACINE + '/mesure_et_integration/integration/mesure-integration-enseignants/site'),
}
FILES=['css/theme.css','js/ui/onglets.js','js/ui/preferences.js','js/ui/infobulle.js','js/ui/theme.js','js/ui/katex.js','js/ui/repere.js','js/ui/format.js','js/ui/controls.js','js/ui/camera3d.js','js/ui/vue3d.js','js/core/ode.js','js/illustrations/commun.js']
LOCAL={'automatique':(["simule"],"import { rk4 } from '../core/ode.js';\n"),
       'calcul':(["champsPoint"],"import { champ } from '../ui/controls.js';\n"),
       'mesure':(["choisitIndice","EXPOSANTS","puissance10","echelleLog","axesLog","choixEchelle"],"")}
def bloc(src,nom):
    # bloc = commentaires qui précèdent + déclaration jusqu'à l'accolade fermante en colonne 0 (ou fin de ligne `;`)
    m=re.search(r"((?:^//[^\n]*\n)*)^(?:export )?(?:function|const) "+nom+r"\b[^\n]*\n",src,re.M)
    if not m: return ''
    i=m.start(); j=m.end()
    if m.group(0).rstrip().endswith(';') : return src[i:j]
    k=src.index("\n}\n",j)+3
    return src[i:k]
for nom,site in SITES.items():
    d=tempfile.mkdtemp(prefix='ovl-'+nom+'-'); dst=d+'/site'; shutil.copytree(site,dst,ignore=shutil.ignore_patterns('node_modules','.git'))
    orig_commun=open(site+'/js/illustrations/commun.js').read()
    for f in FILES:
        if not os.path.exists(dst+'/'+f): continue
        shutil.copyfile(SOC+'/'+f,dst+'/'+f)
    noms,imp=LOCAL[nom]
    extra=''.join(bloc(orig_commun,n)+'\n' for n in noms)
    p=dst+'/js/illustrations/commun.js'; s=open(p).read()
    s=imp+s+'\n'+extra; open(p,'w').write(s)
    r=subprocess.run(['node','--test'],cwd=dst,capture_output=True,text=True)
    resume=[l for l in (r.stdout+r.stderr).splitlines() if re.match(r'^ℹ (tests|pass|fail) ',l)]
    # référence : le site tel quel
    r0=subprocess.run(['node','--test'],cwd=site,capture_output=True,text=True)
    ref=[l for l in (r0.stdout+r0.stderr).splitlines() if re.match(r'^ℹ (tests|pass|fail) ',l)]
    print(nom,'| avant :',' '.join(x[2:] for x in ref),'| après :',' '.join(x[2:] for x in resume))
    if r.returncode: print((r.stdout+r.stderr)[-1500:])
