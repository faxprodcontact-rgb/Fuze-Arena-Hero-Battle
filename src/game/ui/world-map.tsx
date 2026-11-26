// La carte de la campagne (fenêtre ouverte par la pilule du chapitre) : une illustration lisse dessinée par le code
// (atelier backdrop-kit.tsx, une seule lumière en haut à droite, un seul contour par objet, ombres douces).
// Refaite le 26/11 (demande du propriétaire : « des dessins plus soignés ») : une mer de nuit calme, une longue île qui
// monte en lacets du bas vers le haut, et sur elle 8 petits dioramas posés chacun sur un socle de terre (jamais de rond
// au sol) : prairie au moulin, ronciers aux arches d'épines, marais aux lanternes, volcan, pics enneigés, mer d'orage au
// phare, temple ancien, abysses de cristaux (les décors des clans, look.ts). Le chemin déjà fait est d'or ; la région en
// cours brille et porte un fanion planté ; les régions fermées sont éteintes, avec un cadenas. Sous chaque lieu : son
// élément, ses chapitres et un point par chapitre (fait, en cours, à faire). Mouvements : sections/carte.css.
import { CLANS, clanElement, regionChapters } from '../look';
import { Art, Icon, Sign } from './kit';
import { Glow, Mat, Soft, VGrad, Vol, f, rng, rr, spark } from './backdrop-kit';
import './sections/carte.css';

/**
 * Une forme festonnée (nuage, feuillage, fumée) : des demi-cercles qui vont d'un point au suivant, sur une base plate.
 * Les bosses se touchent sans se croiser : un seul contour, sans traits à l'intérieur.
 */
function scallop(pts: (readonly [number, number])[]) {
  let d = `M${f(pts[0]![0])} ${f(pts[0]![1])}`;
  for (let k = 1; k < pts.length; k++) {
    const [ax, ay] = pts[k - 1]!, [bx, by] = pts[k]!, r = Math.hypot(bx - ax, by - ay) / 2;
    d += ` A${f(r)} ${f(r)} 0 0 1 ${f(bx)} ${f(by)}`;
  }
  return `${d} Z`;
}
/** Une touffe : trois bosses, la plus haute au milieu, sur une base plate (x0 = gauche, w = largeur). */
const puff = (x0: number, base: number, w: number) =>
  scallop([[x0, base], [x0 + w * 0.3, base - w * 0.34], [x0 + w * 0.7, base - w * 0.3], [x0 + w, base]]);

const VW = 340, VH = 460;
const P = 'cm';
/** La place de chaque région : centre de son socle (x) et haut du socle (y), dans l'ordre de la campagne (bas → haut). */
const SPOTS: [number, number][] = [
  [86, 394], [256, 390], [254, 284], [86, 288], [86, 180], [254, 176], [254, 70], [86, 74],
];
/** Demi-largeur du socle. */
const PW = 62;
const u = (id: string) => `url(#${P}-${id})`;
const pct = (x: number, y: number) => ({ left: `${(x / VW) * 100}%`, top: `${(y / VH) * 100}%` });

// ---------- Le socle : un bloc de terre aux coins arrondis, le dessus de la couleur du lieu ----------

/** Le dessus du socle : bord arrière arrondi, bord avant qui retombe en petites bosses (herbe, neige, vague, sable). */
function topFace(x: number, y: number, seed: number, drop = 3.5) {
  const r = rng(seed), L = x - PW, R = x + PW;
  let d = `M${L} ${y + 4} Q${L} ${y - 3} ${L + 7} ${y - 3} H${R - 7} Q${R} ${y - 3} ${R} ${y + 4} V${y + 9}`;
  let cx = R;
  while (cx > L + 0.5) {
    const w = Math.min(cx - L, 9 + r() * 9), nx = cx - w;
    d += ` Q${f(cx - w / 2)} ${f(y + 9 + (1.5 + r() * drop) * 2)} ${f(nx)} ${y + 9}`;
    cx = nx;
  }
  return `${d} Z`;
}
const block = (x: number, y: number) => {
  const L = x - PW, R = x + PW;
  return `M${L + 7} ${y - 3} H${R - 7} Q${R} ${y - 3} ${R} ${y + 4} V${y + 15} Q${R} ${y + 25} ${R - 10} ${y + 25} H${L + 10} Q${L} ${y + 25} ${L} ${y + 15} V${y + 4} Q${L} ${y - 3} ${L + 7} ${y - 3} Z`;
};

/** Teintes de chaque lieu : dessus du socle, flanc, et pierres du flanc. */
const SOIL: { top: string; side: string; drop?: number; vein?: string }[] = [
  { top: '#69c26a', side: '#8c6446' },
  { top: '#7d5646', side: '#5e4654' },
  { top: '#5f8450', side: '#56604a' },
  { top: '#4c3d48', side: '#3c2f3e', vein: '#ff8a2a' },
  { top: '#f4f1fa', side: '#7e7f9c', drop: 4.5 },
  { top: '#2c6478', side: '#4b5270' },
  { top: '#e4b26c', side: '#b37a4c', drop: 2 },
  { top: '#27475a', side: '#22344a', vein: '#5ef0d8' },
];

function Plinth({ x, y, i, here }: { x: number; y: number; i: number; here: boolean }) {
  const s = SOIL[i]!, r = rng(40 + i);
  const stones = Array.from({ length: 5 }, (_, k) => [x - PW + 12 + k * 24 + r() * 8, y + 13 + r() * 6, 4 + r() * 4] as const);
  return (
    <g>
      {/* l'ombre portée, vers le bas à gauche (la lumière vient d'en haut à droite) */}
      <path d={rr(x - PW - 2, y + 8, PW * 2, 22, 10)} transform="translate(-6 5)" fill="#05031a" opacity="0.55" filter={u('blur')} />
      {here && <path d={rr(x - PW - 8, y - 30, PW * 2 + 16, 62, 22)} fill="#ffc94d" opacity="0.5" filter={u('blur')} />}
      <Vol p={P} d={block(x, y)} fill={`url(#${P}-side${i})`} depth={4} shade={0.4} rim={0.35}>
        {stones.map(([sx, sy, w]) => <path d={rr(sx, sy, w * 1.6, w, w / 2)} fill="#2a1257" opacity="0.18" />)}
        {s.vein && <path class="cm-glow" d={`M${x - 40} ${y + 25} Q${x - 36} ${y + 17} ${x - 30} ${y + 14} M${x + 16} ${y + 25} Q${x + 20} ${y + 18} ${x + 28} ${y + 16} Q${x + 33} ${y + 14} ${x + 36} ${y + 10}`} fill="none" stroke={s.vein} stroke-width="2" stroke-linecap="round" />}
      </Vol>
      <path d={topFace(x, y, 9 + i, s.drop)} transform="translate(-1 2.5)" fill="#1a0f30" opacity="0.35" filter={u('soft')} />
      <Vol p={P} d={topFace(x, y, 9 + i, s.drop)} fill={`url(#${P}-top${i})`} line={0} depth={3} shade={0.22} rim={0.6} />
      {here && <path d={block(x, y)} fill="none" stroke="#ffd35c" stroke-width="2.2" />}
    </g>
  );
}

