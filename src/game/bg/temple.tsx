// Le temple des sables : un couchant derrière un temple à colonnes. Le soleil, énorme et bas, se couche juste derrière
// le fronton (son cercle de signes tourne) : le temple et ses deux gardiens de pierre sont à contre-jour, ourlés d'or.
// Dunes, palmiers, braseros allumés ; on se bat sur une longue terrasse de grès, sa frise de signes gravés devant.
import { CLOUD_A, CLOUD_C, Flagstones, GlyphRing, Platform, RUNES, RGrad, VGrad, W, bump, cloudSprite, curve, f, rng, tufts } from './kit';
import { Brazier, Emblem, flameSprite, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

const sunAt = (c: Ctx) => ({ x: 360, y: c.hz - 196 });
/** La dune la plus proche, derrière le temple : y de sa crête en chaque x (le palmier y est posé). */
const nearDune = (hz: number) => (x: number) => hz - 12 - bump(x, 40, 120, 26) - bump(x, 700, 140, 30);
/** Le temple : au milieu, au fond. */
const T = { x0: 238, x1: 482, cols: 6 };

/** Un palmier à contre-jour : stipe courbe, palmes, liseré clair. Pied en (x, y). */
function Palm({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="6" cy="1" rx="22" ry="4" fill="#3a1a2a" opacity="0.35" />
      <path d="M-4 0 Q-2 -50 14 -96 L19 -94 Q6 -50 5 0 Z" fill="#5a2a3a" />
      <path d="M14 -96 L19 -94 Q8 -52 5 0 H2 Q4 -50 14 -96 Z" fill="#e8905a" opacity="0.5" />
      {[[-60, 26], [-20, 18], [20, 8], [56, 22], [90, 40]].map(([a, l]) => (
        <path d={`M16 -96 Q${f(16 + Math.cos((a! * Math.PI) / 180 - 1.6) * 30)} ${f(-96 - 26)} ${f(16 + Math.sin((a! * Math.PI) / 180) * 60)} ${f(-96 + l!)} Q${f(16 + Math.sin((a! * Math.PI) / 180) * 30)} ${f(-96 - 6)} 16 -92 Z`} fill="#3a1a2a" />
      ))}
    </g>
  );
}

/** Un gardien de pierre à contre-jour, sur son socle : robe, casque à cimier, lance et bouclier. Pied du socle en (x, y). */
function Guardian({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="2" rx="46" ry="6" fill="#3a1a2a" opacity="0.35" />
      {/* le socle */}
      <rect x="-40" y="-40" width="80" height="40" fill="#7a4a4e" /><rect x="-44" y="-46" width="88" height="8" fill="#8a5a5a" /><rect x="-40" y="-40" width="26" height="40" fill="#5a3240" />
      <rect x="-44" y="-46" width="88" height="2.5" fill="#ffc890" />
      {/* la robe, les épaules, le casque */}
      <path d="M-30 -46 L-22 -150 Q0 -162 22 -150 L30 -46 Z" fill="#8a5458" />
      <path d="M-30 -46 L-22 -150 Q-10 -156 -4 -156 L-8 -46 Z" fill="#6a3a46" />
      {/* les épaules (spalières), les bras qui tiennent la lance */}
      <path d="M-34 -138 Q-30 -156 -14 -156 L-12 -132 Q-24 -128 -34 -138 Z M34 -138 Q30 -156 14 -156 L12 -132 Q24 -128 34 -138 Z" fill="#9a6466" />
      <path d="M26 -134 Q36 -110 36 -96 L30 -94 Q28 -110 20 -128 Z" fill="#8a5458" />
      <path d="M-24 -150 Q0 -164 24 -150 L20 -168 Q0 -176 -20 -168 Z" fill="#9a6466" />
      <path d="M-14 -168 Q0 -200 14 -168 Q16 -188 0 -194 Q-16 -188 -14 -168 Z" fill="#8a5458" />
      <path d="M-9 -176 H9 V-170 H-9 Z" fill="#3a1a26" />
      <path d="M0 -192 Q20 -206 30 -190 Q16 -192 4 -182 Z" fill="#c8504a" />
      <path d="M22 -150 L30 -46 H26 L18 -148 Z M20 -168 L24 -150 L20 -152 Z" fill="#ffc890" opacity="0.75" />
      {/* la lance, le bouclier frappé d'un emblème */}
      <path d="M38 -10 V-206" stroke="#5a3a3a" stroke-width="5" /><path d="M38 -206 L44 -226 L38 -246 L32 -226 Z" fill="#c8a080" /><path d="M38 -246 L44 -226 L38 -214 Z" fill="#ffe0b0" opacity="0.7" />
      <ellipse cx="-30" cy="-104" rx="22" ry="32" fill="#7a4a4e" /><ellipse cx="-30" cy="-104" rx="17" ry="26" fill="#8a5a5a" />
      <g transform="translate(-30 -104) scale(1.1)"><Emblem kind={0} color="#ffc890" /></g>
    </g>
  );
}

function sky(c: Ctx) {
  const sun = sunAt(c);
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#26205a'], [0.34, '#7a3466'], [0.6, '#e06a58'], [0.84, '#ffae6c'], [1, '#ffd696']]} />
        <RGrad id="bloom" stops={[[0, '#fff6d0', 0.95], [0.25, '#ffd890', 0.55], [0.6, '#ffb070', 0.18], [1, '#ffb070', 0]]} />
        <RGrad id="sun" stops={[[0, '#fffbe6'], [0.7, '#fff0b8'], [0.92, '#ffd890'], [1, '#ffd890', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <circle cx={sun.x} cy={sun.y} r="330" fill="url(#bloom)" />
      <circle cx={sun.x} cy={sun.y} r="96" fill="url(#sun)" />
    </>
  );
}

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const r = rng(91);
  const top = hz - 168, base = hz - 30;
  const w = (T.x1 - T.x0) / T.cols;
  return (
    <>
      <defs>
        <VGrad id="duneFar" y0={hz - 80} y1={hz} stops={[[0, '#e89a7a'], [1, '#c8706a']]} />
        <VGrad id="sand" y0={hz} y1={bottom} stops={[[0, '#b86a5a'], [0.2, '#d89a70'], [1, '#e8b47e']]} />
        <VGrad id="facade" y0={top - 60} y1={base} stops={[[0, '#9a5a5e'], [1, '#7a4450']]} />
        <VGrad id="terrace" y0={c.p0} y1={c.p1} stops={[[0, '#d8a070'], [1, '#ecc08a']]} />
        <RGrad id="door" stops={[[0, '#ffd890', 0.9], [1, '#ffd890', 0]]} />
      </defs>
      {/* les dunes lointaines et deux obélisques */}
      <path d={curve((x) => hz - 34 - bump(x, 120, 160, 40) - bump(x, 600, 200, 46), -20, 740, hz + 10)} fill="url(#duneFar)" />
      <g fill="#a85a62"><path d={`M76 ${hz - 60} L82 ${hz - 150} L88 ${hz - 60} Z`} /><path d={`M640 ${hz - 70} L647 ${hz - 170} L654 ${hz - 70} Z`} /></g>
      <path d={curve(nearDune(hz), -20, 740, hz + 10)} fill="#c87a6a" />
      {/* le temple, à contre-jour : marches, colonnes, entablement, fronton et son disque solaire */}
      <rect x={T.x0 - 40} y={base} width={T.x1 - T.x0 + 80} height="14" fill="#6a3a46" /><rect x={T.x0 - 26} y={base - 12} width={T.x1 - T.x0 + 52} height="12" fill="#7a4450" /><rect x={T.x0 - 14} y={base - 22} width={T.x1 - T.x0 + 28} height="10" fill="#8a5058" />
      <rect x={T.x0 - 40} y={base} width={T.x1 - T.x0 + 80} height="2" fill="#ffc890" opacity="0.8" /><rect x={T.x0 - 26} y={base - 12} width={T.x1 - T.x0 + 52} height="2" fill="#ffc890" opacity="0.8" />
      <rect x={T.x0} y={top + 26} width={T.x1 - T.x0} height={base - 22 - top - 26} fill="#4a2232" />
      <ellipse cx={(T.x0 + T.x1) / 2} cy={base - 50} rx="40" ry="60" fill="url(#door)" />
      {Array.from({ length: T.cols }, (_, i) => {
        const x = T.x0 + w * (i + 0.5);
        return <g><rect x={x - 11} y={top + 30} width="22" height={base - 22 - top - 30} fill="url(#facade)" /><rect x={x + 7} y={top + 30} width="4" height={base - 22 - top - 30} fill="#ffc890" opacity="0.55" /><rect x={x - 15} y={top + 24} width="30" height="8" fill="#9a5a5e" /><rect x={x - 15} y={base - 28} width="30" height="6" fill="#8a5058" /></g>;
      })}
      <rect x={T.x0 - 18} y={top} width={T.x1 - T.x0 + 36} height="26" fill="#8a5058" /><rect x={T.x0 - 18} y={top} width={T.x1 - T.x0 + 36} height="3" fill="#ffd8a0" />
      <path d={`M${T.x0 - 24} ${top} L${(T.x0 + T.x1) / 2} ${top - 64} L${T.x1 + 24} ${top} Z`} fill="#7a4450" />
      <path d={`M${T.x0 - 24} ${top} L${(T.x0 + T.x1) / 2} ${top - 64} L${T.x1 + 24} ${top}`} fill="none" stroke="#ffd8a0" stroke-width="3" />
      <g transform={`translate(${(T.x0 + T.x1) / 2} ${top - 24}) scale(1.3)`}><Emblem kind={0} color="#ffc890" /></g>
      {/* les deux gardiens, de part et d'autre */}
      <Guardian x={112} y={hz - 2} s={1} /><Guardian x={608} y={hz - 2} s={1} flip />
      <Palm x={20} y={hz + 6} s={1.3} /><Palm x={700} y={hz + 8} s={1.4} flip /><Palm x={196} y={nearDune(hz)(196) + 3} s={0.8} flip />
      {/* le sable devant le temple, les braseros au pied des marches */}
      <rect y={hz} width={W} height={bottom - hz} fill="url(#sand)" />
      <path d={tufts(5, p0 - 2, 3, 40, 1.4)} fill="#a8604a" opacity="0.6" />
      <Brazier x={206} y={p0 - 4} s={1.2} /><Brazier x={514} y={p0 - 4} s={1.2} />
      {/* la terrasse de grès, d'un bord à l'autre ; sa frise de signes gravés */}
      <Platform y0={p0} y1={p1} th={34} top="url(#terrace)" face="#b8784e" faceDark="#9a603e" lip="#ffe6b8" back="#5a2a2a"
        faceArt={<>
          <rect x="-20" y={p1 + 6} width={W + 40} height="2" fill="#7a4a30" opacity="0.6" /><rect x="-20" y={p1 + 26} width={W + 40} height="2" fill="#7a4a30" opacity="0.6" />
          {Array.from({ length: 18 }, (_, i) => <path d={RUNES[(i * 5) % RUNES.length]} fill="none" stroke="#6a3a26" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(20 + i * 40)} ${p1 + 17}) scale(1.4)`} />)}
        </>}>
        <Flagstones seed={18} y0={p0} y1={p1} rows={4} line="#b88050" light="#fff0c8" lightOpacity={0.22} />
        {Array.from({ length: 10 }, () => <ellipse cx={r() * W} cy={p0 + 10 + r() * (p1 - p0 - 20)} rx={14 + r() * 30} ry="3" fill="#f6d8a0" opacity="0.6" />)}
      </Platform>
      {/* sous la terrasse : le sable, des herbes sèches */}
      <path d={tufts(7, p1 + 60, 4, 60, 1.6)} fill="#b8805a" />
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      {/* des tambours de colonne couchés dans le sable, une jarre */}
      <g transform={`translate(30 ${b - 4})`}>
        <ellipse cx="10" cy="2" rx="48" ry="7" fill="#7a4a3a" opacity="0.35" />
        <rect x="-30" y="-34" width="60" height="34" rx="4" fill="#d8a878" /><rect x="-30" y="-34" width="60" height="10" rx="4" fill="#f0c890" />
        <ellipse cx="30" cy="-17" rx="12" ry="17" fill="#e8b888" /><ellipse cx="30" cy="-17" rx="7" ry="11" fill="#c89868" />
      </g>
      <g transform={`translate(676 ${b - 2})`}>
        <ellipse cx="0" cy="2" rx="30" ry="6" fill="#7a4a3a" opacity="0.35" />
        <path d="M-16 0 Q-26 -20 -14 -38 Q-10 -44 -10 -50 H10 Q10 -44 14 -38 Q26 -20 16 0 Z" fill="#b8603e" />
        <path d="M4 -50 H10 Q10 -44 14 -38 Q26 -20 16 0 H8 Q18 -20 6 -40 Z" fill="#d88050" />
        <rect x="-12" y="-54" width="24" height="5" rx="2" fill="#8a4a2e" />
      </g>
      <path d={`M90 ${b + 10} Q140 ${b - 18} 220 ${b - 6} Q260 ${b} 280 ${b + 10} Z M500 ${b + 10} Q560 ${b - 20} 640 ${b - 10} V${b + 10} Z`} fill="#eec08a" />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const sun = sunAt(c);
  const fl = flameSprite(30, 46);
  return [
    { id: 'cloudA', ...cloudSprite(CLOUD_C, 126, 1.8, { top: '#ffd8c8', mid: '#f0a8a8', low: '#b8708a', light: '#ffe8d8' }), at: [[120, Math.max(180, c.hz * 0.22)]], depth: -28, anim: { k: 'drift', speed: 4, from: -300, to: 1020 }, alpha: 0.9 },
    { id: 'cloudB', ...cloudSprite(CLOUD_A, 90, 1.3, { top: '#ffd8c8', mid: '#f0a8a8', low: '#b8708a', light: '#ffe8d8' }), at: [[560, Math.max(230, c.hz * 0.34)]], depth: -28, anim: { k: 'drift', speed: 6, from: -300, to: 1020 }, alpha: 0.85 },
    { id: 'ring', w: 300, h: 300, draw: () => <g transform="translate(150 150)"><GlyphRing r={124} color="#fff4d0" glyph={1.3} /></g>, at: [[sun.x, sun.y]], depth: -29, anim: { k: 'spin', period: 120 }, alpha: 0.55 },
    { id: 'bloom', ...glowSprite(420, '#ffe0a0', 0.5), at: [[sun.x, sun.y]], depth: -29, anim: { k: 'pulse', min: 0.6, period: 7 }, add: true },
    { id: 'flame', ...fl, origin: [0.5, 1], at: [[206, c.p0 - 4 - 34 * 1.2], [514, c.p0 - 4 - 34 * 1.2]], depth: -12, anim: { k: 'flicker', min: 0.75, period: 1.1 }, scale: [1.2, 1.2] },
    { id: 'fglow', ...glowSprite(150, '#ffb050', 0.6), at: [[206, c.p0 - 60], [514, c.p0 - 60]], depth: -13, anim: { k: 'flicker', min: 0.6, period: 1.6 }, add: true },
    // deux bannières pendues au fronton, qui ondulent
    {
      id: 'banner', w: 44, h: 120, origin: [0.5, 0], at: [[T.x0 + 8, c.hz - 168 + 26], [T.x1 - 8, c.hz - 168 + 26]], depth: -18, anim: { k: 'sway', deg: 2.5, period: 3.2 },
      draw: () => <g><path d="M2 0 H42 V100 L22 118 L2 100 Z" fill="#b8323a" /><path d="M2 0 H14 V108 L2 100 Z" fill="#7a1a26" opacity="0.6" /><path d="M6 6 H38 V96 L22 110 L6 96 Z" fill="none" stroke="#ffc890" stroke-width="2" /><g transform="translate(22 50) scale(0.9)"><Emblem kind={2} color="#ffc890" /></g></g>,
    },
  ];
}

export const TEMPLE: Scene = {
  base: 0xd89a70,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'sand', size: 8, area: [-40, c.hz - 40, -10, c.bottom], depth: -11, vx: [40, 70], vy: [-6, 4], life: [9000, 13000], count: 10, scale: [0.5, 1], alpha: [0.2, 0.6],
      draw: () => <circle cx="4" cy="4" r="3" fill="#ffe8c0" />,
    },
    {
      id: 'spark', size: 10, area: [196, c.p0 - 90, 216, c.p0 - 80], depth: -12, vx: [-8, 8], vy: [-40, -24], life: [1200, 2000], count: 4, scale: [0.4, 0.9], alpha: [0.3, 1], add: true,
      draw: () => <><defs><RGrad id="e" stops={[[0, '#fff0b0'], [0.4, '#ffa040', 0.9], [1, '#ff6020', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#e)" /></>,
    },
    {
      id: 'spark2', size: 10, area: [504, c.p0 - 90, 524, c.p0 - 80], depth: -12, vx: [-8, 8], vy: [-40, -24], life: [1200, 2000], count: 4, scale: [0.4, 0.9], alpha: [0.3, 1], add: true,
      draw: () => <><defs><RGrad id="e" stops={[[0, '#fff0b0'], [0.4, '#ffa040', 0.9], [1, '#ff6020', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#e)" /></>,
    },
  ],
};
