// Le décor de l'onglet Héros, style moderne (26/11/2026) : la salle des héros. Au fond, un mur raisin et une grande
// fenêtre en arc ouverte sur un ciel de beau temps (le soleil en haut à droite : la seule lumière), deux colonnes claires,
// deux bannières (azur et corail, frappées d'une étoile) sous les médaillons ; devant, une estrade plate d'un bord à
// l'autre, au liseré d'or, où se tient la section (les héros sont posés dessus par screens/heroes.tsx : les pieds à 81
// et 89 % de la salle, y = 197 et 217) ; deux lanternes au bord. Sous l'estrade, là où défile la liste, un sol calme.
// Mouvements (backdrops.css) : nuages qui glissent, bannières qui se balancent, lanternes qui respirent, poussières.
import { Glow, H, INK, Mat, Motes, Soft, VGrad, Vol, W, cloud, f, hills, peaks, rr, spark } from './backdrop-kit';

const P = 'bh';
/** Le pied du mur, le dessus de l'estrade (arrière, avant) et le bas de sa face. */
const FLOOR = 150, BACK = 156, EDGE = 210, FACE = 228;
/** La salle fait 0,58 de la largeur + 18 px (style.css) : tout le dessin descend de 18. */
const DY = 18;
/** La fenêtre : bords, centre et rayon de l'arc. */
const WX0 = 116, WX1 = 274, WCX = 195, WCY = 86, WR = 79;

function Banner({ x, color }: { x: number; color: string }) {
  const d = `M${x - 17} 70 H${x + 17} V132 Q${x + 17} 137 ${x + 12} 136 L${x} 127 L${x - 12} 136 Q${x - 17} 137 ${x - 17} 132 Z`;
  return (
    <g>
      <g class="bk-sway" style={{ transformOrigin: `${x}px 68px`, animationDelay: `${-(x % 5)}s` }}>
        <Vol p={P} d={d} fill={`url(#${P}-${color})`} depth={4} />
        <Vol p={P} d={`M${x} 88 A10 10 0 1 1 ${x - 0.01} 88 Z`} fill={`url(#${P}-gold)`} line={1.2} depth={2.5} rim={0.6} />
        <path d={spark(x + 0.5, 98, 6.5)} fill="#fff" opacity="0.95" />
      </g>
      <Vol p={P} d={rr(x - 23, 64, 46, 6, 3)} fill={`url(#${P}-gold)`} line={1.3} depth={2} />
    </g>
  );
}

function Column({ x }: { x: number }) {
  return (
    <g>
      <Vol p={P} d={rr(x - 11, 20, 22, 134, 6)} fill={`url(#${P}-col)`} depth={6} shade={0.4} />
      <Vol p={P} d={rr(x - 16, 14, 32, 11, 5.5)} fill={`url(#${P}-cream)`} line={1.4} depth={3} />
      <Vol p={P} d={rr(x - 16, 141, 32, 12, 5.5)} fill={`url(#${P}-cream)`} line={1.4} depth={3} />
    </g>
  );
}

function Lantern({ x }: { x: number }) {
  return (
    <g>
      <ellipse cx={x} cy={EDGE - 12} rx="14" ry="3.5" fill="#2a1257" opacity="0.28" />
      <Vol p={P} d={rr(x - 2.6, 160, 5.2, 40, 2.6)} fill={`url(#${P}-bronze)`} line={1.2} depth={2} />
      <Vol p={P} d={rr(x - 9, 194, 18, 7, 3.5)} fill={`url(#${P}-bronze)`} line={1.3} depth={2} />
      <circle class="bk-glow" cx={x} cy="152" r="30" fill={`url(#${P}-lamp)`} />
      <Vol p={P} d={rr(x - 9, 139, 18, 23, 8)} fill="#ffe7a0" line={1.4} depth={3} shade={0.2} rim={0.7}>
        <circle cx={x} cy="151" r="6" fill="#fffbe6" />
      </Vol>
      <Vol p={P} d={rr(x - 7, 134, 14, 6, 3)} fill={`url(#${P}-bronze)`} line={1.2} depth={1.5} />
    </g>
  );
}

