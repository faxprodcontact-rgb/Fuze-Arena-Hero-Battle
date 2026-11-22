// Boîte à outils des décors de combat : les mêmes formes que le décor de l'Aventure (backdrop-adventure.tsx), en grand
// (la scène fait 720 px de large). Une seule lumière par décor : les volumes ont une face éclairée et une face à
// l'ombre (bleu-violet), les lointains sont plus pâles, tout ce qui est posé a son ombre courte et mord dans le sol.
import type { ComponentChildren } from 'preact';
import { GLYPHS } from '../ui/backdrop-adventure';
import { BW } from './core';

export { GLYPHS };
export const W = BW;

export function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}
export const f = (n: number) => n.toFixed(1);
export type Pt = [number, number];
export const path = (pts: Pt[]) => pts.map((p, i) => `${i ? 'L' : 'M'}${f(p[0])} ${f(p[1])}`).join(' ');

/** Un dégradé vertical en coordonnées de la scène. `stops` = [position, couleur, opacité ?]. */
export function VGrad({ id, y0, y1, stops }: { id: string; y0: number; y1: number; stops: [number, string, number?][] }) {
  return (
    <linearGradient id={id} x1="0" y1={y0} x2="0" y2={y1} gradientUnits="userSpaceOnUse">
      {stops.map(([o, c, a]) => <stop offset={o} stop-color={c} stop-opacity={a ?? 1} />)}
    </linearGradient>
  );
}
/** Un dégradé rond (centre, rayon) ; `stops` comme ci-dessus. */
export function RGrad({ id, stops, cx = 0.5, cy = 0.5, r = 0.5 }: { id: string; stops: [number, string, number?][]; cx?: number; cy?: number; r?: number }) {
  return (
    <radialGradient id={id} cx={cx} cy={cy} r={r}>
      {stops.map(([o, c, a]) => <stop offset={o} stop-color={c} stop-opacity={a ?? 1} />)}
    </radialGradient>
  );
}

// ---------------------------------------------------------------- lignes de relief

/** Une ligne de collines douces, fermée en bas (jusqu'à `low`). */
export function hills(seed: number, base: number, amp: number, step: number, low: number): string {
  const r = rng(seed);
  let d = `M-20 ${low} L-20 ${base}`;
  for (let x = -20; x <= W + 20; x += step) d += ` Q${f(x + step * 0.5)} ${f(base - amp * (0.4 + 0.6 * r()))} ${f(x + step)} ${f(base - amp * 0.25 * r())}`;
  return `${d} L${W + 20 + step} ${low} Z`;
}
/** La même ligne, ouverte : pour le liseré clair sur la crête. */
export function crest(seed: number, base: number, amp: number, step: number): string {
  const r = rng(seed);
  let d = `M-20 ${base}`;
  for (let x = -20; x <= W + 20; x += step) d += ` Q${f(x + step * 0.5)} ${f(base - amp * (0.4 + 0.6 * r()))} ${f(x + step)} ${f(base - amp * 0.25 * r())}`;
  return d;
}
/** Une forme de relief tracée d'après une fonction y(x) (pour poser exactement sur sa crête maisons, arbres, moulins),
 *  fermée en bas jusqu'à `low` ; `open` = la crête seule. */
export function curve(fn: (x: number) => number, x0: number, x1: number, low: number, open = false, step = 8): string {
  let d = open ? `M${f(x0)} ${f(fn(x0))}` : `M${f(x0)} ${f(low)} L${f(x0)} ${f(fn(x0))}`;
  for (let x = x0 + step; x < x1 + step; x += step) d += ` L${f(Math.min(x, x1))} ${f(fn(Math.min(x, x1)))}`;
  return open ? d : `${d} L${f(x1)} ${f(low)} Z`;
}
/** Une bosse douce (cloche) : hauteur `h` au point `x0`, demi-largeur `w`. */
export const bump = (x: number, x0: number, w: number, h: number) => h * Math.exp(-(((x - x0) / w) ** 2));

