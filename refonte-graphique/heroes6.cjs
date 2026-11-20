// Les 72 héros, version 6 : chaque héros est dessiné pour lui-même (carrure, jambes, visage, pose, objets).
// Par élément, 18 places dans l'ordre de ELEMENT_ROSTER (src/core/data/heroes.ts) :
//  0 commun protecteur · 1 commun guerrier · 2 commun tireur · 3 rare protecteur · 4 rare assassin · 5 rare soigneur
//  6 rare soutien ♛ · 7 épique protecteur ♛ · 8 épique guerrier · 9 épique tireur · 10 épique assassin
//  11 épique soigneur ♛ · 12 épique soutien · 13 légendaire guerrier ♛ · 14 légendaire tireur ♛
//  15 légendaire assassin · 16 légendaire soigneur · 17 légendaire soutien ♛
require('./face6.cjs'); require('./legs6.cjs'); require('./wear6.cjs'); require('./items6.cjs');
const { build, tone, metal } = require('./fig6.cjs');
const ROSTER = [['common', 'protector', false], ['common', 'warrior', false], ['common', 'marksman', false], ['rare', 'protector', false], ['rare', 'assassin', false], ['rare', 'healer', false], ['rare', 'support', true],
  ['epic', 'protector', true], ['epic', 'warrior', false], ['epic', 'marksman', false], ['epic', 'assassin', false], ['epic', 'healer', true], ['epic', 'support', false],
  ['legendary', 'warrior', true], ['legendary', 'marksman', true], ['legendary', 'assassin', false], ['legendary', 'healer', false], ['legendary', 'support', true]];
const ELEMENTS = ['fire', 'wind', 'water', 'earth'];
const ATK = { protector: 'slash', warrior: 'slash', marksman: 'shoot', assassin: 'stab', healer: 'cast', support: 'cast' };
const SPECS = { fire: [], wind: [], water: [], earth: [] };
function H(element, i, name, from, spec) { SPECS[element][i] = { name, from, spec: { id: element[0] + element[1] + i, atk: ATK[ROSTER[i][1]], ...spec } }; }
module.exports = { H, SPECS, ROSTER, ELEMENTS, tone, metal,
  all(only) { const out = []; for (const el of ELEMENTS) SPECS[el].forEach((s, i) => { if (s && (!only || only.includes(el + ':' + i))) out.push({ element: el, index: i, rarity: ROSTER[i][0], role: ROSTER[i][1], leader: ROSTER[i][2], name: s.name, from: s.from, scale: s.spec.scale ?? 1, fig: build(s.spec) }); }); return out; } };
for (const el of ELEMENTS) { try { require('./h6-' + el + '.cjs'); } catch (e) { if (e.code !== 'MODULE_NOT_FOUND' || !String(e.message).includes('h6-' + el)) throw e; } }
