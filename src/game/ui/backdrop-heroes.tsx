// Le décor de l'onglet Héros : la salle des héros. Au fond, une grande verrière dorée qui éclaire la salle à contre-jour ;
// de part et d'autre, des colonnes de pierre bleue, des bannières cramoisies, deux braseros de bronze ; au centre, une
// estrade ronde à deux marches, sertie d'or, où se tient la section (les héros sont posés par-dessus par screens/heroes.tsx).
// Plus bas, sous la liste des héros, le sol reste calme : un dallage sombre, sans rien qui se découpe entre les cases.
// La lumière vient de la verrière : chaque colonne a sa face claire tournée vers elle.
// Quatre dessins superposés, comme pour l'Aventure et l'Invocation : le mur et le sol ; ce qui bouge derrière (verrière qui
// respire, poussières) ; les colonnes, l'estrade, les braseros ; ce qui bouge devant (bannières, flammes, étincelles).
import { GLYPHS } from './backdrop-adventure';
import { spark } from './portal';

const W = 390, H = 844;
/** Le pied du mur : là où le sol commence. */
const FLOOR = 150;
/** L'estrade : centre du dessus, demi-largeurs et hauteur des marches. */
export const DAIS = { cx: 195, cy: 188, rx: 160, ry: 18, step: 7 };

function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}
const f = (n: number) => n.toFixed(1);

/** Une colonne : fût rond (ombre d'un côté, lumière de l'autre), chapiteau, base. `side` = 1 si la verrière est à sa droite. */
function Column({ x, w, side }: { x: number; w: number; side: number }) {
  const h = w / 2;
  return (
    <g transform={`translate(${x} 0) scale(${side} 1)`}>
      <rect x={-h} y="-30" width={w} height={FLOOR + 34} fill="url(#hh-col)" />
      {/* les tambours du fût : deux joints à peine marqués */}
      <path d={`M${-h} 96 H${h} M${-h} 128 H${h}`} stroke="#141a40" stroke-width="1" opacity="0.4" />
      {/* le chapiteau */}
      <path d={`M${-h - 5} 50 H${h + 5} L${h + 2} 58 H${-h - 2} Z`} fill="#6f7fc0" /><path d={`M${-h - 5} 50 H${h + 5} V52.500 H${-h - 5} Z`} fill="#c8d2f5" />
      <path d={`M${-h - 2} 58 H${h + 2} L${h} 63 H${-h} Z`} fill="#3a4888" />
      {/* la base */}
      <path d={`M${-h - 2} ${FLOOR - 9} H${h + 2} L${h + 5} ${FLOOR + 4} H${-h - 5} Z`} fill="#56669e" /><path d={`M${-h - 2} ${FLOOR - 9} H${h + 2} V${FLOOR - 7} H${-h - 2} Z`} fill="#aab6e6" />
      <path d={`M${-h - 5} ${FLOOR + 4} H${h + 5} V${FLOOR + 9} H${-h - 5} Z`} fill="#2c3874" />
    </g>
  );
}

/** Une bannière à deux pointes, galonnée d'or, frappée d'un signe. Elle pend d'une tringle et se balance. */
function Banner({ x, y, len, w, glyph }: { x: number; y: number; len: number; w: number; glyph: number }) {
  const h = w / 2;
  return (
    <g class="bd-banner" style={{ transformOrigin: `${x}px ${y}px`, animationDelay: `${-(x % 5)}s` }}>
      <path d={`M${x - h - 4} ${y} H${x + h + 4}`} stroke="#2f1b0c" stroke-width="4" stroke-linecap="round" /><path d={`M${x - h - 4} ${y - 0.800} H${x + h + 4}`} stroke="#e3b548" stroke-width="1.600" stroke-linecap="round" />
      <path d={`M${x - h} ${y} H${x + h} V${y + len} L${x} ${y + len - w * 0.42} L${x - h} ${y + len} Z`} fill="url(#hh-cloth)" />
      {/* le pli : une moitié dans l'ombre */}
      <path d={`M${x - h} ${y} H${x - h * 0.2} V${y + len - w * 0.34} L${x - h} ${y + len} Z`} fill="#5e1418" opacity="0.45" />
      <path d={`M${x - h + 3} ${y + 1} V${y + len - 7} M${x + h - 3} ${y + 1} V${y + len - 7}`} stroke="#ffd45c" stroke-width="1.300" opacity="0.9" />
      <circle cx={x} cy={y + len * 0.42} r={w * 0.3} fill="#5e1418" stroke="#ffd45c" stroke-width="1.300" />
      <path d={GLYPHS[glyph]} transform={`translate(${x} ${f(y + len * 0.42)}) scale(${f(w / 17)})`} fill="none" stroke="#ffe9a0" stroke-width="1.500" stroke-linecap="round" stroke-linejoin="round" />
    </g>
  );
}

