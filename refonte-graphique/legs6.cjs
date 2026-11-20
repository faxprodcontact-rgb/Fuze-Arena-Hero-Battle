// Bas du corps (version 6) : jambes de toutes sortes, robes et manteaux, corps d'animaux ; et les habits du buste.
const K = require('./fig6.cjs');
const { LIB, CX, f, pt, poly, add, limb, disc, ell, bar, saw, sf, tone, mix } = K;

// ---------- pieds ----------
function foot(h, x, kind, t, o = {}) {
  const { S } = h, y = 228;
  const low = `M${x - 12} 213 L${x + 13} 213 L${x + 16} 219 L${x + 28} 222 C${x + 33} 224 ${x + 32} ${y} ${x + 27} ${y} L${x - 12} ${y} C${x - 16} ${y} ${x - 16} 224 ${x - 14} 220 Z`;
  const boot = `M${x - 14} 204 L${x + 15} 204 L${x + 17} 215 L${x + 29} 221 C${x + 34} 224 ${x + 33} ${y} ${x + 28} ${y} L${x - 14} ${y} C${x - 18} ${y} ${x - 18} 224 ${x - 16} 220 Z`;
  const cuff = `<path d="M${x - 16} 207 L${x + 18} 207" stroke="${t.light}" stroke-width="3" opacity="0.6"/>`;
  switch (kind) {
    case 'boot': return S(boot, t, { sh: 5, inner: cuff });
    case 'fur': S(boot, t, { sh: 5 }); return S(`M${x - 17} 210 L${x - 17} 200 L${x - 9} 204 L${x - 3} 198 L${x + 3} 204 L${x + 10} 198 L${x + 18} 204 L${x + 18} 210 Z`, h.TK(o.furT, 'fur'), { sh: 3 });
    case 'sabaton': return S(`M${x - 14} 204 L${x + 15} 204 L${x + 18} 214 L${x + 36} 225 L${x + 36} ${y} L${x - 14} ${y} C${x - 18} ${y} ${x - 18} 224 ${x - 16} 220 Z`, t, { sh: 5, inner: `<path d="M${x - 16} 212 L${x + 18} 212 M${x + 4} 220 L${x + 24} 220" stroke="${t.shadow}" stroke-width="2" opacity="0.7"/>` });
    case 'shoe': return S(low, t, { sh: 4 });
    case 'bare': return S(low, t, { sh: 4, inner: `<path d="M${x + 20} 222 L${x + 22} 228 M${x + 26} 223 L${x + 28} 228" stroke="${t.shadow}" stroke-width="1.4" opacity="0.7"/>` });
    case 'sandal': return S(low, t, { sh: 4, inner: `<path d="M${x - 14} 217 L${x + 16} 217 M${x + 4} 213 L${x + 20} 224 M${x - 16} 226.5 L${x + 32} 226.5" stroke="${h.TK(o.strapT, 'belt').base}" stroke-width="3"/>` });
    case 'geta': S(`M${x - 14} 221 L${x + 32} 221 L${x + 32} 225 L${x + 12} 225 L${x + 12} ${y} L${x + 2} ${y} L${x + 2} 225 L${x - 14} 225 Z`, h.TK(o.woodT, 'wood'), { sh: 3 }); return S(`M${x - 12} 209 L${x + 13} 209 L${x + 16} 215 L${x + 28} 218 C${x + 32} 219 ${x + 32} 221 ${x + 28} 221 L${x - 12} 221 Z`, t, { sh: 3, inner: `<path d="M${x + 2} 209 L${x + 18} 220" stroke="${h.TK(o.strapT, 'belt').base}" stroke-width="3"/>` });
    case 'hoof': return S(`M${x - 10} 213 L${x + 11} 213 L${x + 18} ${y} L${x - 14} ${y} Z`, t, { sh: 4, inner: `<path d="M${x + 2} 220 L${x + 3} ${y}" stroke="${t.shadow}" stroke-width="2"/>` });
    case 'talon': S(limb([[x - 2, 214], [x - 12, 220], [x - 16, y]], 7, 2), t, { sh: 2, hl: 2 }); S(limb([[x, 213], [x + 14, 218], [x + 28, y]], 8, 2), t, { sh: 2, hl: 2 }); return S(limb([[x, 214], [x + 6, 222], [x + 12, y]], 8, 2), t, { sh: 2, hl: 2 });
    case 'paw': return S(`M${x - 12} 214 C${x - 14} 205 ${x + 12} 205 ${x + 16} 213 L${x + 26} 219 C${x + 33} 221 ${x + 33} ${y} ${x + 26} ${y} L${x - 12} ${y} C${x - 17} 226 ${x - 17} 218 ${x - 12} 214 Z`, t, { sh: 4, inner: `<path d="M${x + 18} 222 L${x + 20} ${y} M${x + 25} 222 L${x + 27} ${y}" stroke="${t.shadow}" stroke-width="1.6"/>` });
    case 'webbed': return S(`M${x - 10} 213 L${x + 10} 213 L${x + 36} 225 L${x + 34} ${y} L${x - 13} ${y} Z`, t, { sh: 4, inner: `<path d="M${x + 4} 216 L${x + 22} ${y} M${x + 8} 215 L${x + 32} 226" stroke="${t.shadow}" stroke-width="1.6" opacity="0.7"/>` });
    case 'stone': return S(`M${x - 17} 202 L${x + 18} 200 L${x + 28} ${y} L${x - 20} ${y} Z`, t, { sh: 5 });
    default: throw new Error('pied inconnu : ' + kind);
  }
}
const STANCE = { wide: [88, 76, 126, 148], narrow: [93, 90, 119, 128], lunge: [86, 62, 126, 156], mid: [90, 82, 124, 140] };