/** Une lisière de sapins : des cimes de tailles variées sur une ligne qui ondule. */
export function forest(seed: number, base: number, hMin: number, hMax: number, wMin: number, wMax: number, x0 = -20, x1 = W + 20): string {
  const r = rng(seed);
  const at = (x: number) => base + Math.sin(x / 80 + seed) * 5;
  let x = x0, d = `M${x0} ${base + 60} L${x0} ${f(at(x0))}`;
  while (x < x1) {
    const w = wMin + r() * (wMax - wMin), h = hMin + r() * (hMax - hMin);
    d += ` L${f(x + w * 0.5)} ${f(at(x + w * 0.5) - h)} L${f(x + w)} ${f(at(x + w) - r() * 3)}`;
    x += w;
  }
  return `${d} L${f(x)} ${base + 60} Z`;
}
/** Le dessus d'un bois de feuillus : des bosses rondes sur une ligne qui ondule. `open` = le trait du haut seul. */
export function canopy(seed: number, base: number, amp: number, r: number, open = false, x0 = -20, x1 = W + 20): string {
  const y = (x: number) => base - amp * (0.5 + 0.5 * Math.sin(x / 90 + seed)) - amp * 0.35 * Math.sin(x / 33 + seed * 2);
  const step = r * 1.7;
  let d = open ? `M${x0} ${f(y(x0))}` : `M${x0} ${base + 90} L${x0} ${f(y(x0))}`;
  let x = x0;
  for (; x < x1; x += step) d += ` a${r} ${r} 0 0 1 ${f(step)} ${f(y(x + step) - y(x))}`;
  return open ? d : `${d} L${f(x)} ${base + 90} Z`;
}
/** Des touffes d'herbe le long d'une ligne (entre x0 et x1). */
export function tufts(seed: number, base: number, amp: number, step: number, k = 1.8, x0 = -10, x1 = W + 10): string {
  const r = rng(seed);
  let d = '';
  for (let x = x0; x < x1; x += step * (0.7 + r() * 0.6)) {
    const y = base - amp * r(), h = (3.5 + r() * 3) * k;
    d += `M${f(x)} ${f(y + 1)} l${f(1.3 * k)} ${f(-h)} l${f(k)} ${f(h - 0.8 * k)} l${f(1.4 * k)} ${f(-h - 1.5 * k)} l${f(k)} ${f(h + k)} l${f(1.3 * k)} ${f(-h + 0.8 * k)} l${f(0.7 * k)} ${f(h)} Z `;
  }
  return d;
}
/** Une chaîne de reliefs fermée en bas : pics aigus (`flat` = 0) ou mesas à sommet plat (`flat` = part du sommet). */
export function ridge(seed: number, base: number, hMin: number, hMax: number, wMin: number, wMax: number, flat = 0, low = base + 80): string {
  const r = rng(seed);
  let x = -20, d = `M-20 ${low} L-20 ${base}`;
  while (x < W + 20) {
    const w = wMin + r() * (wMax - wMin), h = hMin + r() * (hMax - hMin);
    if (flat) d += ` L${f(x + w * 0.12)} ${f(base - h)} L${f(x + w * (0.12 + flat))} ${f(base - h - 3 * r())} L${f(x + w * (0.3 + flat))} ${f(base - h * 0.25 * r())}`;
    else d += ` L${f(x + w * (0.4 + r() * 0.2))} ${f(base - h)} L${f(x + w)} ${f(base - h * 0.2 * r())}`;
    x += w;
  }
  return `${d} L${f(x)} ${low} Z`;
}

function xAt(line: Pt[], y: number): number {
  for (let i = 1; i < line.length; i++) {
    const [x0, y0] = line[i - 1]!, [x1, y1] = line[i]!;
    if (y <= y1) return x0 + ((x1 - x0) * (y - y0)) / (y1 - y0 || 1);
  }
  return line[line.length - 1]![0];
}

