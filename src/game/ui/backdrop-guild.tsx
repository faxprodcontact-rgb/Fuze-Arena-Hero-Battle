// Le décor de l'onglet Guilde : la forteresse de la guilde au coucher du soleil. Deux grandes tours encadrent la scène
// (bannières cramoisies au blason de la guilde, toits d'ardoise, drapeaux), un rempart crénelé les relie ; au fond, le
// soleil se couche derrière les montagnes, les premières étoiles s'allument, et un dragon passe au loin (le boss de la
// guilde). La lumière vient du soleil, derrière : les tours sont à contre-jour, leur bord tourné vers lui s'allume.
// Sous le panorama (là où sont les cartes et les onglets), la cour reste calme : un dallage sombre, rien qui se découpe.
// Quatre dessins superposés, comme les autres parties : le ciel et les montagnes ; ce qui bouge derrière (nuages,
// dragon) ; les tours et le rempart ; ce qui bouge devant (bannières, drapeaux, flammes, braises).
import { spark } from './portal';

const W = 390, H = 844;
/** Le haut du rempart : le bas du panorama (le bandeau de titre se pose juste au-dessus). */
const WALL = 170;
/** Le haut des tours (sous l'encorbellement) : assez bas pour que le toit et le drapeau ne soient pas coupés en haut. */
const TOWER_TOP = 86;
/** Le soleil du soir : bas sur la droite, au-dessus du bandeau de titre (jamais dans son axe, jamais caché par lui). */
const SUN = { x: 292, y: 80, r: 24 };

const f = (n: number) => n.toFixed(1);

function Defs() {
  return (
    <defs>
      <linearGradient id="gd-sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#1f1a48" /><stop offset="0.38" stop-color="#4c2c66" /><stop offset="0.7" stop-color="#b85e66" /><stop offset="0.88" stop-color="#f0985a" /><stop offset="1" stop-color="#ffc277" />
      </linearGradient>
      <radialGradient id="gd-sunglow"><stop offset="0" stop-color="#ffd690" stop-opacity="0.75" /><stop offset="0.45" stop-color="#ff9a5a" stop-opacity="0.28" /><stop offset="1" stop-color="#ff9a5a" stop-opacity="0" /></radialGradient>
      <radialGradient id="gd-sun" cx="0.45" cy="0.4"><stop offset="0" stop-color="#fffbe0" /><stop offset="0.6" stop-color="#ffd27a" /><stop offset="1" stop-color="#ff9a48" /></radialGradient>
      <linearGradient id="gd-floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2440" /><stop offset="0.3" stop-color="#271932" /><stop offset="1" stop-color="#140c1c" /></linearGradient>
      <linearGradient id="gd-cloud" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a4f86" /><stop offset="0.6" stop-color="#c67a82" /><stop offset="1" stop-color="#ffc08a" /></linearGradient>
      {/* les tours : à contre-jour, leur bord tourné vers le soleil s'allume (dégradé dans un sens pour chaque tour) */}
      <linearGradient id="gd-tower-l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c1226" /><stop offset="0.62" stop-color="#3a2546" /><stop offset="0.9" stop-color="#7a4256" /><stop offset="1" stop-color="#e08a62" /></linearGradient>
      <linearGradient id="gd-tower-r" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#1c1226" /><stop offset="0.62" stop-color="#3a2546" /><stop offset="0.9" stop-color="#7a4256" /><stop offset="1" stop-color="#e08a62" /></linearGradient>
      <linearGradient id="gd-roof" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1e44" /><stop offset="0.7" stop-color="#2f3a78" /><stop offset="1" stop-color="#6a64a8" /></linearGradient>
      <linearGradient id="gd-wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a2c4a" /><stop offset="1" stop-color="#26182e" /></linearGradient>
      <linearGradient id="gd-banner" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d84848" /><stop offset="1" stop-color="#8a1e2a" /></linearGradient>
      <linearGradient id="gd-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
      <radialGradient id="gd-fire"><stop offset="0" stop-color="#fff2b0" /><stop offset="0.45" stop-color="#ffa63a" stop-opacity="0.9" /><stop offset="1" stop-color="#ff6a1a" stop-opacity="0" /></radialGradient>
      <radialGradient id="gd-window"><stop offset="0" stop-color="#ffe9a0" /><stop offset="1" stop-color="#e88a2a" /></radialGradient>
    </defs>
  );
}

