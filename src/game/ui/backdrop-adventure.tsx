// L'onglet Aventure, refait le 27/11/2026 (demande du propriétaire : « les 6 carrés prennent tout l'écran, un fond épuré »).
// - AdventureBackdrop : le fond de l'onglet, épuré : le bleu nuit des barres, une seule lueur douce en haut à droite, deux
//   grandes collines très sombres tout en bas, quelques poussières de lumière. Rien qui se découpe entre les tuiles.
// - TileScene : le petit paysage de chaque tuile de mode (dessiné par le code, backdrop-kit.tsx) : un ciel de la couleur
//   du mode, le soleil en haut à droite (la seule lumière), un nuage, un lointain (montagnes, îles, rochers, volcan,
//   collines, dunes), puis un sol plat d'un bord à l'autre où le picto du mode se pose.
import { Component } from 'preact';
import { Flag, Glow, H, Mat, Motes, Soft, VGrad, Vol, W, cloud, f, hills, peaks, spark } from './backdrop-kit';

/** Le fond épuré de l'onglet. */
export function AdventureBackdrop() {
  const P = 'ba';
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMax slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} stops={[[0, '#241d63'], [0.5, '#1a1550'], [1, '#110d38']]} />
        <Glow id={`${P}-light`} c="#9fa0ff" a={0.34} />
        <VGrad id={`${P}-hill`} y1={690} y2={H} stops={[[0, '#262063'], [1, '#17123f']]} />
        <VGrad id={`${P}-hill2`} y1={750} y2={H} stops={[[0, '#1c1750'], [1, '#100c33']]} />
      </defs>
      <rect width={W} height={H} fill={`url(#${P}-sky)`} />
      <circle class="bk-breathe" cx="360" cy="30" r="320" fill={`url(#${P}-light)`} />
      <Vol p={P} d={hills(41, 730, 40, 150)} fill={`url(#${P}-hill)`} line={0} depth={6} shade={0.2} rim={0.12} />
      <Vol p={P} d={hills(13, 786, 30, 120)} fill={`url(#${P}-hill2)`} line={0} depth={6} shade={0.2} rim={0.1} />
      <Motes seed={12} n={9} x0={10} x1={380} y0={160} y1={760} color="#cfd2ff" />
      {[[330, 96, 4], [44, 420, 3.5]].map(([x, y, k], i) => <path class={`bk-twinkle${i % 2 ? ' bk-late' : ''}`} style={{ transformOrigin: `${f(x!)}px ${f(y!)}px` }} d={spark(x!, y!, k!)} fill="#fff" opacity="0.7" />)}
    </svg>
  );
}

// ---------- Les petits paysages des tuiles ----------

/** Largeur et hauteur du dessin d'une tuile ; le sol plat commence à GROUND (le CSS pose le picto dessus). */
export const TW = 200, TH = 150, GROUND = 124;

type Look = {
  /** ciel : haut, milieu, horizon */
  sky: [string, string, string];
  /** le lointain, le plan du milieu, le sol */
  far: string; mid: string; ground: string;
  /** le lointain : des montagnes (peaks) ou des collines (seed, amplitude, pas) */
  shape: 'peaks' | 'hills' | 'dunes' | 'rocks' | 'volcano' | 'isles';
  cloud: string;
};

const LOOKS: Record<string, Look> = {
  tower: { sky: ['#4a32b8', '#8f6cf0', '#f0dcff'], far: '#7458d4', mid: '#5238ae', ground: '#3a2a86', shape: 'peaks', cloud: '#f6f0ff' },
  missions: { sky: ['#0c5e70', '#279c94', '#d4f7e6'], far: '#3a9e8e', mid: '#1d7c72', ground: '#135a58', shape: 'isles', cloud: '#f0fffa' },
  dungeons: { sky: ['#5e2620', '#b85a36', '#ffd49a'], far: '#a05436', mid: '#743a28', ground: '#4e261e', shape: 'rocks', cloud: '#fff0dc' },
  dailyBoss: { sky: ['#4e1030', '#ad2c48', '#ffb08a'], far: '#84223e', mid: '#5e1830', ground: '#421026', shape: 'volcano', cloud: '#ffe2d8' },
  arena: { sky: ['#161e5e', '#3846a8', '#cbc8f6'], far: '#454eac', mid: '#2e358a', ground: '#20276a', shape: 'hills', cloud: '#f2f0ff' },
  defense: { sky: ['#7e440c', '#d08c34', '#ffecb6'], far: '#bc7a30', mid: '#965c20', ground: '#6c4018', shape: 'dunes', cloud: '#fff6de' },
};

