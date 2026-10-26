#!/usr/bin/env python3
"""Ce qu'il reste à un cours une fois le socle posé : son `css/cours.css`.

    scripts/residu-css.py STYLE_DU_COURS.css [--site DOSSIER_SITE] > cours.css

Lit `css/style.css` du socle (ses @import) et celui du cours, puis écrit, dans
l'ordre d'origine, les blocs du cours que le socle ne contient pas à
l'identique : règles propres au cours, et règles dont les déclarations diffèrent
(elles passent après le socle et gardent donc leur effet). Un bloc dont
toutes les règles sont dans le socle est omis.

Les propriétés que le socle règle pour un sélecteur que le cours possède aussi, sans
que le cours les règle, sont remises à `revert` en fin de feuille : le cours garde son
apparence. Un sélecteur absent du cours est une nouveauté, non neutralisée.

Avec `--nouveautes`, écrit à la place les règles du socle que le cours n'a pas
(aucune règle de même sélecteur) : le comportement qu'il gagne en adoptant le
socle ; à relire cours par cours avant de migrer.

Avec `--site`, les blocs dont aucun sélecteur ne peut plus s'appliquer (une
classe ou un identifiant que ni le HTML ni le JavaScript du site n'emploient)
sont écartés et listés sur la sortie d'erreur : du CSS mort.
"""

import argparse
import glob
import re
import sys
from pathlib import Path

SOCLE = Path(__file__).resolve().parent.parent / "css"
EXEMPTS = ("katex", "u-", "uplot")   # classes produites par KaTeX et uPlot


def sans_commentaires(txt):
    return re.sub(r"/\*.*?\*/", "", txt, flags=re.S)


def virgules(tete):
    """Les sélecteurs d'une liste : on coupe aux virgules hors parenthèses (`:is(a, b)`)."""
    morceaux, profondeur, courant = [], 0, ""
    for c in tete:
        profondeur += {"(": 1, ")": -1}.get(c, 0)
        if c == "," and profondeur == 0:
            morceaux.append(courant)
            courant = ""
        else:
            courant += c
    return morceaux + [courant]


def blocs(txt):
    """[(texte d'origine, en-tête, [(sélecteur, déclarations)], sous-blocs)] au niveau racine.

    `sous-blocs` n'est renseigné que pour un @media ou un @supports."""
    sortie, i, n = [], 0, len(txt)
    while i < n:
        debut = i
        while i < n and txt[i] not in "{};":
            if txt.startswith("/*", i):    # un « ; » dans un commentaire ne termine rien
                i = txt.index("*/", i) + 2 if "*/" in txt[i:] else n
            else:
                i += 1
        if i >= n:
            break
        if txt[i] in "};":
            i += 1
            continue
        tete_brute = txt[debut:i]
        tete = " ".join(sans_commentaires(tete_brute).split())
        profondeur, k = 1, i + 1
        while profondeur and k < n:
            profondeur += {"{": 1, "}": -1}.get(txt[k], 0)
            k += 1
        corps = txt[i + 1:k - 1]
        regles, sous_blocs = [], []
        if tete.startswith(("@media", "@supports")):
            sous_blocs = blocs(corps)
            for _, _, sous, _ in sous_blocs:
                regles += [(f"{tete} {{ {s} }}", d) for s, d in sous]
        elif tete.startswith("@"):
            regles.append((tete, " ".join(corps.split())))
        else:
            decl = ";".join(sorted(d.strip() for d in sans_commentaires(corps).split(";") if d.strip()))
            decl = re.sub(r"\s+", " ", decl)
            regles = [(" ".join(sel.split()), decl) for sel in virgules(tete)]
        sortie.append((txt[debut:k], tete, regles, sous_blocs))
        i = k
    return sortie


def texte_socle():
    texte = ""
    for imp in re.findall(r"@import url\('([^']+)'\)", (SOCLE / "style.css").read_text()):
        texte += (SOCLE / imp).read_text() + "\n"
    return texte


def lit_socle():
    return {regle for _, _, regles, _ in blocs(texte_socle()) for regle in regles}


def proprietes(texte):
    """{(contexte, sélecteur): {propriété, ...}} : ce que chaque sélecteur règle."""
    sortie = {}

    def parcours(liste, env=""):
        for _, tete, regles, sous in liste:
            if sous:
                parcours(sous, tete)
                continue
            for selecteur, decl in regles:
                props = {d.split(":", 1)[0].strip() for d in decl.split(";") if ":" in d}
                sortie.setdefault((env, selecteur), set()).update(props)

    parcours(blocs(texte))
    return sortie


