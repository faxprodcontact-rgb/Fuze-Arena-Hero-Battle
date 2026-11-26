// Le décor de l'onglet Aventure, style moderne (26/11/2026) : une terre d'aventure par beau temps. En haut (au-dessus des
// tuiles des modes, 196 unités : le bandeau de titre se pose à son pied), le panorama : ciel bleu, soleil en haut à
// droite (la seule lumière), nuages qui glissent, une montgolfière ; des montagnes aux sommets enneigés ; à gauche la
// tour des épreuves sur sa colline, à droite un château et son chemin ; des arbres ronds au bord. Sous le bandeau, là où
// sont les tuiles, la prairie se fond dans le raisin : rien qui se découpe entre les tuiles.
import { Glow, H, Mat, Motes, Soft, VGrad, Vol, W, cloud, f, hills, peaks, rr, spark, Flag } from './backdrop-kit';

const P = 'ba';
/** Le pied du panorama. */
const BASE = 196;

/** Les sommets du lointain : [x, hauteur, demi-largeur]. */
const FAR: [number, number, number][] = [[30, 62, 62], [126, 92, 78], [224, 70, 70], [322, 100, 86]];

function Tree({ x, y, r, c = 'tree' }: { x: number; y: number; r: number; c?: string }) {
  return (
    <g>
      <Vol p={P} d={rr(x - r * 0.16, y - r * 0.9, r * 0.32, r * 0.9, r * 0.12)} fill={`url(#${P}-trunk)`} line={1.2} depth={1.5} />
      <Vol p={P} d={`M${f(x)} ${f(y - r * 2.3)} A${f(r)} ${f(r)} 0 1 1 ${f(x - 0.01)} ${f(y - r * 2.3)} Z`} fill={`url(#${P}-${c})`} line={1.4} depth={r * 0.35} />
    </g>
  );
}

/** Une tour ronde : corps, toit pointu, une fenêtre allumée, son fanion. */
function Tower({ x, y, w, h, roof, flag }: { x: number; y: number; w: number; h: number; roof: string; flag?: string }) {
  const top = y - h;
  return (
    <g>
      {flag && <Flag p={P} x={x} y={top - w * 0.6} h={16} color={flag} />}
      <Vol p={P} d={rr(x - w / 2, top, w, h, w * 0.18)} fill={`url(#${P}-stone)`} line={1.4} depth={w * 0.22} />
      <Vol p={P} d={rr(x - w * 0.18, top + h * 0.28, w * 0.36, w * 0.5, w * 0.18)} fill="#ffd56a" line={1.1} depth={1.5} shade={0.15} rim={0.6} />
      <Vol p={P} d={`M${f(x - w * 0.64)} ${f(top + 2)} Q${f(x)} ${f(top - w * 1.25)} ${f(x + w * 0.64)} ${f(top + 2)} Z`} fill={`url(#${P}-${roof})`} line={1.4} depth={w * 0.2} />
    </g>
  );
}

