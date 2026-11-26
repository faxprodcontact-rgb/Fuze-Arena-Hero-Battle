// Le décor de l'onglet Guilde, refait le 27/11/2026 (« améliore drastiquement le dessin de fond ») : la forteresse de la
// guilde au soleil couchant, en plans successifs (dessin vectoriel lisse, backdrop-kit.tsx ; une seule lumière, le soleil en
// haut à droite : les faces de droite sont claires, celles de gauche dans l'ombre).
// - le ciel : violet profond → rose → corail → or à l'horizon ; quelques premières étoiles à gauche ; nuages éclairés par
//   en dessous qui glissent ; le soleil et sa grande lueur ;
// - le lointain : montagnes lavande aux sommets clairs, puis des collines et une forêt de sapins ronds ;
// - la forteresse : le donjon (une face, un flanc dans l'ombre, toit de tuiles corail et sa flèche à fanion, corniche,
//   grande bannière violette à l'emblème d'or qui ondule, deux hautes fenêtres allumées, la porte d'où sort une lumière
//   chaude, deux lanternes), deux tourelles derrière lui, deux grandes tours d'angle (toits indigo, fanions qui flottent,
//   fenêtres allumées), le rempart du fond et celui de devant aux merlons arrondis ;
// - la cour : un sol plat d'un bord à l'autre, des buissons sur les bords ; dessous, le raisin calme où se posent la carte de
//   la guilde, les onglets et les listes (sections/guilde.css : la carte se pose sous la porte, y ≈ 144).
// Sur un petit téléphone, le dessin remonte un peu (sections/guilde.css) pour que le toit, la bannière et les fenêtres
// restent visibles au-dessus de la carte.
import { Flag, Glow, H, Mat, Motes, Soft, Stars, VGrad, Vol, W, cloud, f, hills, peaks, rr, spark } from './backdrop-kit';

const P = 'bg';
/** Le pied de la forteresse : la cour commence dessous. */
const BASE = 150;
const CX = W / 2;

/** Une fenêtre en arc (x = gauche, y = haut). */
const arch = (x: number, y: number, w: number, h: number) =>
  `M${f(x)} ${f(y + h)} V${f(y + w / 2)} A${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(x + w)} ${f(y + w / 2)} V${f(y + h)} Z`;

/** Un toit conique aux flancs légèrement creusés (base en y, de x - w/2 à x + w/2, pointe en apex). */
const cone = (x: number, y: number, w: number, apex: number) =>
  `M${f(x - w / 2)} ${f(y)} Q${f(x - w * 0.16)} ${f(y - (y - apex) * 0.42)} ${f(x)} ${f(apex)} Q${f(x + w * 0.16)} ${f(y - (y - apex) * 0.42)} ${f(x + w / 2)} ${f(y)} Q${f(x)} ${f(y + 5)} ${f(x - w / 2)} ${f(y)} Z`;

/** Un mur et ses merlons arrondis, de x0 à x1 (haut des merlons en top, haut du mur en top + 8, pied en bottom). */
function crenel(x0: number, x1: number, top: number, bottom: number, step = 22) {
  const w = top + 8;
  let d = `M${f(x0)} ${f(bottom)} V${f(w)}`;
  for (let x = x0; x < x1 - 4; x += step) {
    const a = x + step * 0.25, b = Math.min(x + step * 0.75, x1);
    d += ` H${f(a)} V${f(top + 3)} Q${f(a)} ${f(top)} ${f(a + 3)} ${f(top)} H${f(b - 3)} Q${f(b)} ${f(top)} ${f(b)} ${f(top + 3)} V${f(w)}`;
  }
  return `${d} H${f(x1)} V${f(bottom)} Z`;
}

