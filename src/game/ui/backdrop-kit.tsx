// L'atelier commun des fonds des menus, style « moderne » (26/11/2026) : des illustrations vectorielles lisses, dessinées
// par le code, dans la même manière que les pictos modernes (refonte-graphique/ui-moderne/pictos/lib.py) :
// - une seule lumière, en haut à droite : chaque volume a un dégradé (clair en haut à droite, sombre en bas à gauche),
//   un liseré de lumière sur son bord haut-droit et une ombre intérieure douce sur son bord bas-gauche ;
// - un seul contour par objet, d'un raisin sombre et adouci (le fond passe derrière le contenu : rien ne doit crier) ;
// - lumières vers le jaune chaud, ombres vers le violet (comme l'interface raisin) ; aucune lettre, seulement des signes.
// Tout est posé : le sol est une bande plate d'un bord à l'autre, jamais un rond.
import type { ComponentChildren } from 'preact';

export const W = 390, H = 844;
/** Le contour : un raisin presque noir, adouci (les fonds restent derrière le contenu). */
export const INK = '#1f1238';
export const f = (n: number) => n.toFixed(1);

/** Hasard fixe (toujours le même dessin). */
export function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}

// ---------- Couleurs ----------
const hx = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
const tohex = (v: number[]) => `#${v.map((x) => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, '0')).join('')}`;
export function mix(a: string, b: string, t: number) {
  const A = hx(a), B = hx(b);
  return tohex(A.map((x, i) => x + (B[i]! - x) * t));
}
/** La lumière (blanc chaud) et l'ombre (violet profond). */
export const lite = (c: string, t: number) => mix(c, '#fff6cf', t);
export const dark = (c: string, t: number) => mix(c, '#2a1257', t);

/** Le dégradé d'une matière : clair en haut à droite, sombre en bas à gauche. */
export function Mat({ id, c, k = 1 }: { id: string; c: string; k?: number }) {
  return (
    <linearGradient id={id} x1="0.9" y1="0" x2="0.1" y2="1">
      <stop offset="0" stop-color={lite(c, 0.32 * k)} />
      <stop offset="0.55" stop-color={c} />
      <stop offset="1" stop-color={dark(c, 0.3 * k)} />
    </linearGradient>
  );
}
/** Un dégradé vertical simple (ciel, mur, sol). */
export function VGrad({ id, stops, y1, y2 }: { id: string; stops: [number, string, number?][]; y1?: number; y2?: number }) {
  const user = y1 !== undefined && y2 !== undefined;
  return (
    <linearGradient id={id} x1="0" y1={user ? y1 : 0} x2="0" y2={user ? y2 : 1} gradientUnits={user ? 'userSpaceOnUse' : undefined}>
      {stops.map(([o, c, a]) => <stop offset={o} stop-color={c} stop-opacity={a ?? 1} />)}
    </linearGradient>
  );
}
/** Une lueur ronde (soleil, lune, lampe). */
export function Glow({ id, c, a = 0.8 }: { id: string; c: string; a?: number }) {
  return (
    <radialGradient id={id}>
      <stop offset="0" stop-color={c} stop-opacity={a} />
      <stop offset="0.45" stop-color={c} stop-opacity={a * 0.35} />
      <stop offset="1" stop-color={c} stop-opacity="0" />
    </radialGradient>
  );
}
/** Le flou des ombres intérieures (une fois par dessin, sous le préfixe du décor). */
// Plus aucun flou (plantage sur iPhone le 26/11, trouvé par le test automatique) : chaque ombre floue d'un volume était
// calculée sur un rectangle géant (BIG) et Safari préparait une image énorme par volume. Les ombres sont maintenant nettes
// et plus transparentes ; `Soft` est gardé vide pour ne rien casser.
export function Soft(_: { p: string }) {
  return null;
}

const BIG = 'M-2000 -2000 H3000 V3000 H-2000 Z';
/** Un identifiant stable tiré de la forme (le même à chaque dessin : rien ne change dans la page d'une fois à l'autre). */
function hash(s: string) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  return (h >>> 0).toString(36);
}