/** Le ciel, les étoiles, le soleil couchant, deux chaînes de montagnes ; la cour sombre en dessous. */
function Back() {
  const stars: [number, number, number][] = [[38, 20, 1.3], [96, 44, 0.9], [148, 14, 1.1], [205, 34, 0.8], [244, 10, 1.2], [318, 30, 1], [178, 62, 0.8], [122, 76, 0.9], [356, 64, 0.8]];
  return (
    <>
      <Defs />
      <rect width={W} height={H} fill="url(#gd-floor)" />
      <rect width={W} height={WALL + 40} fill="url(#gd-sky)" />
      {stars.map(([x, y, r], i) => <circle class="bd-star" style={{ animationDelay: `${-i * 0.7}s` }} cx={x} cy={y} r={r} fill="#fff6e0" />)}
      <circle class="bd-sun" cx={SUN.x} cy={SUN.y} r="120" fill="url(#gd-sunglow)" />
      <circle cx={SUN.x} cy={SUN.y} r={SUN.r} fill="url(#gd-sun)" />
      {/* la chaîne lointaine : flancs tournés vers le soleil plus chauds */}
      <path d="M-10 150 L22 132 L50 143 L84 118 L116 138 L152 112 L186 132 L214 124 L238 136 L286 110 L322 132 L356 116 L400 136 V214 H-10 Z" fill="#6a3c6e" />
      <path d="M84 118 L116 138 L98 140 Z M152 112 L186 132 L166 134 Z M214 124 L238 136 L224 137 Z M22 132 L50 143 L36 144 Z" fill="#a8586a" opacity="0.75" />
      <path d="M286 110 L262 136 L276 137 Z M356 116 L330 134 L344 135 Z" fill="#a8586a" opacity="0.75" />
      <path d="M-10 166 Q36 150 84 160 Q134 170 182 156 Q236 144 288 160 Q340 172 400 154 V214 H-10 Z" fill="#40264e" />
      <path d="M-10 166 Q36 150 84 160 Q134 170 182 156 Q236 144 288 160 Q340 172 400 154" fill="none" stroke="#e8946a" stroke-width="1.2" opacity="0.45" />
      {/* la cour, sous le panorama : quelques grandes dalles à peine marquées */}
      <g fill="none" stroke="#000" stroke-width="1.2" opacity="0.18">
        <path d={`M0 ${WALL + 120} H${W} M0 ${WALL + 260} H${W} M0 ${WALL + 430} H${W}`} />
        <path d={`M110 ${WALL + 120} V${WALL + 260} M270 ${WALL + 120} V${WALL + 260} M60 ${WALL + 260} V${WALL + 430} M200 ${WALL + 260} V${WALL + 430} M330 ${WALL + 260} V${WALL + 430}`} />
      </g>
    </>
  );
}

/** Un nuage du soir : des bosses sombres en haut, éclairées par en dessous (le soleil est bas). */
function DuskCloud({ x, y, s }: { x: number; y: number; s: number }) {
  const lobes: [number, number, number][] = [[14, -12, 12], [34, -20, 17], [58, -16, 14], [76, -10, 10]];
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <g fill="url(#gd-cloud)"><rect x="0" y="-14" width="88" height="14" rx="7" />{lobes.map(([cx, cy, r]) => <circle cx={cx} cy={cy} r={r} />)}</g>
      <path d="M6 -1 H82" stroke="#ffd8a8" stroke-width="2.4" stroke-linecap="round" opacity="0.75" />
    </g>
  );
}

/** Le dragon qui passe au loin : une silhouette sombre, les ailes battent ; il traverse le ciel de droite à gauche. */
function Dragon() {
  return (
    <g class="gd-dragon">
      <g transform="scale(0.9)">
        <path d="M-22 2 Q-8 -4 6 0 Q16 2 24 -3 L30 -5 L27 0 L32 1 L25 3 Q14 8 2 6 Q-10 6 -22 2 Z" fill="#2a1834" />
        <path d="M-22 2 Q-32 6 -40 2 Q-34 4 -30 0 Z" fill="#2a1834" />
        <g class="gd-wing"><path d="M-4 0 Q-10 -18 -26 -24 Q-16 -14 -18 -8 Q-12 -10 -10 -4 Q-6 -6 -4 0 Z" fill="#3a2244" /></g>
        <g class="gd-wing gd-wing-2"><path d="M4 -1 Q2 -22 14 -30 Q10 -18 16 -12 Q18 -10 12 -6 Q8 -4 4 -1 Z" fill="#2a1834" /></g>
        <path d="M26 -3.5 L30 -5" stroke="#ffb070" stroke-width="1" opacity="0.8" />
      </g>
    </g>
  );
}

function Mid() {
  return (
    <>
      <g class="bd-cloud bd-slow"><DuskCloud x={6} y={66} s={0.95} /></g>
      <g class="bd-cloud"><DuskCloud x={214} y={52} s={0.7} /></g>
      <g class="bd-cloud bd-slow"><DuskCloud x={300} y={98} s={0.5} /></g>
      <g transform="translate(0 74)"><Dragon /></g>
    </>
  );
}