/** Un sommet à deux faces (ombre à gauche, lumière à droite) séparées par une arête brisée, coiffé de neige (`snow` = 0 : sans). */
export function Peak({ a, l, r, by, ridge: rg, snow, shade, lit, snowLit = '#ffffff', snowShade = '#c9dcf2' }: { a: Pt; l: number; r: number; by: number; ridge: Pt[]; snow: number; shade: string; lit: string; snowLit?: string; snowShade?: string }) {
  const full: Pt[] = [a, ...rg];
  const end = rg[rg.length - 1]!;
  const sy = a[1] + snow;
  const xL = a[0] + ((l - a[0]) * snow) / (by - a[1]), xR = a[0] + ((r - a[0]) * snow) / (by - a[1]), xM = xAt(full, sy + 6);
  const above = full.filter((p) => p[1] < sy + 6);
  const dl = xM - xL, dr = xR - xM;
  return (
    <g>
      <path d={`${path([a, [l, by], end, ...[...rg].reverse().slice(1)])} Z`} fill={shade} />
      <path d={`${path([a, ...rg, [r, by]])} Z`} fill={lit} />
      {snow > 0 && <path d={`${path([a, [xL, sy], [xL + dl * 0.28, sy - 8], [xL + dl * 0.52, sy + 8], [xL + dl * 0.78, sy - 5], [xM, sy + 6], ...[...above].reverse().slice(0, -1)])} Z`} fill={snowShade} />}
      {snow > 0 && <path d={`${path([...above, [xM, sy + 6], [xM + dr * 0.25, sy - 6], [xM + dr * 0.5, sy + 9], [xM + dr * 0.76, sy - 5], [xR, sy + 2]])} Z`} fill={snowLit} />}
    </g>
  );
}

// ---------------------------------------------------------------- végétation

