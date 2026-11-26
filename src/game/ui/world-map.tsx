// La carte de la campagne (fenêtre ouverte par la pilule du chapitre, demande du propriétaire du 26/11) : une illustration
// lisse dessinée par le code (atelier backdrop-kit.tsx, une lumière en haut à droite) à la place de l'ancienne image en
// pixels. Les 8 régions sont des lieux posés sur une dalle, reliés par un chemin qui monte en lacets du bas vers le haut :
// prairie, ronciers, bayou, cendres, toundra, orage, temple, abysses (les décors des clans, look.ts). Le chemin déjà fait
// est d'or ; la région en cours brille (son fanion sautille) ; les régions fermées sont éteintes, avec un cadenas. Sous
// chaque lieu : son élément, ses chapitres et un point par chapitre (fait, en cours, à faire).
import { CLANS, clanElement, regionChapters } from '../look';
import { Art, Icon, Sign } from './kit';
import { Glow, Mat, Soft, Stars, Vol, f, rr, spark } from './backdrop-kit';

/** Une touffe (feuillage, nuage, fumée) : trois bosses rondes, la plus haute au milieu, sur une base plate (x0 = gauche). */
function puff(x0: number, base: number, w: number) {
  const s = w / 3, r1 = s * 0.6, r2 = s * 0.74;
  return `M${f(x0)} ${f(base)} A${f(r1)} ${f(r1)} 0 1 1 ${f(x0 + s)} ${f(base)} A${f(r2)} ${f(r2)} 0 1 1 ${f(x0 + 2 * s)} ${f(base)} A${f(r1)} ${f(r1)} 0 1 1 ${f(x0 + w)} ${f(base)} Z`;
}

const VW = 340, VH = 460;
const P = 'cm';
/** La place de chaque région : centre de sa dalle (x) et haut de la dalle (y), dans l'ordre de la campagne (bas → haut). */
const XL = 88, XR = 252;
const ROWS = [390, 284, 178, 72];
const SPOTS: [number, number][] = [
  [XL, ROWS[0]!], [XR, ROWS[0]!], [XR, ROWS[1]!], [XL, ROWS[1]!], [XL, ROWS[2]!], [XR, ROWS[2]!], [XR, ROWS[3]!], [XL, ROWS[3]!],
];
const SLAB_W = 112, SLAB_H = 18, TOP = 7;

/** Les teintes du sol (dessus de la dalle) de chaque lieu. */
const GROUND = ['#6cc46a', '#a7794a', '#6f8a4e', '#4a3a3e', '#e8ecf4', '#4f5f7a', '#d9a65e', '#2f6f80'];

const pct = (x: number, y: number) => ({ left: `${(x / VW) * 100}%`, top: `${(y / VH) * 100}%` });

// ---------- Les lieux (x = centre, y = haut de la dalle ; chacun tient dans x ± 52, y − 60 … y) ----------

function Prairie({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={`M${x - 54} ${y + 1} Q${x - 30} ${y - 34} ${x + 2} ${y - 22} Q${x + 30} ${y - 40} ${x + 54} ${y + 1} Z`} fill={`url(#${P}-grass)`} />
      <Vol p={P} d={rr(x + 13, y - 34, 6, 30, 2)} fill={`url(#${P}-wood)`} line={1.2} depth={2} />
      <Vol p={P} d={puff(x - 6, y - 28, 44)} fill={`url(#${P}-leaf)`} depth={4} />
      <Vol p={P} d={`M${x - 30} ${y - 20} V${y - 50} L${x - 14} ${y - 44} L${x - 30} ${y - 38} Z`} fill={`url(#${P}-gold)`} line={1.2} depth={2} />
      <path d={`M${x - 30} ${y - 4} V${y - 50}`} stroke="#1f1238" stroke-width="2.4" stroke-linecap="round" opacity="0.8" />
    </g>
  );
}