/**
 * Une grande tour ronde, de face : fût à contre-jour (`side` 1 = le soleil est à sa droite), créneaux sur leur
 * encorbellement, toit conique d'ardoise et son épi d'or, deux fenêtres allumées. Centre en x, toit en haut.
 */
function Tower({ x, side }: { x: number; side: 1 | -1 }) {
  const w = 76, h = w / 2, top = TOWER_TOP;
  const id = side === 1 ? 'gd-tower-l' : 'gd-tower-r';
  return (
    <g>
      <rect x={x - h} y={top + 8} width={w} height={WALL + 60 - top} fill={`url(#${id})`} />
      {/* l'encorbellement et les créneaux */}
      <rect x={x - h - 5} y={top} width={w + 10} height="10" fill={`url(#${id})`} />
      <path d={`M${x - h - 5} ${top + 10} H${x + h + 5}`} stroke="#000" stroke-width="2" opacity="0.35" />
      {[-34, -18, -2, 14, 30].map((dx) => <rect x={x + dx - 4.5} y={top - 9} width="9" height="10" fill={`url(#${id})`} />)}
      {/* le toit conique et son épi */}
      <path d={`M${x - h - 7} ${top - 9} L${x} ${top - 66} L${x + h + 7} ${top - 9} Z`} fill="url(#gd-roof)" />
      <path d={`M${x} ${top - 66} L${x + side * (h + 7)} ${top - 9} H${x + side * (h - 4)} Z`} fill="#e08a62" opacity="0.4" />
      <path d={`M${x - h - 7} ${top - 9} H${x + h + 7}`} stroke="#140c20" stroke-width="2.4" />
      <path d={`M${x} ${top - 66} V${top - 78}`} stroke="url(#gd-gold)" stroke-width="2.4" />
      <circle cx={x} cy={top - 66} r="3" fill="url(#gd-gold)" />
      {/* deux fenêtres allumées, arc en haut */}
      {[[x - 14, top + 30], [x + 12, top + 92]].map(([wx, wy]) => <path d={`M${wx! - 4.5} ${wy! + 10} V${wy} Q${wx} ${wy! - 6} ${wx! + 4.5} ${wy} V${wy! + 10} Z`} fill="url(#gd-window)" />)}
      {/* l'arête allumée par le soleil */}
      <path d={`M${x + side * (h - 0.8)} ${top + 10} V${WALL + 60}`} stroke="#ffb27a" stroke-width="1.6" opacity="0.65" />
    </g>
  );
}

/** Le rempart crénelé entre les deux tours, ses meurtrières ; le haut du mur accroche la lumière. */
function Wall() {
  const merlons = Array.from({ length: 15 }, (_, i) => 79 + i * 16.5);
  return (
    <g>
      <rect x="0" y={WALL} width={W} height="64" fill="url(#gd-wall)" />
      {merlons.map((mx) => <rect x={mx} y={WALL - 9} width="10" height="10" fill="#4a2c4a" />)}
      <path d={`M0 ${WALL} H${W}`} stroke="#e8946a" stroke-width="1.4" opacity="0.5" />
      {[104, 152, 238, 286].map((sx) => <rect x={sx} y={WALL + 14} width="3" height="12" rx="1.5" fill="#140c20" />)}
      <rect x="0" y={WALL + 40} width={W} height="24" fill="#000" opacity="0.18" />
    </g>
  );
}

/** Un brasero de fer sur le rempart (la flamme est animée dans le calque de devant). */
function Brazier({ x }: { x: number }) {
  return (
    <g>
      <path d={`M${x - 3} ${WALL - 9} L${x - 7} ${WALL - 1} M${x + 3} ${WALL - 9} L${x + 7} ${WALL - 1}`} stroke="#1a1020" stroke-width="2.4" stroke-linecap="round" />
      <path d={`M${x - 9} ${WALL - 17} Q${x} ${WALL - 7} ${x + 9} ${WALL - 17} Z`} fill="#2a1a30" />
      <path d={`M${x - 9} ${WALL - 17} H${x + 9}`} stroke="url(#gd-gold)" stroke-width="1.6" />
    </g>
  );
}

function Front() {
  return (
    <>
      <Wall />
      <Brazier x={74} /><Brazier x={316} />
      <Tower x={30} side={1} /><Tower x={360} side={-1} />
    </>
  );
}