/** Le pied et la vasque d'un brasero (la flamme est dessinée à part, dans le calque qui bouge). */
function BrazierStand({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <ellipse cx="0" cy="1" rx="17" ry="4" fill="#070a1c" opacity="0.6" />
      <path d="M-11 0 L-3 -30 M11 0 L3 -30 M0 0 V-30" stroke="#2f1b0c" stroke-width="4.400" stroke-linecap="round" /><path d="M-11 0 L-3 -30 M11 0 L3 -30 M0 0 V-30" stroke="url(#hh-bronze)" stroke-width="2.400" stroke-linecap="round" />
      <path d="M-8 -16 H8" stroke="#2f1b0c" stroke-width="3.600" stroke-linecap="round" /><path d="M-8 -16 H8" stroke="#c98a3a" stroke-width="1.600" stroke-linecap="round" />
      <path d="M-15 -42 Q-15 -28 0 -28 Q15 -28 15 -42 Z" fill="#2f1b0c" /><path d="M-13 -41 Q-13 -30 0 -30 Q13 -30 13 -41 Z" fill="url(#hh-bronze)" />
      <ellipse cx="0" cy="-42" rx="15" ry="3.600" fill="#2f1b0c" /><ellipse cx="0" cy="-42" rx="12.500" ry="2.400" fill="#ff8a2a" /><ellipse cx="0" cy="-42.300" rx="8" ry="1.400" fill="#ffe08a" />
      <path d="M-11 -37 Q-9 -32 -3 -31" fill="none" stroke="#ffe9a0" stroke-width="1.200" stroke-linecap="round" opacity="0.8" />
    </g>
  );
}

/** La flamme d'un brasero : trois langues emboîtées qui dansent, et sa lueur. */
function BrazierFire({ x, y }: { x: number; y: number }) {
  const drop = (k: number) => `M0 0 C${f(-9 * k)} ${f(-3 * k)} ${f(-8 * k)} ${f(-14 * k)} ${f(-2 * k)} ${f(-25 * k)} C${f(0)} ${f(-18 * k)} ${f(7 * k)} ${f(-16 * k)} ${f(8 * k)} ${f(-7 * k)} C${f(8 * k)} ${f(-2 * k)} ${f(4 * k)} 0 0 0 Z`;
  return (
    <g transform={`translate(${x} ${y - 41})`}>
      <circle class="an-glow" cx="0" cy="-10" r="38" fill="url(#hh-fire-glow)" />
      <path class="ad-flame" d={drop(1.150)} fill="#ff6a1a" /><path class="ad-flame" style={{ animationDelay: '-0.2s', animationDuration: '0.42s' }} d={drop(0.800)} fill="#ffb02a" /><path class="ad-flame" style={{ animationDelay: '-0.35s', animationDuration: '0.36s' }} d={drop(0.460)} fill="#fff3b0" />
      {[[-5, 0], [4, -1.300], [0, -2.400]].map(([dx, d]) => <circle class="ts-ember" style={{ animationDelay: `${d}s` }} cx={dx} cy="-22" r="1.300" fill="#ffd24a" />)}
    </g>
  );
}