/** Le lointain d'une tuile. */
function farShape(shape: Look['shape']): string {
  const base = GROUND - 6;
  switch (shape) {
    case 'peaks': return peaks([[22, 46, 40], [86, 64, 46], [150, 40, 36], [196, 58, 40]], base, TH);
    case 'volcano': return `M-20 ${TH} V${base} L40 ${base} Q70 ${base - 60} 86 ${base - 62} H112 Q130 ${base - 60} 160 ${base} L${TW + 20} ${base} V${TH} Z`;
    case 'rocks': return peaks([[14, 34, 26], [60, 48, 30], [118, 30, 26], [176, 44, 34]], base, TH);
    case 'isles': return `M-20 ${TH} V${base} H12 Q30 ${base - 26} 58 ${base} H120 Q146 ${base - 34} 176 ${base} H${TW + 20} V${TH} Z`;
    case 'dunes': return `M-20 ${TH} V${base - 8} Q40 ${base - 34} 92 ${base - 10} Q140 ${base + 6} ${TW + 20} ${base - 26} V${TH} Z`;
    default: return hills(7, base, 30, 60, TH);
  }
}

/** Le plan du milieu : une ligne de collines rondes, plus basse. */
function midShape(seed: number): string {
  const r = (n: number) => ((Math.sin(seed * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1;
  let d = `M-20 ${TH} V${GROUND}`;
  for (let x = -20; x < TW + 20; x += 50) d += ` Q${f(x + 25)} ${f(GROUND - 8 - 12 * r(x))} ${f(x + 50)} ${GROUND}`;
  return `${d} V${TH} Z`;
}

/** Un sapin rond (pointe adoucie), posé sur le plan du milieu. */
const pine = (x: number, y: number, h: number) => `M${f(x)} ${f(y - h)} Q${f(x + 1.5)} ${f(y - h + 1)} ${f(x + h * 0.36)} ${f(y - 2)} Q${f(x + h * 0.38)} ${f(y)} ${f(x + h * 0.3)} ${f(y)} H${f(x - h * 0.3)} Q${f(x - h * 0.38)} ${f(y)} ${f(x - h * 0.36)} ${f(y - 2)} Q${f(x - 1.5)} ${f(y - h + 1)} ${f(x)} ${f(y - h)} Z`;
/** Un rocher arrondi. */
const rock = (x: number, y: number, w: number, h: number) => `M${f(x - w / 2)} ${f(y)} Q${f(x - w / 2)} ${f(y - h)} ${f(x - w * 0.05)} ${f(y - h)} Q${f(x + w / 2)} ${f(y - h * 0.9)} ${f(x + w / 2)} ${f(y)} Z`;

/** Les petits détails de chaque mode, sur les bords (le picto occupe le milieu). */
function Props({ mode, P }: { mode: string; P: string }) {
  const g = GROUND;
  switch (mode) {
    case 'tower': return <>{[[16, g - 4, 22], [30, g - 2, 16], [178, g - 3, 20]].map(([x, y, h]) => <Vol p={P} d={pine(x!, y!, h!)} fill={`url(#${P}-prop)`} line={1} inkA={0.45} depth={2.5} />)}</>;
    case 'missions': return (
      <g class="bk-float">
        <Vol p={P} d={`M164 ${g - 6} H190 Q188 ${g - 1} 182 ${g - 1} H170 Q166 ${g - 1} 164 ${g - 6} Z`} fill={`url(#${P}-prop)`} line={1} inkA={0.5} depth={1.5} />
        <Vol p={P} d={`M176 ${g - 8} V${g - 30} Q186 ${g - 18} 188 ${g - 8} Z`} fill="#fff6e6" line={1} inkA={0.5} depth={2} shade={0.2} />
      </g>
    );
    case 'dungeons': return <>{[[14, g, 20, 16], [186, g, 24, 20], [32, g, 10, 8]].map(([x, y, w, h]) => <Vol p={P} d={rock(x!, y!, w!, h!)} fill={`url(#${P}-prop)`} line={1} inkA={0.45} depth={2.5} />)}</>;
    case 'dailyBoss': return (
      <>
        <path class="bk-breathe" d={`M84 ${g - 66} Q99 ${g - 76} 114 ${g - 66} Q99 ${g - 62} 84 ${g - 66} Z`} fill="#ffcf6a" />
        <g class="bk-cloud bk-slow" opacity="0.55"><Vol p={P} d={cloud(80, g - 76, 36, 4)} fill="#4a1a2e" line={0} shade={0} rim={0} /></g>
        <Vol p={P} d={rock(184, g, 22, 18)} fill={`url(#${P}-prop)`} line={1} inkA={0.45} depth={2.5} />
      </>
    );
    case 'arena': return <><Flag p={P} x={14} y={g - 2} h={30} color="#ffc22e" w={14} /><Flag p={P} x={184} y={g - 2} h={26} color="#ff6b5e" w={12} /></>;
    case 'defense': return <>{[[16, g, 22, 12], [184, g, 26, 14]].map(([x, y, w, h]) => <Vol p={P} d={rock(x!, y!, w!, h!)} fill={`url(#${P}-prop)`} line={1} inkA={0.45} depth={2.5} />)}</>;
    default: return null;
  }
}

const SEEDS: Record<string, number> = { tower: 3, missions: 5, dungeons: 8, dailyBoss: 11, arena: 13, defense: 17 };

/** Le paysage d'une tuile : dessiné une seule fois (l'application se redessine chaque seconde). */
export class TileScene extends Component<{ mode: string }> {
  shouldComponentUpdate(next: { mode: string }) { return next.mode !== this.props.mode; }
  render({ mode }: { mode: string }) {
    const L = LOOKS[mode] ?? LOOKS.arena!;
    const P = `bt-${mode}`;
    const seed = SEEDS[mode] ?? 1;
    return (
      <svg class="av-tile-svg" viewBox={`0 0 ${TW} ${TH}`} preserveAspectRatio="xMidYMax slice" aria-hidden="true">
        <defs>
          <Soft p={P} />
          <VGrad id={`${P}-sky`} y1={0} y2={GROUND} stops={[[0, L.sky[0]], [0.55, L.sky[1]], [1, L.sky[2]]]} />
          <Glow id={`${P}-sun`} c="#fff4cc" a={0.9} />
          <Mat id={`${P}-far`} c={L.far} k={0.5} />
          <Mat id={`${P}-mid`} c={L.mid} k={0.6} />
          <Mat id={`${P}-prop`} c={mode === 'missions' ? '#a8673a' : L.mid} k={0.9} />
          <VGrad id={`${P}-ground`} y1={GROUND} y2={TH} stops={[[0, L.ground], [1, '#140f3a']]} />
        </defs>
        <rect width={TW} height={TH} fill={`url(#${P}-sky)`} />
        <circle class="bk-breathe" cx="178" cy="16" r="58" fill={`url(#${P}-sun)`} />
        <circle cx="178" cy="16" r="9" fill="#fffbe6" />
        <g class="bk-cloud"><Vol p={P} d={cloud(8 + (seed % 3) * 12, 40 + (seed % 4) * 4, 58, seed)} fill={L.cloud} line={0} depth={3} shade={0.16} rim={0} /></g>
        <g opacity="0.95"><Vol p={P} d={farShape(L.shape)} fill={`url(#${P}-far)`} line={1} inkA={0.3} depth={4} shade={0.2} rim={0.45} /></g>
        <Vol p={P} d={midShape(seed)} fill={`url(#${P}-mid)`} line={1} inkA={0.35} depth={4} shade={0.22} rim={0.35} />
        <Props mode={mode} P={P} />
        {/* le sol : une bande plate d'un bord à l'autre, liseré de lumière en haut */}
        <rect y={GROUND} width={TW} height={TH - GROUND} fill={`url(#${P}-ground)`} />
        <rect y={GROUND} width={TW} height="1.4" fill="#fff6cf" opacity="0.4" />
      </svg>
    );
  }
}