// ---------- Les lieux (x = centre, y = haut du socle ; chacun tient dans x ± 60, y − 62 … y + 8) ----------
// Ce qui est au fond se pose vers y, ce qui est devant vers y + 7 (le dessus du socle est vu un peu d'en haut).

/** Des fleurs (petites taches de couleur). */
function Flowers({ seed, x0, x1, y0, y1 }: { seed: number; x0: number; x1: number; y0: number; y1: number }) {
  const r = rng(seed), cols = ['#ff8fb8', '#ffe27a', '#fff6e8', '#c99bff'];
  return <g>{Array.from({ length: 11 }, (_, k) => <circle cx={f(x0 + r() * (x1 - x0))} cy={f(y0 + r() * (y1 - y0))} r={f(1.3 + r() * 0.8)} fill={cols[k % 4]} stroke="#2a1257" stroke-opacity="0.35" stroke-width="0.6" />)}</g>;
}

function Prairie({ x, y }: { x: number; y: number }) {
  const hx = x + 22, hy = y - 34;
  return (
    <g>
      <Vol p={P} d={`M${x - 58} ${y + 1} Q${x - 42} ${y - 22} ${x - 16} ${y - 14} Q${x + 4} ${y - 9} ${x + 14} ${y + 1} Z`} fill={u('grass2')} depth={4} />
      {/* l'arbre */}
      <Vol p={P} d={`M${x - 40} ${y + 3} Q${x - 38} ${y - 8} ${x - 39} ${y - 18} H${x - 34} Q${x - 34} ${y - 8} ${x - 32} ${y + 3} Z`} fill={u('wood')} line={1.2} depth={2} />
      <Vol p={P} d={puff(x - 54, y - 14, 36)} fill={u('leaf')} depth={4} />
      <circle cx={x - 44} cy={y - 24} r="1.8" fill="#ff6a5a" /><circle cx={x - 30} cy={y - 28} r="1.8" fill="#ff6a5a" /><circle cx={x - 37} cy={y - 18} r="1.6" fill="#ff6a5a" />
      {/* le moulin : la tour, la porte, le toit, les ailes qui tournent */}
      <Vol p={P} d={`M${hx - 11} ${y + 4} L${hx - 7} ${hy + 2} Q${hx} ${hy - 2} ${hx + 7} ${hy + 2} L${hx + 11} ${y + 4} Z`} fill={u('wall')} depth={4} />
      <Vol p={P} d={`M${hx - 3} ${y + 4} V${y - 5} Q${hx} ${y - 9} ${hx + 3} ${y - 5} V${y + 4} Z`} fill={u('wood')} line={1} depth={1.5} shade={0.25} rim={0} />
      <path d={rr(hx - 2, hy + 10, 4, 5, 2)} fill="#ffd35c" stroke="#1f1238" stroke-opacity="0.6" stroke-width="0.8" />
      <Vol p={P} d={`M${hx - 10} ${hy + 3} Q${hx} ${hy - 16} ${hx + 10} ${hy + 3} Z`} fill={u('roof')} depth={2.5} />
      <g class="cm-spin" style={{ transformOrigin: `${hx}px ${hy}px` }}>
        {[0, 90, 180, 270].map((a) => (
          <g transform={`rotate(${a} ${hx} ${hy})`}>
            <Vol p={P} d={`M${hx - 1.2} ${hy} V${hy - 23} H${hx + 1.2} V${hy} Z M${hx + 1} ${hy - 6} H${hx + 6.5} Q${hx + 7.5} ${hy - 14} ${hx + 6.5} ${hy - 22} H${hx + 1} Z`} fill={u('sail')} line={1} depth={1.5} shade={0.2} rim={0.3} />
          </g>
        ))}
        <circle cx={hx} cy={hy} r="2.6" fill="#ffc22e" stroke="#1f1238" stroke-opacity="0.7" stroke-width="1" />
      </g>
      {/* la barrière, devant à droite */}
      <Vol p={P} d={`M${x + 38} ${y + 1} H${x + 58} V${y + 3.5} H${x + 38} Z M${x + 40} ${y + 8} V${y - 4} H${x + 43} V${y + 8} Z M${x + 48} ${y + 8} V${y - 4} H${x + 51} V${y + 8} Z M${x + 55} ${y + 8} V${y - 4} H${x + 58} V${y + 8} Z`} fill={u('wood')} line={1} depth={1} shade={0.2} rim={0.3} />
      <Flowers seed={3} x0={x - 56} x1={x + 34} y0={y - 1} y1={y + 8} />
      <Flowers seed={5} x0={x - 50} x1={x - 4} y0={y - 10} y1={y - 2} />
    </g>
  );
}