/** Une grande bannière cramoisie, ourlée d'or, frappée d'un blason inventé (écu, chevron et étoile). Haut en (x, y). */
function Banner({ x, y }: { x: number; y: number }) {
  const w = 30, h = 74;
  return (
    <g class="bd-banner" style={{ transformOrigin: `${x}px ${y}px`, transformBox: 'view-box' }}>
      <rect x={x - w / 2 - 4} y={y - 3} width={w + 8} height="5" rx="2.5" fill="url(#gd-gold)" />
      <path d={`M${x - w / 2} ${y} H${x + w / 2} V${y + h} L${x} ${y + h + 10} L${x - w / 2} ${y + h} Z`} fill="url(#gd-banner)" />
      <path d={`M${x - w / 2 + 3} ${y + 3} H${x + w / 2 - 3} V${y + h - 2} L${x} ${y + h + 6} L${x - w / 2 + 3} ${y + h - 2} Z`} fill="none" stroke="url(#gd-gold)" stroke-width="1.6" />
      {/* le blason : un écu, un chevron d'or, une étoile */}
      <path d={`M${x - 9} ${y + 22} H${x + 9} V${y + 34} Q${x + 9} ${y + 44} ${x} ${y + 48} Q${x - 9} ${y + 44} ${x - 9} ${y + 34} Z`} fill="#2a1a40" stroke="url(#gd-gold)" stroke-width="1.6" />
      <path d={`M${x - 6} ${y + 38} L${x} ${y + 31} L${x + 6} ${y + 38}`} fill="none" stroke="#ffd45c" stroke-width="2.2" stroke-linejoin="round" />
      <path d={spark(x, y + 26.5, 3)} fill="#ffd45c" />
      <path d={`M${x - w / 2} ${y} H${x - w / 2 + 7} V${y + h + 3} L${x - w / 2} ${y + h} Z`} fill="#000" opacity="0.2" />
    </g>
  );
}

/** Un drapeau qui claque, au bout de l'épi d'une tour. */
function Flag({ x, y, dir }: { x: number; y: number; dir: 1 | -1 }) {
  return (
    <g class="bd-flag" style={{ transformOrigin: `${x}px ${y}px`, transformBox: 'view-box' }}>
      <path d={`M${x} ${y} Q${x + dir * 10} ${y - 3} ${x + dir * 20} ${y + 1} Q${x + dir * 14} ${y + 5} ${x + dir * 20} ${y + 9} Q${x + dir * 10} ${y + 6} ${x} ${y + 9} Z`} fill="#d84848" />
    </g>
  );
}

/** La flamme d'un brasero : trois langues, qui vacillent. */
function Flame({ x, y }: { x: number; y: number }) {
  return (
    <g class="gd-flame" style={{ transformOrigin: `${x}px ${y}px`, transformBox: 'view-box' }}>
      <circle cx={x} cy={y - 8} r="16" fill="url(#gd-fire)" opacity="0.6" />
      <path d={`M${x - 7} ${y} Q${x - 8} ${y - 10} ${x - 1} ${y - 20} Q${x + 1} ${y - 12} ${x + 4} ${y - 14} Q${x + 8} ${y - 8} ${x + 7} ${y} Z`} fill="#ff6a1a" />
      <path d={`M${x - 4} ${y} Q${x - 5} ${y - 7} ${x} ${y - 13} Q${x + 4} ${y - 7} ${x + 4} ${y} Z`} fill="#ffb02a" />
      <path d={`M${x - 2} ${y} Q${x - 2} ${y - 4} ${x + 0.5} ${y - 7} Q${x + 2.5} ${y - 4} ${x + 2} ${y} Z`} fill="#fff2b0" />
    </g>
  );
}

function Top() {
  const embers: [number, number, number][] = [[74, WALL - 26, 0], [78, WALL - 30, -2.4], [316, WALL - 26, -1.2], [312, WALL - 30, -3.6]];
  return (
    <>
      <Banner x={30} y={TOWER_TOP + 22} /><Banner x={360} y={TOWER_TOP + 22} />
      <Flag x={30} y={TOWER_TOP - 76} dir={1} /><Flag x={360} y={TOWER_TOP - 76} dir={-1} />
      <Flame x={74} y={WALL - 17} /><Flame x={316} y={WALL - 17} />
      {embers.map(([x, y, d]) => <circle class="bd-mote" style={{ animationDelay: `${d}s`, animationDuration: '5s' }} cx={x} cy={y} r="1.2" fill="#ffd27a" />)}
      <path class="an-twinkle" style={{ transformOrigin: `${f(SUN.x - 38)}px ${SUN.y - 18}px` }} d={spark(SUN.x - 38, SUN.y - 18, 4)} fill="#fff" />
    </>
  );
}

export function GuildBackdrop() {
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