function Ronces({ x, y }: { x: number; y: number }) {
  const thorns = (cx: number, cy: number, r: number) => {
    let d = '';
    for (let a = 200; a <= 340; a += 35) {
      const t = (a * Math.PI) / 180, px = cx + Math.cos(t) * r, py = cy + Math.sin(t) * r;
      const nx = Math.cos(t), ny = Math.sin(t);
      d += `M${f(px - ny * 3)} ${f(py + nx * 3)} L${f(px + nx * 8)} ${f(py + ny * 8)} L${f(px + ny * 3)} ${f(py - nx * 3)} Z `;
    }
    return d;
  };
  return (
    <g>
      <Vol p={P} d={`M${x - 8} ${y + 1} Q${x - 6} ${y - 34} ${x + 18} ${y - 40} Q${x + 44} ${y - 34} ${x + 46} ${y + 1} Z`} fill={`url(#${P}-rock)`} depth={5} />
      <Vol p={P} d={`M${x - 52} ${y + 1} Q${x - 50} ${y - 46} ${x - 22} ${y - 46} Q${x + 4} ${y - 46} ${x + 6} ${y + 1} L${x - 3} ${y + 1} Q${x - 4} ${y - 36} ${x - 22} ${y - 36} Q${x - 41} ${y - 36} ${x - 42} ${y + 1} Z`} fill={`url(#${P}-thorn)`} depth={3} />
      <Vol p={P} d={thorns(x - 22, y - 41, 6)} fill={`url(#${P}-thorn)`} line={1} depth={1} shade={0} />
      <Vol p={P} d={`M${x + 14} ${y + 1} Q${x + 16} ${y - 26} ${x + 34} ${y - 26} Q${x + 52} ${y - 26} ${x + 54} ${y + 1} L${x + 47} ${y + 1} Q${x + 46} ${y - 19} ${x + 34} ${y - 19} Q${x + 22} ${y - 19} ${x + 21} ${y + 1} Z`} fill={`url(#${P}-thorn)`} depth={3} />
    </g>
  );
}

function Bayou({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={`M${x + 4} ${y + 1} Q${x + 8} ${y - 26} ${x - 2} ${y - 40} Q${x + 10} ${y - 36} ${x + 14} ${y - 24} Q${x + 18} ${y - 40} ${x + 34} ${y - 44} Q${x + 22} ${y - 32} ${x + 22} ${y - 12} L${x + 24} ${y + 1} Z`} fill={`url(#${P}-wood)`} depth={3} />
      <Vol p={P} d={puff(x - 10, y - 36, 26)} fill={`url(#${P}-moss)`} depth={3} />
      <Vol p={P} d={puff(x + 16, y - 42, 24)} fill={`url(#${P}-moss)`} depth={3} />
      <circle cx={x - 34} cy={y - 26} r="14" fill={`url(#${P}-lamp)`} />
      <Vol p={P} d={rr(x - 38, y - 30, 8, 9, 2.5)} fill={`url(#${P}-gold)`} line={1.1} depth={1} />
      <path d={`M${x - 34} ${y - 21} V${y + 1}`} stroke="#1f1238" stroke-width="2" opacity="0.8" />
      {[x - 50, x - 46, x + 40, x + 46].map((rx, i) => (
        <Vol p={P} d={`M${rx - 2} ${y + 1} Q${rx - 3} ${y - 14 - (i % 2) * 6} ${rx + 1} ${y - 22 - (i % 2) * 6} Q${rx + 2} ${y - 12} ${rx + 2} ${y + 1} Z`} fill={`url(#${P}-reed)`} line={1} depth={1} shade={0} />
      ))}
    </g>
  );
}