function Ronces({ x, y }: { x: number; y: number }) {
  /** Une arche de ronces : une bande courbe, des épines sur le dos. */
  const arch = (x0: number, x1: number, base: number, h: number, t: number) => {
    const m = (x0 + x1) / 2, top = base - h;
    return `M${x0} ${base} C${x0} ${top + h * 0.1} ${m - (x1 - x0) * 0.32} ${top} ${m} ${top} C${m + (x1 - x0) * 0.32} ${top} ${x1} ${top + h * 0.1} ${x1} ${base} L${x1 - t} ${base} C${x1 - t} ${top + t + h * 0.14} ${m + (x1 - x0) * 0.26} ${top + t} ${m} ${top + t} C${m - (x1 - x0) * 0.26} ${top + t} ${x0 + t} ${top + t + h * 0.14} ${x0 + t} ${base} Z`;
  };
  const thorns = (x0: number, x1: number, base: number, h: number) => {
    let d = '';
    for (let k = 1; k < 8; k++) {
      const tt = k / 8, a = Math.PI * (1 - tt);
      const cx = (x0 + x1) / 2 + Math.cos(a) * (x1 - x0) / 2 * 0.98, cy = base - h * 0.08 - Math.sin(a) * h * 0.92;
      const nx = Math.cos(a), ny = -Math.sin(a);
      d += `M${f(cx - ny * 2.6)} ${f(cy + nx * 2.6)} L${f(cx + nx * 6 + ny * 1.5)} ${f(cy + ny * 6 - nx * 1.5)} L${f(cx + ny * 2.6)} ${f(cy - nx * 2.6)} Z `;
    }
    return d;
  };
  return (
    <g>
      {/* l'arbre tordu, au fond */}
      <Vol p={P} d={`M${x + 6} ${y + 1} Q${x + 10} ${y - 20} ${x + 2} ${y - 36} Q${x + 10} ${y - 32} ${x + 14} ${y - 24} Q${x + 20} ${y - 40} ${x + 34} ${y - 44} Q${x + 24} ${y - 32} ${x + 22} ${y - 18} Q${x + 21} ${y - 6} ${x + 26} ${y + 1} Z`} fill={u('bark')} depth={3} />
      <Vol p={P} d={puff(x - 8, y - 34, 28)} fill={u('plum')} depth={3} />
      <Vol p={P} d={puff(x + 18, y - 42, 28)} fill={u('plum')} depth={3} />
      <Vol p={P} d={`M${x + 30} ${y + 2} Q${x + 33} ${y - 12} ${x + 44} ${y - 12} Q${x + 56} ${y - 12} ${x + 58} ${y + 2} Z`} fill={u('rock')} depth={3} />
      {/* les arches d'épines */}
      <Vol p={P} d={thorns(x - 54, x - 8, y + 2, 44)} fill={u('thorn')} line={1} depth={1} shade={0} rim={0.3} />
      <Vol p={P} d={arch(x - 54, x - 8, y + 2, 44, 7)} fill={u('thorn')} depth={3} />
      <Vol p={P} d={thorns(x + 4, x + 40, y + 8, 30)} fill={u('thorn')} line={1} depth={1} shade={0} rim={0.3} />
      <Vol p={P} d={arch(x + 4, x + 40, y + 8, 30, 6)} fill={u('thorn')} depth={3} />
      {[[x - 50, y - 26], [x - 30, y - 41], [x - 14, y - 30], [x + 12, y - 14], [x + 30, y - 18]].map(([bx, by]) => <circle cx={bx} cy={by} r="2" fill="#e2405a" stroke="#1f1238" stroke-opacity="0.6" stroke-width="0.8" />)}
      {/* les champignons qui luisent */}
      <circle class="cm-glow" cx={x - 22} cy={y + 2} r="10" fill={u('shroomglow')} />
      {[[x - 27, y + 6, 6], [x - 18, y + 4, 4.5]].map(([mx, my, w]) => (
        <g>
          <Vol p={P} d={rr(mx! - w! * 0.18, my! - w! * 0.9, w! * 0.36, w! * 0.9, 1)} fill={u('wall')} line={0.8} depth={1} shade={0.2} rim={0} />
          <Vol p={P} d={`M${mx! - w!} ${my! - w! * 0.8} Q${mx! - w!} ${my! - w! * 1.9} ${mx} ${my! - w! * 1.9} Q${mx! + w!} ${my! - w! * 1.9} ${mx! + w!} ${my! - w! * 0.8} Z`} fill={u('shroom')} line={1} depth={1.5} />
        </g>
      ))}
      <g class="cm-fly"><circle cx={x - 2} cy={y - 20} r="1.4" fill="#ffe27a" /><circle cx={x + 46} cy={y - 24} r="1.2" fill="#ffe27a" /><circle cx={x - 40} cy={y - 8} r="1.2" fill="#ffe27a" /></g>
    </g>
  );
}

function Bayou({ x, y }: { x: number; y: number }) {
  const cattail = (cx: number, base: number, h: number, lean: number) => (
    <g>
      <path d={`M${cx} ${base} Q${cx + lean * 0.3} ${base - h * 0.6} ${cx + lean} ${base - h}`} fill="none" stroke="#1f1238" stroke-opacity="0.7" stroke-width="2.6" stroke-linecap="round" />
      <path d={`M${cx} ${base} Q${cx + lean * 0.3} ${base - h * 0.6} ${cx + lean} ${base - h}`} fill="none" stroke="#8aa85a" stroke-width="1.2" stroke-linecap="round" />
      <Vol p={P} d={rr(cx + lean * 0.78 - 2.2, base - h * 0.9, 4.4, 9, 2.2)} fill={u('cat')} line={1} depth={1} shade={0.2} rim={0.3} />
    </g>
  );
  return (
    <g>
      {/* l'eau dormante, posée dans le socle */}
      <Vol p={P} d={rr(x - 34, y - 1, 70, 9, 4.5)} fill={u('marsh')} line={1} depth={2} shade={0.35} rim={0.25} />
      <path class="cm-glint" d={`M${x - 20} ${y + 3} h8 M${x + 6} ${y + 5} h10`} stroke="#d9f0c8" stroke-width="1.2" stroke-linecap="round" opacity="0.6" />
      <Vol p={P} d={`M${x + 14} ${y + 2} Q${x + 10} ${y + 6} ${x + 18} ${y + 6.5} Q${x + 25} ${y + 6} ${x + 22} ${y + 2.5} L${x + 18} ${y + 4} Z`} fill={u('grass2')} line={0.8} depth={1} shade={0} rim={0.3} />
      <Vol p={P} d={`M${x - 30} ${y + 2} Q${x - 34} ${y + 6} ${x - 26} ${y + 6.5} Q${x - 20} ${y + 6} ${x - 23} ${y + 2.5} L${x - 27} ${y + 4} Z`} fill={u('grass2')} line={0.8} depth={1} shade={0} rim={0.3} />
      {/* le vieil arbre couvert de mousse */}
      <Vol p={P} d={`M${x - 4} ${y} Q${x} ${y - 24} ${x - 12} ${y - 40} Q${x - 2} ${y - 36} ${x + 4} ${y - 26} Q${x + 10} ${y - 42} ${x + 26} ${y - 46} Q${x + 14} ${y - 34} ${x + 14} ${y - 14} L${x + 16} ${y} Z`} fill={u('bark')} depth={3} />
      <Vol p={P} d={`M${x - 24} ${y - 36} Q${x - 22} ${y - 52} ${x - 4} ${y - 50} Q${x + 10} ${y - 60} ${x + 28} ${y - 50} Q${x + 42} ${y - 48} ${x + 40} ${y - 34} Q${x + 40} ${y - 18} ${x + 36} ${y - 16} Q${x + 33} ${y - 22} ${x + 33} ${y - 32} Q${x + 30} ${y - 20} ${x + 27} ${y - 22} Q${x + 25} ${y - 28} ${x + 24} ${y - 36} Q${x + 18} ${y - 34} ${x + 14} ${y - 38} Q${x + 8} ${y - 34} ${x + 2} ${y - 37} Q${x - 1} ${y - 24} ${x - 4} ${y - 18} Q${x - 7} ${y - 24} ${x - 8} ${y - 35} Q${x - 13} ${y - 22} ${x - 16} ${y - 20} Q${x - 19} ${y - 26} ${x - 18} ${y - 34} Q${x - 22} ${y - 30} ${x - 24} ${y - 36} Z`} fill={u('moss')} depth={4} />
      {/* la lanterne sur son poteau */}
      <circle class="cm-flicker" cx={x - 44} cy={y - 30} r="16" fill={u('lamp')} />
      <Vol p={P} d={`M${x - 46} ${y + 6} V${y - 34} H${x - 36} V${y - 31} H${x - 43} V${y + 6} Z`} fill={u('wood')} line={1.1} depth={1.5} shade={0.25} rim={0.3} />
      <Vol p={P} d={`M${x - 42} ${y - 30} H${x - 33} L${x - 34} ${y - 20} H${x - 41} Z`} fill={u('gold')} line={1.1} depth={1.2} shade={0.2} rim={0.3} />
      <path class="cm-flicker" d={rr(x - 40, y - 28, 5, 6, 2)} fill="#fff1b0" />
      {cattail(x - 52, y + 7, 22, -3)}{cattail(x - 30, y + 2, 18, 2)}{cattail(x + 42, y + 6, 24, 3)}{cattail(x + 50, y + 7, 18, -2)}
      <path class="cm-mist" d={`M${x - 58} ${y - 6} Q${x - 30} ${y - 14} ${x} ${y - 8} Q${x + 30} ${y - 2} ${x + 58} ${y - 9}`} fill="none" stroke="#e8e4ff" stroke-width="7" stroke-linecap="round" opacity="0.22" filter={u('soft')} />
    </g>
  );
}