/** Un sapin à quatre étages, face droite éclairée. Le pied est au point (x, y). */
export function Pine({ x, y, s, dark = '#2a6a46', light = '#4c9a62', trunk = '#5e4026', shadow = '#123a2a' }: { x: number; y: number; s: number; dark?: string; light?: string; trunk?: string; shadow?: string }) {
  const tiers: [number, number, number][] = [[-58, 8, 14], [-49, 12, 17], [-38, 16, 19], [-25, 20, 22]];
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s})`}>
      <ellipse cx="-7" cy="2.5" rx="14" ry="3.2" fill={shadow} opacity="0.25" />
      <rect x="-2.6" y="-5" width="5.2" height="8" fill={trunk} />
      {tiers.map(([top, w, h]) => <path d={`M0 ${top} L${w} ${top + h} Q0 ${top + h + 4} ${-w} ${top + h} Z`} fill={dark} />)}
      {tiers.map(([top, w, h]) => <path d={`M0 ${top} L${w} ${top + h} Q${w * 0.5} ${top + h + 3} 1 ${top + h + 2} Z`} fill={light} />)}
    </g>
  );
}
/** Un arbre rond : tronc, feuillage en trois boules, reflets du côté de la lumière. */
export function Oak({ x, y, s, dark = '#2f7a4a', mid = '#46995c', light = '#74c07a', trunk = '#5e4026', shadow = '#123a2a' }: { x: number; y: number; s: number; dark?: string; mid?: string; light?: string; trunk?: string; shadow?: string }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s})`}>
      <ellipse cx="-8" cy="1.5" rx="16" ry="3.6" fill={shadow} opacity="0.25" />
      <path d="M-3 2 L-2 -14 L2 -14 L3 2 Z" fill={trunk} />
      <circle cx="-9" cy="-20" r="11" fill={dark} /><circle cx="9" cy="-19" r="12" fill={dark} /><circle cx="0" cy="-30" r="13" fill={dark} />
      <circle cx="-6" cy="-23" r="9" fill={mid} /><circle cx="9" cy="-22" r="10" fill={mid} /><circle cx="2" cy="-32" r="10.5" fill={mid} />
      <circle cx="12" cy="-25" r="6" fill={light} /><circle cx="5" cy="-35" r="6.5" fill={light} /><circle cx="-4" cy="-27" r="4" fill={light} opacity="0.8" />
    </g>
  );
}
/** Un buisson à plusieurs bosses, posé au point (x, y). */
export function Bush({ x, y, s, dark = '#256040', mid = '#337a50', light = '#58a868', flip = false }: { x: number; y: number; s: number; dark?: string; mid?: string; light?: string; flip?: boolean }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="-4" cy="13" rx="30" ry="4" fill="#0e2a1c" opacity="0.25" />
      <path d="M-26 14 Q-30 -2 -16 -4 Q-14 -18 0 -14 Q10 -22 18 -10 Q32 -8 26 14 Z" fill={dark} />
      <path d="M-12 14 Q-14 0 -4 -2 Q0 -12 10 -8 Q22 -8 24 4 Q28 10 22 14 Z" fill={mid} />
      <path d="M4 -6 Q12 -12 18 -5 Q12 -4 8 0 Z M-8 0 Q-2 -6 4 -1 Q-2 0 -5 4 Z" fill={light} />
    </g>
  );
}
/** Des fleurs par petit groupe (trois corolles sur tige). */
export function Flowers({ x, y, s = 1, colors = ['#fff', '#ffd45c', '#ff9fb5'], stem = '#2f7448' }: { x: number; y: number; s?: number; colors?: string[]; stem?: string }) {
  const pts: [number, number][] = [[0, 0], [7, 3], [-6, 4]];
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s})`}>
      {pts.map(([dx, dy], i) => (
        <g>
          <path d={`M${dx} ${dy} q${i % 2 ? 1 : -1} 4 0 8`} fill="none" stroke={stem} stroke-width="1.1" />
          <circle cx={dx} cy={dy} r="2.4" fill={colors[i % colors.length]} /><circle cx={dx} cy={dy} r="0.9" fill="#f0a020" />
        </g>
      ))}
    </g>
  );
}

// ---------------------------------------------------------------- pierres

/** Un rocher à facettes : face d'ombre à gauche, face éclairée à droite, arête claire. Posé au point (x, y), largeur w. */
export function Rock({ x, y, w, h, shade = '#5a6aa6', lit = '#a9b9da', top = '#d6dff0', ground = '#0c1430', flip = false }: { x: number; y: number; w: number; h: number; shade?: string; lit?: string; top?: string; ground?: string; flip?: boolean }) {
  const s = flip ? -1 : 1;
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s} 1)`}>
      <ellipse cx={-w * 0.12} cy="1" rx={w * 0.62} ry={Math.max(3, h * 0.12)} fill={ground} opacity="0.28" />
      <path d={`M${-w / 2} 0 L${-w * 0.42} ${-h * 0.55} L${-w * 0.12} ${-h} L${w * 0.2} ${-h * 0.92} L${w * 0.46} ${-h * 0.5} L${w / 2} 0 Z`} fill={lit} />
      <path d={`M${-w / 2} 0 L${-w * 0.42} ${-h * 0.55} L${-w * 0.12} ${-h} L${w * 0.02} ${-h * 0.5} L${-w * 0.06} 0 Z`} fill={shade} />
      <path d={`M${-w * 0.12} ${-h} L${w * 0.2} ${-h * 0.92} L${w * 0.3} ${-h * 0.74} L${w * 0.02} ${-h * 0.5} Z`} fill={top} />
    </g>
  );
}
/** Quelques cailloux épars autour d'un point. */
export function Pebbles({ seed, x, y, n, rx, ry, color = '#8a94b8', lit = '#c9d0e6', k = 1 }: { seed: number; x: number; y: number; n: number; rx: number; ry: number; color?: string; lit?: string; k?: number }) {
  const r = rng(seed);
  return (
    <g>
      {Array.from({ length: n }, () => {
        const a = r() * Math.PI * 2, d = Math.sqrt(r());
        const px = x + Math.cos(a) * rx * d, py = y + Math.sin(a) * ry * d, s = (2 + r() * 3) * k;
        return <g><ellipse cx={f(px)} cy={f(py)} rx={f(s * 1.3)} ry={f(s * 0.7)} fill={color} /><ellipse cx={f(px + s * 0.3)} cy={f(py - s * 0.2)} rx={f(s * 0.7)} ry={f(s * 0.35)} fill={lit} /></g>;
      })}
    </g>
  );
}

