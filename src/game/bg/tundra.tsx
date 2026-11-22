// La toundra : une nuit de grand froid. L'aurore ondule au-dessus des sommets, la lune éclaire la neige ; une forêt de
// sapins blanchis, des falaises de glace ; on se bat sur un lac gelé, cerclé de congères et d'éclats de glace.
// La neige tombe, l'aurore respire, les étoiles scintillent.
import { Peak, Pine, Platform, RGrad, Stars, VGrad, W, forest, rng } from './kit';
import { Crystals, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

/** La lune : à droite (la lumière des sommets vient de la droite), entre deux sommets, sous l'aurore (jamais dedans). */
const moonAt = (c: Ctx) => ({ x: 590, y: Math.max(200, c.hz - 420) });
/** Une petite étoile qui scintille : quatre branches fines et nettes, un cœur à peine flou (pas une tache floue). */
const sparkle = (size: number, color = '#ffffff') => ({
  w: size, h: size,
  draw: () => {
    const m = size / 2, t = size * 0.07;
    return (
      <>
        <defs><RGrad id="sp" stops={[[0, color, 0.8], [0.35, color, 0.2], [1, color, 0]]} /></defs>
        <circle cx={m} cy={m} r={m * 0.6} fill="url(#sp)" />
        <path d={`M${m} 0 L${m + t} ${m - t} L${size} ${m} L${m + t} ${m + t} L${m} ${size} L${m - t} ${m + t} L0 ${m} L${m - t} ${m - t} Z`} fill={color} />
      </>
    );
  },
});
const lift = (c: Ctx) => Math.max(0, Math.min(110, (c.hz - 480) * 0.36));

/** Un sapin sous la neige : le sapin, puis une couche blanche sur le haut de chaque étage. */
function SnowPine({ x, y, s }: { x: number; y: number; s: number }) {
  return (
    <g>
      <Pine x={x} y={y} s={s} dark="#1f4a4a" light="#2f6a64" trunk="#4a3a34" shadow="#2a3a6a" />
      <g transform={`translate(${x} ${y}) scale(${s})`} fill="#f4faff">
        {[[-58, 8, 14], [-49, 12, 17], [-38, 16, 19], [-25, 20, 22]].map(([top, w, h]) => <path d={`M0 ${top} L${w! * 0.7} ${top! + h! * 0.7} Q0 ${top! + h! * 0.5} ${-w! * 0.7} ${top! + h! * 0.7} Z`} />)}
      </g>
    </g>
  );
}

function sky(c: Ctx) {
  const m = moonAt(c);
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#070c26'], [0.45, '#16285a'], [0.8, '#2f5288'], [1, '#5f84b0']]} />
        <RGrad id="moonglow" stops={[[0, '#e8f4ff', 0.7], [0.3, '#b8d8ff', 0.25], [1, '#b8d8ff', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <Stars seed={11} n={90} y0={0} y1={c.hz - 140} />
      <circle cx={m.x} cy={m.y} r="170" fill="url(#moonglow)" />
      <circle cx={m.x} cy={m.y} r="34" fill="#f2f8ff" />
      <circle cx={m.x - 9} cy={m.y - 6} r="7" fill="#d6e4f4" /><circle cx={m.x + 10} cy={m.y + 8} r="5" fill="#d6e4f4" /><circle cx={m.x + 4} cy={m.y - 14} r="3.4" fill="#d6e4f4" />
    </>
  );
}

/** Les stalactites sous le bord de la banquise (x, longueur) et les plaques de neige sur la glace (x, y relatif, largeur). */
const ICICLES: [number, number][] = (() => { const r = rng(71); const o: [number, number][] = []; for (let x = 10; x < W; x += 18 + r() * 34) o.push([x, 8 + r() * 22]); return o; })();
/** Le bord de la congère du fond, de droite à gauche : x, creux. */
const DRIFT: [number, number][] = (() => { const r = rng(73); const o: [number, number][] = []; for (let x = W + 20; x > -20; x -= 50 + r() * 60) o.push([x, 4 + r() * 14]); return o; })();

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const L = lift(c);
  return (
    <>
      <defs>
        <VGrad id="snow" y0={hz} y1={bottom} stops={[[0, '#b8cce8'], [0.2, '#dce8f8'], [1, '#c8d8f0']]} />
        <VGrad id="ice" y0={c.p0} y1={c.p1} stops={[[0, '#b8e0f6'], [0.5, '#d4f0fc'], [1, '#bfe4f8']]} />
        <VGrad id="deep" y0={c.p1} y1={c.bottom} stops={[[0, '#1a3a6a'], [1, '#24508a']]} />
        <VGrad id="cliff" y0={hz - 140} y1={hz} stops={[[0, '#d8f0ff'], [1, '#7fb0d8']]} />
      </defs>
      {/* les sommets : beaucoup de neige, faces d'ombre bleu nuit */}
      <Peak a={[250, hz - 250 - L]} l={110} r={400} by={hz - 50} ridge={[[258, hz - 216 - L * 0.9], [244, hz - 170 - L * 0.6], [262, hz - 120 - L * 0.3], [252, hz - 50]]} snow={120 + L * 0.4} shade="#3a5288" lit="#7f9ccc" snowShade="#a8c0e4" snowLit="#f0f6ff" />
      <Peak a={[520, hz - 220 - L * 0.7]} l={400} r={680} by={hz - 50} ridge={[[528, hz - 188 - L * 0.6], [512, hz - 146 - L * 0.4], [530, hz - 96 - L * 0.2], [520, hz - 50]]} snow={100 + L * 0.3} shade="#33497c" lit="#7390c2" snowShade="#a0b8de" snowLit="#eef4ff" />
      <Peak a={[690, hz - 180 - L * 0.5]} l={600} r={800} by={hz - 50} ridge={[[696, hz - 150], [686, hz - 110], [698, hz - 50]]} snow={70} shade="#3a5288" lit="#7f9ccc" snowShade="#a8c0e4" snowLit="#f0f6ff" />
      <Peak a={[40, hz - 170 - L * 0.4]} l={-70} r={150} by={hz - 50} ridge={[[46, hz - 140], [36, hz - 100], [48, hz - 50]]} snow={64} shade="#33497c" lit="#7390c2" snowShade="#a0b8de" snowLit="#eef4ff" />
      {/* la forêt de sapins blanchis, au pied des sommets */}
      <path d={forest(14, hz - 37, 18, 46, 14, 24)} fill="#e8f2ff" />
      <path d={forest(14, hz - 34, 18, 46, 14, 24)} fill="#2a4a5a" />
      {/* des falaises de glace à gauche et à droite */}
      <path d={`M-20 ${hz + 10} L-20 ${hz - 110} L30 ${hz - 128} L64 ${hz - 96} L96 ${hz - 104} L130 ${hz - 60} L150 ${hz + 10} Z`} fill="url(#cliff)" />
      <path d={`M30 ${hz - 128} L64 ${hz - 96} L52 ${hz + 10} H-20 V${hz - 110} Z`} fill="#6a98c4" opacity="0.7" />
      <path d={`M740 ${hz + 10} L740 ${hz - 120} L690 ${hz - 138} L656 ${hz - 100} L620 ${hz - 110} L590 ${hz - 60} L574 ${hz + 10} Z`} fill="url(#cliff)" />
      <path d={`M656 ${hz - 100} L690 ${hz - 138} L740 ${hz - 120} V${hz + 10} H676 Z`} fill="#e8f6ff" opacity="0.6" />
      {/* la neige : un grand plan, des congères qui ondulent */}
      <rect y={hz - 4} width={W} height={bottom - hz + 4} fill="url(#snow)" />
      <path d={`M-20 ${hz + 20} Q120 ${hz - 6} 260 ${hz + 14} Q380 ${hz + 30} 500 ${hz + 8} Q620 ${hz - 10} 740 ${hz + 18} V${hz - 4} H-20 Z`} fill="#eef4ff" />
      {/* des sapins enneigés de part et d'autre, les pieds dans la neige, derrière la banquise */}
      <SnowPine x={30} y={p0 - 2} s={1.5} /><SnowPine x={78} y={p0 - 8} s={1.1} /><SnowPine x={180} y={p0 - 14} s={0.8} />
      <SnowPine x={548} y={p0 - 14} s={0.85} /><SnowPine x={650} y={p0 - 6} s={1.2} /><SnowPine x={700} y={p0 - 2} s={1.6} />
      <Crystals x={250} y={p0 - 4} s={0.9} color="#9fd8f8" light="#ffffff" dark="#4a8ac0" /><Crystals x={470} y={p0 - 4} s={0.8} color="#9fd8f8" light="#ffffff" dark="#4a8ac0" flip />
      {/* l'eau noire sous la banquise, quelques glaçons qui flottent */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#deep)" />
      {[[70, 30], [260, 22], [470, 26], [640, 34]].map(([x, w]) => <g><ellipse cx={x} cy={p1 + 56} rx={w} ry="6" fill="#dff0ff" /><ellipse cx={x! - 4} cy={p1 + 58} rx={w! * 0.8} ry="3" fill="#a8c8e8" /></g>)}
      {/* la banquise : une longue plaque de glace d'un bord à l'autre, saupoudrée de neige ; son flanc bleu, ses stalactites */}
      <Platform y0={p0} y1={p1} th={34} top="url(#ice)" face="#5a98cc" faceDark="#3f78b0" lip="#ffffff" back="#2a4a7a"
        faceArt={<>
          <rect x="-20" y={p1 + 2} width={W + 40} height="10" fill="#9fd0f0" opacity="0.6" />
          {ICICLES.map(([x, l]) => <path d={`M${x - 5} ${p1 + 30} L${x} ${p1 + 30 + l} L${x + 5} ${p1 + 30} Z`} fill="#bfe4fa" />)}
        </>}>
        <path d={`M-20 ${p0} H${W + 20} V${p0 + 30} ${DRIFT.map(([x, d]) => `Q${x + 30} ${p0 + 30 + d} ${x} ${p0 + 26 + d * 0.4}`).join(' ')} L-20 ${p0 + 34} Z`} fill="#f4faff" opacity="0.85" />
        <path d={`M60 ${p1 - 30} L120 ${p1 - 52} L190 ${p1 - 40} L250 ${p1 - 62} M120 ${p1 - 52} L136 ${p1 - 80} M470 ${p1 - 24} L540 ${p1 - 44} L610 ${p1 - 34} M540 ${p1 - 44} L556 ${p1 - 76}`} fill="none" stroke="#ffffff" stroke-width="2.4" opacity="0.8" stroke-linecap="round" />
      </Platform>
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <path d={`M-20 ${b + 10} Q10 ${b - 36} 70 ${b - 24} Q110 ${b - 14} 126 ${b + 10} Z`} fill="#f4f8ff" />
      <path d={`M-20 ${b + 10} Q10 ${b - 36} 70 ${b - 24} Q36 ${b - 16} 12 ${b + 10} Z`} fill="#c8d8f0" />
      <path d={`M740 ${b + 10} Q712 ${b - 40} 650 ${b - 26} Q612 ${b - 16} 596 ${b + 10} Z`} fill="#f4f8ff" />
      <Crystals x={96} y={b - 4} s={1.1} color="#9fd8f8" light="#ffffff" dark="#4a8ac0" />
      <Crystals x={652} y={b - 2} s={1} color="#9fd8f8" light="#ffffff" dark="#4a8ac0" flip />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const m = moonAt(c);
  // l'aurore passe en biais AU-DESSUS de la lune : basse à gauche, haute à droite ; elle sort des deux bords
  const ay = m.y - 50;
  /** Un rideau d'aurore : une bande douce et ondulée, qui pâlit vers le bas ; `tilt` = de combien elle descend vers la gauche. */
  const curtain = (color: string, w: number, h: number, tilt: number) => ({
    w, h: h + tilt,
    draw: () => (
      <>
        <defs>
          <linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color={color} stop-opacity="0" /><stop offset="0.35" stop-color={color} stop-opacity="0.75" /><stop offset="1" stop-color={color} stop-opacity="0" /></linearGradient>
          <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="0.25" stop-color="#fff" /><stop offset="0.75" stop-color="#fff" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></linearGradient>
          <mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width={w} height={h}><rect width={w} height={h} fill="url(#fade)" /></mask>
        </defs>
        <g transform={`matrix(1 ${(-tilt / w).toFixed(4)} 0 1 0 ${tilt})`}>
          <path mask="url(#m)" d={`M0 ${h * 0.3} Q${w * 0.25} ${h * 0.05} ${w * 0.5} ${h * 0.25} Q${w * 0.75} ${h * 0.45} ${w} ${h * 0.15} V${h * 0.85} Q${w * 0.75} ${h} ${w * 0.5} ${h * 0.8} Q${w * 0.25} ${h * 0.6} 0 ${h * 0.9} Z`} fill="url(#a)" />
        </g>
      </>
    ),
  });
  return [
    { id: 'aurora1', ...curtain('#5affb0', 760, 240, 140), at: [[360, ay]], depth: -29, anim: { k: 'pulse', min: 0.45, period: 7 }, add: true },
    { id: 'aurora2', ...curtain('#9a7aff', 620, 200, 120), at: [[450, ay - 40]], depth: -29, anim: { k: 'pulse', min: 0.3, period: 9 }, add: true },
    { id: 'aurora3', ...curtain('#4ad8ff', 520, 160, 100), at: [[230, ay + 30]], depth: -29, anim: { k: 'bob', amp: 8, period: 8 }, add: true, alpha: 0.7 },
    { id: 'moon', ...glowSprite(260, '#cfe6ff', 0.4), at: [[m.x, m.y]], depth: -28, anim: { k: 'pulse', min: 0.6, period: 6 }, add: true },
    { id: 'twinkle', ...sparkle(22), at: [[300, c.hz * 0.12], [470, c.hz * 0.3], [140, c.hz * 0.2], [60, c.hz * 0.42], [400, c.hz * 0.44], [690, c.hz * 0.1]], depth: -28, anim: { k: 'pulse', min: 0, period: 2.4 }, add: true },
    { id: 'glint', ...sparkle(18), at: [[450, c.p0 + 60], [180, c.p1 - 30], [620, c.p1 - 24]], depth: -14, anim: { k: 'pulse', min: 0, period: 3.4 }, add: true },
  ];
}

export const TUNDRA: Scene = {
  base: 0xc8d8f0,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'snowB', size: 10, area: [-40, -10, W + 40, 10], depth: -11, vx: [-14, 10], vy: [26, 46], life: [12000, 18000], count: 40, scale: [0.4, 0.8], alpha: [0.5, 0.9],
      draw: () => <><defs><RGrad id="s" stops={[[0, '#ffffff'], [0.6, '#ffffff', 0.8], [1, '#ffffff', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#s)" /></>,
    },
    {
      id: 'snowF', size: 14, area: [-40, -10, W + 40, 10], depth: 1295, vx: [-20, 14], vy: [50, 80], life: [8000, 12000], count: 12, scale: [0.6, 1], alpha: [0.6, 0.95],
      draw: () => <><defs><RGrad id="s" stops={[[0, '#ffffff'], [0.6, '#ffffff', 0.8], [1, '#ffffff', 0]]} /></defs><circle cx="7" cy="7" r="7" fill="url(#s)" /></>,
    },
  ],
};