function Cendres({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <ellipse class="cm-glow" cx={x - 6} cy={y - 46} rx="26" ry="16" fill={u('ember')} />
      <Vol p={P} d={puff(x - 26, y - 46, 36)} fill={u('smoke')} depth={3} rim={0.3} />
      {[0, 1, 2].map((k) => <path class="cm-smoke" style={{ animationDelay: `${-k * 1.3}s` }} d={puff(x - 16 + k * 6, y - 60 - k * 3, 20 - k * 3)} fill={u('smoke')} stroke="#1f1238" stroke-opacity="0.35" stroke-width="1" />)}
      {/* les roches noires, derrière à droite */}
      <Vol p={P} d={`M${x + 30} ${y + 1} L${x + 34} ${y - 22} Q${x + 37} ${y - 26} ${x + 40} ${y - 22} L${x + 42} ${y - 14} L${x + 46} ${y - 30} Q${x + 49} ${y - 34} ${x + 52} ${y - 30} L${x + 57} ${y + 1} Z`} fill={u('basalt')} depth={3} />
      {/* le volcan, sa bouche de lave et ses coulées */}
      <Vol p={P} d={`M${x - 56} ${y + 4} Q${x - 36} ${y - 14} ${x - 20} ${y - 44} Q${x - 6} ${y - 50} ${x + 8} ${y - 44} Q${x + 22} ${y - 14} ${x + 42} ${y + 4} Z`} fill={u('ash')} depth={6}>
        <path d={`M${x - 16} ${y - 45} Q${x - 6} ${y - 40} ${x + 4} ${y - 45} Q${x + 1} ${y - 30} ${x + 8} ${y - 20} Q${x + 14} ${y - 8} ${x + 8} ${y + 4} L${x + 1} ${y + 4} Q${x + 5} ${y - 10} ${x - 2} ${y - 22} Q${x - 8} ${y - 32} ${x - 16} ${y - 45} Z`} fill={u('lava')} />
        <path d={`M${x - 14} ${y - 40} Q${x - 18} ${y - 30} ${x - 28} ${y - 20} Q${x - 36} ${y - 12} ${x - 34} ${y + 4} L${x - 29} ${y + 4} Q${x - 30} ${y - 10} ${x - 24} ${y - 17} Q${x - 16} ${y - 26} ${x - 12} ${y - 38} Z`} fill={u('lava')} />
      </Vol>
      <Vol p={P} d={`M${x - 18} ${y - 45} Q${x - 6} ${y - 51} ${x + 6} ${y - 45} Q${x - 6} ${y - 40} ${x - 18} ${y - 45} Z`} fill={u('lavatop')} line={1} depth={1} shade={0} rim={0.5} />
      {/* la lave qui coule devant, dans le socle */}
      <path d={`M${x + 1} ${y + 4} Q${x + 10} ${y + 6} ${x + 22} ${y + 5} Q${x + 30} ${y + 6} ${x + 34} ${y + 8} L${x + 26} ${y + 8.5} Q${x + 12} ${y + 8} ${x + 4} ${y + 8} Z`} fill={u('lava')} stroke="#1f1238" stroke-opacity="0.5" stroke-width="0.8" />
      <Vol p={P} d={`M${x - 58} ${y + 8} Q${x - 56} ${y - 1} ${x - 48} ${y} Q${x - 44} ${y + 2} ${x - 44} ${y + 8} Z`} fill={u('basalt')} line={1.1} depth={1.5} />
      <g fill="#ffc25a">{[[x - 6, y - 56], [x + 4, y - 62], [x - 12, y - 60]].map(([ex, ey], k) => <circle class="cm-spark" style={{ animationDelay: `${-k * 0.8}s` }} cx={ex} cy={ey} r="1.4" />)}</g>
    </g>
  );
}

