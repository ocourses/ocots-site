// Catalogue du cours minimal : deux thèmes, deux illustrations disponibles et une
// annoncée (carte « à venir » sur l'accueil).

export const themes = [
  {
    id: 'fonctions',
    titre: 'Fonctions',
    source: 'Exemple, chapitre 1',
    illustrations: [
      { id: 'droite', titre: 'Une droite', resume: 'La pente d’une droite passant par l’origine.', source: 'Exemple, 1.1', disponible: true },
      { id: 'parabole', titre: 'Une parabole', resume: 'Annoncée, pas encore écrite.', source: 'Exemple, 1.2', disponible: false },
    ],
  },
  {
    id: 'integrales',
    titre: 'Intégrales',
    source: 'Exemple, chapitre 2',
    illustrations: [{ id: 'aire', titre: 'Une somme de Riemann', resume: 'L’aire sous une courbe, approchée par des rectangles.', source: 'Exemple, 2.1', disponible: true }],
  },
];
