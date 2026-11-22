// Le bayou : un marais à l'heure dorée. Au loin, une rive de cyprès et une cabane sur pilotis ; la lagune reflète le
// soleil ; deux vieux cyprès encadrent la scène, leur mousse grise pend et se balance. On se bat sur une grande plateforme
// ronde de planches, posée sur pilotis, avec deux lanternes. Roseaux et nénuphars au premier plan, lucioles.
import { CLOUD_A, CLOUD_B, Platform, RGrad, VGrad, W, cloudSprite, forest, rng } from './kit';
import { LanternPost, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

const sunAt = (c: Ctx) => ({ x: 588, y: Math.max(140, c.hz - 190) });

/** Un nénuphar : feuille ronde fendue, parfois une fleur. */
function Pad({ x, y, s, flower = false }: { x: number; y: number; s: number; flower?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M0 0 L12 -2 A14 6 0 1 1 10 3 Z" fill="#3f8a4a" /><path d="M0 0 L12 -2 A14 6 0 0 0 -8 -4 Z" fill="#62b060" opacity="0.8" />
      {flower && <g transform="translate(-3 -3)"><path d="M0 0 L-5 -6 L0 -4 L2 -9 L4 -4 L9 -6 L4 0 Z" fill="#ffb8d0" /><circle cx="1" cy="-2" r="1.8" fill="#ffd45c" /></g>}
    </g>
  );
}

/** La ramure d'un cyprès : des touffes rondes superposées (ombre en dessous, lumière dessus), sur des branches. */
function Crown({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  const lumps: [number, number, number][] = [[-120, 26, 46], [-60, -10, 58], [10, -34, 62], [80, -6, 52], [136, 30, 40], [-10, 30, 54], [60, 34, 46]];
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d="M-4 120 Q-10 60 -60 30 M-2 90 Q20 40 80 20 M0 60 Q-4 20 10 -20" fill="none" stroke="#5a4a3a" stroke-width="7" stroke-linecap="round" />
      {lumps.map(([dx, dy, r]) => <circle cx={dx} cy={dy} r={r} fill="#24523e" />)}
      {lumps.map(([dx, dy, r]) => <circle cx={dx + r * 0.12} cy={dy - r * 0.16} r={r * 0.8} fill="#3a7656" />)}
      {lumps.map(([dx, dy, r]) => <circle cx={dx + r * 0.3} cy={dy - r * 0.36} r={r * 0.42} fill="#5f9e6e" />)}
      <path d="M-150 44 Q-100 70 -40 62 Q20 76 80 60 Q140 70 176 48 Q150 84 80 82 Q20 92 -40 80 Q-110 88 -150 44 Z" fill="#1a3e30" opacity="0.6" />
    </g>
  );
}

/** Un vieux cyprès dans l'eau : tronc évasé à cannelures douces, genoux autour, ramure en haut (mousse animée à part). */
function Cypress({ x, y, w, h, flip = false }: { x: number; y: number; w: number; h: number; flip?: boolean }) {
  const s = flip ? -1 : 1;
  return (
    <g transform={`translate(${x} ${y}) scale(${s} 1)`}>
      <ellipse cx="0" cy="4" rx={w * 1.4} ry="7" fill="#1f4a46" opacity="0.4" />
      <path d={`M${-w * 1.3} 2 Q${-w * 0.7} ${-w * 0.3} ${-w * 0.42} ${-w * 1.4} L${-w * 0.3} ${-h} H${w * 0.3} L${w * 0.42} ${-w * 1.4} Q${w * 0.7} ${-w * 0.3} ${w * 1.4} 2 Z`} fill="#6a5a48" />
      <path d={`M${-w * 1.3} 2 Q${-w * 0.7} ${-w * 0.3} ${-w * 0.42} ${-w * 1.4} L${-w * 0.3} ${-h} H${-w * 0.02} L${-w * 0.1} ${-w * 1.2} Q${-w * 0.3} ${-w * 0.2} ${-w * 0.5} 2 Z`} fill="#4a3e34" />
      <path d={`M${w * 0.1} ${-h} L${w * 0.16} ${-w * 1.2} Q${w * 0.4} ${-w * 0.2} ${w * 0.9} 2 H${w * 1.4} Q${w * 0.7} ${-w * 0.3} ${w * 0.42} ${-w * 1.4} L${w * 0.3} ${-h} Z`} fill="#8f7a60" />
      {/* les genoux du cyprès, qui sortent de l'eau */}
      {[[-w * 1.9, 6, 0.9], [w * 1.8, 4, 0.7], [-w * 2.6, 10, 0.6]].map(([dx, dy, k]) => <g transform={`translate(${dx} ${dy}) scale(${k})`}><path d="M-6 0 Q-4 -14 0 -16 Q4 -14 6 0 Z" fill="#6a5a48" /><path d="M0 -16 Q4 -14 6 0 H2 Q2 -10 0 -16 Z" fill="#8f7a60" /></g>)}
    </g>
  );
}

function sky(c: Ctx) {
  const sun = sunAt(c);
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#255f86'], [0.42, '#5fa8b8'], [0.78, '#e8deac'], [1, '#f8d898']]} />
        <RGrad id="bloom" stops={[[0, '#fff8e0', 0.95], [0.3, '#ffe8a0', 0.5], [0.7, '#ffd890', 0.15], [1, '#ffd890', 0]]} />
        <RGrad id="sun" stops={[[0, '#fffbe8'], [0.6, '#fff0b8'], [0.9, '#ffd98a'], [1, '#ffd98a', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <circle cx={sun.x} cy={sun.y} r="300" fill="url(#bloom)" />
      <circle cx={sun.x} cy={sun.y} r="54" fill="url(#sun)" />
    </>
  );
}

/** Les pilotis sous le ponton. */
const PILES = [30, 150, 270, 390, 510, 630];
/** Les planches du ponton (y, épaisseur), de plus en plus larges vers le devant. */
const BOARDS = (p0: number, p1: number): [number, number][] => {
  const n = 7, w = Array.from({ length: n }, (_, i) => 0.7 + (0.6 * i) / n), t = w.reduce((a, b) => a + b, 0);
  let y = p0;
  return w.map((k) => { const h = ((p1 - p0) * k) / t; const out: [number, number] = [y, h]; y += h; return out; });
};

function land(c: Ctx) {
  const { hz, bottom, cx, p0, p1 } = c;
  const sun = sunAt(c);
  const r = rng(29);
  const canopyY = Math.min(hz - 300, hz * 0.36);
  return (
    <>
      <defs>
        <VGrad id="water" y0={hz - 40} y1={bottom} stops={[[0, '#a8d8c8'], [0.18, '#6fb4a8'], [0.55, '#3f8a80'], [1, '#2a6a64']]} />
        <RGrad id="refl" stops={[[0, '#fff2c0', 0.7], [0.5, '#ffe6a0', 0.25], [1, '#ffe6a0', 0]]} />
        <VGrad id="deck" y0={c.p0} y1={c.p1} stops={[[0, '#b8875a'], [1, '#c99a68']]} />
        <VGrad id="moss" y0={canopyY - 200} y1={canopyY + 40} stops={[[0, '#1f4a3a'], [1, '#3f7a5a']]} />
      </defs>
      {/* la rive lointaine : une lisière de cyprès bleutée, une cabane sur pilotis */}
      <path d={forest(8, hz - 34, 22, 60, 16, 30)} fill="#7fa8a0" />
      <path d={forest(12, hz - 26, 12, 34, 12, 22)} fill="#5f8f86" />
      <g transform={`translate(120 ${hz - 40})`}>
        <path d="M-22 0 V-10 M-8 0 V-10 M8 0 V-10 M22 0 V-10" stroke="#4a5a54" stroke-width="2.4" />
        <rect x="-24" y="-30" width="48" height="20" fill="#7a8a80" /><rect x="-24" y="-30" width="16" height="20" fill="#5f6f68" />
        <path d="M-30 -29 L0 -46 L30 -29 Z" fill="#5a6a64" /><rect x="4" y="-24" width="8" height="8" fill="#ffd98a" opacity="0.85" />
      </g>
      {/* la lagune : toute la scène est sur l'eau ; le reflet du soleil s'y étale */}
      <rect y={hz - 40} width={W} height={bottom - hz + 40} fill="url(#water)" />
      <ellipse cx={sun.x} cy={hz - 10} rx="150" ry="26" fill="url(#refl)" />
      <ellipse cx={sun.x} cy={hz + 30} rx="90" ry="40" fill="url(#refl)" opacity="0.6" />
      {Array.from({ length: 14 }, () => <ellipse cx={r() * W} cy={hz - 30 + r() * 70} rx={20 + r() * 50} ry="2" fill="#ffffff" opacity={0.15 + r() * 0.2} />)}
      {/* nénuphars au loin */}
      {[[60, hz - 6, 0.9], [210, hz + 4, 1.1, true], [300, hz - 14, 0.7], [470, hz + 6, 1, true], [520, hz - 8, 0.8], [690, hz + 10, 1.2]].map(([x, y, k, fl]) => <Pad x={x as number} y={y as number} s={k as number} flower={!!fl} />)}
      {/* deux vieux cyprès encadrent la scène ; leur ramure couvre les coins du haut */}
      <Cypress x={70} y={hz + 26} w={30} h={hz + 30 - canopyY} />
      <Cypress x={664} y={hz + 30} w={34} h={hz + 30 - canopyY} flip />
      <Crown x={92} y={canopyY} s={1} />
      <Crown x={640} y={canopyY - 6} s={1.08} flip />

      {/* la plateforme : un long ponton de planches d'un bord à l'autre, sur pilotis ; les lanternes au fond */}
      {PILES.map((x) => <g><rect x={x - 8} y={p1 + 10} width="16" height="46" fill="#4a3426" /><rect x={x - 8} y={p1 + 10} width="6" height="46" fill="#33241a" /><ellipse cx={x} cy={p1 + 56} rx="14" ry="3.5" fill="#cfeee8" opacity="0.45" /></g>)}
      <Platform y0={p0} y1={p1} th={22} top="url(#deck)" face="#6a4a30" faceDark="#553a24" lip="#e6b888" back="#1f4a46"
        faceArt={<>{PILES.map((x) => <circle cx={x} cy={p1 + 11} r="3" fill="#2a1c12" />)}</>}>
        {BOARDS(p0, p1).map(([y, h], i) => <g><rect x="-20" y={y} width={W + 40} height={h} fill={i % 2 ? '#c49466' : '#b8885a'} /><rect x="-20" y={y + h - 2.2} width={W + 40} height="2.2" fill="#7a5236" opacity="0.6" /></g>)}
        {Array.from({ length: 16 }, (_, i) => <g><circle cx={20 + i * 46} cy={p0 + 8 + (i % 3) * 30} r="1.8" fill="#5a3a24" /><circle cx={40 + i * 46} cy={p1 - 14 - (i % 2) * 34} r="2" fill="#5a3a24" /></g>)}
        <ellipse cx={cx + 90} cy={(p0 + p1) / 2} rx="300" ry="60" fill="#f0c890" opacity="0.18" />
      </Platform>
      {/* les lanternes, debout sur le bord du fond du ponton, reliées par une corde */}
      <path d={`M${128 + 25} ${p0 + 8 - 88 * 1.15} Q${cx} ${p0 - 40} ${592 - 25} ${p0 + 8 - 88 * 1.15}`} fill="none" stroke="#5e4026" stroke-width="2" />
      <LanternPost x={128} y={p0 + 8} s={1.15} /><LanternPost x={592} y={p0 + 8} s={1.15} flip />
      {/* l'eau devant le ponton : quelques nénuphars */}
      <Pad x={60} y={bottom - 14} s={1.5} flower /><Pad x={300} y={bottom - 8} s={1.2} /><Pad x={650} y={bottom - 12} s={1.6} flower />
    </>
  );
}

/** Roseaux et massettes, un nénuphar : dans les coins du bas. */
function Reeds({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d="M-14 0 Q-18 -40 -26 -70 Q-12 -40 -8 0 Z" fill="#3f7a4a" /><path d="M-4 0 Q-2 -50 4 -86 Q6 -48 2 0 Z" fill="#5a9a58" />
      <path d="M6 0 Q14 -36 26 -60 Q16 -30 12 0 Z" fill="#3f7a4a" /><path d="M-10 0 Q-6 -30 -14 -50 Q-2 -28 -4 0 Z" fill="#6fae62" />
      <rect x="2" y="-84" width="5" height="18" rx="2.5" fill="#7a4a2a" /><rect x="-24" y="-66" width="4.5" height="15" rx="2.2" fill="#7a4a2a" />
      <path d="M4.5 -84 V-94 M-21.8 -66 V-74" stroke="#5a9a58" stroke-width="1.4" />
    </g>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <Reeds x={20} y={b + 4} s={1.6} /><Reeds x={64} y={b + 10} s={1.1} flip /><Reeds x={704} y={b + 6} s={1.7} flip /><Reeds x={660} y={b + 12} s={1} />
      <Pad x={140} y={b - 6} s={2} /><Pad x={560} y={b - 4} s={1.8} flower />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const sun = sunAt(c);
  const canopyY = Math.min(c.hz - 300, c.hz * 0.36);
  const cA = cloudSprite(CLOUD_A, 90, 1.6, { top: '#fff8ec', mid: '#f8e8d0', low: '#e8c8a8' }), cB = cloudSprite(CLOUD_B, 62, 1.3, { top: '#fff8ec', mid: '#f8e8d0', low: '#e8c8a8' });
  return [
    { id: 'sun', ...glowSprite(360, '#fff0c0', 0.5), at: [[sun.x, sun.y]], depth: -29, anim: { k: 'pulse', min: 0.6, period: 7 }, add: true },
    { id: 'cloudA', ...cA, at: [[200, Math.max(110, c.hz * 0.3)]], depth: -28, anim: { k: 'drift', speed: 4, from: -300, to: 1020 }, alpha: 0.9 },
    { id: 'cloudB', ...cB, at: [[520, Math.max(90, c.hz * 0.18)], [-80, Math.max(160, c.hz * 0.46)]], depth: -28, anim: { k: 'drift', speed: 6, from: -300, to: 1020 }, alpha: 0.8, scale: [1, 0.8] },
    // la mousse grise qui pend des cyprès
    {
      id: 'moss', w: 46, h: 150, origin: [0.5, 0], at: [[30, canopyY + 20], [96, canopyY + 26], [168, canopyY + 6], [214, canopyY - 4], [516, canopyY + 6], [580, canopyY + 30], [646, canopyY + 26], [716, canopyY + 34]], depth: -21,
      anim: { k: 'sway', deg: 3, period: 6 }, scale: [1, 0.8, 1.15, 0.7, 0.75, 1.1, 0.9, 1],
      draw: () => (
        <g>
          <path d="M8 0 Q2 40 10 80 Q14 110 8 146 Q18 112 20 80 Q24 40 18 0 Z" fill="#9fb0a0" /><path d="M20 0 Q18 50 26 90 Q30 120 24 140 Q36 110 34 80 Q32 40 30 0 Z" fill="#c4d0c0" />
          <path d="M30 0 Q34 30 30 60 Q28 80 34 100 Q40 76 40 54 Q40 24 38 0 Z" fill="#8a9c8c" />
        </g>
      ),
    },
    // les lanternes : leur lueur vacille
    { id: 'lamp', ...glowSprite(130, '#ffcf6a', 0.8), at: [[128 + 25 * 1.15, c.p0 + 8 - 71 * 1.15], [592 - 25 * 1.15, c.p0 + 8 - 71 * 1.15]], depth: -12, anim: { k: 'flicker', min: 0.6, period: 2.2 }, add: true },
    // une nappe de brume qui glisse au ras de l'eau, au fond
    {
      id: 'mist', w: 360, h: 50, at: [[180, c.hz - 18], [700, c.hz - 8]], depth: -16, anim: { k: 'drift', speed: 6, from: -260, to: 980 }, alpha: 0.5,
      draw: () => <><defs><RGrad id="m" stops={[[0, '#ffffff', 0.85], [1, '#ffffff', 0]]} /></defs><ellipse cx="180" cy="25" rx="180" ry="25" fill="url(#m)" /></>,
    },
    // des reflets qui scintillent sur l'eau
    { id: 'glint', ...glowSprite(70, '#fff6d0', 0.7), at: [[540, c.hz - 6], [620, c.hz + 14], [90, c.bottom - 18], [400, c.bottom - 10]], depth: -15, anim: { k: 'pulse', min: 0.1, period: 2.6 }, add: true, scale: [1, 0.7, 0.8, 0.6] },
    // les roseaux du devant ondulent
    {
      id: 'reedtip', w: 40, h: 90, origin: [0.5, 1], at: [[100, c.bottom + 8], [620, c.bottom + 6]], depth: 1301, anim: { k: 'sway', deg: 4, period: 4 }, scale: [1.2, 1.3],
      draw: () => <g><path d="M18 90 Q14 50 6 10 Q22 46 24 90 Z" fill="#4a8a50" /><path d="M22 90 Q26 56 34 26 Q30 58 28 90 Z" fill="#6fae62" /><rect x="3" y="4" width="5" height="16" rx="2.5" fill="#7a4a2a" /></g>,
    },
  ];
}

export const BAYOU: Scene = {
  base: 0x3f8a80,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'firefly', size: 14, area: [0, c.hz - 60, W, c.bottom - 40], depth: -11, vx: [-10, 10], vy: [-8, 4], life: [4000, 7000], count: 14, scale: [0.6, 1], alpha: [0.2, 1], add: true,
      draw: () => <><defs><RGrad id="f" stops={[[0, '#ffffe8'], [0.3, '#ffe080', 0.8], [1, '#ffc040', 0]]} /></defs><circle cx="7" cy="7" r="7" fill="url(#f)" /></>,
    },
  ],
};