function Toundra({ x, y }: { x: number; y: number }) {
  /** Un sapin : trois étages, la neige sur chaque étage. */
  const pine = (cx: number, b: number, h: number, w: number) => {
    const pt = (dx: number, dy: number) => `${f(cx + dx * w)} ${f(b - dy * h)}`;
    const d = `M${pt(0, 1)} L${pt(0.3, 0.64)} L${pt(0.18, 0.64)} L${pt(0.42, 0.32)} L${pt(0.27, 0.32)} L${pt(0.5, 0.06)} L${pt(-0.5, 0.06)} L${pt(-0.27, 0.32)} L${pt(-0.42, 0.32)} L${pt(-0.18, 0.64)} L${pt(-0.3, 0.64)} Z`;
    const snow = `M${pt(0, 1)} L${pt(0.17, 0.8)} Q${pt(0.06, 0.76)} ${pt(0, 0.8)} Q${pt(-0.08, 0.74)} ${pt(-0.17, 0.8)} Z M${pt(0.12, 0.64)} L${pt(0.26, 0.45)} Q${pt(0.1, 0.42)} ${pt(0.02, 0.48)} Q${pt(-0.1, 0.42)} ${pt(-0.18, 0.5)} L${pt(-0.12, 0.64)} Z`;
    return (
      <g>
        <Vol p={P} d={rr(cx - 1.6, b - h * 0.1, 3.2, h * 0.1 + 1, 1)} fill={u('wood')} line={1} depth={1} shade={0} rim={0} />
        <Vol p={P} d={d} fill={u('pine')} line={1.2} depth={2.5}><path d={snow} fill="#fbfaff" opacity="0.95" /></Vol>
      </g>
    );
  };
  return (
    <g>
      {/* les pics, la neige sur leurs têtes */}
      <Vol p={P} d={`M${x - 58} ${y + 1} L${x - 26} ${y - 52} Q${x - 22} ${y - 57} ${x - 18} ${y - 52} L${x + 2} ${y - 22} L${x + 14} ${y - 38} Q${x + 18} ${y - 42} ${x + 22} ${y - 38} L${x + 50} ${y + 1} Z`} fill={u('peak')} depth={6}>
        <path d={`M${x - 36} ${y - 36} L${x - 26} ${y - 52} Q${x - 22} ${y - 57} ${x - 18} ${y - 52} L${x - 8} ${y - 37} Q${x - 12} ${y - 33} ${x - 15} ${y - 38} Q${x - 19} ${y - 30} ${x - 23} ${y - 38} Q${x - 30} ${y - 32} ${x - 36} ${y - 36} Z`} fill={u('snow')} />
        <path d={`M${x + 7} ${y - 28} L${x + 14} ${y - 38} Q${x + 18} ${y - 42} ${x + 22} ${y - 38} L${x + 29} ${y - 28} Q${x + 25} ${y - 24} ${x + 21} ${y - 29} Q${x + 16} ${y - 23} ${x + 12} ${y - 29} Q${x + 10} ${y - 25} ${x + 7} ${y - 28} Z`} fill={u('snow')} />
      </Vol>
      {/* le petit chalet, sa fenêtre chaude */}
      <Vol p={P} d={`M${x - 46} ${y + 5} V${y - 6} H${x - 28} V${y + 5} Z`} fill={u('wood')} line={1.2} depth={2} />
      <path class="cm-flicker" d={rr(x - 40, y - 3, 6, 5, 1.5)} fill="#ffd35c" stroke="#1f1238" stroke-opacity="0.6" stroke-width="0.8" />
      <Vol p={P} d={`M${x - 50} ${y - 5} L${x - 37} ${y - 16} L${x - 24} ${y - 5} Q${x - 30} ${y - 3} ${x - 37} ${y - 5} Q${x - 44} ${y - 3} ${x - 50} ${y - 5} Z`} fill={u('snow')} line={1.2} depth={2} />
      {pine(x + 26, y + 3, 30, 18)}{pine(x + 44, y + 7, 36, 20)}{pine(x + 8, y + 8, 22, 14)}{pine(x - 56, y + 8, 20, 12)}
      <g fill="#fff">{[[x - 30, y - 50], [x + 4, y - 56], [x + 36, y - 46], [x - 50, y - 30], [x + 52, y - 52]].map(([sx, sy], k) => <circle class="cm-snow" style={{ animationDelay: `${-k * 0.9}s` }} cx={sx} cy={sy} r="1.3" />)}</g>
    </g>
  );
}

function Orage({ x, y }: { x: number; y: number }) {
  return (
    <g>
      {/* le nuage d'orage et son éclair courbe */}
      <path class="cm-flash" d={rr(x - 14, y - 56, 74, 60, 24)} fill={u('boltglow')} />
      <Vol p={P} d={scallop([[x + 2, y - 40], [x + 12, y - 50], [x + 30, y - 55], [x + 46, y - 48], [x + 54, y - 40]])} fill={u('storm2')} depth={4} rim={0.2} />
      <Vol p={P} d={scallop([[x - 14, y - 30], [x - 8, y - 40], [x + 6, y - 47], [x + 24, y - 49], [x + 40, y - 44], [x + 50, y - 37], [x + 56, y - 30]])} fill={u('storm')} depth={4} rim={0.35} />
      <path class="cm-bolt" d={`M${x + 26} ${y - 34} Q${x + 18} ${y - 26} ${x + 22} ${y - 20} L${x + 16} ${y - 20} Q${x + 14} ${y - 10} ${x + 22} ${y - 1} Q${x + 22} ${y - 11} ${x + 29} ${y - 16} L${x + 24} ${y - 16} Q${x + 28} ${y - 25} ${x + 34} ${y - 34} Z`} fill="#ffe27a" stroke="#1f1238" stroke-opacity="0.6" stroke-width="1" stroke-linejoin="round" />
      {/* le rocher et son phare */}
      <circle class="cm-flicker" cx={x - 34} cy={y - 46} r="15" fill={u('lamp')} />
      <Vol p={P} d={`M${x - 58} ${y + 5} Q${x - 56} ${y - 6} ${x - 46} ${y - 8} Q${x - 34} ${y - 12} ${x - 22} ${y - 6} Q${x - 14} ${y - 2} ${x - 14} ${y + 5} Z`} fill={u('rock')} depth={3} />
      <Vol p={P} d={`M${x - 42} ${y - 7} L${x - 39} ${y - 38} H${x - 29} L${x - 26} ${y - 7} Z`} fill={u('wall')} depth={3}>
        <path d={`M${x - 42} ${y - 22} L${x - 40} ${y - 28} H${x - 28} L${x - 26} ${y - 22} Z`} fill="#c8482e" opacity="0.9" />
      </Vol>
      <path d={rr(x - 35.5, y - 16, 3, 5, 1.5)} fill="#3a2a5a" />
      <Vol p={P} d={rr(x - 42, y - 40, 16, 3.5, 1.5)} fill={u('gold')} line={1} depth={1} shade={0.2} rim={0.4} />
      <path class="cm-flicker" d={rr(x - 38, y - 47, 8, 7, 2)} fill="#fff1b0" stroke="#1f1238" stroke-opacity="0.6" stroke-width="1" />
      <Vol p={P} d={`M${x - 40} ${y - 46} Q${x - 34} ${y - 56} ${x - 28} ${y - 46} Z`} fill={u('roof')} line={1.1} depth={1.5} />
      {/* les vagues et le petit voilier */}
      <g class="cm-bob">
        <Vol p={P} d={`M${x + 4} ${y + 1} H${x + 26} Q${x + 24} ${y + 7} ${x + 18} ${y + 7} H${x + 10} Q${x + 5} ${y + 7} ${x + 4} ${y + 1} Z`} fill={u('wood')} line={1.1} depth={1.5} />
        <Vol p={P} d={`M${x + 15} ${y - 1} V${y - 20} Q${x + 24} ${y - 10} ${x + 24} ${y - 1} Z`} fill={u('sail')} line={1.1} depth={1.5} />
      </g>
      {[[x - 8, y + 6], [x + 36, y + 3], [x + 48, y + 8]].map(([wx, wy]) => (
        <Vol p={P} d={`M${wx! - 8} ${wy} Q${wx! - 4} ${wy! - 6} ${wx! + 2} ${wy! - 4} Q${wx! - 2} ${wy! - 2} ${wx} ${wy! + 1} Q${wx! + 5} ${wy! - 1} ${wx! + 8} ${wy} Z`} fill={u('foam')} line={0.9} depth={1} shade={0.15} rim={0} />
      ))}
    </g>
  );
}

