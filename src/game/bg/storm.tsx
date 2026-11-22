// Les pics de l'orage : de hautes aiguilles noires sous un ciel violet et bas. Un pont de corde relie deux falaises, une
// tour de guet en ruine garde le col, son fanion claque au vent ; on se bat sur un plateau de dalles fendues.
// Les éclairs zèbrent le ciel par instants, les nuages filent, des débris passent dans le vent.
import { CLOUD_A, CLOUD_C, Cloud, CloudGrad, Flagstones, Peak, Pebbles, Platform, VGrad, W, cloudSprite, ridge, rng, tufts } from './kit';
import { glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

const lift = (c: Ctx) => Math.max(0, Math.min(110, (c.hz - 480) * 0.36));

function sky(c: Ctx) {
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#120e22'], [0.45, '#2e2648'], [0.85, '#5a5278'], [1, '#7a7298']]} />
        <CloudGrad id="k-cloud" top="#4a4266" mid="#352e50" low="#241e3a" />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      {/* un plafond de nuages lourds, en haut */}
      {[[-60, 3, CLOUD_C, 126], [180, 2.6, CLOUD_A, 90], [360, 3.2, CLOUD_C, 126], [580, 2.6, CLOUD_A, 90]].map(([x, s, lobes, w], i) => (
        <g transform={`translate(${x} ${Math.max(60, c.hz * 0.16) + (i % 2) * 24}) scale(${s})`}><Cloud lobes={lobes as [number, number, number][]} w={w as number} light="#5a5280" /></g>
      ))}
      <rect y="-10" width={W} height={Math.max(50, c.hz * 0.1)} fill="#120e22" />
    </>
  );
}