/**
 * Un volume : sa forme `d`, sa matière `fill` ; un liseré de lumière en haut à droite, une ombre douce en bas à gauche
 * (la forme elle-même, décalée, découpée dans la forme), un seul contour.
 */
export function Vol({ p, d, fill, line = 1.6, ink = INK, inkA = 0.7, depth = 5, shade = 0.32, rim = 0.55, ring = false, children }: {
  p: string; d: string; fill: string; line?: number; ink?: string; inkA?: number; depth?: number; shade?: number; rim?: number;
  /** une forme percée (plusieurs tracés : le second fait le trou) */
  ring?: boolean; children?: ComponentChildren;
}) {
  const rule = ring ? 'evenodd' : undefined;
  const id = `${p}-v${hash(d + fill)}`;
  return (
    <g>
      <clipPath id={id}><path d={d} clip-rule={rule} /></clipPath>
      <path d={d} fill={fill} fill-rule={rule} />
      <g clip-path={`url(#${id})`}>
        {children}
        {shade > 0 && <path d={`${BIG} ${d}`} fill-rule="evenodd" fill="#2a1257" opacity={shade * 0.7} transform={`translate(${depth} ${-depth})`} />}
        {rim > 0 && <path d={`${BIG} ${d}`} fill-rule="evenodd" fill="#fff6cf" opacity={rim} transform="translate(-1.6 1.6)" />}
      </g>
      {line > 0 && <path d={d} fill="none" stroke={ink} stroke-opacity={inkA} stroke-width={line} stroke-linejoin="round" />}
    </g>
  );
}

// ---------- Formes ----------

/** Un rectangle aux coins arrondis, en chemin. */
export function rr(x: number, y: number, w: number, h: number, r: number) {
  r = Math.min(r, w / 2, h / 2);
  return `M${f(x + r)} ${f(y)} H${f(x + w - r)} Q${f(x + w)} ${f(y)} ${f(x + w)} ${f(y + r)} V${f(y + h - r)} Q${f(x + w)} ${f(y + h)} ${f(x + w - r)} ${f(y + h)} H${f(x + r)} Q${f(x)} ${f(y + h)} ${f(x)} ${f(y + h - r)} V${f(y + r)} Q${f(x)} ${f(y)} ${f(x + r)} ${f(y)} Z`;
}

/** Un nuage en volume : des bosses rondes posées sur une base plate (x = gauche, y = base, w = largeur). */
export function cloud(x: number, y: number, w: number, seed: number) {
  const r = rng(seed);
  const k = 3 + Math.floor(r() * 2);
  const step = w / k;
  let d = `M${f(x)} ${f(y)}`;
  for (let i = 0; i < k; i++) {
    const mid = Math.abs(i - (k - 1) / 2) / ((k - 1) / 2 || 1);
    const rad = step * (0.62 + 0.3 * (1 - mid) + 0.12 * r());
    d += ` A${f(rad)} ${f(rad)} 0 0 1 ${f(x + step * (i + 1))} ${f(y - (i === k - 1 ? 0 : 1.5 * r()))}`;
  }
  return `${d} Z`;
}

/** Une ligne de collines rondes, fermée en bas (jusqu'à `bottom`). */
export function hills(seed: number, base: number, amp: number, step: number, bottom = H) {
  const r = rng(seed);
  let d = `M-20 ${bottom} L-20 ${f(base)}`;
  for (let x = -20; x <= W + 20; x += step) d += ` Q${f(x + step * 0.5)} ${f(base - amp * (0.5 + 0.5 * r()))} ${f(x + step)} ${f(base - amp * 0.15 * r())}`;
  return `${d} L${W + 40} ${bottom} Z`;
}

