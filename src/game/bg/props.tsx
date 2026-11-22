// Les pièces des décors de combat (forêts, marais, salles, ruines…), dans le trait de la boîte à outils (kit.tsx) :
// une face éclairée, une face à l'ombre, un pied qui mord dans le sol. Les flammes et les lueurs sont des éléments animés
// à part (`flameSprite`, `glowSprite`) : ici, seulement ce qui ne bouge pas.
import type preact from 'preact';
import { RGrad, VGrad, f, rng } from './kit';

/**
 * Un grand tronc de la forêt : racines qui mordent le sol, écorce en deux tons, un nœud. Pied en (x, y), hauteur h vers le
 * haut. `band` = l'anneau de mousse à mi-hauteur (à retirer quand le tronc est très haut : il ressemble à une feuille collée).
 */
export function Trunk({ x, y, w, h, dark = '#3a2a24', mid = '#5e4334', lit = '#8a6448', moss = '#5f9a4a', flip = false, band = true }: { x: number; y: number; w: number; h: number; dark?: string; mid?: string; lit?: string; moss?: string; flip?: boolean; band?: boolean }) {
  const s = flip ? -1 : 1;
  const hw = w / 2;
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s} 1)`}>
      <ellipse cx={-hw * 0.2} cy="2" rx={w * 1.25} ry={w * 0.16} fill="#0d1a10" opacity="0.32" />
      <path d={`M${-hw * 2.1} 0 Q${-hw * 1.2} ${-w * 0.2} ${-hw} ${-w * 0.7} L${-hw * 0.82} ${-h} H${hw * 0.82} L${hw} ${-w * 0.7} Q${hw * 1.25} ${-w * 0.18} ${hw * 2.3} 0 Q${hw * 1.2} ${-w * 0.08} ${hw * 0.5} ${-w * 0.12} Q0 ${-w * 0.02} ${-hw * 0.6} ${-w * 0.1} Q${-hw * 1.3} ${-w * 0.04} ${-hw * 2.1} 0 Z`} fill={mid} />
      <path d={`M${-hw * 2.1} 0 Q${-hw * 1.2} ${-w * 0.2} ${-hw} ${-w * 0.7} L${-hw * 0.82} ${-h} H${-hw * 0.2} L${-hw * 0.3} ${-w * 0.6} Q${-hw * 0.6} ${-w * 0.14} ${-hw * 0.6} ${-w * 0.1} Q${-hw * 1.3} ${-w * 0.04} ${-hw * 2.1} 0 Z`} fill={dark} />
      <path d={`M${hw * 0.3} ${-h} L${hw * 0.4} ${-w * 0.7} Q${hw * 0.7} ${-w * 0.14} ${hw * 1.5} ${-w * 0.03} Q${hw * 1.2} ${-w * 0.2} ${hw} ${-w * 0.7} L${hw * 0.82} ${-h} Z`} fill={lit} />
      <ellipse cx={hw * 0.05} cy={-h * 0.42} rx={w * 0.09} ry={w * 0.14} fill={dark} /><ellipse cx={hw * 0.1} cy={-h * 0.42} rx={w * 0.05} ry={w * 0.08} fill="#1c120e" />
      {band && <path d={`M${-hw * 0.82} ${-h * 0.62} Q${-hw * 0.2} ${-h * 0.66} ${hw * 0.3} ${-h * 0.6} L${hw * 0.2} ${-h * 0.57} Q${-hw * 0.3} ${-h * 0.61} ${-hw * 0.84} ${-h * 0.57} Z`} fill={moss} opacity="0.8" />}
      <path d={`M${-hw * 1.9} -1 Q${-hw * 1.3} ${-w * 0.14} ${-hw * 0.9} ${-w * 0.4} L${-hw * 0.75} ${-w * 0.36} Q${-hw * 1.2} ${-w * 0.1} ${-hw * 1.8} 0 Z`} fill={moss} opacity="0.7" />
    </g>
  );
}

/** Un champignon : chapeau à pois (bord sombre dessous), pied crème. Pied en (x, y). */
export function Mushroom({ x, y, s, cap = '#e0453a', lit = '#ff7a5a', dots = '#fff6e8', stem = '#f6e8c8', flip = false }: { x: number; y: number; s: number; cap?: string; lit?: string; dots?: string; stem?: string; flip?: boolean }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="-2" cy="1" rx="14" ry="3" fill="#0d1a10" opacity="0.3" />
      <path d="M-5 0 Q-6 -12 -3 -20 H5 Q7 -12 6 0 Z" fill={stem} /><path d="M-5 0 Q-6 -12 -3 -20 H0 Q-2 -10 -1 0 Z" fill="#d6c4a0" />
      <path d="M-20 -18 Q-18 -40 0 -41 Q19 -40 21 -18 Q0 -12 -20 -18 Z" fill={cap} />
      <path d="M0 -41 Q19 -40 21 -18 Q12 -16 6 -16 Q12 -28 0 -41 Z" fill={lit} />
      <path d="M-20 -18 Q0 -12 21 -18 Q0 -9 -20 -18 Z" fill="#7a2a24" opacity="0.6" />
      <circle cx="-9" cy="-29" r="3.4" fill={dots} /><circle cx="5" cy="-34" r="2.6" fill={dots} /><circle cx="11" cy="-23" r="2.4" fill={dots} /><circle cx="-2" cy="-22" r="2" fill={dots} />
    </g>
  );
}

/** Une fougère : un éventail de frondes (foncées derrière, claires devant). Pied en (x, y). */
export function Fern({ x, y, s, dark = '#2a6a46', light = '#58b070', flip = false }: { x: number; y: number; s: number; dark?: string; light?: string; flip?: boolean }) {
  const frond = (a: number, l: number, c: string) => <path d={`M0 0 Q${f(Math.cos(a) * l * 0.5 - 4)} ${f(Math.sin(a) * l * 0.5 - 6)} ${f(Math.cos(a) * l)} ${f(Math.sin(a) * l)} Q${f(Math.cos(a) * l * 0.5 + 5)} ${f(Math.sin(a) * l * 0.5 + 3)} 0 0 Z`} fill={c} />;
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="1" rx="22" ry="3.5" fill="#0d1a10" opacity="0.28" />
      {[-2.7, -2.25, -1.85, -1.3, -0.85, -0.45].map((a, i) => frond(a, 34 + (i % 2) * 8, dark))}
      {[-2.5, -2.05, -1.55, -1.05, -0.65].map((a, i) => frond(a, 28 + (i % 2) * 6, light))}
    </g>
  );
}

/** La flamme d'un feu (dessin seul, pour un élément animé qui vacille) : pied au milieu du bas. */
export function flameSprite(w: number, h: number, colors: [string, string, string] = ['#ff6a1a', '#ffb02a', '#fff2b0']) {
  return {
    w, h,
    draw: () => {
      const cx = w / 2;
      const tongue = (k: number, c: string, dx = 0) => (
        <path d={`M${f(cx + dx - w * 0.36 * k)} ${h} Q${f(cx + dx - w * 0.42 * k)} ${f(h - h * 0.45 * k)} ${f(cx + dx - w * 0.04)} ${f(h - h * k)} Q${f(cx + dx + w * 0.08 * k)} ${f(h - h * 0.62 * k)} ${f(cx + dx + w * 0.22 * k)} ${f(h - h * 0.7 * k)} Q${f(cx + dx + w * 0.42 * k)} ${f(h - h * 0.4 * k)} ${f(cx + dx + w * 0.36 * k)} ${h} Z`} fill={c} />
      );
      return <g>{tongue(1, colors[0])}{tongue(0.72, colors[1], 1)}{tongue(0.42, colors[2], 2)}</g>;
    },
  };
}

/** Une lueur ronde et floue (dessin seul, pour un élément animé qui respire), de la couleur donnée. */
export function glowSprite(size: number, color: string, strength = 0.75) {
  return {
    w: size, h: size,
    draw: () => (
      <>
        <defs><RGrad id="g" stops={[[0, color, strength], [0.4, color, strength * 0.4], [1, color, 0]]} /></defs>
        <circle cx={size / 2} cy={size / 2} r={size / 2} fill="url(#g)" />
      </>
    ),
  };
}

/** Un brasero : coupe de métal sur trépied, braises (la flamme est animée à part, posée en (x, y - 30·s)). */
export function Brazier({ x, y, s, metal = '#4a3a3a', lit = '#8a7060', ember = '#ff7a2a' }: { x: number; y: number; s: number; metal?: string; lit?: string; ember?: string }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s})`}>
      <ellipse cx="-3" cy="1" rx="20" ry="4" fill="#000" opacity="0.32" />
      <path d="M-12 0 L-5 -18 M12 0 L5 -18 M0 1 V-16" stroke={metal} stroke-width="3" stroke-linecap="round" />
      <path d="M-16 -30 Q-15 -18 0 -17 Q15 -18 16 -30 Z" fill={metal} />
      <path d="M2 -17 Q15 -18 16 -30 H6 Q8 -22 2 -17 Z" fill={lit} />
      <ellipse cx="0" cy="-30" rx="16" ry="4" fill="#2a1a14" /><ellipse cx="0" cy="-30.5" rx="12" ry="2.6" fill={ember} />
      <path d="M-16 -30 H16" stroke="#c9a46a" stroke-width="1.6" opacity="0.7" />
    </g>
  );
}

