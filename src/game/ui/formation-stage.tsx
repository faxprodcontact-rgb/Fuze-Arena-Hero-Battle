// Le décor du choix de la section : la salle des héros, vue de près. Au fond le mur, la grande verrière au ciel du soir,
// deux niches et leurs bannières, quatre colonnes ; au sol, deux braseros et la grande estrade ronde à deux marches,
// sertie d'or, ceinte d'une frise de signes gravés qui tourne lentement. La formation y est tracée : deux postes à
// l'arrière, le chef au centre, deux à l'avant, et trois chevrons du côté des ennemis.
// Chaque poste a sa dalle (`Plate`) : pierre claire cerclée de la couleur de l'élément du héros, or pour le chef.
import type { Slot } from '../../core/battle/types';
import './anim.css';
import { GLYPHS } from './backdrop-adventure';
import { spark } from './portal';

export const STAGE_W = 420, STAGE_H = 360;
/** Le pied du mur. */
const FL = 92;
/** Le dessus de l'estrade. */
const D = { cx: 210, cy: 228, rx: 198, ry: 106, step: 8 };
/** Le point où chaque héros pose les pieds (le centre de sa dalle). */
export const STAGE_POS: Record<Slot, [number, number]> = { 3: [100, 180], 4: [100, 292], 2: [210, 236], 0: [320, 180], 1: [320, 292] };

const f = (n: number) => n.toFixed(1);

function Column({ x, w, side }: { x: number; w: number; side: number }) {
  const h = w / 2;
  return (
    <g transform={`translate(${x} 0) scale(${side} 1)`}>
      <rect x={-h} y="-10" width={w} height={FL + 12} fill="url(#fs-col)" />
      <path d={`M${-h} 46 H${h}`} stroke="#141a40" stroke-width="1" opacity="0.4" />
      <path d={`M${-h - 4} 6 H${h + 4} L${h + 1.500} 13 H${-h - 1.500} Z`} fill="#6f7fc0" /><path d={`M${-h - 4} 6 H${h + 4} V8 H${-h - 4} Z`} fill="#c8d2f5" /><path d={`M${-h - 1.500} 13 H${h + 1.500} L${h} 17 H${-h} Z`} fill="#3a4888" />
      <path d={`M${-h - 2} ${FL - 8} H${h + 2} L${h + 5} ${FL + 3} H${-h - 5} Z`} fill="#56669e" /><path d={`M${-h - 2} ${FL - 8} H${h + 2} V${FL - 6} H${-h - 2} Z`} fill="#aab6e6" /><path d={`M${-h - 5} ${FL + 3} H${h + 5} V${FL + 7} H${-h - 5} Z`} fill="#2c3874" />
    </g>
  );
}

function Banner({ x, y, len, w, glyph }: { x: number; y: number; len: number; w: number; glyph: number }) {
  const h = w / 2;
  return (
    <g class="bd-banner" style={{ transformOrigin: `${x}px ${y}px`, animationDelay: `${-(x % 5)}s` }}>
      <path d={`M${x - h - 3} ${y} H${x + h + 3}`} stroke="#2f1b0c" stroke-width="3.600" stroke-linecap="round" /><path d={`M${x - h - 3} ${y - 0.700} H${x + h + 3}`} stroke="#e3b548" stroke-width="1.400" stroke-linecap="round" />
      <path d={`M${x - h} ${y} H${x + h} V${y + len} L${x} ${y + len - w * 0.42} L${x - h} ${y + len} Z`} fill="url(#fs-cloth)" />
      <path d={`M${x - h} ${y} H${x - h * 0.2} V${y + len - w * 0.34} L${x - h} ${y + len} Z`} fill="#5e1418" opacity="0.45" />
      <path d={`M${x - h + 2.600} ${y + 1} V${y + len - 6} M${x + h - 2.600} ${y + 1} V${y + len - 6}`} stroke="#ffd45c" stroke-width="1.200" opacity="0.9" />
      <circle cx={x} cy={y + len * 0.42} r={w * 0.3} fill="#5e1418" stroke="#ffd45c" stroke-width="1.200" />
      <path d={GLYPHS[glyph]} transform={`translate(${x} ${f(y + len * 0.42)}) scale(${f(w / 17)})`} fill="none" stroke="#ffe9a0" stroke-width="1.500" stroke-linecap="round" stroke-linejoin="round" />
    </g>
  );
}