export function HeroesBackdrop() {
  const win = `M${WX0} ${FLOOR} V${WCY} A${WR} ${WR} 0 0 1 ${WX1} ${WCY} V${FLOOR} Z`;
  const frame = `M${WX0 - 9} ${FLOOR} V${WCY} A${WR + 9} ${WR + 9} 0 0 1 ${WX1 + 9} ${WCY} V${FLOOR} Z ${win}`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMin slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-wall`} y1={-40} y2={FLOOR} stops={[[0, '#1f1656'], [0.5, '#33287f'], [1, '#4a3ca6']]} />
        <VGrad id={`${P}-sky`} y1={6} y2={FLOOR} stops={[[0, '#3f9bff'], [0.45, '#86c2ff'], [0.85, '#ffd9bf'], [1, '#ffe8c4']]} />
        <VGrad id={`${P}-stage`} y1={BACK} y2={EDGE} stops={[[0, '#9a8fea'], [1, '#7d70d8']]} />
        <VGrad id={`${P}-face`} y1={EDGE} y2={FACE} stops={[[0, '#4c3fa6'], [1, '#2f246f']]} />
        <VGrad id={`${P}-floor`} y1={FACE} y2={H} stops={[[0, '#241a5c'], [0.35, '#1c144c'], [1, '#130d33']]} />
        <VGrad id={`${P}-beam`} y1={FLOOR} y2={EDGE + 4} stops={[[0, '#fff3c7', 0.22], [1, '#fff3c7', 0]]} />
        <linearGradient id={`${P}-sheen`} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6cf" stop-opacity="0" /><stop offset="1" stop-color="#fff6cf" stop-opacity="0.2" /></linearGradient>
        <Glow id={`${P}-sun`} c="#fff3c7" a={0.9} />
        <Glow id={`${P}-lamp`} c="#ffd24a" a={0.55} />
        <Mat id={`${P}-col`} c="#7a6dd4" />
        <Mat id={`${P}-cream`} c="#e4dcff" k={0.6} />
        <Mat id={`${P}-gold`} c="#ffc22e" />
        <Mat id={`${P}-bronze`} c="#c98a3a" />
        <Mat id={`${P}-azure`} c="#2f8cff" />
        <Mat id={`${P}-coral`} c="#ff6b5e" />
        <Mat id={`${P}-hill`} c="#9f9bf0" k={0.5} />
        <Mat id={`${P}-hill2`} c="#7471d6" k={0.5} />
                <clipPath id={`${P}-win`}><path d={win} /></clipPath>
      </defs>

      {/* le sol calme sous l'estrade ; tout le reste descend de 18 (la salle commence sous la barre du haut) */}
      <rect y={FACE + DY} width={W} height={H - FACE - DY} fill={`url(#${P}-floor)`} />
      <g transform={`translate(0 ${DY})`}>
      <rect y="-40" width={W} height={FLOOR + 50} fill={`url(#${P}-wall)`} />

      {/* la fenêtre : le ciel, le soleil (en haut à droite), les nuages qui glissent, les collines au loin */}
      <g clip-path={`url(#${P}-win)`}>
        <rect x={WX0} y="0" width={WX1 - WX0} height={FLOOR} fill={`url(#${P}-sky)`} />
        <circle class="bk-breathe" cx="240" cy="46" r="58" fill={`url(#${P}-sun)`} />
        <circle cx="240" cy="46" r="12" fill="#fffbe6" />
        <g class="bk-cloud"><Vol p={P} d={cloud(118, 74, 56, 3)} fill="#ffffff" line={0} depth={4} shade={0.18} rim={0} /></g>
        <g class="bk-cloud bk-slow"><Vol p={P} d={cloud(200, 104, 46, 8)} fill="#ffffff" line={0} depth={4} shade={0.18} rim={0} /></g>
        <Vol p={P} d={peaks([[150, 34, 40], [214, 46, 46], [262, 30, 36]], 134, FLOOR)} fill={`url(#${P}-hill)`} line={0} depth={4} shade={0.2} rim={0.4} />
        <Vol p={P} d={hills(5, 144, 10, 60, FLOOR)} fill={`url(#${P}-hill2)`} line={0} depth={4} shade={0.2} rim={0.35} />
        <Motes seed={11} n={10} x0={WX0} x1={WX1} y0={40} y1={150} color="#fffbe6" />
      </g>
      <Vol p={P} d={frame} ring fill={`url(#${P}-cream)`} line={1.6} depth={4} shade={0.3} />
      <Vol p={P} d={rr(WX0 - 13, FLOOR - 8, WX1 - WX0 + 26, 8, 4)} fill={`url(#${P}-cream)`} line={1.4} depth={2} />

      {/* deux colonnes de part et d'autre de la fenêtre, deux bannières sous les médaillons */}
      <Column x={84} /><Column x={306} />
      <Banner x={40} color="azure" /><Banner x={350} color="coral" />

      {/* l'estrade : plate, d'un bord à l'autre ; la lumière de la fenêtre s'y couche ; liseré d'or ; sa face, son ombre */}
      <rect y={FLOOR - 2} width={W} height="10" fill="#2a1257" opacity="0.35" />
      <rect y={FLOOR} width={W} height={EDGE - FLOOR} fill={`url(#${P}-stage)`} />
      <rect y={FLOOR} width={W} height={EDGE - FLOOR} fill={`url(#${P}-sheen)`} />
      <path d={`M${WX0 + 6} ${FLOOR} H${WX1 - 4} L${WX1 - 24} ${EDGE} H${WX0 - 54} Z`} fill={`url(#${P}-beam)`} />
      <rect y={FLOOR} width={W} height="1.4" fill="#fff6cf" opacity="0.35" />
      <rect y={EDGE + 6} width={W} height={FACE - EDGE - 6} fill={`url(#${P}-face)`} />
      <Vol p={P} d={rr(-12, EDGE - 1, W + 24, 8, 4)} fill={`url(#${P}-gold)`} line={1.4} depth={2.5} />
      <rect y={FACE} width={W} height="16" fill="#0c0822" opacity="0.4" />
      <path d={`M0 ${FACE} H${W}`} stroke={INK} stroke-opacity="0.7" stroke-width="1.6" />

      {/* deux lanternes, au bord de l'estrade */}
      <Lantern x={18} /><Lantern x={372} />
      <Motes seed={4} n={6} x0={20} x1={370} y0={150} y1={210} color="#ffe9a0" />
      {[[134, 40, 5], [288, 120, 4], [62, 176, 3.5]].map(([x, y, k], i) => <path class={`bk-twinkle${i % 2 ? ' bk-late' : ''}`} style={{ transformOrigin: `${f(x!)}px ${f(y!)}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
      </g>
    </svg>
  );
}