/** Une torche murale : support de fer, manche (la flamme est animée à part, posée en (x, y - 34·s)). */
export function Torch({ x, y, s, metal = '#3a2c28' }: { x: number; y: number; s: number; metal?: string }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${s})`}>
      <path d="M-8 0 H8 L4 6 H-4 Z" fill={metal} />
      <path d="M-3 -26 L-2 4 H2 L3 -26 Z" fill="#6a4630" /><path d="M0 -26 L1 4 H2 L3 -26 Z" fill="#8a6040" />
      <path d="M-6 -34 Q-7 -26 0 -24 Q7 -26 6 -34 Z" fill={metal} /><ellipse cx="0" cy="-34" rx="6" ry="2" fill="#ff8a3a" />
    </g>
  );
}

/** Un emblème inventé (jamais de lettre) : 0 losange et soleil, 1 croissant et étoile, 2 flamme, 3 deux lames croisées. */
export function Emblem({ kind, color }: { kind: number; color: string }) {
  const k = kind % 4;
  if (k === 0) return <g fill={color}><path d="M0 -12 L10 0 L0 12 L-10 0 Z" /><circle r="4" fill="none" stroke={color} stroke-width="2" /></g>;
  // (le croissant : un grand arc dehors, un arc plus petit dedans ; l'étoile loge dans son creux)
  if (k === 1) return <g fill={color} transform="translate(1 0)"><path d="M5.5 -9.5 A11 11 0 1 0 5.5 9.5 A9.67 9.67 0 1 1 5.5 -9.5 Z" /><path d="M5 -4.5 L6.12 -1.54 L9.28 -1.39 L6.81 0.59 L7.65 3.64 L5 1.9 L2.35 3.64 L3.19 0.59 L0.72 -1.39 L3.88 -1.54 Z" /></g>;
  if (k === 2) return <path d="M0 -13 Q9 -4 7 4 Q5 11 0 12 Q-5 11 -7 4 Q-8 -2 -3 -6 Q-2 0 1 1 Q2 -6 0 -13 Z" fill={color} />;
  return <g stroke={color} stroke-width="3" stroke-linecap="round"><path d="M-9 -10 L9 10 M9 -10 L-9 10" /><path d="M-11 6 L-6 11 M11 6 L6 11" stroke-width="2.4" /></g>;
}

/** Une bannière suspendue (étoffe à pointe, emblème inventé), sa barre en haut au point (x, y). */
export function Banner({ x, y, w, h, color, dark, trim = '#ffd45c', emblem = 0 }: { x: number; y: number; w: number; h: number; color: string; dark: string; trim?: string; emblem?: number }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)})`}>
      <rect x={-w / 2 - 6} y="-4" width={w + 12} height="7" rx="3" fill="#5a3a20" /><circle cx={-w / 2 - 6} cy="-0.5" r="4.5" fill={trim} /><circle cx={w / 2 + 6} cy="-0.5" r="4.5" fill={trim} />
      <path d={`M${-w / 2} 2 H${w / 2} V${h} L0 ${h + w * 0.32} L${-w / 2} ${h} Z`} fill={color} />
      <path d={`M${-w / 2} 2 H${-w * 0.18} V${h + w * 0.1} L${-w / 2} ${h} Z`} fill={dark} opacity="0.55" />
      <path d={`M${-w / 2 + 4} 8 H${w / 2 - 4} V${h - 3} L0 ${h + w * 0.32 - 6} L${-w / 2 + 4} ${h - 3} Z`} fill="none" stroke={trim} stroke-width="2" opacity="0.85" />
      <g transform={`translate(0 ${f(h * 0.45)}) scale(${f(w / 34)})`}><Emblem kind={emblem} color={trim} /></g>
    </g>
  );
}