// ---------- jambes : forme de la jambe + type de pied + façon de se tenir ----------
LIB.legs.legs = { draw(h, o) {
  const { S } = h, [hb, fb, hf, ff] = STANCE[o.stance ?? 'wide'], hy = h.hipY, leg = o.leg ?? 'straight', t = h.TK(o.t, leg === 'bare' ? 'skin' : 'pants'), ft = h.TK(o.footT, 'boot'), fk = o.foot ?? 'boot';
  const top = ['boot', 'fur', 'sabaton', 'stone'].includes(fk) ? 212 : 216, bendF = o.stance === 'lunge' ? 16 : 6, bendB = o.stance === 'lunge' ? -2 : -4;
  const one = (hx, fx, bend, far) => {
    const pts = [[hx, hy], [(hx + fx) / 2 + bend, (hy + top) / 2], [fx, top]];
    if (leg === 'hakama') { S(poly([[hx - 15, hy - 4], [hx + 15, hy - 4], [fx + 21, top + 2], [fx - 21, top + 2]]), t, { sh: 7, far, inner: `<path d="M${hx - 4} ${hy} L${fx - 8} ${top + 2} M${hx + 5} ${hy} L${fx + 6} ${top + 2}" stroke="${t.shadow}" stroke-width="2" opacity="0.6"/>` }); return; }
    const w = leg === 'baggy' ? [36, 22] : leg === 'thick' ? [31, 26] : leg === 'thin' ? [19, 15] : [25, 21];
    let inner = '';
    if (o.knee) { const p = K.qpoint(pts, 0.5); inner += `<circle cx="${f(p[0] + 3)}" cy="${f(p[1])}" r="10" fill="${h.TK(o.knee).base}"/>`; }
    if (o.shin) { const p = K.qpoint(pts, 0.56), q = K.qpoint(pts, 1); inner += `<path d="M${pt(p)} L${pt(q)}" stroke="${h.TK(o.shin).base}" stroke-width="15" stroke-linecap="round"/><path d="M${pt(add(p, [3, 0]))} L${pt(add(q, [3, 0]))}" stroke="${h.TK(o.shin).light}" stroke-width="3" opacity="0.6"/>`; }
    if (o.wrap) { for (const tt of [0.55, 0.7, 0.85]) { const p = K.qpoint(pts, tt); inner += `<path d="M${f(p[0] - 16)} ${f(p[1] - 3)} L${f(p[0] + 16)} ${f(p[1] + 3)}" stroke="${h.TK(o.wrap).base}" stroke-width="4"/>`; } }
    if (o.anklet) { const p = K.qpoint(pts, 0.9); inner += `<path d="M${f(p[0] - 16)} ${f(p[1])} L${f(p[0] + 16)} ${f(p[1])}" stroke="${h.TK(o.anklet).base}" stroke-width="5"/>`; }
    if (o.stripe) inner += `<path d="M${hx - 20} ${hy + 14} L${fx + 20} ${hy + 14} M${hx - 20} ${hy + 30} L${fx + 20} ${hy + 30}" stroke="${h.TK(o.stripe).base}" stroke-width="6"/>`;
    S(limb(pts, w[0], w[1]), t, { sh: 6, far, inner });
    if (leg === 'baggy') S(limb([[fx - 9, top], [fx, top + 2], [fx + 9, top]], 8, 8, 4), h.TK(o.cuffT, 'belt'), { sh: 2, hl: 2, rim: false, far });
  };
  one(hb, fb, bendB, false); foot(h, fb, fk, ft, o);
  one(hf, ff, bendF, false); foot(h, ff, fk, ft, o);
} };
// pattes d'animal : cuisse vers l'avant, jarret vers l'arrière, puis sabot, serres ou patte
LIB.legs.beast = { draw(h, o) {
  const { S } = h, hy = h.hipY, t = h.TK(o.t, 'pants'), ft = h.TK(o.footT, 'boot'), fk = o.foot ?? 'hoof';
  for (const [hx, fx] of [[90, 78], [124, 144]]) {
    S(limb([[hx, hy], [hx + 16, hy + 14], [fx + 8, hy + 26]], 27, 19), t, { sh: 6 });
    S(limb([[fx + 8, hy + 26], [fx - 8, hy + 36], [fx, 214]], 17, 12), t, { sh: 4 });
    foot(h, fx, fk, ft, o);
  }
} };
// une jambe levée (danse) ; jambes jointes qui flottent ; blocs de pierre
LIB.legs.dance = { draw(h, o) {
  const { S } = h, hy = h.hipY, t = h.TK(o.t, 'pants'), ft = h.TK(o.footT, 'boot');
  S(limb([[94, hy], [92, 192], [98, 214]], 24, 19), t, { sh: 6 }); foot(h, 98, o.foot ?? 'bare', ft, o);
  S(limb([[122, hy], [156, hy + 8], [146, 204]], 24, 17), t, { sh: 6 });
  S('M136 200 L156 200 L172 214 C176 218 172 222 166 220 L138 212 Z', ft, { sh: 3 });
} };
LIB.legs.float = { draw(h, o) {
  const { S } = h, hy = h.hipY, t = h.TK(o.t, 'pants'), ft = h.TK(o.footT, 'boot');
  S(limb([[98, hy], [88, 190], [84, 208]], 20, 13), t, { sh: 5 }); S('M76 204 L92 206 L90 222 C88 228 80 226 78 220 Z', ft, { sh: 3 });
  S(limb([[116, hy], [112, 192], [104, 212]], 20, 13), t, { sh: 5 }); S('M96 208 L112 210 L108 226 C106 232 98 230 96 224 Z', ft, { sh: 3 });
} };
LIB.legs.stone = { draw(h, o) {
  const { S } = h, hy = h.hipY, t = h.TK(o.t, 'pants'), ft = h.TK(o.footT, 'boot');
  S(poly([[72, hy - 4], [104, hy - 4], [100, 206], [62, 206]]), t, { sh: 6 }); foot(h, 80, 'stone', ft);
  S(poly([[110, hy - 4], [144, hy - 4], [158, 206], [122, 206]]), t, { sh: 6 }); foot(h, 140, 'stone', ft);
} };
// ---------- corps d'animaux à la place des jambes ----------
LIB.legs.tail = { draw(h, o) { // queue de poisson, nageoire vers l'arrière
  const { S, T } = h;
  S('M96 214 C78 198 58 196 36 178 C46 200 44 216 28 232 C56 226 82 232 104 230 Z', T.fin ?? T.tail, { sh: 5, inner: `<path d="M94 218 L48 192 M96 222 L42 216" stroke="${(T.fin ?? T.tail).shadow}" stroke-width="2" opacity="0.5"/>` });
  let sc = ''; for (let r = 0; r < 3; r++) for (let i = 0; i < 4; i++) sc += `<path d="M${96 + i * 16 + r * 6} ${182 + r * 12} q7 7 14 0" stroke="${T.tail.light}" stroke-width="2" fill="none" opacity="0.6"/>`;
  S(limb([[CX, h.hipY - 2], [158, 200], [100, 220]], 50, 18, 16), T.tail, { sh: 8, inner: sc });
} };
LIB.legs.naga = { draw(h, o) { // corps de serpent enroulé
  const { S, T } = h, bl = (T.belly ?? T.tail).light;
  S(limb([[124, 216], [70, 236], [30, 198]], 26, 4), T.tail, { sh: 6 });
  S(limb([[CX, h.hipY - 2], [170, 196], [118, 220]], 48, 26, 16), T.tail, { sh: 8, inner: `<path d="M98 ${h.hipY + 8} C122 198 142 204 154 200" stroke="${bl}" stroke-width="10" fill="none" opacity="0.5"/>` });
} };
LIB.legs.smoke = { draw(h, o) { // pas de jambes : une volute
  const { S, T } = h;
  h.glow(`<ellipse cx="96" cy="210" rx="42" ry="16" fill="${T.smoke.base}" opacity="0.5" filter="url(#glow)"/>`);
  S(limb([[CX, h.hipY - 2], [146, 206], [72, 226]], 52, 4, 18), T.smoke, { sh: 8, inner: sf('M96 180 C114 202 110 216 90 224', T.smoke.light, 5, 0.5, 2) });
} };
LIB.legs.tentacles = { draw(h, o) {
  const { S, T } = h, y = h.hipY;
  for (const p of [[[90, y], [50, 186], [30, 226]], [[122, y], [164, 186], [186, 222]], [[100, y + 2], [84, 208], [58, 230]], [[114, y + 2], [134, 210], [158, 230]]]) S(limb(p, 23, 4), T.tail, { sh: 5 });
  S(limb([[CX, y], [114, 206], [104, 231]], 23, 5), T.tail, { sh: 5, inner: `<g fill="${T.tail.light}" opacity="0.7"><circle cx="108" cy="190" r="2.6"/><circle cx="110" cy="202" r="2.4"/><circle cx="108" cy="214" r="2"/></g>` });
} };
LIB.legs.scorpion = { draw(h, o) { // corps de scorpion : abdomen bas, quatre pattes
  const { S, T } = h, t = T.tail, y = h.hipY;
  for (const [p, far] of [[[[126, 196], [150, 176], [176, 228]], 1], [[[116, 198], [134, 186], [150, 228]], 1], [[[92, 198], [72, 182], [54, 228]], 0], [[[84, 196], [56, 172], [30, 228]], 0]]) S(limb(p, 9, 3), t, { sh: 3, far: !!far });
  S(ell(CX, 196, 34, 20), t, { sh: 7, inner: `<path d="M80 190 Q106 204 132 190 M76 200 Q106 214 136 200" stroke="${t.shadow}" stroke-width="2.4" fill="none" opacity="0.7"/>` });
} };
LIB.legs.spider = { draw(h, o) { // abdomen d'araignée à l'arrière, six pattes
  const { S, T } = h, t = T.tail;
  S(ell(70, 194, 34, 26), t, { sh: 8, inner: o.mark ? `<path d="M58 184 L70 198 L82 184 L70 208 Z" fill="${o.mark}"/>` : '' });
  for (const [p, far] of [[[[126, 192], [162, 150], [190, 228]], 1], [[[120, 196], [146, 168], [164, 228]], 1], [[[112, 198], [128, 184], [138, 228]], 1], [[[96, 198], [80, 178], [58, 228]], 0], [[[92, 194], [56, 160], [26, 228]], 0], [[[100, 200], [100, 190], [96, 228]], 0]]) S(limb(p, 8, 2.5), t, { sh: 3, far: !!far });
  S(ell(CX, 192, 22, 14), t, { sh: 5 });
} };

