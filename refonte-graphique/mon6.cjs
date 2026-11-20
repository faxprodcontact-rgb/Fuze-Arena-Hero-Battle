// Les monstres : 12 familles de 6, des créatures (pas des humains), dessinées par morceaux animables.
// Dans chaque famille, 6 places : 0 rapide · 1 costaud · 2 tireur · 3 sorts ou soin · 4 élite · 5 boss.
// Même boîte que les héros (200 × 240, sol à y = 228, centre x = 106), tournés vers la droite : le combat les retourne.
const K = require('./fig6.cjs');
const { painter, tone, metal, mix, sf, blob } = require('./kit.cjs');
const { f, pt, limb, disc, ell } = K;

const FAMILIES = [
  { key: 'parade', name: 'La Parade des pétards', element: 'fire' }, { key: 'fauves', name: 'Les Fauves de cendre', element: 'fire' }, { key: 'idoles', name: 'Les Idoles d\'airain', element: 'fire' },
  { key: 'epouvantails', name: 'Les Épouvantails', element: 'wind' }, { key: 'ruche', name: 'La Ruche', element: 'wind' }, { key: 'voliere', name: 'La Volière d\'orage', element: 'wind' },
  { key: 'abysses', name: 'Les Abysses', element: 'water' }, { key: 'glaces', name: 'La Horde des glaces', element: 'water' }, { key: 'bayou', name: 'Le Bayou', element: 'water' },
  { key: 'echiquier', name: 'L\'Échiquier', element: 'earth' }, { key: 'cuirasses', name: 'Les Cuirassés', element: 'earth' }, { key: 'ronciers', name: 'Les Ronciers', element: 'earth' },
];
const SLOTS = ['fast', 'tank', 'shooter', 'caster', 'elite', 'boss'];
const SLOT_FR = { fast: 'Rapide', tank: 'Costaud', shooter: 'Tireur', caster: 'Sorts', elite: 'Élite', boss: 'Boss' };

let eyeId = 0;
/**
 * Construit une créature. spec : { id, colors, scale, atk, swing, far, piv, grp, wind, hit, shine, fx }
 * draw(h) peint les morceaux avec h.G(nom, () => …) ; chaque morceau a son contour et peut bouger seul.
 */