/** Une colonne de marbre (fût lisse en cylindre, chapiteau, base) ; `broken` = cassée en biais. Pied en (x, y). */
export function Column({ x, y, w, h, broken = false, lit = '#fdf6e4', mid = '#e2d6bc', dark = '#a99a86', ivy = false }: { x: number; y: number; w: number; h: number; broken?: boolean; lit?: string; mid?: string; dark?: string; ivy?: boolean }) {
  const top = y - h;
  const id = `col${Math.round(x)}${Math.round(y)}`;
  return (
    <g>
      <defs><linearGradient id={id} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color={dark} /><stop offset="0.3" stop-color={mid} /><stop offset="0.72" stop-color={lit} /><stop offset="1" stop-color={mid} /></linearGradient></defs>
      <ellipse cx={x - w * 0.3} cy={y + 2} rx={w * 1.2} ry={w * 0.22} fill="#000" opacity="0.25" />
      <rect x={x - w * 0.72} y={y - w * 0.34} width={w * 1.44} height={w * 0.34} fill={`url(#${id})`} />
      <rect x={x - w * 0.62} y={y - w * 0.52} width={w * 1.24} height={w * 0.2} fill={`url(#${id})`} />
      {broken
        ? <path d={`M${x - w / 2} ${y - w * 0.5} V${top + w * 0.5} L${x - w * 0.1} ${top + w * 0.18} L${x + w * 0.12} ${top + w * 0.4} L${x + w / 2} ${top} V${y - w * 0.5} Z`} fill={`url(#${id})`} />
        : <>
          <rect x={x - w / 2} y={top + w * 0.5} width={w} height={h - w} fill={`url(#${id})`} />
          <rect x={x - w * 0.64} y={top + w * 0.28} width={w * 1.28} height={w * 0.24} fill={`url(#${id})`} />
          <rect x={x - w * 0.76} y={top} width={w * 1.52} height={w * 0.3} fill={`url(#${id})`} />
          <path d={`M${x - w * 0.76} ${top + w * 0.3} H${x + w * 0.76}`} stroke="#000" stroke-opacity="0.15" stroke-width="2" />
        </>}
      {ivy && <path d={`M${x - w / 2} ${y - h * 0.3} Q${x} ${y - h * 0.38} ${x + w * 0.2} ${y - h * 0.5} Q${x + w * 0.5} ${y - h * 0.58} ${x + w * 0.4} ${y - h * 0.7} L${x + w * 0.5} ${y - h * 0.66} Q${x + w * 0.62} ${y - h * 0.56} ${x + w * 0.3} ${y - h * 0.46} Q${x + w * 0.1} ${y - h * 0.34} ${x - w / 2} ${y - h * 0.25} Z`} fill="#4f9a58" />}
    </g>
  );
}