function Temple({ x, y }: { x: number; y: number }) {
  const brazier = (bx: number, b: number) => (
    <g>
      <circle class="cm-flicker" cx={bx} cy={b - 16} r="11" fill={u('ember')} />
      <Vol p={P} d={`M${bx - 1.5} ${b} V${b - 8} H${bx + 1.5} V${b} Z M${bx - 5} ${b} H${bx + 5} V${b - 1.5} H${bx - 5} Z`} fill={u('stone')} line={1} depth={1} shade={0} rim={0.3} />
      <Vol p={P} d={`M${bx - 5} ${b - 11} H${bx + 5} Q${bx + 4} ${b - 7} ${bx} ${b - 7} Q${bx - 4} ${b - 7} ${bx - 5} ${b - 11} Z`} fill={u('gold')} line={1} depth={1} shade={0.2} rim={0.4} />
      <path class="cm-flame" style={{ transformOrigin: `${bx}px ${b - 11}px` }} d={`M${bx - 4} ${b - 11} Q${bx - 5} ${b - 17} ${bx - 1} ${b - 22} Q${bx} ${b - 17} ${bx + 2} ${b - 19} Q${bx + 5} ${b - 15} ${bx + 4} ${b - 11} Z`} fill={u('fire')} />
    </g>
  );
  return (
    <g>
      {/* les marches, les colonnes, le fronton marqué d'un signe */}
      <Vol p={P} d={`M${x - 40} ${y + 6} V${y + 1} H${x - 36} V${y - 3} H${x + 36} V${y + 1} H${x + 40} V${y + 6} Z`} fill={u('sand')} depth={2} />
      {[-27, -9, 9, 27].map((dx) => (
        <Vol p={P} d={`M${x + dx - 4} ${y - 3} V${y - 33} H${x + dx - 5.5} V${y - 36} H${x + dx + 5.5} V${y - 33} H${x + dx + 4} V${y - 3} Z`} fill={u('column')} line={1.2} depth={2} />
      ))}
      <Vol p={P} d={`M${x - 38} ${y - 36} H${x + 38} V${y - 40} H${x - 38} Z M${x - 40} ${y - 40} L${x} ${y - 56} L${x + 40} ${y - 40} Z`} fill={u('column')} depth={3}>
        <path d={`M${x} ${y - 51} Q${x + 2.4} ${y - 47.4} ${x + 4} ${y - 45} Q${x + 2.4} ${y - 42.6} ${x} ${y - 41} Q${x - 2.4} ${y - 42.6} ${x - 4} ${y - 45} Q${x - 2.4} ${y - 47.4} ${x} ${y - 51} Z`} fill="#ffc22e" stroke="#7a3a14" stroke-opacity="0.6" stroke-width="0.8" />
      </Vol>
      {/* le lierre au coin du fronton */}
      <Vol p={P} d={`M${x + 22} ${y - 46} Q${x + 34} ${y - 44} ${x + 38} ${y - 37} Q${x + 39} ${y - 30} ${x + 35} ${y - 26} Q${x + 34} ${y - 32} ${x + 30} ${y - 34} Q${x + 26} ${y - 36} ${x + 22} ${y - 46} Z`} fill={u('leaf')} line={1} depth={1.5} />
      {/* la colonne tombée, devant à gauche */}
      <Vol p={P} d={`M${x - 58} ${y + 3} V${y - 14} H${x - 50} V${y + 3} Z`} fill={u('column')} line={1.2} depth={2} />
      <Vol p={P} d={rr(x - 52, y + 2, 16, 6, 3)} fill={u('column')} line={1.1} depth={1.5} />
      {brazier(x - 47, y + 2)}{brazier(x + 50, y + 3)}
    </g>
  );
}

function Abysses({ x, y }: { x: number; y: number }) {
  const crystal = (cx: number, b: number, w: number, h: number, tilt: number, mat: string) => {
    const d = `M${f(cx - w / 2)} ${b} L${f(cx - w / 2 + tilt)} ${f(b - h * 0.72)} L${f(cx + tilt)} ${f(b - h)} L${f(cx + w / 2 + tilt)} ${f(b - h * 0.72)} L${f(cx + w / 2)} ${b} Z`;
    const facet = `M${f(cx + tilt * 0.4)} ${b} L${f(cx + tilt)} ${f(b - h)} L${f(cx + w / 2 + tilt)} ${f(b - h * 0.72)} L${f(cx + w / 2)} ${b} Z`;
    return <Vol p={P} d={d} fill={u(mat)} line={1.1} depth={1.5} shade={0.25}><path d={facet} fill="#fff6cf" opacity="0.28" /></Vol>;
  };
  return (
    <g>
      {/* les aiguilles de roche sombre, au fond */}
      <Vol p={P} d={`M${x - 46} ${y + 1} L${x - 38} ${y - 30} Q${x - 35} ${y - 36} ${x - 32} ${y - 30} L${x - 29} ${y - 18} L${x - 22} ${y - 44} Q${x - 18} ${y - 50} ${x - 14} ${y - 44} L${x - 6} ${y - 14} L${x - 2} ${y - 22} Q${x + 1} ${y - 26} ${x + 4} ${y - 22} L${x + 10} ${y + 1} Z`} fill={u('deep')} depth={4}>
        <path class="cm-glow" d={`M${x - 19} ${y - 38} L${x - 16} ${y - 28} L${x - 19} ${y - 20} M${x - 36} ${y - 24} L${x - 33} ${y - 16}`} fill="none" stroke="#5ef0d8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </Vol>
      {/* le gouffre qui luit, dans le socle */}
      <ellipse class="cm-glow" cx={x - 14} cy={y - 6} rx="26" ry="16" fill={u('abyssglow')} />
      <Vol p={P} d={rr(x - 30, y - 1, 32, 8, 4)} fill={u('pit')} line={1.1} depth={2} shade={0.5} rim={0} />
      {/* les cristaux */}
      {crystal(x - 52, y + 5, 8, 24, 2, 'crystal')}{crystal(x - 44, y + 7, 7, 16, -1, 'crystal')}
      {crystal(x + 22, y + 2, 10, 38, 1, 'crystal')}{crystal(x + 31, y + 4, 8, 26, 3, 'violet')}{crystal(x + 14, y + 5, 6, 16, -2, 'violet')}
      {/* les coraux et l'algue qui ondule */}
      <Vol p={P} d={`M${x + 44} ${y + 7} Q${x + 44} ${y - 4} ${x + 38} ${y - 12} Q${x + 36} ${y - 16} ${x + 40} ${y - 15} Q${x + 46} ${y - 8} ${x + 47} ${y - 4} Q${x + 48} ${y - 16} ${x + 46} ${y - 24} Q${x + 46} ${y - 28} ${x + 50} ${y - 25} Q${x + 52} ${y - 14} ${x + 51} ${y - 4} Q${x + 54} ${y - 10} ${x + 57} ${y - 14} Q${x + 60} ${y - 14} ${x + 58} ${y - 10} Q${x + 54} ${y - 2} ${x + 52} ${y + 7} Z`} fill={u('coral')} depth={2} />
      <g class="cm-sway" style={{ transformOrigin: `${x + 6}px ${y + 6}px` }}>
        <Vol p={P} d={`M${x + 4} ${y + 6} Q${x} ${y - 6} ${x + 6} ${y - 14} Q${x + 11} ${y - 22} ${x + 6} ${y - 30} Q${x + 12} ${y - 24} ${x + 11} ${y - 14} Q${x + 6} ${y - 6} ${x + 9} ${y + 6} Z`} fill={u('kelp')} line={1} depth={1.5} />
      </g>
      {[[x - 18, y - 18, 2.4], [x - 10, y - 30, 1.8], [x - 22, y - 40, 1.4], [x + 26, y - 44, 1.6]].map(([cx, cy, r], i) => (
        <circle class="cm-bubble" style={{ animationDelay: `${-i * 0.9}s` }} cx={cx} cy={cy} r={r} fill="none" stroke="#bff6ea" stroke-width="1.1" opacity="0.8" />
      ))}
    </g>
  );
}