/** Une grande tour ronde : son flanc dans l'ombre, sa couronne, son toit, sa fenêtre allumée et son fanion. */
function Tower({ x, top, w, roof, flag, apex, flagW = 22, banner }: { x: number; top: number; w: number; roof: string; flag: string; apex: number; flagW?: number; banner: string }) {
  const bottom = BASE + 4;
  return (
    <g>
      <Flag p={P} x={x} y={apex + 2} h={20} color={flag} w={flagW} />
      <Vol p={P} d={rr(x - w / 2, top, w, bottom - top, w * 0.12)} fill={`url(#${P}-stone)`} depth={w * 0.3} shade={0.38} />
      {/* le flanc de gauche, dans l'ombre (la tour est ronde) */}
      <path d={rr(x - w / 2 + 1, top + 1, w * 0.26, bottom - top - 2, w * 0.1)} fill="#4a2a7a" opacity="0.22" />
      {/* une bannière pendue sous la couronne, puis une fenêtre allumée et sa lueur */}
      <g class="bk-sway" style={{ transformOrigin: `${f(x)}px ${f(top + 8)}px` }}>
        <Vol p={P} d={`M${f(x - 9)} ${f(top + 7)} H${f(x + 9)} V${f(top + 34)} L${f(x)} ${f(top + 29)} L${f(x - 9)} ${f(top + 34)} Z`} fill={`url(#${P}-${banner})`} line={1.2} depth={3} />
        <path d={spark(x, top + 18, 4.5)} fill="#ffe27a" />
      </g>
      <circle class="bk-glow" cx={f(x)} cy={f(top + 52)} r={f(w * 0.34)} fill={`url(#${P}-warm)`} opacity="0.55" />
      <Vol p={P} d={arch(x - w * 0.12, top + 42, w * 0.24, w * 0.38)} fill={`url(#${P}-lamp)`} line={1.1} depth={1.5} shade={0.12} rim={0.7} />
      <Vol p={P} d={crenel(x - w * 0.62, x + w * 0.62, top - 14, top + 6, w * 0.31)} fill={`url(#${P}-stone2)`} depth={3} />
      <Vol p={P} d={cone(x, top - 12, w * 1.34, apex)} fill={`url(#${P}-${roof})`} depth={w * 0.22} shade={0.34} />
    </g>
  );
}

/** Un sapin rond (forêt du lointain). */
const pine = (x: number, y: number, h: number) =>
  `M${f(x)} ${f(y - h)} Q${f(x + 2)} ${f(y - h + 2)} ${f(x + h * 0.34)} ${f(y - 3)} Q${f(x + h * 0.36)} ${f(y)} ${f(x + h * 0.28)} ${f(y)} H${f(x - h * 0.28)} Q${f(x - h * 0.36)} ${f(y)} ${f(x - h * 0.34)} ${f(y - 3)} Q${f(x - 2)} ${f(y - h + 2)} ${f(x)} ${f(y - h)} Z`;

/** Un gros nuage du couchant : des bosses en demi-cercles (la plus grande au milieu) sur une base plate aux bouts arrondis. */
function puff(x: number, y: number, w: number, k: number[] = [0.2, 0.32, 0.26, 0.22]) {
  const sum = k.reduce((a, b) => a + b, 0);
  let d = `M${f(x)} ${f(y)}`, cx = x;
  for (const kk of k) {
    const bw = (w * kk) / sum;
    d += ` A${f(bw / 2)} ${f(bw / 2)} 0 0 1 ${f(cx + bw)} ${f(y)}`;
    cx += bw;
  }
  return `${d} Q${f(cx + 4)} ${f(y + 5)} ${f(cx - 4)} ${f(y + 6)} H${f(x + 4)} Q${f(x - 4)} ${f(y + 5)} ${f(x)} ${f(y)} Z`;
}

/** Un buisson rond posé sur le sol (bosses sur une base plate). */
const bush = (x: number, y: number, w: number, seed: number) => cloud(x, y, w, seed);