function Cendres({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={puff(x + 2, y - 50, 26)} fill={`url(#${P}-smoke)`} depth={3} rim={0.3} />
      <Vol p={P} d={`M${x - 50} ${y + 1} L${x - 14} ${y - 44} Q${x - 2} ${y - 48} ${x + 10} ${y - 44} L${x + 50} ${y + 1} Z`} fill={`url(#${P}-ash)`} depth={6} />
      <path d={`M${x - 11} ${y - 44} Q${x - 2} ${y - 50} ${x + 7} ${y - 44} Q${x + 2} ${y - 30} ${x + 8} ${y - 18} Q${x + 12} ${y - 8} ${x + 6} ${y + 1} L${x + 1} ${y + 1} Q${x + 4} ${y - 14} ${x - 3} ${y - 28} Q${x - 6} ${y - 36} ${x - 11} ${y - 44} Z`} fill={`url(#${P}-lava)`} />
      <ellipse class="cm-ember" cx={x - 2} cy={y - 46} rx="18" ry="10" fill={`url(#${P}-ember)`} />
    </g>
  );
}

function Toundra({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={`M${x - 54} ${y + 1} L${x - 22} ${y - 46} Q${x - 18} ${y - 50} ${x - 14} ${y - 46} L${x + 12} ${y - 12} L${x + 24} ${y - 30} Q${x + 27} ${y - 33} ${x + 30} ${y - 30} L${x + 54} ${y + 1} Z`} fill={`url(#${P}-ice)`} depth={6} />
      <path d={`M${x - 29} ${y - 36} L${x - 22} ${y - 46} Q${x - 18} ${y - 50} ${x - 14} ${y - 46} L${x - 7} ${y - 35} L${x - 13} ${y - 38} L${x - 18} ${y - 33} L${x - 23} ${y - 39} Z`} fill="#ffffff" opacity="0.92" />
      {[[x + 34, 0], [x + 44, 4]].map(([px, k]) => (
        <Vol p={P} d={`M${px! - 9 + k! * 0.5} ${y + 1} L${px} ${y - 28 + k! * 2} L${px! + 9 - k! * 0.5} ${y + 1} Z`} fill={`url(#${P}-pine)`} line={1.2} depth={2} />
      ))}
    </g>
  );
}

function Orage({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={`M${x - 54} ${y + 1} Q${x - 40} ${y - 12} ${x - 26} ${y - 4} Q${x - 10} ${y - 14} ${x + 6} ${y - 4} Q${x + 22} ${y - 14} ${x + 38} ${y - 4} Q${x + 48} ${y - 10} ${x + 54} ${y + 1} Z`} fill={`url(#${P}-sea)`} depth={3} />
      <Vol p={P} d={puff(x - 36, y - 30, 66)} fill={`url(#${P}-storm)`} depth={5} rim={0.3} />
      <path class="cm-bolt" d={`M${x + 2} ${y - 34} L${x - 8} ${y - 18} L${x} ${y - 18} L${x - 6} ${y - 4} L${x + 10} ${y - 22} L${x + 2} ${y - 22} L${x + 8} ${y - 34} Z`} fill="#ffe27a" stroke="#1f1238" stroke-opacity="0.6" stroke-width="1" stroke-linejoin="round" />
    </g>
  );
}

function Temple({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={rr(x - 36, y - 8, 72, 9, 2)} fill={`url(#${P}-sand)`} depth={2} />
      {[-24, -8, 8, 24].map((dx) => <Vol p={P} d={rr(x + dx - 4, y - 34, 8, 27, 2)} fill={`url(#${P}-sand)`} line={1.2} depth={2} />)}
      <Vol p={P} d={`M${x - 40} ${y - 34} L${x} ${y - 52} L${x + 40} ${y - 34} Z`} fill={`url(#${P}-roof)`} depth={3} />
      <path class="cm-flame" style={{ transformOrigin: `${x}px ${y - 52}px` }} d={`M${x} ${y - 52} Q${x - 7} ${y - 58} ${x - 2} ${y - 66} Q${x} ${y - 61} ${x + 3} ${y - 64} Q${x + 8} ${y - 57} ${x} ${y - 52} Z`} fill={`url(#${P}-fire)`} />
    </g>
  );
}