/** Un groupe de cristaux (trois à cinq prismes), face claire à droite. Pied en (x, y). */
export function Crystals({ x, y, s, color = '#9a6cff', light = '#e0ccff', dark = '#4a2a9a', flip = false }: { x: number; y: number; s: number; color?: string; light?: string; dark?: string; flip?: boolean }) {
  const prism = (dx: number, h: number, w: number, tilt: number) => (
    <g transform={`translate(${dx} 0) rotate(${tilt})`}>
      <path d={`M${-w} 0 V${-h} L0 ${-h - w * 1.4} L${w} ${-h} V0 Z`} fill={color} />
      <path d={`M${-w} 0 V${-h} L0 ${-h - w * 1.4} V0 Z`} fill={dark} opacity="0.55" />
      <path d={`M0 ${-h - w * 1.4} L${w} ${-h} V${-h * 0.4} L${w * 0.3} ${-h * 0.5} Z`} fill={light} opacity="0.9" />
    </g>
  );
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="1" rx="22" ry="4" fill="#000" opacity="0.3" />
      {prism(-10, 22, 5, -18)}{prism(10, 18, 4.5, 20)}{prism(0, 38, 7, 2)}{prism(-4, 14, 4, -40)}
    </g>
  );
}

/** De l'eau calme : le plan, plus clair au loin, quelques reflets et des ronds à la surface (pas de bandes). */
export function Water({ y0, y1, x0 = -20, x1 = 740, top, low, glint = '#ffffff', seed = 1 }: { y0: number; y1: number; x0?: number; x1?: number; top: string; low: string; glint?: string; seed?: number }) {
  const r = rng(seed);
  const id = `wt${seed}`;
  return (
    <g>
      <defs><VGrad id={id} y0={y0} y1={y1} stops={[[0, top], [1, low]]} /></defs>
      <rect x={x0} y={y0} width={x1 - x0} height={y1 - y0} fill={`url(#${id})`} />
      {Array.from({ length: 9 }, () => {
        const x = x0 + r() * (x1 - x0), y = y0 + 6 + r() * (y1 - y0 - 12), w = 20 + r() * 60;
        return <ellipse cx={f(x)} cy={f(y)} rx={f(w)} ry={f(1.6 + r() * 1.6)} fill={glint} opacity={f(0.18 + r() * 0.2)} />;
      })}
    </g>
  );
}