export function GuildBackdrop() {
  const PINES: [number, number, number][] = [[8, 140, 22], [24, 142, 28], [40, 140, 20], [104, 138, 18], [116, 140, 24],
    [274, 140, 22], [288, 138, 18], [352, 141, 26], [368, 139, 20], [384, 142, 24]];
  const FAR: [number, number, number][] = [[20, 46, 56], [104, 70, 70], [196, 52, 58], [286, 80, 76], [378, 56, 60]];
  const caps = FAR.map(([x, h, w]) => {
    const top = 124 - h;
    return <path d={`M${f(x - w)} ${f(top - 8)} H${f(x + w)} V${f(top + h * 0.26)} Q${f(x + w * 0.4)} ${f(top + h * 0.2)} ${f(x + w * 0.12)} ${f(top + h * 0.3)} Q${f(x - w * 0.2)} ${f(top + h * 0.2)} ${f(x - w)} ${f(top + h * 0.28)} Z`} fill="#ffe9f0" opacity="0.85" />;
  });
  return (
    <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMin slice">
      <defs>
        <Soft p={P} />
        <VGrad id={`${P}-sky`} y1={0} y2={BASE} stops={[[0, '#2a1f74'], [0.22, '#5a35a6'], [0.46, '#b8509e'], [0.66, '#f47a8a'], [0.84, '#ffaa78'], [1, '#ffd894']]} />
        <VGrad id={`${P}-court`} y1={BASE} y2={H} stops={[[0, '#5a3f8e'], [0.05, '#3a2a78'], [0.16, '#251a62'], [0.5, '#1a1249'], [1, '#120c33']]} />
        <VGrad id={`${P}-path`} y1={BASE} y2={BASE + 40} stops={[[0, '#ffcf8a', 0.55], [1, '#ffcf8a', 0]]} />
        <Glow id={`${P}-sun`} c="#ffe9b0" a={0.95} />
        <Glow id={`${P}-warm`} c="#ffc46a" a={0.85} />
        <Mat id={`${P}-far`} c="#b47fcf" k={0.45} />
        <Mat id={`${P}-hill`} c="#9564bc" k={0.55} />
        <VGrad id={`${P}-cloud`} stops={[[0, '#ffe6f2'], [0.55, '#ffc8d6'], [1, '#ffb894']]} />
        <VGrad id={`${P}-horizon`} y1={60} y2={136} stops={[[0, '#ffd39a', 0], [1, '#ffd39a', 0.75]]} />
        <linearGradient id={`${P}-sunside`} x1="0" y1="0" x2="1" y2="0"><stop offset="0.55" stop-color="#ffd59a" stop-opacity="0" /><stop offset="1" stop-color="#ffd59a" stop-opacity="0.38" /></linearGradient>
        <Mat id={`${P}-pine`} c="#4e2f8e" k={0.6} />
        <Mat id={`${P}-stone`} c="#f0d6d6" k={0.7} />
        <Mat id={`${P}-stone2`} c="#d9bcd8" k={0.7} />
        <Mat id={`${P}-side`} c="#8f6cb8" k={0.4} />
        <Mat id={`${P}-wall`} c="#c4a2d4" k={0.6} />
        <Mat id={`${P}-wallf`} c="#9274c4" k={0.7} />
        <Mat id={`${P}-coral`} c="#e8574e" />
        <Mat id={`${P}-indigo`} c="#4c40bc" />
        <Mat id={`${P}-violet`} c="#7b4dff" />
        <Mat id={`${P}-gold`} c="#ffc22e" />
        <Mat id={`${P}-wood`} c="#8a5a3a" />
        <Mat id={`${P}-bush`} c="#5a3a9a" k={0.7} />
        <VGrad id={`${P}-lamp`} stops={[[0, '#fff1b8'], [0.5, '#ffcf5a'], [1, '#f09a3a']]} />
        <VGrad id={`${P}-gate`} stops={[[0, '#2a1650'], [0.6, '#6a3a5a'], [1, '#ffb45a']]} />
        <VGrad id={`${P}-far2`} y1={690} y2={H} stops={[[0, '#2c2272'], [1, '#1a1349']]} />
        <VGrad id={`${P}-near`} y1={740} y2={H} stops={[[0, '#221a5c'], [1, '#140e3a']]} />
      </defs>

      {/* le ciel, les premières étoiles, le soleil et les nuages éclairés par dessous */}
      <rect width={W} height={BASE + 10} fill={`url(#${P}-sky)`} />
      <g opacity="0.75"><Stars seed={9} n={10} y1={44} /></g>
      <circle class="bk-breathe" cx="292" cy="50" r="130" fill={`url(#${P}-sun)`} />
      <circle cx="292" cy="50" r="15" fill="#fff8de" />
      <rect y="60" width={W} height="80" fill={`url(#${P}-horizon)`} />
      <g class="bk-cloud"><Vol p={P} d={puff(-10, 70, 112, [0.18, 0.3, 0.22, 0.16])} fill={`url(#${P}-cloud)`} line={0} depth={5} shade={0.2} rim={0.7} /></g>
      <g class="bk-cloud bk-slow"><Vol p={P} d={puff(206, 46, 84, [0.22, 0.34, 0.2])} fill={`url(#${P}-cloud)`} line={0} depth={5} shade={0.2} rim={0.7} /></g>
      <g class="bk-cloud" opacity="0.85"><Vol p={P} d={puff(100, 32, 52, [0.3, 0.4, 0.26])} fill={`url(#${P}-cloud)`} line={0} depth={4} shade={0.2} rim={0.6} /></g>

      {/* le lointain : montagnes lavande, collines, forêt de sapins */}
      <Vol p={P} d={peaks(FAR, 124, BASE + 10)} fill={`url(#${P}-far)`} line={1.1} inkA={0.28} depth={6} shade={0.2} rim={0.5}>{caps}</Vol>
      <Vol p={P} d={hills(29, 134, 14, 80, BASE + 10)} fill={`url(#${P}-hill)`} line={1.2} inkA={0.35} depth={5} shade={0.22} rim={0.4} />
      {PINES.map(([x, y, h]) => <Vol p={P} d={pine(x, y, h)} fill={`url(#${P}-pine)`} line={1.1} inkA={0.45} depth={3} shade={0.3} rim={0.35} />)}

      {/* le rempart du fond, qui relie les deux grandes tours */}
      <Vol p={P} d={crenel(60, 330, 104, BASE)} fill={`url(#${P}-wall)`} depth={5} />
      {/* deux tourelles derrière le donjon */}
      {[[132, 80, 18], [258, 76, 20]].map(([x, top, w]) => (
        <g>
          <Vol p={P} d={rr(x! - w! / 2, top!, w!, BASE - top!, 4)} fill={`url(#${P}-stone2)`} depth={4} />
          <Vol p={P} d={arch(x! - 3, top! + 12, 6, 10)} fill={`url(#${P}-lamp)`} line={1} depth={1} shade={0.1} rim={0.6} />
          <Vol p={P} d={cone(x!, top! + 1, w! * 1.4, top! - 26)} fill={`url(#${P}-indigo)`} depth={4} />
        </g>
      ))}

      {/* le donjon : flanc dans l'ombre, face, corniche, toit de tuiles et sa flèche */}
      <Vol p={P} d={`M146 ${BASE} V58 L156 52 V${BASE} Z`} fill={`url(#${P}-side)`} depth={3} shade={0.3} rim={0.2} />
      <Vol p={P} d={rr(154, 52, 92, BASE - 52, 6)} fill={`url(#${P}-stone)`} depth={9} shade={0.34} />
      <Flag p={P} x={CX} y={20} h={18} color="#ffc22e" w={22} />
      <Vol p={P} d={cone(CX + 2, 50, 128, 18)} fill={`url(#${P}-coral)`} depth={8} shade={0.34} />
      <Vol p={P} d={rr(140, 46, 112, 10, 5)} fill={`url(#${P}-stone2)`} line={1.4} depth={2} />
      {/* les corbeaux de la corniche : quelques consoles arrondies sous la corniche */}
      {[160, 178, 196, 214, 232].map((x) => <Vol p={P} d={rr(x - 4, 55, 8, 7, 3)} fill={`url(#${P}-stone2)`} line={1} depth={1.5} shade={0.25} />)}
      {/* deux hautes fenêtres allumées, de part et d'autre de la bannière */}
      {/* la lumière chaude du couchant sur la face droite */}
      <path d={rr(154, 52, 92, BASE - 52, 6)} fill={`url(#${P}-sunside)`} />
      {[168.5, 232.5].map((x) => <circle class="bk-glow" cx={x} cy="84" r="16" fill={`url(#${P}-warm)`} opacity="0.6" />)}
      <Vol p={P} d={arch(162, 70, 13, 26)} fill={`url(#${P}-lamp)`} line={1.2} depth={2} shade={0.12} rim={0.7} />
      <Vol p={P} d={arch(226, 70, 13, 26)} fill={`url(#${P}-lamp)`} line={1.2} depth={2} shade={0.12} rim={0.7} />
      {/* la grande bannière de la guilde, qui ondule doucement */}
      <g class="bk-sway" style={{ transformOrigin: `${CX}px 62px` }}>
        <Vol p={P} d={rr(CX - 24, 60, 48, 5, 2.5)} fill={`url(#${P}-wood)`} line={1.2} depth={1.5} />
        <Vol p={P} d={`M${CX - 20} 64 H${CX + 20} V108 Q${CX + 20} 113 ${CX + 15} 112 L${CX} 104 L${CX - 15} 112 Q${CX - 20} 113 ${CX - 20} 108 Z`} fill={`url(#${P}-violet)`} depth={5} />
        <Vol p={P} d={`M${CX - 11} 72 H${CX + 11} V85 Q${CX + 11} 96 ${CX} 100 Q${CX - 11} 96 ${CX - 11} 85 Z`} fill={`url(#${P}-gold)`} line={1.2} depth={2.5} rim={0.7} />
        <path d={spark(CX + 0.5, 85, 6.5)} fill="#fff" />
      </g>
      {/* la porte : une arche sombre d'où sort une lumière chaude, deux lanternes */}
      <circle class="bk-breathe" cx={CX} cy={BASE - 22} r="34" fill={`url(#${P}-warm)`} opacity="0.7" />
      <Vol p={P} d={rr(CX - 20, 114, 40, BASE - 114, 4)} fill={`url(#${P}-stone2)`} line={1.3} depth={2} />
      <Vol p={P} d={arch(CX - 13, 120, 26, BASE - 120)} fill={`url(#${P}-gate)`} line={1.4} depth={3} shade={0.3} rim={0.3} />
      {[CX - 30, CX + 30].map((x) => (
        <g>
          <circle class="bk-glow" cx={x} cy={124} r="10" fill={`url(#${P}-warm)`} />
          <Vol p={P} d={rr(x - 3.5, 119, 7, 10, 2.5)} fill={`url(#${P}-lamp)`} line={1.1} depth={1} shade={0.1} rim={0.6} />
        </g>
      ))}

      {/* les deux grandes tours d'angle */}
      <Tower x={46} top={80} w={48} roof="indigo" flag="#ffc22e" apex={34} banner="violet" />
      <Tower x={344} top={76} w={50} roof="indigo" flag="#ff6b5e" apex={30} flagW={24} banner="coral" />

      {/* le rempart de devant, ouvert devant la porte */}
      <Vol p={P} d={crenel(-20, 150, 128, BASE + 6)} fill={`url(#${P}-wallf)`} depth={4} />
      <Vol p={P} d={crenel(240, 410, 128, BASE + 6)} fill={`url(#${P}-wallf)`} depth={4} />

      {/* la cour : sol plat d'un bord à l'autre ; la lumière de la porte s'étale ; des buissons sur les bords */}
      <rect y={BASE} width={W} height={H - BASE} fill={`url(#${P}-court)`} />
      <rect y={BASE} width={W} height="1.4" fill="#fff0c8" opacity="0.45" />
      <path d={`M${CX - 16} ${BASE} H${CX + 16} L${CX + 46} ${BASE + 40} H${CX - 46} Z`} fill={`url(#${P}-path)`} />
      <Vol p={P} d={bush(-8, BASE + 4, 44, 3)} fill={`url(#${P}-bush)`} line={1.1} inkA={0.45} depth={3} shade={0.28} rim={0.35} />
      <Vol p={P} d={bush(356, BASE + 4, 44, 7)} fill={`url(#${P}-bush)`} line={1.1} inkA={0.45} depth={3} shade={0.28} rim={0.35} />

      {/* tout en bas, sous les listes : des collines douces */}
      <Vol p={P} d={hills(17, 730, 40, 130)} fill={`url(#${P}-far2)`} line={0} depth={6} shade={0.25} rim={0.16} />
      <Vol p={P} d={hills(23, 784, 30, 110)} fill={`url(#${P}-near)`} line={0} depth={6} shade={0.25} rim={0.12} />
      <Motes seed={21} n={10} x0={10} x1={380} y0={30} y1={BASE} color="#ffe2b0" />
      <Motes seed={5} n={8} x0={10} x1={380} y0={300} y1={760} color="#ffd9b0" />
    </svg>
  );
}