function Abysses({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <Vol p={P} d={`M${x - 46} ${y + 1} L${x - 38} ${y - 30} Q${x - 34} ${y - 36} ${x - 30} ${y - 30} L${x - 22} ${y + 1} Z`} fill={`url(#${P}-deep)`} depth={3} />
      <Vol p={P} d={`M${x + 8} ${y + 1} L${x + 22} ${y - 46} Q${x + 27} ${y - 52} ${x + 32} ${y - 46} L${x + 46} ${y + 1} Z`} fill={`url(#${P}-deep)`} depth={4} />
      {[[x - 10, y - 2, 12], [x - 2, y - 2, 18], [x + 4, y - 2, 10]].map(([cx, cy, h]) => (
        <Vol p={P} d={`M${cx! - 4} ${cy} L${cx} ${cy! - h!} L${cx! + 4} ${cy} Z`} fill={`url(#${P}-crystal)`} line={1} depth={1} />
      ))}
      <ellipse cx={x - 3} cy={y - 10} rx="16" ry="12" fill={`url(#${P}-lamp2)`} />
      {[[x - 14, y - 30, 2.4], [x - 6, y - 42, 1.8], [x + 2, y - 34, 1.4]].map(([cx, cy, r], i) => (
        <circle class="cm-bubble" style={{ animationDelay: `${-i * 1.1}s` }} cx={cx} cy={cy} r={r} fill="none" stroke="#bff6ea" stroke-width="1.2" opacity="0.8" />
      ))}
    </g>
  );
}

const PLACES = [Prairie, Ronces, Bayou, Cendres, Toundra, Orage, Temple, Abysses];

/** Le chemin d'une région à la suivante (même rangée : tout droit ; rangée du dessus : un lacet par l'extérieur). */
function leg(i: number): string {
  const [x0, y0] = SPOTS[i]!, [x1, y1] = SPOTS[i + 1]!;
  const a = y0 + SLAB_H - 4, b = y1 + SLAB_H - 4;
  if (y0 === y1) return `M${x0} ${a} Q${(x0 + x1) / 2} ${a + 14} ${x1} ${b}`;
  const out = x0 < VW / 2 ? -1 : 1;
  return `M${x0} ${a} C${x0 + out * 78} ${a} ${x1 + out * 78} ${b} ${x1} ${b}`;
}