// ---------- robes : le buste et le bas en une seule forme, jusqu'au sol ----------
function robe(shapeOf) {
  return { robe: true, draw(h, o, inner) {
    const { S, B } = h, G = h.ground, t = h.TK(o.t, 'cloth'), w = o.w ?? 52, sw = B.sw, sy = B.sy;
    let extra = '';
    if (o.panel) extra += `<path d="M${CX - 9} 100 L${CX + 13} 100 L${CX + 26} 240 L${CX - 22} 240 Z" fill="${h.TK(o.panel).base}"/>`;
    if (o.trim) extra += `<path d="M${CX - w - 6} ${G - 8} Q${CX} ${G + 6} ${CX + w + 8} ${G - 8}" stroke="${h.TK(o.trim).base}" stroke-width="7" fill="none"/>`;
    if (o.tiers) extra += `<path d="M${CX - w} ${G - 34} Q${CX} ${G - 22} ${CX + w} ${G - 34} M${CX - w} ${G - 62} Q${CX} ${G - 50} ${CX + w} ${G - 62}" stroke="${t.shadow}" stroke-width="2.6" fill="none" opacity="0.7"/>`;
    if (o.folds) extra += sf(`M${CX - 18} ${G - 60} L${CX - 26} ${G} M${CX + 22} ${G - 60} L${CX + 34} ${G}`, t.shadow, 3, 0.35, 1);
    if (o.base === 'mist') h.glow(`<ellipse cx="${CX}" cy="${G - 2}" rx="${w + 10}" ry="12" fill="${o.baseC ?? '#dff4ff'}" opacity="0.7" filter="url(#glow)"/>`);
    S(shapeOf(CX, sw, sy, w, G - 6, o), t, { sh: 10, inner: extra + (inner ?? '') });
    if (o.feet) { const ft = h.TK(o.feet, 'boot'); S(`M${CX + 6} ${G - 9} L${CX + 34} ${G - 9} C${CX + 42} ${G - 7} ${CX + 42} ${G} ${CX + 36} ${G} L${CX + 6} ${G} Z`, ft, { sh: 3 }); }
    if (o.base === 'water') S(ell(CX, G - 3, w + 14, 7), tone(o.baseC ?? '#6fc8f0'), { sh: 2, hl: 2 });
  } };
}
const side = (cx, sw, sy) => `M${cx - sw} ${sy} Q${cx} ${sy - 11} ${cx + sw} ${sy}`;
LIB.legs.bell = robe((cx, sw, sy, w, g) => `${side(cx, sw, sy)} C${cx + sw + 8} ${sy + 30} ${cx + w - 6} ${g - 40} ${cx + w} ${g} Q${cx} ${g + 12} ${cx - w} ${g} C${cx - w + 6} ${g - 40} ${cx - sw - 8} ${sy + 30} ${cx - sw} ${sy} Z`);
LIB.legs.straight = robe((cx, sw, sy, w, g) => { const k = Math.min(w, 42); return `${side(cx, sw, sy)} C${cx + sw + 2} ${sy + 20} ${cx + k - 4} ${sy + 50} ${cx + k} ${g} Q${cx} ${g + 9} ${cx - k} ${g} C${cx - k + 4} ${sy + 50} ${cx - sw - 2} ${sy + 20} ${cx - sw} ${sy} Z`; });
LIB.legs.mermaid = robe((cx, sw, sy, w, g) => `${side(cx, sw, sy)} C${cx + sw + 2} ${sy + 24} ${cx + 30} ${g - 60} ${cx + 30} ${g - 34} C${cx + 32} ${g - 16} ${cx + w - 8} ${g - 8} ${cx + w} ${g} Q${cx} ${g + 12} ${cx - w} ${g} C${cx - w + 8} ${g - 8} ${cx - 32} ${g - 16} ${cx - 30} ${g - 34} C${cx - 30} ${g - 60} ${cx - sw - 2} ${sy + 24} ${cx - sw} ${sy} Z`);
LIB.legs.ragged = robe((cx, sw, sy, w, g) => { const pts = Array.from({ length: 8 }, (_, i) => [cx + w - (2 * w) * i / 7, g - (i % 2 ? 0 : 3)]); return `${side(cx, sw, sy)} C${cx + sw + 8} ${sy + 30} ${cx + w - 6} ${g - 40} ${cx + w} ${g - 3}` + saw(pts, 9, [0, 0]) + ` C${cx - w + 6} ${g - 40} ${cx - sw - 8} ${sy + 30} ${cx - sw} ${sy} Z`; });