/** Des montagnes aux sommets arrondis (x de chaque sommet, hauteur), fermées en bas. */
export function peaks(list: [number, number, number][], base: number, bottom = H) {
  // [x du sommet, hauteur au-dessus de la base, demi-largeur]
  let d = `M-20 ${bottom} L-20 ${base}`;
  for (const [x, h, w] of list) {
    const top = base - h;
    d += ` L${f(x - w)} ${base} Q${f(x - w * 0.25)} ${f(top)} ${f(x)} ${f(top)} Q${f(x + w * 0.25)} ${f(top)} ${f(x + w)} ${base}`;
  }
  return `${d} L${W + 40} ${base} L${W + 40} ${bottom} Z`;
}

/** Une étoile à quatre branches, signe de lumière (inventé, jamais une lettre). */
export function spark(x: number, y: number, r: number) {
  const q = r * 0.28;
  return `M${f(x)} ${f(y - r)} Q${f(x + q * 0.4)} ${f(y - q * 0.4)} ${f(x + r)} ${f(y)} Q${f(x + q * 0.4)} ${f(y + q * 0.4)} ${f(x)} ${f(y + r)} Q${f(x - q * 0.4)} ${f(y + q * 0.4)} ${f(x - r)} ${f(y)} Q${f(x - q * 0.4)} ${f(y - q * 0.4)} ${f(x)} ${f(y - r)} Z`;
}

// ---------- Ce qui bouge (backdrops.css) ----------

/** Des poussières de lumière qui montent doucement, dans une zone. */
export function Motes({ seed, n: count, x0, x1, y0, y1, color }: { seed: number; n: number; x0: number; x1: number; y0: number; y1: number; color: string }) {
  const r = rng(seed);
  return (
    <g fill={color}>
      {Array.from({ length: count }, () => {
        const x = x0 + r() * (x1 - x0), y = y0 + r() * (y1 - y0), s = 0.9 + r() * 1.5;
        return <circle class="bk-mote" style={{ animationDelay: `${f(-r() * 10)}s`, animationDuration: `${f(8 + r() * 6)}s` }} cx={f(x)} cy={f(y)} r={f(s)} />;
      })}
    </g>
  );
}

/** Des étoiles qui scintillent (ciel de nuit). */
export function Stars({ seed, n: count, y1, color = '#fff' }: { seed: number; n: number; y1: number; color?: string }) {
  const r = rng(seed);
  return (
    <g fill={color}>
      {Array.from({ length: count }, (_, i) => {
        const x = r() * W, y = r() * y1, s = 0.6 + r() * 1.2;
        return i % 6 === 0
          ? <path class="bk-twinkle" style={{ animationDelay: `${f(-r() * 4)}s`, transformOrigin: `${f(x)}px ${f(y)}px` }} d={spark(x, y, s * 3)} />
          : <circle class="bk-star" style={{ animationDelay: `${f(-r() * 4)}s` }} cx={f(x)} cy={f(y)} r={f(s)} />;
      })}
    </g>
  );
}

/** Un fanion qui flotte au bout d'un mât (le pied du mât en x, y). */
export function Flag({ p, x, y, h, color, w = 18 }: { p: string; x: number; y: number; h: number; color: string; w?: number }) {
  const top = y - h;
  return (
    <g>
      <path d={`M${f(x)} ${f(y)} V${f(top)}`} stroke={INK} stroke-opacity="0.75" stroke-width="2.6" stroke-linecap="round" />
      <path d={`M${f(x)} ${f(y)} V${f(top)}`} stroke="#fff1c7" stroke-width="1" stroke-linecap="round" />
      <circle cx={f(x)} cy={f(top - 1.5)} r="2.2" fill="#ffc22e" stroke={INK} stroke-opacity="0.6" stroke-width="1" />
      <g class="bk-flag" style={{ transformOrigin: `${f(x)}px ${f(top + 6)}px` }}>
        <Vol p={p} d={`M${f(x + 1)} ${f(top + 1)} Q${f(x + w * 0.5)} ${f(top - 1)} ${f(x + w)} ${f(top + 5)} Q${f(x + w * 0.5)} ${f(top + 8)} ${f(x + 1)} ${f(top + 11)} Z`} fill={color} line={1.2} depth={2} shade={0.25} rim={0.4} />
      </g>
    </g>
  );
}
