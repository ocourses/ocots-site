// Rendu KaTeX : `rend` pour une formule en mode display, `rendTexte` pour un
// texte contenant des formules entre $…$.

import { typographie } from './format.js';

const options = { throwOnError: false };

export function rend(element, latex, display = true) {
  window.katex.render(latex, element, { ...options, displayMode: display });
}

export function rendTexte(element, texte) {
  element.textContent = '';
  let formule = null;
  texte.split(/(\$[^$]+\$)/).forEach((morceau) => {
    if (morceau.startsWith('$') && morceau.endsWith('$') && morceau.length > 1) {
      formule = document.createElement('span');
      window.katex.render(morceau.slice(1, -1), formule, { ...options, displayMode: false });
      element.appendChild(formule);
    } else if (morceau) {
      const t = typographie(morceau);
      // La ponctuation qui suit une formule reste collée à elle : on ne coupe
      // pas la ligne avant « , », « . » ou « : » (précédé d'une espace insécable).
      const colle = formule && t.match(/^(\u00a0[:;!?»]|[,.)])/);
      if (colle) {
        const bloc = document.createElement('span');
        bloc.className = 'insecable';
        formule.replaceWith(bloc);
        bloc.append(formule, colle[0]);
        element.appendChild(document.createTextNode(t.slice(colle[0].length)));
      } else {
        element.appendChild(document.createTextNode(t));
      }
      formule = null;
    }
  });
}

// Rend les formules $…$ des textes statiques de la page.
export function rendStatique(racine) {
  const marcheur = document.createTreeWalker(racine, NodeFilter.SHOW_TEXT);
  const noeuds = [];
  while (marcheur.nextNode()) if (/\$[^$]+\$/.test(marcheur.currentNode.nodeValue)) noeuds.push(marcheur.currentNode);
  for (const noeud of noeuds) {
    const span = document.createElement('span');
    rendTexte(span, noeud.nodeValue);
    noeud.replaceWith(...span.childNodes);
  }
}
