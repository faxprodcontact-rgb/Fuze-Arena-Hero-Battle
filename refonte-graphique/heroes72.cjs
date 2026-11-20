// Les 72 héros (habillage provisoire des 72 gabarits de src/core/data/heroes.ts), style épuré v5.
// Par élément, 18 places dans cet ordre (rareté, rôle, chef) — le même que ELEMENT_ROSTER :
//  0 commun protecteur · 1 commun guerrier · 2 commun tireur · 3 rare protecteur · 4 rare assassin · 5 rare soigneur
//  6 rare soutien ♛ · 7 épique protecteur ♛ · 8 épique guerrier · 9 épique tireur · 10 épique assassin
//  11 épique soigneur ♛ · 12 épique soutien · 13 légendaire guerrier ♛ · 14 légendaire tireur ♛
//  15 légendaire assassin · 16 légendaire soigneur · 17 légendaire soutien ♛
// Inspirations : mythologies et légendes du monde (domaine public), jamais un personnage d'un autre jeu.
require('./lib72.cjs'); require('./arms72.cjs');
const { build, tone, metal } = require('./fig72.cjs');

const ROSTER = [['common', 'protector', false], ['common', 'warrior', false], ['common', 'marksman', false], ['rare', 'protector', false], ['rare', 'assassin', false], ['rare', 'healer', false], ['rare', 'support', true],
  ['epic', 'protector', true], ['epic', 'warrior', false], ['epic', 'marksman', false], ['epic', 'assassin', false], ['epic', 'healer', true], ['epic', 'support', false],
  ['legendary', 'warrior', true], ['legendary', 'marksman', true], ['legendary', 'assassin', false], ['legendary', 'healer', false], ['legendary', 'support', true]];
const ELEMENTS = ['fire', 'wind', 'water', 'earth'];
const SPECS = { fire: [], wind: [], water: [], earth: [] };
/** Déclare un héros : élément, place (0 à 17), nom provisoire, inspiration, puis ses options de dessin. */
function H(element, i, name, from, spec) { SPECS[element][i] = { name, from, spec: { id: element[0] + element[1] + i, ...spec } }; }
module.exports = { H, SPECS, ROSTER, ELEMENTS, tone, metal,
  all() { const out = []; for (const el of ELEMENTS) SPECS[el].forEach((s, i) => { if (s) out.push({ element: el, index: i, rarity: ROSTER[i][0], role: ROSTER[i][1], leader: ROSTER[i][2], name: s.name, from: s.from, scale: s.spec.scale ?? 1, fig: build(s.spec) }); }); return out; } };
for (const el of ELEMENTS) require('./heroes-' + el + '.cjs');