const PLACES = [Prairie, Ronces, Bayou, Cendres, Toundra, Orage, Temple, Abysses];

/** Le chemin d'une région à la suivante (même rangée : tout droit ; rangée du dessus : un lacet par l'extérieur). */
function leg(i: number): string {
  const [x0, y0] = SPOTS[i]!, [x1, y1] = SPOTS[i + 1]!;
  const a = y0 + 12, b = y1 + 12;
  if (Math.abs(y0 - y1) < 20) return `M${x0} ${a} C${x0 + (x1 - x0) * 0.3} ${a + 26} ${x1 - (x1 - x0) * 0.3} ${b + 26} ${x1} ${b}`;
  const out = x0 < VW / 2 ? -1 : 1;
  return `M${x0} ${a} C${x0 + out * 92} ${a + 4} ${x1 + out * 92} ${b - 4} ${x1} ${b}`;
}

/** Une île à bord souple autour d'un point (le sol vu d'en haut, sur la carte). */
function isle(cx: number, cy: number, rx: number, ry: number, seed: number) {
  const r = rng(seed), n = 16;
  const pts = Array.from({ length: n }, (_, k) => {
    const a = (k / n) * Math.PI * 2, j = 0.9 + r() * 0.16;
    return [cx + Math.cos(a) * rx * j, cy + Math.sin(a) * ry * j] as const;
  });
  const mid = (k: number) => { const a = pts[k % n]!, b = pts[(k + 1) % n]!; return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2] as const; };
  let d = `M${f(mid(0)[0])} ${f(mid(0)[1])}`;
  for (let k = 1; k <= n; k++) { const p = pts[k % n]!, m = mid(k); d += ` Q${f(p[0])} ${f(p[1])} ${f(m[0])} ${f(m[1])}`; }
  return `${d} Z`;
}
const ISLES = SPOTS.map(([x, y], i) => isle(x, y + 10, 76, 40, 60 + i));

/** Les vaguelettes de la mer (petits reflets courbes, peu nombreux). */
const GLINTS = (() => {
  const r = rng(21);
  return Array.from({ length: 14 }, () => [8 + r() * (VW - 16), 10 + r() * (VH - 20), 5 + r() * 5, -r() * 6] as const);
})();