function Back() {
  return (
    <>
      <defs>
        <linearGradient id="hh-wall" x1="0" y1="0" x2="0" y2={FLOOR} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#10153a" /><stop offset="0.55" stop-color="#232e6a" /><stop offset="1" stop-color="#3d4c96" /></linearGradient>
        <linearGradient id="hh-floor" x1="0" y1={FLOOR} x2="0" y2="560" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#5565b2" /><stop offset="0.1" stop-color="#34407e" /><stop offset="0.3" stop-color="#232b5c" /><stop offset="1" stop-color="#141938" /></linearGradient>
        <linearGradient id="hh-glass" x1="0" y1="0" x2="0" y2={FLOOR} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#4a5ab8" /><stop offset="0.36" stop-color="#9a78c8" /><stop offset="0.62" stop-color="#f09a8a" /><stop offset="0.84" stop-color="#ffd088" /><stop offset="1" stop-color="#ffe9a8" /></linearGradient>
        <radialGradient id="hh-sunset"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.95" /><stop offset="0.35" stop-color="#ffe08a" stop-opacity="0.6" /><stop offset="1" stop-color="#ffb86a" stop-opacity="0" /></radialGradient>
        <radialGradient id="hh-shine" cx="195" cy="108" r="200" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.42" /><stop offset="0.4" stop-color="#ffb86a" stop-opacity="0.2" /><stop offset="1" stop-color="#ffb86a" stop-opacity="0" /></radialGradient>
        <radialGradient id="hh-pool" cx="195" cy="214" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(195 214) scale(230 46) translate(-195 -214)"><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.7" /><stop offset="0.55" stop-color="#ffb86a" stop-opacity="0.22" /><stop offset="1" stop-color="#ffb86a" stop-opacity="0" /></radialGradient>
      </defs>
      <rect y="-40" width={W} height={FLOOR + 40} fill="url(#hh-wall)" />
      {/* les travées latérales : deux niches en ogive, à peine plus claires que le mur */}
      {[43, 347].map((x) => <path d={`M${x - 24} ${FLOOR} V70 Q${x - 24} 38 ${x} 26 Q${x + 24} 38 ${x + 24} 70 V${FLOOR} Z`} fill="#1a2254" stroke="#3a4888" stroke-width="1.500" />)}
      {/* la grande verrière : une ogive large, son remplage (trois lancettes et leurs arcs) */}
      <clipPath id="hh-win"><path d="M103 150 V58 Q103 -6 195 -40 Q287 -6 287 58 V150 Z" /></clipPath>
      <g clip-path="url(#hh-win)">
        <rect x="100" y="-40" width="190" height="192" fill="url(#hh-glass)" />
        {/* le soleil bas, derrière la section */}
        <circle cx="195" cy="126" r="66" fill="url(#hh-sunset)" /><circle cx="195" cy="126" r="15" fill="#fffbe6" />
        {/* le lointain : deux chaînes de collines, un donjon et ses tours */}
        <path d="M100 150 V122 L118 108 L134 120 L150 104 L168 118 L186 110 L204 122 L222 106 L240 120 L258 110 L276 124 L290 114 V150 Z" fill="#a8689a" opacity="0.8" />
        <path d="M100 150 V134 L122 124 L146 136 L166 126 L190 138 L214 128 L238 138 L262 126 L290 136 V150 Z" fill="#6a4a8e" />
        <path d="M236 136 V112 H240 V108 H243 V112 H247 V108 H250 V112 H254 V136 Z M254 136 V122 H266 V136 Z M226 136 V124 H236 V136 Z M243 108 L246.500 98 L250 108 Z" fill="#553a7c" />
      </g>
      <g fill="none" stroke="#1a2254" stroke-linecap="round"><path d="M134 150 V74 Q134 52 164.500 44 Q195 52 195 74 V150 M195 74 Q195 52 225.500 44 Q256 52 256 74 V150 M134 74 Q134 62 118.500 56 M256 74 Q256 62 271.500 56" stroke-width="3" /><path d="M164.500 44 V8 M225.500 44 V8" stroke-width="2.400" /></g>
      <path d="M103 150 V58 Q103 -6 195 -40 Q287 -6 287 58 V150" fill="none" stroke="#141a40" stroke-width="6" /><path d="M106 150 V58 Q106 -3 195 -36 Q284 -3 284 58 V150" fill="none" stroke="#7f8fd0" stroke-width="1.400" opacity="0.8" />
      <rect y="-40" width={W} height={FLOOR + 60} fill="url(#hh-shine)" />
      {/* la plinthe du mur */}
      <rect y={FLOOR - 5} width={W} height="5" fill="#56669e" /><rect y={FLOOR - 5} width={W} height="1.300" fill="#aab6e6" opacity="0.8" />
      {/* le sol : dalles polies, la lumière de la verrière s'y couche */}
      <rect y={FLOOR} width={W} height={H} fill="url(#hh-floor)" />
      <rect y={FLOOR} width={W} height="130" fill="url(#hh-pool)" />
      {/* la voûte : elle s'assombrit tout en haut */}
      <rect y="-40" width={W} height="70" fill="#080b22" opacity="0.5" />
    </>
  );
}