/** Une lanterne suspendue à son poteau courbé (la lueur est animée à part, posée en (x + 22·s, y - 70·s)). */
export function LanternPost({ x, y, s, wood = '#5e4026', flip = false }: { x: number; y: number; s: number; wood?: string; flip?: boolean }) {
  return (
    <g transform={`translate(${f(x)} ${f(y)}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="1" rx="10" ry="2.5" fill="#000" opacity="0.3" />
      <path d="M-2 0 L-1.5 -88 Q6 -96 22 -90 L22 -86 Q8 -91 2 -85 L2 0 Z" fill={wood} />
      <path d="M22 -86 V-80" stroke="#2a1c12" stroke-width="1.2" />
      <path d="M16 -80 H28 L26 -62 H18 Z" fill="#3a2c20" /><path d="M18 -78 H26 L24.5 -64 H19.5 Z" fill="#ffd77a" />
      <path d="M15 -80 L22 -85 L29 -80 Z" fill="#2a1c12" />
    </g>
  );
}

/**
 * Une paroi de roche (grotte, mine) de y0 à y1 : des strates en grandes plaques irrégulières, chacune avec son arête
 * claire en haut ; plus sombre vers le haut (la voûte), des stalactites qui pendent du haut.
 */
export function RockWall({ seed, y0, y1, dark, mid, light, edge, drips = true }: { seed: number; y0: number; y1: number; dark: string; mid: string; light: string; edge: string; drips?: boolean }) {
  const r = rng(seed);
  const layers = 3;
  const out: preact.ComponentChildren[] = [];
  for (let i = 0; i < layers; i++) {
    const base = y0 + ((y1 - y0) * (i + 0.7)) / layers;
    let d = `M-20 ${f(y1 + 20)} L-20 ${f(base)}`;
    for (let x = -20; x < 760;) {
      const w = 110 + r() * 140, h = 14 + r() * 40;
      d += ` L${f(x + w * 0.3)} ${f(base - h)} L${f(x + w * 0.7)} ${f(base - h * (0.5 + r() * 0.5))} L${f(x + w)} ${f(base - r() * 6)}`;
      x += w;
    }
    d += ` L760 ${f(y1 + 20)} Z`;
    out.push(<path d={d} fill={i % 2 ? mid : dark} />);
    out.push(<path d={d.replace(/ L760 [^Z]*Z$/, '').replace(/^M-20 [^L]*L/, 'M')} fill="none" stroke={edge} stroke-width="2.4" opacity="0.28" />);
  }
  if (drips) {
    // les stalactites, puis la voûte par-dessus : une masse de roche au bord bosselé, qui cache leur racine (aucune ne pend
    // du vide) ; elle se fond dans le noir vers le haut
    for (let x = 10; x < 720;) {
      const w = 14 + r() * 22, l = 20 + r() * 60;
      out.push(<path d={`M${f(x)} ${f(y0 - 16)} L${f(x + w / 2)} ${f(y0 + l)} L${f(x + w)} ${f(y0 - 16)} Z`} fill={dark} />);
      out.push(<path d={`M${f(x + w / 2)} ${f(y0 + l)} L${f(x + w)} ${f(y0 - 16)} H${f(x + w * 0.62)} Z`} fill={light} opacity="0.5" />);
      x += w + 20 + r() * 70;
    }
    const pts: [number, number][] = [];
    for (let x = 760; x > -40; x -= 34 + r() * 40) pts.push([x, y0 + r() * 14 - 6]);
    pts.push([-40, y0 + 2]);
    const first = pts[0]!, last = pts[pts.length - 1]!;
    let curve = '';
    for (let i = 1; i < pts.length; i++) {
      const [px, py] = pts[i - 1]!, [qx, qy] = pts[i]!;
      curve += ` Q${f(px)} ${f(py)} ${f((px + qx) / 2)} ${f((py + qy) / 2)}`;
    }
    curve += ` L${f(last[0])} ${f(last[1])}`;
    const edgeD = `M${f(first[0])} ${f(first[1])}${curve}`;
    const id = `rwc${seed}`;
    out.push(<defs><VGrad id={id} y0={y0 - 300} y1={y0 + 10} stops={[[0, dark, 0], [0.55, dark, 0.85], [1, dark, 1]]} /></defs>);
    out.push(<path d={`M-40 ${f(y0 - 320)} H760 V${f(first[1])}${curve} Z`} fill={`url(#${id})`} />);
    out.push(<path d={edgeD} fill="none" stroke={mid} stroke-width="7" opacity="0.8" transform="translate(0 -3)" />);
    out.push(<path d={edgeD} fill="none" stroke={edge} stroke-width="2.4" opacity="0.35" />);
  }
  return <g>{out}</g>;
}

/** Un mur de pierres taillées de y0 à y1 : rangées de blocs de largeurs inégales, arête claire en haut de chaque bloc. */
export function Masonry({ seed, y0, y1, color, light, line, rowH = 46 }: { seed: number; y0: number; y1: number; color: string; light: string; line: string; rowH?: number }) {
  const r = rng(seed);
  const out: preact.ComponentChildren[] = [<rect x="-20" y={y0} width="760" height={y1 - y0} fill={line} />];
  let row = 0;
  for (let y = y0; y < y1; y += rowH, row++) {
    for (let x = -20 - (row % 2) * 30 - r() * 20; x < 740;) {
      const w = 80 + r() * 70;
      out.push(<rect x={f(x + 1.5)} y={f(y + 1.5)} width={f(w - 3)} height={f(rowH - 3)} rx="3" fill={color} opacity={f(0.7 + r() * 0.3)} />);
      out.push(<rect x={f(x + 1.5)} y={f(y + 1.5)} width={f(w - 3)} height="5" rx="2.5" fill={light} opacity="0.4" />);
      x += w;
    }
  }
  return <g>{out}</g>;
}