function Brazier({ x, y }: { x: number; y: number }) {
  const drop = (k: number) => `M0 0 C${f(-9 * k)} ${f(-3 * k)} ${f(-8 * k)} ${f(-14 * k)} ${f(-2 * k)} ${f(-25 * k)} C0 ${f(-18 * k)} ${f(7 * k)} ${f(-16 * k)} ${f(8 * k)} ${f(-7 * k)} C${f(8 * k)} ${f(-2 * k)} ${f(4 * k)} 0 0 0 Z`;
  return (
    <g transform={`translate(${x} ${y})`}>
      <ellipse cx="0" cy="1" rx="16" ry="4" fill="#070a1c" opacity="0.6" />
      <ellipse class="an-glow" cx="0" cy="4" rx="46" ry="12" fill="url(#fs-fire)" />
      <path d="M-10 0 L-3 -28 M10 0 L3 -28 M0 0 V-28" stroke="#2f1b0c" stroke-width="4.200" stroke-linecap="round" /><path d="M-10 0 L-3 -28 M10 0 L3 -28 M0 0 V-28" stroke="url(#fs-bronze)" stroke-width="2.200" stroke-linecap="round" />
      <path d="M-7.500 -15 H7.500" stroke="#2f1b0c" stroke-width="3.400" stroke-linecap="round" /><path d="M-7.500 -15 H7.500" stroke="#c98a3a" stroke-width="1.500" stroke-linecap="round" />
      <path d="M-14 -39 Q-14 -26 0 -26 Q14 -26 14 -39 Z" fill="#2f1b0c" /><path d="M-12 -38 Q-12 -28 0 -28 Q12 -28 12 -38 Z" fill="url(#fs-bronze)" />
      <ellipse cx="0" cy="-39" rx="14" ry="3.400" fill="#2f1b0c" /><ellipse cx="0" cy="-39" rx="11.500" ry="2.200" fill="#ff8a2a" /><ellipse cx="0" cy="-39.300" rx="7.500" ry="1.300" fill="#ffe08a" />
      <g transform="translate(0 -38)">
        <circle class="an-glow" cx="0" cy="-10" r="34" fill="url(#fs-fire)" />
        <path class="ad-flame" d={drop(1.050)} fill="#ff6a1a" /><path class="ad-flame" style={{ animationDelay: '-0.2s', animationDuration: '0.42s' }} d={drop(0.740)} fill="#ffb02a" /><path class="ad-flame" style={{ animationDelay: '-0.35s', animationDuration: '0.36s' }} d={drop(0.420)} fill="#fff3b0" />
        {[[-5, 0], [4, -1.300], [0, -2.400]].map(([dx, d]) => <circle class="ts-ember" style={{ animationDelay: `${d}s` }} cx={dx} cy="-22" r="1.200" fill="#ffd24a" />)}
      </g>
    </g>
  );
}

