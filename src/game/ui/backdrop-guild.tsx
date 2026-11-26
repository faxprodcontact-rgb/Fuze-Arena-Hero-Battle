// Le décor de l'onglet Guilde, style moderne (26/11/2026) : le donjon de la guilde au soleil couchant. Un ciel chaud
// (violet → corail → or), le soleil en haut à droite (la seule lumière), des nuages roses qui glissent ; le donjon au
// milieu (une grande bannière d'or frappée d'une étoile sur sa façade), deux tours aux toits azur et leurs fanions, un
// rempart aux merlons arrondis. La carte de la guilde se pose au pied du donjon (y = 110 : sections/guilde.css) : tout ce
// qui compte est au-dessus ; dessous, la cour reste calme, raisin, sous les onglets et les listes (des collines douces en bas).
import { Glow, H, Mat, Motes, Soft, VGrad, Vol, W, cloud, f, hills, rr, spark, Flag } from './backdrop-kit';

const P = 'bg';
/** Le pied du rempart (la cour commence dessous). */
const WALL = 132;

/** Une tour ronde, son toit pointu et son fanion. */
function Tower({ x, top, w, roof, flag }: { x: number; top: number; w: number; roof: string; flag: string }) {
  return (
    <g>
      <Flag p={P} x={x} y={top - w * 0.6} h={18} color={flag} w={20} />
      <Vol p={P} d={rr(x - w / 2, top, w, WALL - top + 4, w * 0.16)} fill={`url(#${P}-stone)`} depth={w * 0.22} />
      <Vol p={P} d={rr(x - w * 0.16, top + 22, w * 0.32, w * 0.42, w * 0.16)} fill="#ffd56a" line={1.1} depth={1.5} shade={0.15} rim={0.6} />
      <Vol p={P} d={rr(x - w * 0.62, top - 4, w * 1.24, 9, 4.5)} fill={`url(#${P}-stone2)`} line={1.4} depth={2} />
      <Vol p={P} d={`M${f(x - w * 0.6)} ${f(top - 3)} Q${f(x)} ${f(top - w * 1.25)} ${f(x + w * 0.6)} ${f(top - 3)} Z`} fill={`url(#${P}-${roof})`} depth={w * 0.2} />
    </g>
  );
}

export function GuildBackdrop() {
  // le rempart : un mur et ses merlons arrondis
  let merlons = `M-20 ${WALL + 30} V${WALL - 30}`;
  for (let x = -20; x < W + 20; x += 26) merlons += ` H${x + 6} V${WALL - 38} Q${x + 6} ${WALL - 42} ${x + 10} ${WALL - 42} H${x + 18} Q${x + 22} ${WALL - 42} ${x + 22} ${WALL - 38} V${WALL - 30}`;
  merlons += ` H${W + 20} V${WALL + 30} Z`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMin slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={0} y2={WALL} stops={[[0, '#4a2f9e'], [0.34, '#9a5ad0'], [0.72, '#ff8f8a'], [1, '#ffc98e']]} />
        <VGrad id={`${P}-court`} y1={WALL} y2={H} stops={[[0, '#3a2a7e'], [0.12, '#251a62'], [0.45, '#1a1249'], [1, '#120c33']]} />
        <Glow id={`${P}-sun`} c="#fff0b8" a={0.95} />
        <Mat id={`${P}-hill`} c="#8a5cc8" k={0.5} />
        <Mat id={`${P}-stone`} c="#e8e0ff" k={0.55} />
        <Mat id={`${P}-stone2`} c="#cfc4f6" k={0.55} />
        <Mat id={`${P}-wall`} c="#b4a6ec" k={0.55} />
        <Mat id={`${P}-azure`} c="#2f8cff" />
        <Mat id={`${P}-coral`} c="#ff6b5e" />
        <Mat id={`${P}-gold`} c="#ffc22e" />
        <Mat id={`${P}-violet`} c="#8b5cff" />
        <VGrad id={`${P}-far`} y1={690} y2={H} stops={[[0, '#33287f'], [1, '#1d1550']]} />
        <VGrad id={`${P}-near`} y1={740} y2={H} stops={[[0, '#251b62'], [1, '#150f3d']]} />
      </defs>

      {/* le ciel, le soleil, les nuages roses */}
      <rect width={W} height={WALL + 10} fill={`url(#${P}-sky)`} />
      <circle class="bk-breathe" cx="322" cy="50" r="80" fill={`url(#${P}-sun)`} />
      <circle cx="322" cy="50" r="15" fill="#fffbe6" />
      <g class="bk-cloud"><Vol p={P} d={cloud(70, 58, 64, 5)} fill="#ffd6e6" line={0} depth={4} shade={0.18} rim={0} /></g>
      <g class="bk-cloud bk-slow"><Vol p={P} d={cloud(236, 90, 56, 10)} fill="#ffd6e6" line={0} depth={4} shade={0.18} rim={0} /></g>
      <Vol p={P} d={hills(37, WALL - 22, 20, 90, WALL + 10)} fill={`url(#${P}-hill)`} line={1.2} inkA={0.4} depth={5} shade={0.2} rim={0.35} />

      {/* le donjon, au milieu, et sa grande bannière */}
      <Vol p={P} d={rr(150, 40, 90, WALL - 36, 10)} fill={`url(#${P}-stone)`} depth={8} />
      <Vol p={P} d={`M140 ${44} Q195 ${-12} 250 ${44} Z`} fill={`url(#${P}-coral)`} depth={6} />
      <Vol p={P} d={rr(136, 38, 118, 10, 5)} fill={`url(#${P}-stone2)`} line={1.4} depth={2} />
      <g class="bk-sway" style={{ transformOrigin: '195px 52px' }}>
        <Vol p={P} d={`M176 54 H214 V96 Q214 101 209 100 L195 92 L181 100 Q176 101 176 96 Z`} fill={`url(#${P}-violet)`} depth={4} />
        <Vol p={P} d={`M185 62 H205 V74 Q205 84 195 88 Q185 84 185 74 Z`} fill={`url(#${P}-gold)`} line={1.2} depth={2.5} rim={0.6} />
        <path d={spark(195.5, 73, 6)} fill="#fff" />
      </g>
      <Vol p={P} d={rr(171, 51, 48, 5, 2.5)} fill={`url(#${P}-gold)`} line={1.2} depth={1.5} />

      {/* le rempart et les deux tours */}
      <Vol p={P} d={merlons} fill={`url(#${P}-wall)`} depth={6} />
      <Tower x={40} top={70} w={44} roof="azure" flag="#ffc22e" />
      <Tower x={350} top={64} w={46} roof="azure" flag="#ff6b5e" />

      {/* la cour : calme sous la carte, les onglets et les listes */}
      <rect y={WALL} width={W} height={H - WALL} fill={`url(#${P}-court)`} />
      <rect y={WALL} width={W} height="1.4" fill="#fff6cf" opacity="0.3" />
      <Vol p={P} d={hills(17, 730, 40, 130)} fill={`url(#${P}-far)`} line={0} depth={6} shade={0.25} rim={0.16} />
      <Vol p={P} d={hills(23, 784, 30, 110)} fill={`url(#${P}-near)`} line={0} depth={6} shade={0.25} rim={0.12} />
      <Motes seed={21} n={8} x0={10} x1={380} y0={40} y1={WALL} color="#fff0b8" />
      <Motes seed={5} n={8} x0={10} x1={380} y0={300} y1={760} color="#ffd9b0" />
    </svg>
  );
}