// ---------- habits du buste (peints DANS le buste, donc toujours d'un bord à l'autre) ----------
const Ch = LIB.chest;
Ch.plate = (h, o) => { const t = h.TK(o.t, 'steel'), y = h.B.wy; return `<path d="M20 90 L190 90 L190 ${y - 2} C130 ${y + 8} 90 ${y + 8} 20 ${y - 2} Z" fill="${t.base}"/><path d="M${CX + 2} 112 L${CX + 2} ${y + 4}" stroke="${t.shadow}" stroke-width="2" opacity="0.6"/><path d="M62 128 C90 119 126 119 152 128" stroke="${t.light}" stroke-width="3" fill="none" opacity="0.7"/>`; };
Ch.segments = (h, o) => { const t = h.TK(o.t, 'steel'), y = h.B.wy; let s = Ch.plate(h, o); for (let i = 1; i < 4; i++) s += `<path d="M20 ${118 + i * 10} C90 ${126 + i * 10} 130 ${126 + i * 10} 190 ${118 + i * 10}" stroke="${t.shadow}" stroke-width="2.2" fill="none" opacity="0.7"/>`; return s; };
Ch.scales = (h, o) => { const t = h.TK(o.t, 'steel'), y = h.B.wy; let s = `<path d="M20 90 L190 90 L190 ${y + 30} L20 ${y + 30} Z" fill="${t.base}"/>`; for (let r = 0; r < 6; r++) for (let i = 0; i < 9; i++) s += `<path d="M${52 + i * 13 + (r % 2) * 6} ${116 + r * 11} q6.5 7 13 0" stroke="${t.shadow}" stroke-width="1.8" fill="none" opacity="0.7"/>`; return s; };
Ch.vest = (h, o) => { const t = h.TK(o.t, 'cloth'); return `<path d="M20 90 L${CX - 8} 90 L${CX - 16} 200 L20 200 Z M${CX + 12} 90 L190 90 L190 200 L${CX + 24} 200 Z" fill="${t.base}"/><path d="M${CX - 8} 104 L${CX - 16} 200 M${CX + 12} 104 L${CX + 24} 200" stroke="${t.shadow}" stroke-width="2.4" opacity="0.7"/>`; };
Ch.apron = (h, o) => { const t = h.TK(o.t, 'cloth'); return `<path d="M${CX - 20} 108 L${CX + 22} 108 L${CX + 34} 210 L${CX - 30} 210 Z" fill="${t.base}"/><path d="M${CX - 20} 108 L${CX - 30} 210 M${CX + 22} 108 L${CX + 34} 210" stroke="${t.shadow}" stroke-width="2" opacity="0.6"/>`; };
Ch.belly = (h, o) => `<path d="M${CX - 10} 118 C${CX + 12} 113 ${CX + 30} 124 ${CX + 32} 152 C${CX + 18} 162 ${CX - 2} 162 ${CX - 12} 150 Z" fill="${h.TK(o.t, 'muz').base}"/>`;
Ch.sash = (h, o) => { const t = h.TK(o.t, 'belt'); return `<path d="M60 108 L84 104 L160 158 L160 178 L134 178 Z" fill="${t.base}"/><path d="M60 108 L134 178" stroke="${t.shadow}" stroke-width="2" opacity="0.6"/>`; };
Ch.straps = (h, o) => { const t = h.TK(o.t, 'belt'); return `<path d="M66 110 L150 166 M146 110 L62 166" stroke="${t.base}" stroke-width="8"/><circle cx="${CX}" cy="138" r="7" fill="${h.T.gold.base}" stroke="${t.shadow}" stroke-width="2"/>`; };
Ch.stripe = (h, o) => `<path d="M${CX - 9} 90 L${CX + 13} 90 L${CX + 26} 240 L${CX - 22} 240 Z" fill="${h.TK(o.t, 'belt').base}"/>`;
Ch.muscle = (h) => `<path d="M82 138 C94 147 104 147 ${CX + 4} 140 C116 147 128 147 140 137 M${CX + 4} 142 L${CX + 4} 158 M92 154 C100 158 108 158 ${CX + 4} 156 C118 158 126 158 132 153" stroke="${h.T.skin.shadow}" stroke-width="2.2" fill="none" opacity="0.55" stroke-linecap="round"/>`;
Ch.toga = (h, o) => { const t = h.TK(o.t, 'cloth'); return `<path d="M20 152 L20 250 L190 250 L190 90 L128 90 C120 122 92 142 20 152 Z" fill="${t.base}"/><path d="M128 100 C118 126 92 144 40 152 M150 110 C140 140 110 160 60 172" stroke="${t.shadow}" stroke-width="2.4" fill="none" opacity="0.5"/>`; };
Ch.lamellar = (h, o) => { const t = h.TK(o.t, 'steel'), y = h.B.wy; let s = `<path d="M20 90 L190 90 L190 ${y + 26} L20 ${y + 26} Z" fill="${t.base}"/>`; for (let i = 0; i < 5; i++) s += `<path d="M20 ${118 + i * 11} L190 ${118 + i * 11}" stroke="${t.shadow}" stroke-width="2" opacity="0.6"/>`; for (let i = 0; i < 10; i++) s += `<path d="M${54 + i * 11} 112 L${54 + i * 11} ${y + 26}" stroke="${t.shadow}" stroke-width="1.2" opacity="0.45"/>`; return s; };
Ch.collarV = (h, o) => { const t = h.TK(o.t, 'belt'); return `<path d="M82 106 L${CX + 4} 150 L132 104" stroke="${t.base}" stroke-width="7" fill="none" stroke-linejoin="round"/>`; };
Ch.wrap = (h, o) => { const t = h.TK(o.t, 'belt'); return `<path d="M78 104 L${CX + 22} 160 M134 104 L${CX + 2} 132" stroke="${t.base}" stroke-width="6" fill="none" stroke-linecap="round"/>`; }; // croisé de kimono
Ch.spots = (h, o) => { let s = ''; for (const [x, y, r] of o.at ?? [[84, 134, 5], [80, 152, 4], [128, 146, 4]]) s += `<circle cx="${x}" cy="${y}" r="${r}" fill="${o.c ?? '#3a2a22'}"/>`; return s; };
Ch.cracks = (h, o) => `<path d="${o.d ?? 'M80 126 L96 142 L88 160 L102 176 M132 124 L122 144 L134 160 M96 142 L112 148'}" stroke="${o.c}" stroke-width="${o.w ?? 3.2}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
Ch.raw = (h, o) => o.svg;
module.exports = { foot, STANCE, robe };