export function AdventureBackdrop() {
  const caps = FAR.map(([x, h, w]) => {
    const top = BASE - 22 - h;
    return <path d={`M${f(x - w)} ${f(top - 8)} H${f(x + w)} V${f(top + h * 0.3)} Q${f(x + w * 0.45)} ${f(top + h * 0.22)} ${f(x + w * 0.15)} ${f(top + h * 0.34)} Q${f(x - w * 0.2)} ${f(top + h * 0.22)} ${f(x - w)} ${f(top + h * 0.32)} Z`} fill="#ffffff" opacity="0.95" />;
  });
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMin slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={0} y2={BASE} stops={[[0, '#3a95ff'], [0.5, '#7cc2ff'], [0.82, '#cfe7ff'], [1, '#ffe6c8']]} />
        <VGrad id={`${P}-ground`} y1={BASE - 20} y2={BASE + 110} stops={[[0, '#2f9e6e', 0], [0.28, '#2a5f7a', 0.75], [0.6, '#1c144c', 1], [1, '#130d33', 1]]} />
        <Glow id={`${P}-sun`} c="#fff3c7" a={0.95} />
        <Mat id={`${P}-far`} c="#a7a3f0" k={0.55} />
        <Mat id={`${P}-mid`} c="#7f9bf0" k={0.5} />
        <Mat id={`${P}-hill`} c="#53c983" k={0.7} />
        <Mat id={`${P}-hill2`} c="#3cae74" k={0.7} />
        <Mat id={`${P}-tree`} c="#3ec27a" />
        <Mat id={`${P}-tree2`} c="#2f9e6e" />
        <Mat id={`${P}-trunk`} c="#a8673a" />
        <Mat id={`${P}-stone`} c="#ebe5ff" k={0.6} />
        <Mat id={`${P}-coral`} c="#ff6b5e" />
        <Mat id={`${P}-azure`} c="#2f8cff" />
        <Mat id={`${P}-gold`} c="#ffc22e" />
        <Mat id={`${P}-path`} c="#ffe3a8" k={0.5} />
      </defs>

      {/* le ciel, le soleil, les nuages */}
      <rect width={W} height={BASE + 40} fill={`url(#${P}-sky)`} />
      <circle class="bk-breathe" cx="338" cy="40" r="86" fill={`url(#${P}-sun)`} />
      <circle cx="338" cy="40" r="15" fill="#fffbe6" />
      <g class="bk-cloud"><Vol p={P} d={cloud(10, 64, 84, 4)} fill="#ffffff" line={0} depth={5} shade={0.16} rim={0} /></g>
      <g class="bk-cloud bk-slow"><Vol p={P} d={cloud(236, 96, 70, 7)} fill="#ffffff" line={0} depth={5} shade={0.16} rim={0} /></g>
      <g class="bk-cloud"><Vol p={P} d={cloud(162, 40, 44, 12)} fill="#ffffff" line={0} depth={4} shade={0.14} rim={0} /></g>

      {/* la montgolfière, qui dérive lentement */}
      <g class="bk-balloon">
        <g class="bk-float">
          <path d="M100 84 L104 98 M118 84 L114 98" stroke="#5a3a2a" stroke-width="1" opacity="0.8" />
          <Vol p={P} d="M109 50 C124 50 130 62 127 72 C124 80 116 85 109 87 C102 85 94 80 91 72 C88 62 94 50 109 50 Z" fill={`url(#${P}-coral)`} line={1.4} depth={4} />
          <Vol p={P} d="M92 70 C100 73 118 73 126 70 C125 74 124 77 122 79 C114 81 104 81 96 79 C94 77 93 74 92 70 Z" fill={`url(#${P}-gold)`} line={1.1} depth={2} />
          <Vol p={P} d={rr(103, 96, 12, 8, 2.5)} fill={`url(#${P}-trunk)`} line={1.2} depth={1.5} />
        </g>
      </g>

      {/* le lointain : montagnes enneigées, puis une ligne bleue */}
      <Vol p={P} d={peaks(FAR, BASE - 22, BASE + 10)} fill={`url(#${P}-far)`} line={1.2} inkA={0.35} depth={6} shade={0.22} rim={0.45}>{caps}</Vol>
      <Vol p={P} d={hills(31, BASE - 18, 18, 70, BASE + 10)} fill={`url(#${P}-mid)`} line={1.2} inkA={0.35} depth={5} shade={0.2} rim={0.35} />

      {/* le château, à droite, et son chemin */}
      <g>
        <Tower x={276} y={BASE - 14} w={14} h={36} roof="azure" />
        <Tower x={342} y={BASE - 14} w={14} h={40} roof="azure" flag="#ffc22e" />
        <Vol p={P} d={`M276 ${BASE - 14} V${BASE - 40} H286 V${BASE - 45} H292 V${BASE - 40} H300 V${BASE - 45} H306 V${BASE - 40} H314 V${BASE - 45} H320 V${BASE - 40} H342 V${BASE - 14} Z`} fill={`url(#${P}-stone)`} line={1.4} depth={4} />
        <Tower x={309} y={BASE - 34} w={20} h={40} roof="coral" flag="#2f8cff" />
        <Vol p={P} d={`M302 ${BASE - 14} V${BASE - 24} Q309 ${BASE - 32} 316 ${BASE - 24} V${BASE - 14} Z`} fill="#4a3a8a" line={1.2} depth={2} shade={0.2} rim={0.2} />
      </g>
      <Vol p={P} d={hills(9, BASE - 2, 16, 90, BASE + 20)} fill={`url(#${P}-hill)`} line={1.4} inkA={0.4} depth={5} />
      <Vol p={P} d={`M150 ${BASE + 8} C200 ${BASE - 2} 250 ${BASE - 2} 270 ${BASE - 8} C284 ${BASE - 12} 296 ${BASE - 13} 304 ${BASE - 14} L314 ${BASE - 14} C304 ${BASE - 9} 292 ${BASE - 4} 280 ${BASE} C260 ${BASE + 6} 222 ${BASE + 10} 200 ${BASE + 12} Z`} fill={`url(#${P}-path)`} line={1.1} inkA={0.4} depth={2} shade={0.18} />

      {/* la tour des épreuves, à gauche, sur sa colline */}
      <Vol p={P} d={`M-20 ${BASE + 12} V${BASE - 22} Q30 ${BASE - 46} 92 ${BASE - 12} Q106 ${BASE - 4} 120 ${BASE + 12} Z`} fill={`url(#${P}-hill2)`} line={1.4} inkA={0.45} depth={6} />
      <Tower x={44} y={BASE - 34} w={26} h={74} roof="coral" flag="#ffc22e" />

      {/* des arbres ronds, au bord */}
      <Tree x={96} y={BASE - 10} r={10} c="tree2" /><Tree x={110} y={BASE - 4} r={8} />
      <Tree x={366} y={BASE - 4} r={11} c="tree2" /><Tree x={250} y={BASE - 6} r={7} />

      {/* sous le bandeau : la prairie se fond dans le raisin, calme sous les tuiles */}
      <rect y={BASE - 20} width={W} height={H - BASE + 20} fill={`url(#${P}-ground)`} />
      <Motes seed={6} n={8} x0={10} x1={380} y0={60} y1={170} color="#fffbe6" />
      {[[214, 22, 5], [72, 30, 4]].map(([x, y, k], i) => <path class={`bk-twinkle${i % 2 ? ' bk-late' : ''}`} style={{ transformOrigin: `${f(x!)}px ${f(y!)}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
    </svg>
  );
}