def neutralisations(socle_txt, cours_txt):
    """Propriétés que le socle règle pour un sélecteur du cours, et que le cours ne règle pas :
    `revert` les rend au cours (sans quoi le socle y ajouterait un comportement)."""
    du_socle, du_cours = proprietes(socle_txt), proprietes(cours_txt)
    sortie, par_contexte = "", {}
    for (env, sel), props in sorted(du_socle.items()):
        if (env, sel) not in du_cours:
            continue
        manque = sorted(props - du_cours[(env, sel)])
        if manque:
            par_contexte.setdefault(env, []).append(f"{sel} {{ " + " ".join(f"{p}: revert;" for p in manque) + " }")
    for env, regles in par_contexte.items():
        corps = "\n".join(("  " if env else "") + r for r in regles)
        sortie += (f"{env} {{\n{corps}\n}}\n" if env else corps + "\n")
    return sortie


def jetons(selecteur):
    return set(re.findall(r"[.#]([A-Za-z_][\w-]*)", selecteur))


def sources(site):
    """Textes où un nom de classe ou d'identifiant peut apparaître : les chaînes
    littérales du JavaScript et du HTML (dont les valeurs des attributs class et id) (pas les noms
    de variables ni les commentaires)."""
    morceaux = []
    for chemin in glob.glob(f"{site}/**/*", recursive=True):
        if "/node_modules/" in chemin or "/tests/" in chemin or not chemin.endswith((".js", ".mjs", ".html")):
            continue
        t = Path(chemin).read_text(errors="ignore")
        t = re.sub(r"<!--.*?-->|/\*.*?\*/", "", t, flags=re.S)
        t = re.sub(r"(?m)^\s*//.*$", "", t)
        morceaux += re.findall(r"""'(?:\\.|[^'\\\n])*'|"(?:\\.|[^"\\\n])*"|`(?:\\.|[^`\\])*`""", t, flags=re.S)
    return "\n".join(morceaux)


def employe(jeton, src):
    if jeton.startswith(EXEMPTS):
        return True
    if re.search(r"(?<![\w-])" + re.escape(jeton) + r"(?![\w-])", src):
        return True
    # nom construit : `disposition-${x}` ou 'disposition-' + x
    return "-" in jeton and re.search(re.escape(jeton.rsplit("-", 1)[0] + "-") + r"(\$\{|['\"`]\s*\+)", src) is not None


def mort(regles, src):
    def peut_servir(selecteur):
        base = re.sub(r"^.*@media[^{]*\{\s*|\s*\}\s*$", "", selecteur)
        return all(employe(j, src) for j in jetons(base))
    return not any(peut_servir(s) for s, _ in regles)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("style")
    p.add_argument("--site")
    p.add_argument("--nouveautes", action="store_true")
    args = p.parse_args()
    socle = lit_socle()
    if args.nouveautes:
        connus = {r[0] for _, _, regles, _ in blocs(Path(args.style).read_text()) for r in regles}
        connus |= {f"{t} {{ {s} }}" for _, t, _, sous in blocs(Path(args.style).read_text()) for _, _, rs, _ in sous for s, _ in rs}
        nouvelles = sorted({s for s, _ in socle if s not in connus})
        print("\n".join(nouvelles))
        return
    src = sources(args.site) if args.site else None
    stats = {"socle": 0, "gardés": 0, "écartés": 0}

    def filtre(liste, enveloppe=""):
        """Texte des blocs à garder ; `enveloppe` : en-tête du @media qui les contient."""
        sortie = ""
        for brut, tete, regles, sous_blocs in liste:
            if sous_blocs:
                interieur = filtre(sous_blocs, tete)
                if interieur:
                    sortie += f"{tete} {{\n{interieur.rstrip()}\n}}\n\n"
            elif all(((f"{enveloppe} {{ {s} }}" if enveloppe else s), d) in socle for s, d in regles):
                stats["socle"] += 1
            elif src is not None and mort(regles, src):
                stats["écartés"] += 1
                print(f"écarté (mort) : {(enveloppe + ' > ' if enveloppe else '') + tete[:90]}", file=sys.stderr)
            else:
                stats["gardés"] += 1
                sortie += brut.strip("\n") + "\n\n"
        return sortie

    cours_txt = Path(args.style).read_text()
    sys.stdout.write(filtre(blocs(cours_txt)))
    neutres = neutralisations(texte_socle(), cours_txt)
    if neutres:
        sys.stdout.write("/* Ce que le socle règle en plus pour ces sélecteurs : le cours ne l'avait pas. */\n" + neutres)
    print("blocs : {socle} dans le socle, {gardés} gardés, {écartés} écartés".format(**stats), file=sys.stderr)

if __name__ == "__main__":
    main()
