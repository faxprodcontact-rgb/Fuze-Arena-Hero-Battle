// Outils de peinture : chaque forme reçoit un contour coloré sombre, une zone éclairée, une ombre, un dégradé de volume
// et un contre-jour. Les détails (reflets, gravures, plis) se peignent à l'intérieur de la forme.
let uid = 0;
const hx = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, t) => { const A = hx(a), B = hx(b); return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
const tone = (base, o = {}) => ({
  base, light: mix(base, o.lightTo ?? '#fff3d0', o.l ?? 0.45), shadow: mix(base, o.shadowTo ?? '#2c1250', o.s ?? 0.48),
  outline: mix(base, '#150a20', 0.8), edge: mix(base, '#2a1238', 0.62), rim: mix(base, '#d6ecff', 0.65), metal: !!o.metal,
});
const metal = (base) => tone(base, { metal: true, l: 0.7, s: 0.55, shadowTo: '#1d1840' });

function painter(L = [0.5, -0.85]) {
  let defs = '';
  const out = [];
  const sx = L[0] >= 0 ? 1 : -1;
  /** Peint une forme. Renvoie l'identifiant de sa découpe (pour y projeter des ombres ensuite). */
  function S(d, t, o = {}) {
    const id = 's' + uid++;
    const sh = o.sh ?? (t.metal ? 6 : 8), hl = o.hl ?? (t.metal ? 3.5 : 5), bl = o.bl ?? (t.metal ? 1 : 2);
    defs += `<clipPath id="${id}"><path d="${d}"/></clipPath>`;
    defs += `<mask id="${id}m" maskUnits="userSpaceOnUse" x="-150" y="-150" width="600" height="600"><rect x="-150" y="-150" width="600" height="600" fill="#fff"/><path d="${d}" fill="#000" transform="translate(${(L[0] * sh).toFixed(1)} ${(L[1] * sh).toFixed(1)})" filter="url(#g${bl})"/></mask>`;
    defs += `<mask id="${id}r" maskUnits="userSpaceOnUse" x="-150" y="-150" width="600" height="600"><rect x="-150" y="-150" width="600" height="600" fill="#fff"/><path d="${d}" fill="#000" transform="translate(${sx * 3.2} 0.8)" filter="url(#g1)"/></mask>`;
    let s = o.line ? `<path d="${d}" fill="${t.edge}" stroke="${t.edge}" stroke-width="${o.line}" stroke-linejoin="round"/>` : '';
    s += `<g clip-path="url(#${id})">`;
    s += `<path d="${d}" fill="${t.light}"/>`;
    s += `<path d="${d}" fill="${t.base}" transform="translate(${(-L[0] * hl).toFixed(1)} ${(-L[1] * hl).toFixed(1)})" filter="url(#g${bl})"/>`;
    s += `<path d="${d}" fill="${t.shadow}" mask="url(#${id}m)" opacity="${o.so ?? 0.92}"/>`;
    s += `<path d="${d}" fill="url(#vol)"/>`;
    if (o.far) s += `<path d="${d}" fill="#1a0c2e" opacity="0.28"/>`;
    if (o.inner) s += o.inner;
    if (o.rim !== false) s += `<path d="${d}" fill="${t.rim}" mask="url(#${id}r)" opacity="${o.ro ?? 0.32}"/>`;
    s += `</g>`;
    out.push(s);
    return id;
  }
  const raw = (s) => out.push(s);
  /** Ombre projetée d'une forme quelconque (svg) sur une pièce déjà peinte. */
  const cast = (clip, svg, op = 0.38) => out.push(`<g clip-path="url(#${clip})" opacity="${op}">${svg}</g>`);
  return { S, raw, cast, sx, get defs() { return defs; }, get body() { return out.join(''); } };
}
const ln = (d, c, w, op = 1) => `<path d="${d}" stroke="${c}" stroke-width="${w}" fill="none" opacity="${op}" stroke-linecap="round" stroke-linejoin="round"/>`;
const sf = (d, c, w, op, b = 2) => `<path d="${d}" stroke="${c}" stroke-width="${w}" fill="none" opacity="${op}" stroke-linecap="round" filter="url(#g${b})"/>`;
const blob = (d, c, op, b = 3) => `<path d="${d}" fill="${c}" opacity="${op}" filter="url(#g${b})"/>`;

const SHARED_DEFS = [1, 2, 3, 4, 5, 6].map((r) => `<filter id="g${r}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="${r * 0.85}"/></filter>`).join('') +
  `<linearGradient id="vol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.14"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#1a0828" stop-opacity="0.24"/></linearGradient>` +
  `<filter id="ol" x="-15%" y="-15%" width="130%" height="130%"><feMorphology in="SourceAlpha" operator="dilate" radius="1.25" result="d"/><feFlood flood-color="#2c1626"/><feComposite in2="d" operator="in" result="o"/><feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter>` +
  `<filter id="sil" x="-15%" y="-15%" width="130%" height="130%"><feMorphology in="SourceAlpha" operator="dilate" radius="1.5" result="d"/><feFlood flood-color="#190c24"/><feComposite in2="d" operator="in" result="o"/><feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter>` +
  `<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5"/></filter>`;

module.exports = { painter, tone, metal, mix, ln, sf, blob, SHARED_DEFS };