/** La carte : `cur` = le chapitre en cours. */
export function ChapterMap({ cur }: { cur: number }) {
  const regions = regionChapters();
  const here = Math.max(0, regions.findIndex((r) => cur >= r.from && cur <= r.to));
  return (
    <div class="cmap">
      <svg class="cmap-art" viewBox={`0 0 ${VW} ${VH}`} aria-hidden="true">
        <defs>
          <Soft p={P} />
          <linearGradient id={`${P}-sky`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#2f2672" /><stop offset="0.55" stop-color="#221a55" /><stop offset="1" stop-color="#150f3a" />
          </linearGradient>
          <Mat id={`${P}-grass`} c="#5bb85e" /><Mat id={`${P}-leaf`} c="#3f9e55" /><Mat id={`${P}-wood`} c="#8a5a3a" /><Mat id={`${P}-gold`} c="#ffc22e" />
          <Mat id={`${P}-rock`} c="#8d7058" /><Mat id={`${P}-thorn`} c="#5e4a3a" /><Mat id={`${P}-moss`} c="#5d7a44" /><Mat id={`${P}-reed`} c="#7d9a4a" />
          <Mat id={`${P}-ash`} c="#4b3f4a" /><Mat id={`${P}-smoke`} c="#6a6082" /><Mat id={`${P}-ice`} c="#c9d3e6" /><Mat id={`${P}-pine`} c="#2f7a5a" />
          <Mat id={`${P}-sea`} c="#2f7f8f" /><Mat id={`${P}-storm`} c="#57557a" /><Mat id={`${P}-sand`} c="#e3b878" /><Mat id={`${P}-roof`} c="#c8482e" />
          <Mat id={`${P}-deep`} c="#2c5a6e" /><Mat id={`${P}-crystal`} c="#58e0c8" /><Mat id={`${P}-stone`} c="#4d4a6a" />
          <linearGradient id={`${P}-lava`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe27a" /><stop offset="0.5" stop-color="#ff8a2a" /><stop offset="1" stop-color="#e2401f" /></linearGradient>
          <linearGradient id={`${P}-fire`} x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ff5a1f" /><stop offset="1" stop-color="#ffe27a" /></linearGradient>
          <Glow id={`${P}-ember`} c="#ff9a3a" a={0.75} /><Glow id={`${P}-lamp`} c="#ffd35c" a={0.7} /><Glow id={`${P}-lamp2`} c="#5ef0d8" a={0.55} />
          <filter id={`${P}-blur`} x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="5" /></filter>
        </defs>
        <rect x="0" y="0" width={VW} height={VH} fill={`url(#${P}-sky)`} />
        <Stars seed={7} n={16} y1={VH * 0.5} color="#fff6cf" />
        <path d={spark(312, 26, 7)} fill="#ffe27a" opacity="0.8" />
        {/* le chemin : une route de pierre ; la part faite, d'or */}
        <g fill="none" stroke-linecap="round">
          {SPOTS.slice(0, -1).map((_, i) => <path d={leg(i)} stroke="#1f1238" stroke-opacity="0.55" stroke-width="15" />)}
          {SPOTS.slice(0, -1).map((_, i) => <path d={leg(i)} stroke="#4d4a6a" stroke-width="11" />)}
          {SPOTS.slice(0, -1).map((_, i) => <path d={leg(i)} stroke="#6a6788" stroke-width="3" transform="translate(-1 -2)" opacity="0.7" />)}
          {SPOTS.slice(0, -1).map((_, i) => i < here && <path class="cm-done-road" d={leg(i)} stroke="#ffc94d" stroke-width="5" />)}
        </g>
        {SPOTS.map(([x, y], i) => {
          const Place = PLACES[i]!;
          const state = i < here ? 'done' : i === here ? 'here' : 'locked';
          return (
            <g class={`cm-place ${state}`}>
              {state === 'here' && <rect x={x - SLAB_W / 2 - 6} y={y - 26} width={SLAB_W + 12} height={SLAB_H + 34} rx="14" fill="#ffc94d" opacity="0.45" filter={`url(#${P}-blur)`} />}
              {/* la dalle : le dessus de la couleur du sol du lieu, le côté en pierre */}
              <Vol p={P} d={rr(x - SLAB_W / 2, y, SLAB_W, SLAB_H, 7)} fill={`url(#${P}-stone)`} depth={3} />
              <Vol p={P} d={rr(x - SLAB_W / 2 + 1, y, SLAB_W - 2, TOP + 2, 5)} fill={GROUND[i]!} line={0} depth={2} shade={0.25} rim={0.5} />
              {state === 'here' && <path d={rr(x - SLAB_W / 2, y, SLAB_W, SLAB_H, 7)} fill="none" stroke="#ffd35c" stroke-width="2" />}
              <Place x={x} y={y + 2} />
            </g>
          );
        })}
      </svg>
      {regions.map((r, i) => {
        const [x, y] = SPOTS[i]!;
        const state = i < here ? 'done' : i === here ? 'here' : 'locked';
        const chapters = Array.from({ length: r.to - r.from + 1 }, (_, k) => r.from + k);
        return (
          <>
            <span class={`cm-tag ${state}`} style={pct(x, y + SLAB_H + 12)}>
              <Art name={clanElement(CLANS[i]!)} size={16} />
              <b>{r.from}-{r.to}</b>
              <span class="cm-pips">{chapters.map((c) => <i class={c < cur ? 'done' : c === cur ? 'here' : ''} />)}</span>
            </span>
            {state === 'locked' && <span class="cm-lock" style={pct(x, y - 24)}><Icon name="lock" size={30} /></span>}
            {state === 'done' && <span class="cm-check" style={pct(x + SLAB_W / 2 - 6, y + 2)}><Sign name="check" /></span>}
            {state === 'here' && <span class="cm-flag" style={pct(x + SLAB_W / 2 - 10, Math.max(y - 44, 26))}><Icon name="campaign" size={32} /></span>}
          </>
        );
      })}
    </div>
  );
}
