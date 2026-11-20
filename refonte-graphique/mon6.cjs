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
  const G = (name, fn) => { const start = P.body.length; raw('<g filter="url(#ol)">'); fn(); raw('</g>'); marks.push({ name, start, end: P.body.length }); };
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
      if (o.claws && !far) raw(`<path d="M${f(x + w * 0.3)} ${g - 1} l3 -6 M${f(x + w * 0.55)} ${g - 1} l3 -5 M${f(x + w * 0.05)} ${g - 1} l3 -6" stroke="#2a1a16" stroke-width="1.6" stroke-linecap="round" opacity="0.7"/>`);
    };
    const fleg = (x, far) => { S(limb([[x, top], [x + 3, (top + g) / 2], [x, g - 7]], w, w * 0.86), TK(far ? o.dark : o.t), { sh: 4, far }); paw(x, far); };
    const hleg = (x, far) => { S(ell(x, top + 2, w * 1.02, w * 1.16), TK(far ? o.dark : o.t), { sh: 5, far }); S(limb([[x - 2, top + 10], [x - w * 0.75, (top + g) / 2 + 6], [x, g - 7]], w * 0.86, w * 0.76), TK(far ? o.dark : o.t), { sh: 4, far }); paw(x, far); };
    return { far: () => { fleg(o.front + gap, true); hleg(o.hind + gap, true); }, near: () => { hleg(o.hind, false); fleg(o.front, false); } };
  };
  /** Frange de poils : zigzag de (x0, y) à (x1, y), pointes vers le bas (d > 0) ou le haut. À coller dans un chemin. */
  const fringe = (x0, x1, y, n, d) => { let p = ''; for (let i = 0; i < n; i++) { const a = x0 + (x1 - x0) * (i + 0.5) / n, b = x0 + (x1 - x0) * (i + 1) / n; p += ` L${f(a)} ${f(y + d)} L${f(b)} ${f(y)}`; } return p; };
  const h = { S, raw, T, TK, G, L, beast, fringe, glow, halo, eye, teeth, tone, metal, mix, sf, blob, ...K };
  draw(h);
  const body = P.body;
  const bloom = (x, y, r, c) => `<g transform="translate(${f(x)} ${f(y)})"><circle r="${f(r * 1.25)}" fill="${c}" opacity="0.7" filter="url(#glow)"/><circle r="${f(r * 0.6)}" fill="#fff" opacity="0.55" filter="url(#glow)"/></g>`;
  const fx = (s.shine ?? []).map(([x, y, r = 11, c = '#dff4ff']) => bloom(x, y, r, c)).join('');
  const rig = { swing: s.swing ?? [], far: s.far ?? [], piv: { swing: [106, 150], far: [130, 150], head: [106, 140], back: [80, 150], torso: [106, 190], ...(s.piv ?? {}) },
    atk: s.atk ?? 'slash', wind: s.wind ?? -40, hit: s.hit ?? 35, grp: { ...(s.grp ?? {}), ...(fx ? { shine: s.shineGrp ?? 'torso' } : {}) }, ...(s.fx ? { fx: s.fx } : {}), ...(s.heal ? { heal: true } : {}) };
  return { defs: P.defs, body, glow: glows.join(''), fx, parts: marks.map((k) => ({ name: k.name, svg: body.slice(k.start, k.end) })), rig, spec: s };
}

const SPECS = {};
/** Inscrit un monstre : famille, place (0 à 5), nom, réglages, dessin. */
function Mo(family, i, name, spec, draw) { (SPECS[family] ??= [])[i] = { name, spec: { id: family + '-' + (i + 1), ...spec }, draw }; }
function all(only) {
  const out = [];
  for (const fam of FAMILIES) (SPECS[fam.key] ?? []).forEach((m, i) => { if (m && (!only || only.includes(fam.key + ':' + i) || only.includes(fam.key))) out.push({ id: fam.key + '-' + (i + 1), family: fam.key, familyName: fam.name, element: fam.element, index: i, slot: SLOTS[i], name: m.name, scale: m.spec.scale ?? 1, fig: creature(m.spec, m.draw) }); });
  return out;
}
module.exports = { Mo, all, creature, FAMILIES, SLOTS, SLOT_FR, tone, metal, mix };
for (const fam of FAMILIES) { try { require('./m-' + fam.key + '.cjs'); } catch (e) { if (e.code !== 'MODULE_NOT_FOUND' || !String(e.message).includes('m-' + fam.key)) throw e; } }