function creature(s, draw) {
  const P = painter(s.light ?? [0.5, -0.85]);
  const { S, raw } = P;
  const T = {};
  for (const [k, v] of Object.entries(s.colors ?? {})) T[k] = typeof v === 'string' ? tone(v) : v;
  const TK = (k, d) => (k && typeof k === 'object' ? k : k && k[0] === '#' ? tone(k) : T[k ?? d] ?? T[d]);
  const marks = [], glows = [];
  // Un morceau = un groupe SANS contour : la créature n'a qu'un contour, autour de sa silhouette entière. Là où un morceau
  // en recouvre un autre, il pose une ombre douce (et un filet léger) au lieu d'un trait dur : plus d'effet « formes collées ».
  const G = (name, fn) => { const id = `${s.id}-p${marks.length}`, start = P.body.length; raw(`<g id="${id}">`); fn(); raw('</g>'); marks.push({ name, id, start, end: P.body.length }); };
  const glow = (svg) => glows.push(svg);
  const halo = (x, y, r, c, op = 0.8) => glow(`<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" fill="${c}" opacity="${op}" filter="url(#glow)"/>`);
  /**
   * Un œil de bête : rond ou en amande, iris coloré, pupille ronde ou fendue, paupière en biais (regard dur).
   * o : { iris, sclera, pupil: 'slit' | 'round' | 'none', lid (0 = aucune … 1 = œil presque fermé), tilt (pente de la paupière), lidC, look: [dx, dy] }
   */
  const eye = (x, y, rx, ry, o = {}) => {
    const id = 'me' + eyeId++, lidC = o.lidC ?? '#1c1020', look = o.look ?? [rx * 0.18, 0], ir = Math.min(rx, ry) * (o.irisK ?? 0.72), tilt = o.tilt ?? 0.5, lid = o.lid ?? 0.3;
    let e = `<clipPath id="${id}"><ellipse cx="${f(x)}" cy="${f(y)}" rx="${f(rx)}" ry="${f(ry)}"/></clipPath><ellipse cx="${f(x)}" cy="${f(y)}" rx="${f(rx)}" ry="${f(ry)}" fill="${o.sclera ?? '#fbf6ef'}"/><g clip-path="url(#${id})">`;
    if (o.iris !== false) e += `<circle cx="${f(x + look[0])}" cy="${f(y + look[1])}" r="${f(ir)}" fill="${o.iris ?? '#ffcf3a'}"/>`;
    if (o.pupil === 'slit') e += `<ellipse cx="${f(x + look[0])}" cy="${f(y + look[1])}" rx="${f(ir * 0.26)}" ry="${f(ir * 0.92)}" fill="#120810"/>`;
    else if (o.pupil !== 'none') e += `<circle cx="${f(x + look[0])}" cy="${f(y + look[1])}" r="${f(ir * (o.pupilK ?? 0.5))}" fill="#120810"/>`;
    e += `<circle cx="${f(x + look[0] - ir * 0.36)}" cy="${f(y + look[1] - ir * 0.4)}" r="${f(Math.max(1.1, ir * 0.24))}" fill="#fff"/>`;
    if (lid > 0) { const yo = y - ry + 2 * ry * lid * (1 - tilt), yi = y - ry + 2 * ry * lid * (1 + tilt); e += `<path d="M${f(x - rx - 2)} ${f(y - ry - 3)} L${f(x + rx + 2)} ${f(y - ry - 3)} L${f(x + rx + 2)} ${f(yi)} L${f(x - rx - 2)} ${f(yo)} Z" fill="${lidC}"/>`; }
    e += `</g><ellipse cx="${f(x)}" cy="${f(y)}" rx="${f(rx)}" ry="${f(ry)}" fill="none" stroke="${lidC}" stroke-width="1.8"/>`;
    raw(e);
  };
  /** Des dents pointues le long d'une ligne a → b ; dir = +1 pointes vers le bas, −1 vers le haut. */
  const teeth = (a, b, n, len, dir = 1, c = '#fff8e6') => {
    let d = '';
    for (let i = 0; i < n; i++) { const t0 = (i + 0.1) / n, t1 = (i + 0.9) / n, p0 = [a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0], p1 = [a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1]; d += `M${pt(p0)} L${f((p0[0] + p1[0]) / 2)} ${f((p0[1] + p1[1]) / 2 + dir * len)} L${pt(p1)} Z `; }
    raw(`<path d="${d}" fill="${c}" stroke="#2a1420" stroke-width="0.9" stroke-linejoin="round"/>`);
  };
  /** Plusieurs membres d'un coup : [[points, largeur début, largeur fin], …]. */
  const L = (list, t, o = {}) => { for (const [p, w0 = 12, w1 = w0] of list) S(limb(p, w0, w1, o.N ?? 14), TK(t), { sh: o.sh ?? 4, far: o.far, inner: o.inner }); };
  /**
   * Pattes d'une bête à quatre pattes, trapue (grosse tête, pattes courtes) : cuisse ronde et jarret derrière, patte droite devant.
   * o : { front, hind (x des pattes de devant / de derrière), top (y de l'attache), w, t, dark, gap (décalage des pattes du fond), hoof, claws }
   * Renvoie { far(), near() } à appeler AVANT le corps : il recouvre les attaches.
   */
  const beast = (o) => {
    const g = 227, w = o.w ?? 18, top = o.top ?? 186, gap = o.gap ?? 14;
    const paw = (x, far) => {
      if (o.hoof) return S(`M${f(x - w * 0.5)} ${g - 10} L${f(x + w * 0.55)} ${g - 10} L${f(x + w * 0.62)} ${g} L${f(x - w * 0.58)} ${g} Z`, TK(o.hoofT ?? '#2a2026'), { sh: 2, far });
      S(`M${f(x - w * 0.62)} ${g} C${f(x - w * 0.7)} ${g - 10} ${f(x + w * 0.2)} ${g - 13} ${f(x + w * 0.72)} ${g - 8} C${f(x + w * 0.95)} ${g - 5} ${f(x + w * 0.95)} ${g} ${f(x + w * 0.8)} ${g} Z`, TK(far ? o.dark : o.t), { sh: 3, far });
      if (o.claws) raw(`<g fill="${o.clawC ?? '#f4ead0'}" stroke="#2a1a16" stroke-width="1" stroke-linejoin="round" opacity="${far ? 0.6 : 1}">${[0.2, 0.5, 0.8].map((k) => `<path d="M${f(x + w * k - 2.6)} ${g - 3} L${f(x + w * k + 3.4)} ${g + 1.5} L${f(x + w * k + 2.6)} ${g - 5} Z"/>`).join('')}</g>`);
      if (!far && !o.hoof) raw(`<path d="M${f(x + w * 0.02)} ${g - 3} q1 -5 4 -8 M${f(x + w * 0.34)} ${g - 3} q1 -5 4 -8" stroke="#2a1a16" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.45"/>`);
    };
    const fleg = (x, far) => { S(limb([[x, top], [x + 3, (top + g) / 2], [x, g - 7]], w, w * 0.86), TK(far ? o.dark : o.t), { sh: 4, far }); paw(x, far); };
    const hleg = (x, far) => { S(ell(x, top + 2, w * 1.02, w * 1.16), TK(far ? o.dark : o.t), { sh: 5, far }); S(limb([[x - 2, top + 10], [x - w * 0.75, (top + g) / 2 + 6], [x, g - 7]], w * 0.86, w * 0.76), TK(far ? o.dark : o.t), { sh: 4, far }); paw(x, far); };
    return { far: () => { fleg(o.front + gap, true); hleg(o.hind + gap, true); }, near: () => { hleg(o.hind, false); fleg(o.front, false); } };
  };
  /** Frange de poils : zigzag de (x0, y) à (x1, y), pointes vers le bas (d > 0) ou le haut. À coller dans un chemin. */
  const fringe = (x0, x1, y, n, d) => { let p = ''; for (let i = 0; i < n; i++) { const a = x0 + (x1 - x0) * (i + 0.5) / n, b = x0 + (x1 - x0) * (i + 1) / n; p += ` L${f(a)} ${f(y + d)} L${f(b)} ${f(y)}`; } return p; };
  /** Place et tourne ce qu'on dessine dedans (une tête baissée, une patte levée…). */
  const at = (t, fn) => { raw(`<g transform="${t}">`); fn(); raw('</g>'); };
  /** Un cou : il relie le corps à la tête d'un seul tenant (à dessiner dans le morceau du corps, la tête le recouvre). */
  const neck = (a, c, b, w0, w1, t, o = {}) => S(limb([a, c, b], w0, w1, 16), TK(t), { sh: o.sh ?? 6, hl: o.hl ?? 4, inner: o.inner });
  /** Une touffe de poils : n pointes en éventail autour de (x, y), tournée de « a » degrés. */
  const tuft = (x, y, a, len, w, t, o = {}) => { const n = o.n ?? 3; let d = `M${f(-w / 2)} 0`; for (let i = 0; i < n; i++) { const x0 = -w / 2 + w * i / n, x1 = -w / 2 + w * (i + 1) / n; d += ` L${f((x0 + x1) / 2 + (o.lean ?? 0))} ${f(-len * (i % 2 ? 0.78 : 1))} L${f(x1)} 0`; } at(`translate(${f(x)} ${f(y)}) rotate(${a})`, () => S(d + ` Q0 ${f(w * 0.3)} ${f(-w / 2)} 0 Z`, TK(t), { sh: 3, hl: 2, far: o.far })); };
  /** Sourcil : un trait épais au-dessus d'un œil, incliné vers le nez (regard dur). */
  const brow = (x, y, w, tilt = 1, c = '#1c1020', k = 4.5) => raw(`<path d="M${f(x - w / 2)} ${f(y - tilt * w * 0.22)} L${f(x + w / 2)} ${f(y + tilt * w * 0.22)}" stroke="${c}" stroke-width="${k}" stroke-linecap="round"/>`);
  /** Rayures, taches, ventre : à mettre dans « inner » d'une forme (elles restent dedans). */
  const stripes = (list, c, w = 5, op = 0.75) => `<g stroke="${c}" stroke-width="${w}" stroke-linecap="round" fill="none" opacity="${op}">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;
  const spots = (list, c, op = 0.7) => `<g fill="${c}" opacity="${op}">${list.map(([x, y, r, ry]) => `<ellipse cx="${x}" cy="${y}" rx="${r}" ry="${ry ?? r}"/>`).join('')}</g>`;
  const under = (d, c, op = 0.8) => `<path d="${d}" fill="${c}" opacity="${op}" filter="url(#g3)"/>`;
  const h = { S, raw, T, TK, G, L, at, neck, tuft, brow, stripes, spots, under, beast, fringe, glow, halo, eye, teeth, tone, metal, mix, sf, blob, ...K };
  draw(h);
  const flat = P.body, mk = 'mk-' + s.id;
  const maskDef = `<mask id="${mk}" maskUnits="userSpaceOnUse" x="-150" y="-150" width="600" height="600"><g filter="url(#mwh)">${marks.map((k) => `<use href="#${k.id}"/>`).join('')}</g></mask>`;
  const body = marks.map((k, i) => (i ? `<use href="#${k.id}" filter="url(#mcs)" mask="url(#${mk})"/>` : '') + flat.slice(k.start, k.end)).join('');
  const bloom = (x, y, r, c) => `<g transform="translate(${f(x)} ${f(y)})"><circle r="${f(r * 1.25)}" fill="${c}" opacity="0.7" filter="url(#glow)"/><circle r="${f(r * 0.6)}" fill="#fff" opacity="0.55" filter="url(#glow)"/></g>`;
  const fx = (s.shine ?? []).map(([x, y, r = 11, c = '#dff4ff']) => bloom(x, y, r, c)).join('');
  const rig = { swing: s.swing ?? [], far: s.far ?? [], piv: { swing: [106, 150], far: [130, 150], head: [106, 140], back: [80, 150], torso: [106, 190], ...(s.piv ?? {}) },
    atk: s.atk ?? 'slash', wind: s.wind ?? -40, hit: s.hit ?? 35, grp: { ...(s.grp ?? {}), ...(fx ? { shine: s.shineGrp ?? 'torso' } : {}) }, ...(s.fx ? { fx: s.fx } : {}), ...(s.heal ? { heal: true } : {}) };
  rig.soft = true;
  return { defs: P.defs + maskDef, body, glow: glows.join(''), fx, parts: marks.map((k) => ({ name: k.name, svg: flat.slice(k.start, k.end) })), rig, spec: s };
}

const SPECS = {};
/** Inscrit un monstre : famille, place (0 à 5), nom, réglages, dessin. */
function Mo(family, i, name, spec, draw) { (SPECS[family] ??= [])[i] = { name, spec: { id: family + '-' + (i + 1), ...spec }, draw }; }
function all(only) {
  const out = [];
  for (const fam of FAMILIES) (SPECS[fam.key] ?? []).forEach((m, i) => { if (m && (!only || only.includes(fam.key + ':' + i) || only.includes(fam.key))) out.push({ id: fam.key + '-' + (i + 1), family: fam.key, familyName: fam.name, element: fam.element, index: i, slot: SLOTS[i], name: m.name, scale: m.spec.scale ?? 1, fig: creature(m.spec, m.draw) }); });
  return out;
}
/** Filtres des monstres : ombre de contact entre morceaux (mcs), masque de la silhouette (mwh), contour unique (sil2). */
const MON_DEFS = '<filter id="mcs" x="-40%" y="-40%" width="180%" height="180%"><feMorphology in="SourceAlpha" operator="dilate" radius="0.6" result="d"/><feGaussianBlur in="SourceAlpha" stdDeviation="3.2" result="b"/><feOffset in="b" dy="1" result="o"/><feFlood flood-color="#1a0c2e" flood-opacity="0.46" result="c1"/><feComposite in="c1" in2="o" operator="in" result="sh"/><feFlood flood-color="#1a0c2e" flood-opacity="0.2" result="c2"/><feComposite in="c2" in2="d" operator="in" result="ln"/><feMerge><feMergeNode in="sh"/><feMergeNode in="ln"/></feMerge></filter>'
  + '<filter id="mwh" x="-10%" y="-10%" width="120%" height="120%"><feFlood flood-color="#fff"/><feComposite in2="SourceAlpha" operator="in"/></filter>'
  + '<filter id="sil2" x="-15%" y="-15%" width="130%" height="130%"><feOffset in="SourceAlpha" dx="5" dy="-7" result="a1"/><feComposite in="SourceAlpha" in2="a1" operator="out" result="r1"/><feGaussianBlur in="r1" stdDeviation="3.2" result="r1b"/><feFlood flood-color="#1a0c2e" flood-opacity="0.42"/><feComposite in2="r1b" operator="in" result="s0"/><feComposite in="s0" in2="SourceAlpha" operator="in" result="sh"/>'
  + '<feOffset in="SourceAlpha" dx="-4" dy="6" result="a2"/><feComposite in="SourceAlpha" in2="a2" operator="out" result="r2"/><feGaussianBlur in="r2" stdDeviation="2.2" result="r2b"/><feFlood flood-color="#fff6d8" flood-opacity="0.34"/><feComposite in2="r2b" operator="in" result="l0"/><feComposite in="l0" in2="SourceAlpha" operator="in" result="li"/>'
  + '<feMorphology in="SourceAlpha" operator="dilate" radius="2.3" result="d"/><feFlood flood-color="#190c24"/><feComposite in2="d" operator="in" result="o"/><feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/><feMergeNode in="sh"/><feMergeNode in="li"/></feMerge></filter>'
  // aura des élites (orangée) et des boss (rouge), derrière la créature
  + '<filter id="auraEl" x="-40%" y="-40%" width="180%" height="180%"><feMorphology in="SourceAlpha" operator="dilate" radius="3"/><feGaussianBlur stdDeviation="6" result="b"/><feFlood flood-color="#ff8a2a" flood-opacity="0.75"/><feComposite in2="b" operator="in"/></filter>'
  + '<filter id="auraBo" x="-40%" y="-40%" width="180%" height="180%"><feMorphology in="SourceAlpha" operator="dilate" radius="4"/><feGaussianBlur stdDeviation="7" result="b"/><feFlood flood-color="#ff2a3a" flood-opacity="0.9"/><feComposite in2="b" operator="in"/></filter>';
module.exports = { Mo, all, creature, FAMILIES, SLOTS, SLOT_FR, MON_DEFS, tone, metal, mix };
for (const fam of FAMILIES) { try { require('./m-' + fam.key + '.cjs'); } catch (e) { if (e.code !== 'MODULE_NOT_FOUND' || !String(e.message).includes('m-' + fam.key)) throw e; } }