// ---------------------------------------------------------------- ciel

/** Un nuage en volume : dessous plat et bleuté, bosses rondes, haut des bosses qui prend la lumière. Repère : le bas à gauche. */
export function Cloud({ lobes, w, fill = 'url(#k-cloud)', light = '#fff' }: { lobes: [number, number, number][]; w: number; fill?: string; light?: string }) {
  return (
    <g fill={fill}>
      <rect x="0" y="-18" width={w} height="18" rx="9" />
      {lobes.map(([cx, cy, r]) => <circle cx={cx} cy={cy - 2} r={r} />)}
      <g fill={light}>{lobes.map(([cx, cy, r]) => <circle cx={cx + r * 0.14} cy={cy - 2 - r * 0.16} r={r * 0.78} />)}</g>
    </g>
  );
}
export const CLOUD_A: [number, number, number][] = [[14, -14, 13], [34, -24, 19], [58, -18, 16], [76, -13, 11]];
export const CLOUD_B: [number, number, number][] = [[12, -12, 11], [30, -20, 15], [50, -14, 12]];
export const CLOUD_C: [number, number, number][] = [[16, -16, 15], [40, -28, 22], [68, -30, 20], [92, -20, 17], [112, -13, 11]];

/** Le dégradé des nuages (à mettre dans les <defs> du dessin qui les montre). */
export function CloudGrad({ id = 'k-cloud', top = '#ffffff', mid = '#eaf3fb', low = '#d3e4f4' }: { id?: string; top?: string; mid?: string; low?: string }) {
  return <VGrad id={id} y0={-46} y1={0} stops={[[0.3, top], [0.8, mid], [1, low]]} />;
}

/** Un dessin de nuage seul, prêt à animer (repère w × h, le nuage posé en bas). */
export function cloudSprite(lobes: [number, number, number][], cw: number, s: number, colors?: { top?: string; mid?: string; low?: string; light?: string }) {
  const h = Math.ceil(52 * s), w = Math.ceil((cw + 12) * s);
  return {
    w, h,
    draw: () => (
      <>
        <defs><CloudGrad top={colors?.top} mid={colors?.mid} low={colors?.low} /></defs>
        <g transform={`translate(${2 * s} ${h - 1}) scale(${s})`}><Cloud lobes={lobes} w={cw} light={colors?.light} /></g>
      </>
    ),
  };
}

/** Des étoiles semées dans une bande du ciel (petits points et quelques croix de lumière). */
export function Stars({ seed, n, y0, y1, color = '#fff' }: { seed: number; n: number; y0: number; y1: number; color?: string }) {
  const r = rng(seed);
  return (
    <g fill={color}>
      {Array.from({ length: n }, (_, i) => {
        const x = r() * W, y = y0 + r() * (y1 - y0), s = 0.6 + r() * 1.4;
        return i % 9 === 0
          ? <path d={`M${f(x)} ${f(y - s * 3)} L${f(x + s * 0.7)} ${f(y)} L${f(x)} ${f(y + s * 3)} L${f(x - s * 0.7)} ${f(y)} Z M${f(x - s * 3)} ${f(y)} L${f(x)} ${f(y + s * 0.7)} L${f(x + s * 3)} ${f(y)} L${f(x)} ${f(y - s * 0.7)} Z`} opacity="0.9" />
          : <circle cx={f(x)} cy={f(y)} r={f(s)} opacity={f(0.45 + r() * 0.5)} />;
      })}
    </g>
  );
}