/** La carte : `cur` = le chapitre en cours. */
export function ChapterMap({ cur }: { cur: number }) {
  const regions = regionChapters();
  const here = Math.max(0, regions.findIndex((r) => cur >= r.from && cur <= r.to));
  const legs = SPOTS.slice(0, -1).map((_, i) => leg(i));
  return (
    <div class="cmap">
      <svg class="cmap-art" viewBox={`0 0 ${VW} ${VH}`} aria-hidden="true">
        <defs>
          <Soft p={P} />
          <VGrad id={`${P}-sea`} stops={[[0, '#0e1034'], [0.5, '#141a46'], [1, '#1b2858']]} />
          <VGrad id={`${P}-land`} y1={VH} y2={0} stops={[[0, '#4f8a56'], [0.2, '#5e6a48'], [0.42, '#5e4c52'], [0.62, '#6a6886'], [0.8, '#4f5a76'], [1, '#2e5866']]} />
          <VGrad id={`${P}-shore`} y1={VH} y2={0} stops={[[0, '#b9a678'], [0.5, '#a08f86'], [1, '#6f8a86']]} />
          <Glow id={`${P}-moon`} c="#ffe9a8" a={0.32} />
          {SOIL.map((s, i) => <><Mat id={`${P}-top${i}`} c={s.top} k={0.8} /><Mat id={`${P}-side${i}`} c={s.side} /></>)}
          <Mat id={`${P}-grass2`} c="#4fa85a" /><Mat id={`${P}-leaf`} c="#3f9e55" /><Mat id={`${P}-wood`} c="#8a5a3a" /><Mat id={`${P}-gold`} c="#ffc22e" />
          <Mat id={`${P}-wall`} c="#efe0c4" /><Mat id={`${P}-roof`} c="#c8482e" /><Mat id={`${P}-sail`} c="#f6eedd" />
          <Mat id={`${P}-rock`} c="#7d6a70" /><Mat id={`${P}-bark`} c="#5a3f3e" /><Mat id={`${P}-plum`} c="#5a4a6e" /><Mat id={`${P}-thorn`} c="#7a3f52" />
          <Mat id={`${P}-shroom`} c="#ff6a4a" /><Mat id={`${P}-moss`} c="#6f8a48" /><Mat id={`${P}-cat`} c="#8a5a36" /><Mat id={`${P}-marsh`} c="#2f5a4e" />
          <Mat id={`${P}-ash`} c="#54444f" /><Mat id={`${P}-basalt`} c="#3a2f3e" /><Mat id={`${P}-smoke`} c="#8f86a6" />
          <Mat id={`${P}-peak`} c="#9396b4" /><Mat id={`${P}-snow`} c="#fbfaff" k={0.6} /><Mat id={`${P}-pine`} c="#2f7a5a" />
          <Mat id={`${P}-storm`} c="#5e5a86" /><Mat id={`${P}-storm2`} c="#3e3a62" /><Mat id={`${P}-foam`} c="#f1eefa" k={0.6} />
          <Mat id={`${P}-sand`} c="#e3b878" /><Mat id={`${P}-column`} c="#eed6a8" /><Mat id={`${P}-stone`} c="#8d8aa8" />
          <Mat id={`${P}-deep`} c="#2c4f62" /><Mat id={`${P}-crystal`} c="#4fe0c0" /><Mat id={`${P}-violet`} c="#a684ff" />
          <Mat id={`${P}-coral`} c="#ff7a7a" /><Mat id={`${P}-kelp`} c="#3fae7a" />
          <linearGradient id={`${P}-pit`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1828" /><stop offset="1" stop-color="#1f8a7e" /></linearGradient>
          <linearGradient id={`${P}-lava`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe27a" /><stop offset="0.5" stop-color="#ff8a2a" /><stop offset="1" stop-color="#e2401f" /></linearGradient>
          <linearGradient id={`${P}-lavatop`} x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff1b0" /><stop offset="1" stop-color="#ff8a2a" /></linearGradient>
          <linearGradient id={`${P}-fire`} x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ff5a1f" /><stop offset="1" stop-color="#ffe27a" /></linearGradient>
          <Glow id={`${P}-ember`} c="#ff9a3a" a={0.75} /><Glow id={`${P}-lamp`} c="#ffd35c" a={0.7} /><Glow id={`${P}-abyssglow`} c="#5ef0d8" a={0.6} />
          <Glow id={`${P}-shroomglow`} c="#ff8a5a" a={0.55} /><Glow id={`${P}-boltglow`} c="#ffe27a" a={0.5} />
          <filter id={`${P}-blur`} x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="5" /></filter>
        </defs>
        {/* la mer de nuit, une lueur de lune en haut à droite */}
        <rect x="0" y="0" width={VW} height={VH} fill={u('sea')} />
        <circle cx={VW - 10} cy={6} r="120" fill={u('moon')} />
        <g fill="none" stroke="#9aa6e8" stroke-width="1.2" stroke-linecap="round">
          {GLINTS.map(([gx, gy, w, dl]) => <path class="cm-glint" style={{ animationDelay: `${f(dl)}s` }} d={`M${f(gx - w)} ${f(gy)} Q${f(gx)} ${f(gy - 2.4)} ${f(gx + w)} ${f(gy)}`} />)}
        </g>
        {/* l'île qui serpente : la rive de sable, puis la terre (vert en bas, gris des cendres, sarcelle des abysses) */}
        <g fill="none" stroke-linecap="round" stroke-linejoin="round">
          {legs.map((d) => <path d={d} stroke="#05031a" stroke-opacity="0.5" stroke-width="52" transform="translate(-6 7)" filter={u('blur')} />)}
          {ISLES.map((d) => <path d={d} fill="#05031a" fill-opacity="0.5" transform="translate(-6 7)" filter={u('blur')} />)}
          {legs.map((d) => <path d={d} stroke="#26366e" stroke-opacity="0.55" stroke-width="70" filter={u('blur')} />)}
          {ISLES.map((d) => <path d={d} fill="#26366e" fill-opacity="0.55" stroke="#26366e" stroke-opacity="0.55" stroke-width="22" filter={u('blur')} />)}
          {legs.map((d) => <path d={d} stroke={u('shore')} stroke-width="48" />)}
          {ISLES.map((d) => <path d={d} fill={u('shore')} stroke={u('shore')} stroke-width="6" />)}
          {legs.map((d) => <path d={d} stroke="#2e2750" stroke-width="42" />)}
          {ISLES.map((d) => <path d={d} fill="#2e2750" />)}
          <g transform="translate(1.6 -1.6)">
            {legs.map((d) => <path d={d} stroke={u('land')} stroke-width="41" />)}
            {ISLES.map((d) => <path d={d} fill={u('land')} />)}
          </g>
        </g>
        {/* le chemin : des pas de pierre ; la part faite, d'or */}
        <g fill="none" stroke-linecap="round">
          {legs.map((d) => <path d={d} stroke="#1f1238" stroke-opacity="0.45" stroke-width="11" transform="translate(-1.5 2)" />)}
          {legs.map((d, i) => <path d={d} stroke={i < here ? '#b8802a' : '#6e6584'} stroke-width="9" />)}
          {legs.map((d, i) => <path class={i < here ? 'cm-done-road' : undefined} d={d} stroke={i < here ? '#ffd35c' : '#a79fbd'} stroke-width="4.5" stroke-dasharray="0.1 9" />)}
        </g>
        {/* les nuages qui passent, au bord */}
        <g class="cm-cloud" fill="#d8d2f4" opacity="0.2">
          <path d={scallop([[-26, 240], [-14, 228], [6, 222], [28, 228], [42, 240]])} /><path d={scallop([[292, 130], [300, 120], [318, 115], [336, 120], [348, 130]])} />
        </g>
        {SPOTS.map(([x, y], i) => {
          const Place = PLACES[i]!;
          const state = i < here ? 'done' : i === here ? 'here' : 'locked';
          return (
            <g class={`cm-place ${state}`}>
              <Plinth x={x} y={y} i={i} here={state === 'here'} />
              <Place x={x} y={y} />
              {state === 'here' && (
                <g class="cm-flag">
                  <path d={`M${x + PW - 12} ${y + 8} V${y - 30}`} stroke="#1f1238" stroke-opacity="0.75" stroke-width="3" stroke-linecap="round" />
                  <path d={`M${x + PW - 12} ${y + 8} V${y - 30}`} stroke="#fff1c7" stroke-width="1.2" stroke-linecap="round" />
                  <circle cx={x + PW - 12} cy={y - 32} r="2.6" fill="#ffc22e" stroke="#1f1238" stroke-opacity="0.6" stroke-width="1" />
                  <g class="cm-cloth" style={{ transformOrigin: `${x + PW - 12}px ${y - 24}px` }}>
                    <Vol p={P} d={`M${x + PW - 11} ${y - 29} Q${x + PW - 1} ${y - 32} ${x + PW + 9} ${y - 26} Q${x + PW + 3} ${y - 22} ${x + PW + 8} ${y - 16} Q${x + PW - 2} ${y - 19} ${x + PW - 11} ${y - 17} Z`} fill={u('roof')} line={1.2} depth={2} shade={0.25} rim={0.45}>
                      <path d={spark(x + PW - 2, y - 23, 3.6)} fill="#ffd35c" />
                    </Vol>
                  </g>
                </g>
              )}
            </g>
          );
        })}
        <path d={spark(318, 20, 6)} fill="#ffe27a" opacity="0.85" />
        <path d={spark(300, 40, 3)} fill="#ffe27a" opacity="0.6" />
      </svg>
      {regions.map((r, i) => {
        const [x, y] = SPOTS[i]!;
        const state = i < here ? 'done' : i === here ? 'here' : 'locked';
        const chapters = Array.from({ length: r.to - r.from + 1 }, (_, k) => r.from + k);
        return (
          <>
            <span class={`cm-tag ${state}`} style={pct(x, y + 34)}>
              <Art name={clanElement(CLANS[i]!)} size={16} />
              <b>{r.from}-{r.to}</b>
              <span class="cm-pips">{chapters.map((c) => <i class={c < cur ? 'done' : c === cur ? 'here' : ''} />)}</span>
            </span>
            {state === 'locked' && <span class="cm-lock" style={pct(x, y - 22)}><Icon name="lock" size={30} /></span>}
            {state === 'done' && <span class="cm-check" style={pct(x + PW - 8, y + 19)}><Sign name="check" /></span>}
          </>
        );
      })}
    </div>
  );
}