/** Les pierres taillées du mur de la terrasse : x, largeur, rangée (deux rangées décalées). */
const BLOCKS: [number, number, number][] = (() => {
  const r = rng(81);
  const o: [number, number, number][] = [];
  for (const row of [0, 1]) for (let x = -20 - row * 30; x < W + 20;) { const w = 60 + r() * 30; o.push([x, w, row]); x += w; }
  return o;
})();

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const L = lift(c);
  return (
    <>
      <defs>
        <VGrad id="floor" y0={hz} y1={bottom} stops={[[0, '#3a3450'], [0.3, '#4a4462'], [1, '#3a3450']]} />
        <VGrad id="slab" y0={c.p0} y1={c.p1} stops={[[0, '#5a5478'], [1, '#6a6488']]} />
        <VGrad id="void" y0={c.p1} y1={c.bottom} stops={[[0, '#1a1630'], [1, '#2e2848']]} />
      </defs>
      {/* trois rangs d'aiguilles : les lointaines pâles, les proches presque noires */}
      <path d={ridge(21, hz - 60, 90 + L * 0.6, 170 + L * 0.6, 110, 170)} fill="#4e4870" />
      <Peak a={[150, hz - 250 - L]} l={70} r={250} by={hz - 20} ridge={[[156, hz - 210 - L * 0.9], [146, hz - 150 - L * 0.6], [160, hz - 90 - L * 0.3], [152, hz - 20]]} snow={0} shade="#2a2442" lit="#4e4674" />
      <Peak a={[390, hz - 200 - L * 0.7]} l={318} r={470} by={hz - 20} ridge={[[396, hz - 164 - L * 0.6], [386, hz - 110 - L * 0.4], [398, hz - 20]]} snow={0} shade="#2e2848" lit="#544c7a" />
      <Peak a={[500, hz - 290 - L]} l={420} r={590} by={hz - 20} ridge={[[506, hz - 246 - L * 0.9], [494, hz - 180 - L * 0.6], [508, hz - 100 - L * 0.3], [500, hz - 20]]} snow={0} shade="#2a2442" lit="#4e4674" />
      <path d={`M150 ${hz - 250 - L} L163 ${hz - 214 - L * 0.9} L156 ${hz - 210 - L * 0.9} Z M500 ${hz - 290 - L} L513 ${hz - 252 - L * 0.9} L506 ${hz - 246 - L * 0.9} Z`} fill="#8a80c0" opacity="0.8" />
      {/* les deux falaises et le pont de corde qui les relie, à gauche */}
      <path d={`M-20 ${hz} V${hz - 210 - L * 0.5} L40 ${hz - 226 - L * 0.5} L70 ${hz - 200 - L * 0.5} L84 ${hz} Z`} fill="#2a2440" />
      <path d={`M40 ${hz - 226 - L * 0.5} L70 ${hz - 200 - L * 0.5} L84 ${hz} H50 Z`} fill="#4a4268" />
      <path d={`M200 ${hz} L210 ${hz - 170 - L * 0.4} L240 ${hz - 190 - L * 0.4} L268 ${hz - 160 - L * 0.4} L280 ${hz} Z`} fill="#2a2440" />
      <path d={`M240 ${hz - 190 - L * 0.4} L268 ${hz - 160 - L * 0.4} L280 ${hz} H250 Z`} fill="#4a4268" />
      <path d={`M66 ${hz - 206 - L * 0.5} Q140 ${hz - 150 - L * 0.45} 214 ${hz - 172 - L * 0.4}`} fill="none" stroke="#8a7a60" stroke-width="3" />
      <path d={`M66 ${hz - 218 - L * 0.5} Q140 ${hz - 166 - L * 0.45} 214 ${hz - 184 - L * 0.4}`} fill="none" stroke="#8a7a60" stroke-width="2" />
      {Array.from({ length: 11 }, (_, i) => {
        const t = (i + 0.5) / 11, x = 66 + t * 148, y = (1 - t) * (1 - t) * (hz - 206 - L * 0.5) + 2 * t * (1 - t) * (hz - 150 - L * 0.45) + t * t * (hz - 172 - L * 0.4);
        return <rect x={x - 5} y={y - 1} width="10" height="5" fill="#6a5a44" />;
      })}
      {/* la tour de guet en ruine, à droite, sur son éperon */}
      <path d={`M540 ${hz} L560 ${hz - 120 - L * 0.4} L640 ${hz - 130 - L * 0.4} L680 ${hz} Z`} fill="#2a2440" />
      <path d={`M600 ${hz - 128 - L * 0.4} L640 ${hz - 130 - L * 0.4} L680 ${hz} H630 Z`} fill="#4a4268" />
      <g transform={`translate(600 ${hz - 126 - L * 0.4})`}>
        <path d="M-26 0 V-110 L-18 -110 V-118 H-8 V-110 H2 V-122 H12 V-104 L26 -96 V0 Z" fill="#5a5470" />
        <path d="M-26 0 V-110 L-18 -110 V-118 H-10 V0 Z" fill="#3a3450" />
        <path d="M12 -104 L26 -96 V0 H14 Z" fill="#7a7494" />
        <path d="M-4 -70 V-84 Q2 -90 8 -84 V-70 Z M-4 -30 V-44 Q2 -50 8 -44 V-30 Z" fill="#1a1428" />
        <path d="M-2 -66 V-80 Q2 -84 6 -80 V-66 Z" fill="#ffcf6a" opacity="0.7" />
        <path d="M7 -122 V-150" stroke="#2a2018" stroke-width="2.4" />
      </g>
      {/* le col derrière la terrasse : un arbre mort tordu par le vent, des rochers */}
      <rect y={hz} width={W} height={bottom - hz} fill="url(#floor)" />
      <g transform={`translate(54 ${p0 - 2})`}>
        <ellipse cx="0" cy="2" rx="40" ry="6" fill="#000" opacity="0.35" />
        <path d="M-4 0 Q-6 -40 4 -70 Q20 -100 50 -110 M4 -70 Q-20 -86 -34 -84 M14 -90 Q30 -84 44 -90 M30 -102 Q40 -120 56 -122" fill="none" stroke="#2a2030" stroke-width="7" stroke-linecap="round" />
        <path d="M-4 0 Q-6 -40 4 -70 Q20 -100 50 -110" fill="none" stroke="#5a4a5a" stroke-width="2.4" stroke-linecap="round" />
      </g>
      {[[700, p0 - 2, 70, 50], [470, p0 - 2, 44, 28]].map(([x, y, w, h]) => (
        <g transform={`translate(${x} ${y})`}>
          <ellipse cx="0" cy="2" rx={w! * 0.6} ry="6" fill="#000" opacity="0.4" />
          <path d={`M${-w! / 2} 0 L${-w! * 0.4} ${-h! * 0.6} L${-w! * 0.05} ${-h!} L${w! * 0.3} ${-h! * 0.8} L${w! / 2} 0 Z`} fill="#3a3452" />
          <path d={`M${-w! * 0.05} ${-h!} L${w! * 0.3} ${-h! * 0.8} L${w! / 2} 0 H${w! * 0.1} Z`} fill="#6a6488" />
        </g>
      ))}
      <path d={tufts(31, p0 - 2, 4, 26, 1.8)} fill="#5a5070" />
      {/* sous la terrasse, le vide : la brume du précipice */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#void)" />
      {/* la terrasse de dalles d'ardoise, d'un bord à l'autre, sur son mur de pierres taillées */}
      <Platform y0={p0} y1={p1} th={34} top="url(#slab)" face="#4a4466" faceDark="#3a3454" lip="#a8a2c8" back="#120e22"
        faceArt={<>{BLOCKS.map(([x, w, row]) => <rect x={x + 2} y={p1 + 3 + row * 16} width={w - 4} height="13" rx="2" fill={row ? '#5a5478' : '#625c82'} />)}</>}>
        <Flagstones seed={14} y0={p0} y1={p1} rows={4} line="#3a3452" light="#8a84aa" lightOpacity={0.18} />
        <Pebbles seed={13} x={360} y={(p0 + p1) / 2} n={16} rx={360} ry={(p1 - p0) * 0.42} color="#3a3452" lit="#8a84aa" k={1.2} />
      </Platform>
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <path d={`M-20 ${b + 10} L-8 ${b - 34} L32 ${b - 46} L64 ${b - 22} L82 ${b + 10} Z`} fill="#221c36" />
      <path d={`M32 ${b - 46} L64 ${b - 22} L82 ${b + 10} H48 Z`} fill="#3e3858" />
      <path d={`M740 ${b + 10} L728 ${b - 36} L690 ${b - 48} L656 ${b - 20} L640 ${b + 10} Z`} fill="#221c36" />
      <path d={`M690 ${b - 48} L728 ${b - 36} L740 ${b + 10} H700 Z`} fill="#3e3858" />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const L = lift(c);
  const dark = { top: '#3e3660', mid: '#2e284a', low: '#201a36', light: '#4a4270' };
  const cA = cloudSprite(CLOUD_C, 126, 2, dark), cB = cloudSprite(CLOUD_A, 90, 1.5, dark);
  /** Un éclair : un trait brisé blanc dans un halo violet. */
  const bolt = (h: number) => ({
    w: 140, h,
    draw: () => {
      const pts = [[70, 0], [56, h * 0.22], [80, h * 0.36], [52, h * 0.58], [74, h * 0.7], [48, h]];
      const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join(' ');
      return <g fill="none" stroke-linecap="round" stroke-linejoin="round"><path d={d} stroke="#b89aff" stroke-width="14" opacity="0.35" /><path d={d} stroke="#e8dcff" stroke-width="6" /><path d={d} stroke="#ffffff" stroke-width="2.4" /><path d={`M56 ${h * 0.22} L30 ${h * 0.34} M52 ${h * 0.58} L84 ${h * 0.66}`} stroke="#e8dcff" stroke-width="3" /></g>;
    },
  });
  return [
    { id: 'cloudA', ...cA, at: [[100, Math.max(140, c.hz * 0.32)], [560, Math.max(110, c.hz * 0.24)]], depth: -28, anim: { k: 'drift', speed: 22, from: -320, to: 1040 }, alpha: 0.95 },
    { id: 'cloudB', ...cB, at: [[380, Math.max(180, c.hz * 0.42)]], depth: -28, anim: { k: 'drift', speed: 34, from: -320, to: 1040 }, alpha: 0.9 },
    { id: 'flashSky', ...glowSprite(900, '#c8b0ff', 0.55), at: [[460, Math.max(160, c.hz * 0.3)]], depth: -27, anim: { k: 'flash', every: 6 }, add: true },
    { id: 'bolt', ...bolt(Math.max(160, c.hz - 260 - L)), origin: [0.5, 0], at: [[470, Math.max(40, c.hz * 0.1)]], depth: -27, anim: { k: 'flash', every: 6 }, add: true },
    {
      id: 'flag', w: 60, h: 30, origin: [0, 0.5], at: [[607, c.hz - 126 - L * 0.4 - 146]], depth: -18, anim: { k: 'sway', deg: 9, period: 0.9 },
      draw: () => <path d="M0 4 Q20 0 34 8 Q46 14 58 10 Q48 20 34 18 Q18 16 0 22 Z" fill="#c83a4a" />,
    },
  ];
}

export const STORM: Scene = {
  base: 0x3a3450,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'debris', size: 12, area: [-60, c.hz - 200, -20, c.p1], depth: -11, vx: [160, 240], vy: [-20, 30], life: [3500, 5000], count: 5, scale: [0.6, 1], alpha: [0.5, 0.9], spin: 300,
      draw: () => <path d="M6 1 Q11 5 6 11 Q1 5 6 1 Z" fill="#8a7a60" />,
    },
    {
      id: 'mist', size: 60, area: [-60, c.p1 + 10, -30, c.bottom], depth: -12, vx: [40, 70], vy: [-4, 4], life: [12000, 16000], count: 7, scale: [1, 2.2], alpha: [0.2, 0.55],
      draw: () => <circle cx="30" cy="30" r="28" fill="#6a6290" opacity="0.5" />,
    },
  ],
};