export function FormationStage() {
  const { cx, cy, rx, ry, step } = D;
  const rx2 = rx + 16, ry2 = ry + 8, cy2 = cy + step;
  const [a, b, c, d, e] = [STAGE_POS[3], STAGE_POS[4], STAGE_POS[2], STAGE_POS[0], STAGE_POS[1]];
  const lines = `M${a[0]} ${a[1]} L${c[0]} ${c[1]} L${d[0]} ${d[1]} M${b[0]} ${b[1]} L${c[0]} ${c[1]} L${e[0]} ${e[1]} M${a[0]} ${a[1]} L${b[0]} ${b[1]} M${d[0]} ${d[1]} L${e[0]} ${e[1]}`;
  return (
    <svg class="field-bg" viewBox={`0 0 ${STAGE_W} ${STAGE_H}`} preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <linearGradient id="fs-wall" x1="0" y1="0" x2="0" y2={FL} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#10153a" /><stop offset="0.5" stop-color="#232e6a" /><stop offset="1" stop-color="#3d4c96" /></linearGradient>
        <linearGradient id="fs-floor" x1="0" y1={FL} x2="0" y2={STAGE_H} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#5565b2" /><stop offset="0.14" stop-color="#34407e" /><stop offset="0.55" stop-color="#1f2756" /><stop offset="1" stop-color="#141938" /></linearGradient>
        <linearGradient id="fs-glass" x1="0" y1="-44" x2="0" y2={FL} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#4a5ab8" /><stop offset="0.42" stop-color="#9a78c8" /><stop offset="0.68" stop-color="#f09a8a" /><stop offset="0.88" stop-color="#ffd088" /><stop offset="1" stop-color="#ffe9a8" /></linearGradient>
        <radialGradient id="fs-sun"><stop offset="0" stop-color="#fffbe6" stop-opacity="0.95" /><stop offset="0.35" stop-color="#ffe08a" stop-opacity="0.6" /><stop offset="1" stop-color="#ffb86a" stop-opacity="0" /></radialGradient>
        <linearGradient id="fs-col" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#161c46" /><stop offset="0.5" stop-color="#34407e" /><stop offset="0.86" stop-color="#7f8fd0" /><stop offset="1" stop-color="#ffe0a8" /></linearGradient>
        <linearGradient id="fs-cloth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2574c" /><stop offset="0.6" stop-color="#b8343a" /><stop offset="1" stop-color="#8a2028" /></linearGradient>
        <linearGradient id="fs-bronze" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd98a" /><stop offset="0.45" stop-color="#c98a3a" /><stop offset="1" stop-color="#6b4016" /></linearGradient>
        <radialGradient id="fs-fire"><stop offset="0" stop-color="#ffb02a" stop-opacity="0.7" /><stop offset="0.5" stop-color="#ff7a1a" stop-opacity="0.2" /><stop offset="1" stop-color="#ff7a1a" stop-opacity="0" /></radialGradient>
        <radialGradient id="fs-top" cx={cx} cy={cy - 30} r="1" gradientUnits="userSpaceOnUse" gradientTransform={`translate(${cx} ${cy - 30}) scale(${rx} ${ry * 1.300}) translate(${-cx} ${-(cy - 30)})`}><stop offset="0" stop-color="#f4f5ff" /><stop offset="0.5" stop-color="#c3caf0" /><stop offset="1" stop-color="#8a94d0" /></radialGradient>
        <linearGradient id="fs-riser" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a336e" /><stop offset="0.5" stop-color="#6672ba" /><stop offset="1" stop-color="#2a336e" /></linearGradient>
        <linearGradient id="fs-seam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="0.5" stop-color="#fff" stop-opacity="0.95" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></linearGradient>
        <radialGradient id="fs-pool" cx="210" cy={FL + 18} r="1" gradientUnits="userSpaceOnUse" gradientTransform={`translate(210 ${FL + 18}) scale(230 70) translate(-210 ${-(FL + 18)})`}><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.65" /><stop offset="0.6" stop-color="#ffb86a" stop-opacity="0.16" /><stop offset="1" stop-color="#ffb86a" stop-opacity="0" /></radialGradient>
        <radialGradient id="fs-warm" cx="210" cy="150" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(210 150) scale(190 90) translate(-210 -150)"><stop offset="0" stop-color="#ffe9b0" stop-opacity="0.55" /><stop offset="1" stop-color="#ffe9b0" stop-opacity="0" /></radialGradient>
        <linearGradient id="fs-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.5" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
        <clipPath id="fs-win"><path d="M128 92 V34 Q128 -20 210 -44 Q292 -20 292 34 V92 Z" /></clipPath>
      </defs>

      {/* ---- le mur : les niches, la grande verrière et son lointain ---- */}
      <rect y="-10" width={STAGE_W} height={FL + 10} fill="url(#fs-wall)" />
      {[60, 360].map((x) => <path d={`M${x - 24} ${FL} V34 Q${x - 24} 6 ${x} -4 Q${x + 24} 6 ${x + 24} 34 V${FL} Z`} fill="#161d4c" stroke="#3a4888" stroke-width="1.500" />)}
      <g clip-path="url(#fs-win)">
        <rect x="126" y="-46" width="168" height="140" fill="url(#fs-glass)" />
        <circle cx="210" cy="76" r="52" fill="url(#fs-sun)" /><circle cx="210" cy="76" r="12" fill="#fffbe6" />
        <path d="M126 92 V70 L142 58 L156 68 L172 54 L188 66 L204 60 L220 70 L236 56 L252 68 L268 60 L282 70 L294 62 V92 Z" fill="#a8689a" opacity="0.8" />
        <path d="M126 92 V80 L146 72 L166 82 L186 74 L206 84 L228 76 L250 84 L272 74 L294 82 V92 Z" fill="#6a4a8e" />
        <path d="M246 84 V62 H250 V58 H253 V62 H257 V58 H260 V62 H264 V84 Z M264 84 V72 H275 V84 Z M236 84 V74 H246 V84 Z M253 58 L256.500 49 L260 58 Z" fill="#553a7c" />
      </g>
      <g fill="none" stroke="#1a2254" stroke-linecap="round"><path d="M169 92 V40 Q169 22 189.500 14 Q210 22 210 40 V92 M210 40 Q210 22 230.500 14 Q251 22 251 40 V92 M169 40 Q169 30 148.500 22 M251 40 Q251 30 271.500 22" stroke-width="2.800" /><path d="M189.500 14 V-14 M230.500 14 V-14" stroke-width="2.200" /></g>
      <path d="M128 92 V34 Q128 -20 210 -44 Q292 -20 292 34 V92" fill="none" stroke="#141a40" stroke-width="6" /><path d="M131 92 V34 Q131 -17 210 -40 Q289 -17 289 34 V92" fill="none" stroke="#7f8fd0" stroke-width="1.300" opacity="0.8" />
      {/* la plinthe */}
      <rect y={FL - 4} width={STAGE_W} height="4" fill="#56669e" /><rect y={FL - 4} width={STAGE_W} height="1.200" fill="#aab6e6" opacity="0.85" />

      {/* ---- le sol : dalles polies, la lumière de la verrière s'y couche ---- */}
      <rect y={FL} width={STAGE_W} height={STAGE_H - FL} fill="url(#fs-floor)" />
      <rect y={FL} width={STAGE_W} height="110" fill="url(#fs-pool)" />
      <circle class="bd-sun" cx="210" cy="70" r="120" fill="url(#fs-sun)" opacity="0.35" />

      {/* ---- les colonnes, les bannières dans leurs niches ---- */}
      <Column x={108} w={16} side={1} /><Column x={312} w={16} side={-1} /><Column x={6} w={14} side={1} /><Column x={414} w={14} side={-1} />
      <Banner x={60} y={14} len={54} w={26} glyph={1} /><Banner x={360} y={14} len={54} w={26} glyph={4} />

      {/* ---- l'estrade : deux marches, le dessus de pierre claire ---- */}
      <ellipse cx={cx} cy={cy2 + step + 5} rx={rx2 + 10} ry={ry2 + 4} fill="#070a1c" opacity="0.55" />
      <path d={`M${cx - rx2} ${cy2} V${cy2 + step} A${rx2} ${ry2} 0 0 0 ${cx + rx2} ${cy2 + step} V${cy2} Z`} fill="url(#fs-riser)" />
      <ellipse cx={cx} cy={cy2} rx={rx2} ry={ry2} fill="#8d97d2" />
      <path d={`M${cx - rx2} ${cy2 + 1} A${rx2} ${ry2} 0 0 0 ${cx + rx2} ${cy2 + 1}`} fill="none" stroke="url(#fs-seam)" stroke-width="1.600" />
      <path d={`M${cx - rx} ${cy} V${cy + step} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + step} V${cy} Z`} fill="url(#fs-riser)" />
      <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="url(#fs-top)" />
      <path d={`M${cx - rx} ${cy + 1} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + 1}`} fill="none" stroke="url(#fs-seam)" stroke-width="2" />
      {/* le filet d'or, puis la frise : une bande plus sombre où des signes gravés tournent lentement */}
      <ellipse cx={cx} cy={cy} rx={rx - 7} ry={ry - 4} fill="none" stroke="#c9952a" stroke-width="2.200" /><ellipse cx={cx} cy={cy} rx={rx - 10.500} ry={ry - 6} fill="none" stroke="#fff6dc" stroke-width="0.800" opacity="0.9" />
      <g transform={`translate(${cx} ${cy}) scale(1 ${(ry / rx).toFixed(3)})`}>
        <circle r={rx - 24} fill="none" stroke="#7c86c4" stroke-width="15" opacity="0.4" />
        <circle r={rx - 16} fill="none" stroke="#6a74b8" stroke-width="1" /><circle r={rx - 32} fill="none" stroke="#6a74b8" stroke-width="1" />
        <g class="hh-ring" fill="none" stroke="#4f5aa4">
          {Array.from({ length: 30 }, (_, i) => { const t = (i / 30) * Math.PI * 2, r = rx - 24; return <path d={GLYPHS[i % GLYPHS.length]} stroke-width="1.500" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(Math.cos(t) * r)} ${f(Math.sin(t) * r)}) rotate(${((t * 180) / Math.PI + 90).toFixed(0)}) scale(1.500)`} />; })}
        </g>
      </g>
      <rect y={FL} width={STAGE_W} height="200" fill="url(#fs-warm)" />
      {/* le tracé de la formation : une rainure sombre, un filet d'or dedans, un clou d'or aux croisements */}
      <path d={lines} fill="none" stroke="#6a74b8" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0.75" />
      <path d={lines} fill="none" stroke="#d9a63e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      {[[a, c], [b, c], [c, d], [c, e]].map(([p, q]) => { const x = (p![0] + q![0]) / 2, y = (p![1] + q![1]) / 2; return <g><path d={`M${x} ${y - 5} L${x + 5} ${y} L${x} ${y + 5} L${x - 5} ${y} Z`} fill="#2f1b0c" /><path d={`M${x} ${y - 3.400} L${x + 3.400} ${y} L${x} ${y + 3.400} L${x - 3.400} ${y} Z`} fill="url(#fs-gold)" /></g>; })}
      {/* vers l'avant : trois chevrons d'or s'allument l'un après l'autre, du côté des ennemis */}
      {[0, 1, 2].map((i) => (
        <g class="fd-chevron" style={{ animationDelay: `${i * 0.25}s` }}>
          <path d={`M${366 + i * 10} ${cy - 3} L${376 + i * 10} ${cy + 10} L${366 + i * 10} ${cy + 23}`} fill="none" stroke="#2f1b0c" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />
          <path d={`M${366 + i * 10} ${cy - 3} L${376 + i * 10} ${cy + 10} L${366 + i * 10} ${cy + 23}`} fill="none" stroke="url(#fs-gold)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
        </g>
      ))}

      {/* ---- les braseros, de chaque côté, et la poussière qui danse dans la lumière ---- */}
      <Brazier x={30} y={134} /><Brazier x={390} y={134} />
      {[[150, 150, 0], [196, 120, -2], [262, 140, -4], [232, 176, -6], [176, 190, -3], [286, 118, -7.500]].map(([x, y, dl], i) => <circle class="bd-mote" style={{ animationDelay: `${dl}s`, animationDuration: `${8 + (i % 3) * 2}s` }} cx={x} cy={y} r={i % 2 ? 1.300 : 0.900} fill="#fff6c8" />)}
      {[[150, 60, 3], [274, 50, 2.600]].map(([x, y, k], i) => <path class={`an-twinkle ${i ? 'an-late' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
    </svg>
  );
}

/**
 * La dalle d'un poste : un disque de pierre claire, cerclé de la couleur de l'élément du héros qui s'y tient (`color`).
 * Celle du chef est en or, avec son cercle de signes qui tourne. Vide, elle appelle un héros (pointillés et « + »).
 */
export function Plate({ leader, empty, color }: { leader: boolean; empty: boolean; color?: string }) {
  const ring = empty ? (leader ? '#b8720a' : '#6a74b8') : (color ?? '#8d97d2');
  return (
    <svg class="field-plate" viewBox="0 0 120 52" aria-hidden="true">
      <ellipse cx="60" cy="32" rx="57" ry="19" fill="#070a1c" opacity="0.4" />
      <path d="M8 24 V30 A52 17 0 0 0 112 30 V24 Z" fill={leader ? '#8a5a12' : '#3a4486'} />
      <path d="M8 29 A52 17 0 0 0 112 29" fill="none" stroke={leader ? '#ffd45c' : '#8d97d2'} stroke-width="1" opacity="0.7" />
      <ellipse cx="60" cy="24" rx="52" ry="17" fill={leader ? '#fff0c0' : '#e2e6fb'} />
      <ellipse cx="60" cy="24" rx="52" ry="17" fill="none" stroke={leader ? '#b8720a' : '#5e6ab0'} stroke-width="1.600" />
      {!empty && <ellipse cx="60" cy="24" rx="44" ry="13" fill={ring} opacity="0.3" />}
      <ellipse cx="60" cy="24" rx="45" ry="13.500" fill="none" stroke={leader && !empty ? '#e0a020' : ring} stroke-width="2.400" stroke-dasharray={empty ? '5 5' : undefined} />
      {leader && (
        <g transform="translate(60 24) scale(1 0.3)">
          <g class="fd-ring" fill="none" stroke="#d08a10">
            {Array.from({ length: 10 }, (_, i) => <path d={GLYPHS[i % GLYPHS.length]} stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round" transform={`rotate(${i * 36}) translate(0 -34) scale(1.700)`} />)}
          </g>
        </g>
      )}
      {empty && <path class="fd-plus" d="M60 16 V32 M46 24 H74" stroke={ring} stroke-width="3.600" stroke-linecap="round" />}
    </svg>
  );
}