function Mid() {
  const r = rng(7);
  return (
    <>
      <defs>
        <radialGradient id="hh-breath" cx="195" cy="96" r="150" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.34" /><stop offset="0.5" stop-color="#ffd98a" stop-opacity="0.12" /><stop offset="1" stop-color="#ffd98a" stop-opacity="0" /></radialGradient>
      </defs>
      <circle class="bd-sun" cx="195" cy="96" r="150" fill="url(#hh-breath)" />
      {/* les poussières qui dansent dans la lumière */}
      {Array.from({ length: 14 }, (_, i) => {
        const x = 96 + r() * 198, y = 60 + r() * 110;
        return <circle class="bd-mote" style={{ animationDelay: `${(-r() * 9).toFixed(1)}s`, animationDuration: `${(7 + r() * 6).toFixed(1)}s` }} cx={f(x)} cy={f(y)} r={f(0.700 + r() * 1.100)} fill={i % 3 ? '#fff6c8' : '#ffd98a'} />;
      })}
      {[[120, 84, 4], [262, 100, 3.500], [196, 66, 3]].map(([x, y, k], i) => <path class={`an-twinkle ${i % 2 ? 'an-late' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
    </>
  );
}

function Front() {
  const { cx, cy, rx, ry, step } = DAIS;
  const rx2 = rx + 20, ry2 = ry + 3, cy2 = cy + step + 2;
  return (
    <>
      <defs>
        <linearGradient id="hh-col" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#161c46" /><stop offset="0.5" stop-color="#34407e" /><stop offset="0.86" stop-color="#7f8fd0" /><stop offset="1" stop-color="#ffe0a8" /></linearGradient>
        <linearGradient id="hh-cloth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2574c" /><stop offset="0.6" stop-color="#b8343a" /><stop offset="1" stop-color="#8a2028" /></linearGradient>
        <linearGradient id="hh-bronze" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd98a" /><stop offset="0.45" stop-color="#c98a3a" /><stop offset="1" stop-color="#6b4016" /></linearGradient>
        <radialGradient id="hh-dais" cx={cx} cy={cy - 4} r="1" gradientUnits="userSpaceOnUse" gradientTransform={`translate(${cx} ${cy - 4}) scale(${rx} ${ry * 1.600}) translate(${-cx} ${-(cy - 4)})`}><stop offset="0" stop-color="#eef0ff" /><stop offset="0.55" stop-color="#b3bbe8" /><stop offset="1" stop-color="#7c86c4" /></radialGradient>
        <linearGradient id="hh-riser" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a336e" /><stop offset="0.5" stop-color="#5e6ab0" /><stop offset="1" stop-color="#2a336e" /></linearGradient>
        <linearGradient id="hh-seam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff3c7" stop-opacity="0" /><stop offset="0.5" stop-color="#fff3c7" stop-opacity="0.95" /><stop offset="1" stop-color="#fff3c7" stop-opacity="0" /></linearGradient>
      </defs>
      {/* les colonnes : deux près de la verrière, deux au bord de l'écran */}
      <Column x={90} w={18} side={1} /><Column x={300} w={18} side={-1} />
      <Column x={-2} w={16} side={1} /><Column x={392} w={16} side={-1} />
      {/* l'estrade : ombre au sol, marche du bas, marche du haut, filet d'or */}
      <ellipse cx={cx} cy={cy2 + step + 4} rx={rx2 + 10} ry={ry2 + 3} fill="#0a0d24" opacity="0.5" />
      <path d={`M${cx - rx2} ${cy2} V${cy2 + step} A${rx2} ${ry2} 0 0 0 ${cx + rx2} ${cy2 + step} V${cy2} Z`} fill="url(#hh-riser)" />
      <ellipse cx={cx} cy={cy2} rx={rx2} ry={ry2} fill="#8d97d2" />
      <path d={`M${cx - rx2} ${cy2 + 1} A${rx2} ${ry2} 0 0 0 ${cx + rx2} ${cy2 + 1}`} fill="none" stroke="url(#hh-seam)" stroke-width="1.600" />
      <path d={`M${cx - rx} ${cy} V${cy + step} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + step} V${cy} Z`} fill="url(#hh-riser)" />
      <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="url(#hh-dais)" />
      <path d={`M${cx - rx} ${cy + 1} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + 1}`} fill="none" stroke="url(#hh-seam)" stroke-width="1.800" />
      <ellipse cx={cx} cy={cy} rx={rx - 9} ry={ry - 2.200} fill="none" stroke="#e3b548" stroke-width="1.600" /><ellipse cx={cx} cy={cy} rx={rx - 13} ry={ry - 3.400} fill="none" stroke="#fff3c7" stroke-width="0.700" opacity="0.8" />
      {/* les braseros, au pied des colonnes */}
      <BrazierStand x={28} y={214} /><BrazierStand x={362} y={214} />
    </>
  );
}

function Top() {
  const { cx, cy, rx, ry } = DAIS;
  return (
    <>
      <defs>
        <radialGradient id="hh-fire-glow"><stop offset="0" stop-color="#ffb02a" stop-opacity="0.75" /><stop offset="0.5" stop-color="#ff7a1a" stop-opacity="0.22" /><stop offset="1" stop-color="#ff7a1a" stop-opacity="0" /></radialGradient>
      </defs>
      {/* le cercle de signes gravé dans l'estrade : il tourne lentement, à plat */}
      <g transform={`translate(${cx} ${cy}) scale(1 ${f(ry / rx)})`}>
        <g class="hh-ring" fill="none" stroke="#c9952a" opacity="0.85">
          <circle r={rx - 30} stroke-width="1.200" /><circle r={rx - 58} stroke-width="1" stroke-dasharray="3 9" />
          {Array.from({ length: 16 }, (_, i) => { const a = (i / 16) * Math.PI * 2, d = rx - 44; return <path d={GLYPHS[i % GLYPHS.length]} stroke-width="1.500" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(Math.cos(a) * d)} ${f(Math.sin(a) * d)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(1.900)`} />; })}
        </g>
      </g>
      {/* les bannières, sous les médaillons */}
      <Banner x={43} y={70} len={62} w={30} glyph={1} /><Banner x={347} y={70} len={62} w={30} glyph={4} />
      {/* les flammes des braseros et leurs étincelles */}
      <BrazierFire x={28} y={214} /><BrazierFire x={362} y={214} />
    </>
  );
}

export function HeroesBackdrop() {
  const box = { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMin slice' };
  return (
    <>
      <svg {...box}><Back /></svg>
      <svg {...box}><Mid /></svg>
      <svg {...box}><Front /></svg>
      <svg {...box}><Top /></svg>
    </>
  );
}