/** Le cercle de signes (comme autour du soleil de l'Aventure), dans un repère centré : à faire tourner. */
export function GlyphRing({ r, color = '#fff', glyph = 0.9 }: { r: number; color?: string; glyph?: number }) {
  return (
    <g fill="none" stroke={color}>
      <circle r={r} stroke-width="2.2" /><circle r={r + 5} stroke-width="1.1" opacity="0.7" />
      <circle r={r * 0.74} stroke-width="1.6" stroke-dasharray="1.5 11" stroke-linecap="round" />
      {GLYPHS.map((d, i) => {
        const a = (i / GLYPHS.length) * Math.PI * 2;
        return <path d={d} stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(Math.cos(a) * r * 0.87)} ${f(Math.sin(a) * r * 0.87)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(${glyph})`} />;
      })}
      {[0, 1, 2, 3].map((i) => {
        const a = (i / 4) * Math.PI * 2 + Math.PI / 4, x = Math.cos(a) * r, y = Math.sin(a) * r;
        return <path d={`M${f(x)} ${f(y - 6)} L${f(x + 3)} ${f(y)} L${f(x)} ${f(y + 6)} L${f(x - 3)} ${f(y)} Z`} transform={`rotate(${f((a * 180) / Math.PI + 90)} ${f(x)} ${f(y)})`} fill={color} stroke="none" />;
      })}
    </g>
  );
}

// ---------------------------------------------------------------- la plateforme de combat

/**
 * La plateforme où se tiennent les deux équipes : une longue bande d'un bord à l'autre de l'écran (jamais un rond : tous
 * les combattants sont dessus). Le dessus va de `y0` (bord du fond) à `y1` (bord de devant) ; le chant, de `y1` à
 * `y1 + th`, est plus sombre ; il projette une ombre sur ce qui est dessous. `lip` = l'arête claire du bord de devant,
 * `back` = la petite ombre du bord du fond. Les enfants (dalles, planches, cailloux…) se dessinent sur le dessus.
 */
export function Platform({ y0, y1, th, top, face, lip, back = '#000', faceDark, children, faceArt }: {
  y0: number; y1: number; th: number; top: string; face: string; lip: string; back?: string; faceDark?: string;
  children?: ComponentChildren; faceArt?: ComponentChildren;
}) {
  return (
    <g>
      {/* l'ombre portée sous le chant */}
      <rect x="-20" y={y1 + th} width={W + 40} height="22" fill="#000" opacity="0.22" />
      <rect x="-20" y={y1 + th} width={W + 40} height="9" fill="#000" opacity="0.2" />
      {/* le chant */}
      <rect x="-20" y={y1} width={W + 40} height={th} fill={face} />
      {faceDark && <rect x="-20" y={y1 + th * 0.62} width={W + 40} height={th * 0.38} fill={faceDark} />}
      {faceArt}
      {/* le dessus */}
      <rect x="-20" y={y0} width={W + 40} height={y1 - y0} fill={top} />
      {children}
      <rect x="-20" y={y0} width={W + 40} height="5" fill={back} opacity="0.22" />
      <rect x="-20" y={y1 - 3} width={W + 40} height="4" fill={lip} />
    </g>
  );
}

/** Une bordure d'herbe qui déborde par-dessus une arête : des touffes de tailles et d'écarts inégaux (jamais une frange
 *  régulière), chacune de 3 à 5 brins qui pendent. */
export function Overhang({ seed, y, color, light, k = 1 }: { seed: number; y: number; color: string; light?: string; k?: number }) {
  const r = rng(seed);
  const out: ComponentChildren[] = [];
  for (let x = -10 - r() * 30; x < W + 10;) {
    const w = (16 + r() * 46) * k, n = 3 + Math.floor(r() * 3);
    let d = `M${f(x)} ${f(y - 2)}`;
    for (let i = 0; i < n; i++) {
      const bx = x + ((i + 0.5) / n) * w, len = (4 + r() * 10) * k;
      d += ` L${f(bx - 2.5 * k)} ${f(y)} L${f(bx + (r() - 0.5) * 3)} ${f(y + len)} L${f(bx + 2.5 * k)} ${f(y)}`;
    }
    d += ` L${f(x + w)} ${f(y - 2)} Z`;
    out.push(<path d={d} fill={r() < 0.5 || !light ? color : light} />);
    x += w + (6 + r() * 70) * k;
  }
  return <g>{out}</g>;
}

/** Des pierres prises dans le flanc d'une plateforme (terre, roche) : tailles, hauteurs et écarts inégaux, dessus éclairé. */
export function FaceStones({ seed, y0, y1, color, lit, n = 14 }: { seed: number; y0: number; y1: number; color: string; lit: string; n?: number }) {
  const r = rng(seed);
  return (
    <g>
      {Array.from({ length: n }, () => {
        const x = r() * W, y = y0 + (y1 - y0) * (0.3 + r() * 0.55), w = 6 + r() * 14, h = w * (0.45 + r() * 0.2);
        return <g><ellipse cx={f(x)} cy={f(y)} rx={f(w)} ry={f(h)} fill={color} /><ellipse cx={f(x + w * 0.15)} cy={f(y - h * 0.35)} rx={f(w * 0.6)} ry={f(h * 0.45)} fill={lit} /></g>;
      })}
    </g>
  );
}

/** Des dalles irrégulières sur le dessus d'une plateforme, en rangées qui s'élargissent vers le devant (perspective). */
export function Flagstones({ seed, y0, y1, rows, line, light, lightOpacity = 0.25 }: { seed: number; y0: number; y1: number; rows: number; line: string; light?: string; lightOpacity?: number }) {
  const r = rng(seed);
  const out: ComponentChildren[] = [];
  const weights = Array.from({ length: rows }, (_, i) => 0.6 + (0.8 * (i + 0.5)) / rows);
  const total = weights.reduce((a, b) => a + b, 0);
  let y = y0;
  weights.forEach((wt, i) => {
    const k = (i + 1) / rows;
    const yb = i === rows - 1 ? y1 : y + ((y1 - y0) * wt) / total;
    if (i < rows - 1) out.push(<path d={`M-20 ${f(yb)} H${W + 20}`} stroke={line} stroke-width={f(1.4 + k)} opacity="0.55" />);
    let x = -20 - r() * 60;
    const step = 70 + 60 * k;
    while (x < W + 20) {
      const w = step * (0.7 + r() * 0.6);
      out.push(<path d={`M${f(x + w)} ${f(y + 1)} L${f(x + w + (r() - 0.5) * 8)} ${f(yb - 1)}`} stroke={line} stroke-width={f(1.3 + k)} opacity="0.5" />);
      if (light && r() < 0.35) out.push(<rect x={f(x + 5)} y={f(y + 3)} width={f(w - 10)} height={f((yb - y) * 0.45)} rx="4" fill={light} opacity={lightOpacity} />);
      x += w;
    }
    y = yb;
  });
  return <g stroke-linecap="round">{out}</g>;
}

/** Un groupe d'éléments posé à (x, y), réduit de `s`. */
export function At({ x, y, s = 1, flip = false, children }: { x: number; y: number; s?: number; flip?: boolean; children: ComponentChildren }) {
  return <g transform={`translate(${f(x)} ${f(y)}) scale(${flip ? -s : s} ${s})`}>{children}</g>;
}

/** Un petit point lumineux flou (lueur), pour les particules et les lumières. */
export function GlowDot({ size, color, core = '#fff' }: { size: number; color: string; core?: string }) {
  const c = size / 2;
  return (
    <>
      <defs><RGrad id="gd" stops={[[0, core], [0.25, color], [1, color, 0]]} /></defs>
      <circle cx={c} cy={c} r={c} fill="url(#gd)" />
    </>
  );
}
