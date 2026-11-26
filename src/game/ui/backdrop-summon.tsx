// Le décor de l'onglet Invoquer, style moderne (26/11/2026) : un sanctuaire, la nuit. Une voûte étoilée violette, la
// lune en croissant en haut à droite (la seule lumière), deux voiles d'aurore qui ondulent doucement, deux îlots de
// roche qui flottent au bord du ciel, portant leurs cristaux ; à l'horizon des monts arrondis ; au sol un plateau plat,
// d'un bord à l'autre, où se pose l'estrade du portail (le portail et son estrade : sections/summon-gate.tsx).
// Le milieu reste sombre et calme : c'est la place du portail.
import { Glow, H, Mat, Motes, Soft, Stars, VGrad, Vol, W, f, hills, peaks, rr } from './backdrop-kit';

const P = 'bs';
/** L'horizon : là où le plateau commence (sous l'estrade du portail). */
const GROUND = 380;

/** Une gerbe de cristaux : trois prismes aux bouts arrondis, posés sur un îlot. */
function Crystals({ x, y, s, c }: { x: number; y: number; s: number; c: string }) {
  const prism = (dx: number, h: number, w: number) =>
    `M${f(x + (dx - w) * s)} ${f(y)} V${f(y - h * s * 0.72)} Q${f(x + dx * s)} ${f(y - h * s * 1.1)} ${f(x + (dx + w) * s)} ${f(y - h * s * 0.72)} V${f(y)} Z`;
  return (
    <g>
      <Vol p={P} d={prism(-8, 18, 4.5)} fill={`url(#${P}-${c})`} line={1.2} depth={2} rim={0.7} />
      <Vol p={P} d={prism(7, 16, 4)} fill={`url(#${P}-${c})`} line={1.2} depth={2} rim={0.7} />
      <Vol p={P} d={prism(0, 28, 5.5)} fill={`url(#${P}-${c})`} line={1.3} depth={2.5} rim={0.7} />
    </g>
  );
}

/** Un îlot de roche qui flotte : dessus plat (herbe violette), dessous arrondi. */
function Island({ x, y, w, c, cls }: { x: number; y: number; w: number; c: string; cls: string }) {
  const h = w * 0.5;
  return (
    <g class={`bk-float ${cls}`}>
      <Vol p={P} d={`M${f(x - w / 2)} ${f(y)} Q${f(x - w * 0.42)} ${f(y + h * 0.7)} ${f(x - w * 0.1)} ${f(y + h)} Q${f(x + w * 0.15)} ${f(y + h * 1.1)} ${f(x + w * 0.3)} ${f(y + h * 0.6)} Q${f(x + w * 0.46)} ${f(y + h * 0.3)} ${f(x + w / 2)} ${f(y)} Z`} fill={`url(#${P}-rock)`} depth={5} shade={0.35} />
      <Vol p={P} d={rr(x - w / 2 - 3, y - 5, w + 6, 9, 4.5)} fill={`url(#${P}-moss)`} line={1.4} depth={2} />
      <Crystals x={x + w * 0.08} y={y - 4} s={w / 46} c={c} />
    </g>
  );
}

export function SummonBackdrop() {
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMin slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={0} y2={GROUND} stops={[[0, '#0f0930'], [0.42, '#251a6e'], [0.8, '#4b33a8'], [1, '#7a55d0']]} />
        <VGrad id={`${P}-ground`} y1={GROUND} y2={H} stops={[[0, '#3b2a8c'], [0.18, '#2a1d6c'], [0.5, '#1b1350'], [1, '#100a30']]} />
        <VGrad id={`${P}-aur`} y1={110} y2={240} stops={[[0, '#6fffd8', 0], [0.4, '#6fffd8', 0.3], [0.75, '#b07cff', 0.22], [1, '#b07cff', 0]]} />
        <VGrad id={`${P}-aur2`} y1={150} y2={270} stops={[[0, '#ff8fe0', 0], [0.5, '#c58aff', 0.2], [1, '#6fd0ff', 0]]} />
        <Glow id={`${P}-moon`} c="#e7dcff" a={0.6} />
        <Mat id={`${P}-far`} c="#5b44b8" k={0.5} />
        <Mat id={`${P}-near`} c="#3f2d8e" k={0.5} />
        <Mat id={`${P}-rock`} c="#6a58c8" />
        <Mat id={`${P}-moss`} c="#8a6cf0" />
        <Mat id={`${P}-cyan`} c="#5ce1ff" />
        <Mat id={`${P}-pink`} c="#ff7ad9" />
        <Mat id={`${P}-moonm`} c="#fff3d6" k={0.4} />
      </defs>

      {/* la voûte, ses étoiles, la lune */}
      <rect width={W} height={GROUND + 4} fill={`url(#${P}-sky)`} />
      <Stars seed={7} n={46} y1={300} />
      <circle class="bk-breathe" cx="334" cy="58" r="70" fill={`url(#${P}-moon)`} />
      <Vol p={P} d="M334 34 A24 24 0 1 1 312 70 A19 19 0 1 0 334 34 Z" fill={`url(#${P}-moonm)`} line={1.4} depth={3} shade={0.2} rim={0.5} />

      {/* deux voiles d'aurore : larges, doux, ils ondulent */}
      <path class="bk-aurora" d="M-30 190 C40 120 120 200 200 150 C270 108 330 170 420 120 L420 168 C340 214 270 152 200 196 C120 244 40 172 -30 236 Z" fill={`url(#${P}-aur)`} />
      <path class="bk-aurora bk-aurora-2" d="M-30 238 C60 190 140 250 220 214 C300 180 350 226 420 196 L420 226 C350 256 300 214 220 246 C140 278 60 230 -30 268 Z" fill={`url(#${P}-aur2)`} />

      {/* les îlots qui flottent au bord du ciel */}
      <Island x={34} y={262} w={52} c="cyan" cls="" />
      <Island x={362} y={302} w={44} c="pink" cls="bk-float-2" />

      {/* l'horizon : des monts arrondis, puis le plateau plat */}
      <Vol p={P} d={peaks([[20, 70, 70], [118, 46, 60], [282, 52, 64], [372, 84, 74]], GROUND, GROUND + 20)} fill={`url(#${P}-far)`} line={1.2} inkA={0.45} depth={6} shade={0.25} rim={0.4} />
      <Vol p={P} d={hills(29, GROUND + 2, 20, 80, GROUND + 30)} fill={`url(#${P}-near)`} line={1.2} inkA={0.45} depth={5} shade={0.25} rim={0.3} />
      <rect y={GROUND + 6} width={W} height={H - GROUND - 6} fill={`url(#${P}-ground)`} />
      <rect y={GROUND + 6} width={W} height="1.4" fill="#d9c8ff" opacity="0.35" />
      <Motes seed={12} n={12} x0={10} x1={380} y0={200} y1={GROUND + 120} color="#c9f4ff" />
    </svg>
  );
}
