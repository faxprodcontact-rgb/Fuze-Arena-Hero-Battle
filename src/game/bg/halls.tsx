// Trois décors bâtis.
//   L'armurerie (donjon des équipements) : une salle de pierre, son râtelier d'armes, ses boucliers, ses bannières, sa forge
//   qui rougeoie ; on se bat sur une estrade de dalles cerclée de bronze.
//   L'antre (boss du jour, boss de guilde) : une salle volcanique, sa grande herse sous un arc à cornes, deux chutes de lave,
//   des braseros sur des piliers d'obsidienne ; on se bat sur une dalle noire au-dessus d'un fleuve de lave.
//   L'arène : un amphithéâtre sous le ciel, ses arcades, ses bannières et ses fanions ; on se bat sur la piste de sable.
import { CLOUD_A, CLOUD_B, CLOUD_C, Cloud, CloudGrad, Flagstones, Pebbles, Platform, RUNES, RGrad, VGrad, W, cloudSprite, f, rng } from './kit';
import { Brazier, Emblem, Masonry, Torch, flameSprite, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

const bannerSprite = (color: string, dark: string, emblem: number, h = 120) => ({
  w: 52, h: h + 20,
  draw: () => (
    <g>
      <rect x="0" y="0" width="52" height="7" rx="3" fill="#5a3a20" />
      <path d={`M6 5 H46 V${h} L26 ${h + 16} L6 ${h} Z`} fill={color} />
      <path d={`M6 5 H18 V${h + 6} L6 ${h} Z`} fill={dark} opacity="0.55" />
      <path d={`M10 10 H42 V${h - 4} L26 ${h + 10} L10 ${h - 4} Z`} fill="none" stroke="#ffd45c" stroke-width="2" />
      <g transform={`translate(26 ${h * 0.45})`}><Emblem kind={emblem} color="#ffd45c" /></g>
    </g>
  ),
});

// ---------------------------------------------------------------- l'armurerie

/** Le râtelier : un cadre de bois, des épées, des lances et une hache debout. Pied en (x, y). */
function Rack({ x, y }: { x: number; y: number }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <ellipse cx="0" cy="2" rx="120" ry="8" fill="#000" opacity="0.3" />
      <rect x="-110" y="-16" width="220" height="12" fill="#7a4e2c" /><rect x="-110" y="-16" width="220" height="3" fill="#b07a48" />
      <rect x="-110" y="-120" width="220" height="10" fill="#7a4e2c" /><rect x="-110" y="-120" width="220" height="3" fill="#b07a48" />
      <rect x="-114" y="-130" width="10" height="130" fill="#6a4226" /><rect x="104" y="-130" width="10" height="130" fill="#8a5a34" />
      {[-80, -50, 50, 80].map((sx, i) => (
        <g><path d={`M${sx} -10 V${i % 2 ? -150 : -140}`} stroke="#d8dee8" stroke-width="7" /><path d={`M${sx + 1} -10 V${i % 2 ? -150 : -140}`} stroke="#ffffff" stroke-width="2" /><path d={`M${sx - 3.5} ${i % 2 ? -150 : -140} L${sx} ${i % 2 ? -162 : -152} L${sx + 3.5} ${i % 2 ? -150 : -140} Z`} fill="#d8dee8" /><rect x={sx - 10} y="-38" width="20" height="5" rx="2" fill="#c8a040" /><rect x={sx - 3} y="-33" width="6" height="20" fill="#5a3a24" /></g>
      ))}
      {[-18, 18].map((lx) => <g><path d={`M${lx} -4 V-200`} stroke="#7a5236" stroke-width="5" /><path d={`M${lx} -200 L${lx + 7} -214 L${lx} -238 L${lx - 7} -214 Z`} fill="#c8ced8" /></g>)}
      <g transform="translate(0 -60)"><path d="M0 50 V-70" stroke="#6a4226" stroke-width="6" /><path d="M0 -66 Q30 -80 32 -50 Q30 -30 0 -36 Z" fill="#b8c0cc" /><path d="M0 -66 Q30 -80 32 -50 L22 -52 Q20 -66 0 -60 Z" fill="#e8eef6" /></g>
    </g>
  );
}

/** Un bouclier rond accroché au mur, frappé d'un emblème. */
function Shield({ x, y, r, color, emblem }: { x: number; y: number; r: number; color: string; emblem: number }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <circle r={r + 3} fill="#000" opacity="0.25" transform="translate(-3 4)" />
      <circle r={r} fill="#8a8e98" /><circle r={r - 4} fill={color} />
      <path d={`M${-r + 4} 0 A${r - 4} ${r - 4} 0 0 1 ${r - 4} 0 Z`} fill="#fff" opacity="0.12" />
      <g transform={`scale(${(r / 22).toFixed(2)})`}><Emblem kind={emblem} color="#ffd45c" /></g>
      <circle r="4" fill="#d8c070" />
    </g>
  );
}

/** Le haut d'une salle : le mur monte jusqu'en haut de l'écran et se perd dans le noir (un fondu, jamais un bord droit). */
function Gloom({ id, y1, color }: { id: string; y1: number; color: string }) {
  return (
    <>
      <defs><VGrad id={id} y0={-20} y1={y1} stops={[[0, color], [0.45, color, 0.82], [1, color, 0]]} /></defs>
      <rect x="-20" y="-20" width={W + 40} height={y1 + 20} fill={`url(#${id})`} />
    </>
  );
}

/** La hotte de la forge, à droite : son conduit monte jusqu'à la poutre (il ne s'arrête pas au milieu du mur). */
const FORGE_X = 650;

function armorySky(c: Ctx) {
  const vault = Math.max(30, c.hz - 560);
  return (
    <>
      <defs><VGrad id="wall" y0={0} y1={c.hz} stops={[[0, '#14100e'], [0.4, '#2a221e'], [1, '#3e342c']]} /></defs>
      <rect width={W} height={c.hz + 60} fill="url(#wall)" />
      <Masonry seed={3} y0={-20} y1={c.hz + 40} color="#5a4c42" light="#8a7a6a" line="#2a221e" />
      <Gloom id="gloom" y1={vault + 120} color="#14100e" />
      {/* le conduit de la forge (la hotte, posée par-dessus, en cache le pied) */}
      <rect x={FORGE_X - 30} y={vault + 30} width="60" height={c.p0 - 150 - vault - 26} fill="#4a3e36" />
      <rect x={FORGE_X - 30} y={vault + 30} width="16" height={c.p0 - 150 - vault - 26} fill="#3a302a" />
      <rect x={FORGE_X + 20} y={vault + 30} width="10" height={c.p0 - 150 - vault - 26} fill="#5a4c42" />
      {[0.3, 0.62].map((k) => <rect x={FORGE_X - 34} y={vault + 30 + (c.p0 - 150 - vault - 26) * k} width="68" height="8" fill="#2e2622" />)}
      {/* les poutres de la voûte */}
      {[60, 360, 660].map((x) => <g><rect x={x - 14} y={-10} width="28" height={vault + 40} fill="#4a3020" /><rect x={x + 6} y={-10} width="8" height={vault + 40} fill="#6a4630" /></g>)}
      <rect x="-20" y={vault + 20} width="760" height="24" fill="#4a3020" /><rect x="-20" y={vault + 20} width="760" height="5" fill="#7a5236" />
    </>
  );
}

function armoryLand(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  return (
    <>
      <defs>
        <VGrad id="floor" y0={hz} y1={bottom} stops={[[0, '#2a221e'], [1, '#3a302a']]} />
        <VGrad id="dais" y0={c.p0} y1={c.p1} stops={[[0, '#7a6a5e'], [1, '#8e7e70']]} />
        <RGrad id="forge" stops={[[0, '#fff0a0'], [0.4, '#ff8a2a', 0.9], [1, '#ff5a1a', 0]]} />
      </defs>
      {/* deux boucliers au mur, une torche à gauche (à droite, c'est la forge qui éclaire) */}
      <Shield x={190} y={hz - 150} r={30} color="#2a5aa8" emblem={1} /><Shield x={530} y={hz - 160} r={34} color="#a8322e" emblem={3} />
      <Torch x={90} y={hz - 110} s={1.3} />
      <rect y={hz - 4} width={W} height={bottom - hz + 4} fill="url(#floor)" />
      <path d={`M-20 ${hz - 4} H740 V${p0} H-20 Z`} fill="#2a221e" />
      {/* le râtelier au milieu, la forge et l'enclume à droite, des tonneaux à gauche, tous posés derrière l'estrade */}
      <Rack x={360} y={p0 - 2} />
      <g transform={`translate(${FORGE_X} ${p0 - 2})`}>
        <path d="M-70 0 V-100 L-50 -150 H50 L70 -100 V0 Z" fill="#4a3e36" /><path d="M-70 0 V-100 L-50 -150 H-30 L-46 -100 V0 Z" fill="#3a302a" />
        <rect x="-54" y="-156" width="108" height="9" rx="2" fill="#2e2622" /><rect x="-54" y="-156" width="108" height="3" rx="1.5" fill="#6a5a4e" />
        <path d="M-40 0 V-54 Q0 -84 40 -54 V0 Z" fill="#1a0e0a" /><ellipse cx="0" cy="-22" rx="34" ry="24" fill="url(#forge)" />
      </g>
      <g transform={`translate(540 ${p0 - 2})`}>
        <ellipse cx="0" cy="2" rx="34" ry="5" fill="#000" opacity="0.35" />
        <path d="M-12 0 L-8 -22 H8 L12 0 Z" fill="#3a3a40" /><path d="M-30 -22 H22 Q36 -24 40 -32 H-24 Q-30 -30 -30 -22 Z" fill="#5a5a64" /><path d="M-24 -32 H40 L36 -36 H-20 Z" fill="#9a9aa8" />
      </g>
      {[[60, 1], [104, 0.85]].map(([x, k]) => (
        <g transform={`translate(${x} ${p0 - 2}) scale(${k})`}>
          <ellipse cx="0" cy="2" rx="28" ry="5" fill="#000" opacity="0.35" />
          <path d="M-24 0 Q-30 -30 -24 -60 H24 Q30 -30 24 0 Z" fill="#8a5a34" /><path d="M-24 0 Q-30 -30 -24 -60 H-10 Q-14 -30 -10 0 Z" fill="#6a4226" />
          <path d="M-27 -14 H27 M-28 -46 H28" stroke="#4a4a52" stroke-width="5" /><ellipse cx="0" cy="-60" rx="24" ry="6" fill="#a87a4a" />
        </g>
      ))}
      {/* l'estrade de dalles, d'un bord à l'autre, cerclée de bronze */}
      <Platform y0={p0} y1={p1} th={30} top="url(#dais)" face="#5a4c42" faceDark="#4a3e36" lip="#d8b060" back="#000"
        faceArt={<>{Array.from({ length: 13 }, (_, i) => <circle cx={30 + i * 56} cy={p1 + 15} r="4.5" fill="#c8a040" />)}<rect x="-20" y={p1 + 3} width={W + 40} height="3" fill="#a8803a" /></>}>
        <Flagstones seed={36} y0={p0} y1={p1} rows={4} line="#5a4c42" light="#c8b8a8" lightOpacity={0.15} />
        <Pebbles seed={37} x={360} y={(p0 + p1) / 2} n={8} rx={360} ry={(p1 - p0) * 0.4} color="#5a4c42" lit="#a89888" k={1} />
      </Platform>
    </>
  );
}

function armoryFront(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <g transform={`translate(34 ${b + 4}) scale(1.2)`}>
        <path d="M-24 0 Q-30 -30 -24 -60 H24 Q30 -30 24 0 Z" fill="#8a5a34" /><path d="M-24 0 Q-30 -30 -24 -60 H-10 Q-14 -30 -10 0 Z" fill="#6a4226" />
        <path d="M-27 -14 H27 M-28 -46 H28" stroke="#4a4a52" stroke-width="5" /><ellipse cx="0" cy="-60" rx="24" ry="6" fill="#a87a4a" />
      </g>
      <g transform={`translate(680 ${b})`}><rect x="-36" y="-44" width="72" height="44" fill="#7a4e2c" /><rect x="-36" y="-44" width="72" height="5" fill="#b07a48" /><path d="M-36 -44 L36 0 M36 -44 L-36 0" stroke="#4a2e18" stroke-width="3" /></g>
    </>
  );
}

function armorySprites(c: Ctx): Sprite[] {
  const fl = flameSprite(30, 44);
  return [
    { id: 'flame', ...fl, origin: [0.5, 1], at: [[90, c.hz - 110 - 34 * 1.3]], depth: -16, anim: { k: 'flicker', min: 0.75, period: 1 }, scale: [1.1] },
    { id: 'tglow', ...glowSprite(170, '#ffb050', 0.55), at: [[90, c.hz - 170]], depth: -17, anim: { k: 'flicker', min: 0.6, period: 1.4 }, add: true },
    { id: 'forge', ...glowSprite(200, '#ff8a2a', 0.7), at: [[FORGE_X, c.p0 - 26]], depth: -15, anim: { k: 'flicker', min: 0.55, period: 1.8 }, add: true },
    { id: 'fwall', ...glowSprite(320, '#ff8a2a', 0.28), at: [[FORGE_X - 30, c.p0 - 90]], depth: -17, anim: { k: 'flicker', min: 0.6, period: 2.2 }, add: true },
    { id: 'bannerA', ...bannerSprite('#a8322e', '#6a1a1a', 3), origin: [0.5, 0], at: [[262, c.hz - 260], [458, c.hz - 260]], depth: -18, anim: { k: 'sway', deg: 2, period: 3.4 } },
  ];
}

export const ARMORY: Scene = {
  base: 0x3a302a,
  sky: armorySky, land: armoryLand, front: armoryFront, sprites: armorySprites,
  particles: (c) => [
    {
      id: 'spark', size: 10, area: [630, c.p0 - 40, 670, c.p0 - 20], depth: -14, vx: [-30, 10], vy: [-70, -40], life: [900, 1600], count: 6, scale: [0.3, 0.8], alpha: [0.3, 1], add: true,
      draw: () => <><defs><RGrad id="e" stops={[[0, '#fff0b0'], [0.4, '#ffa040', 0.9], [1, '#ff6020', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#e)" /></>,
    },
    {
      id: 'dust', size: 10, area: [0, 0, W, c.p1], depth: -11, vx: [-4, 4], vy: [-4, 4], life: [6000, 10000], count: 10, scale: [0.4, 0.8], alpha: [0.1, 0.4], add: true,
      draw: () => <><defs><RGrad id="d" stops={[[0, '#fff0d0'], [1, '#fff0d0', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#d)" /></>,
    },
  ],
};

// ---------------------------------------------------------------- l'antre

function lairSky(c: Ctx) {
  const gx = 360, gy = c.hz - 4;
  return (
    <>
      <defs>
        <VGrad id="wall" y0={0} y1={c.hz} stops={[[0, '#0e0608'], [0.5, '#2a0e12'], [1, '#4a161a']]} />
        <RGrad id="glow" stops={[[0, '#ff7a2a', 0.6], [1, '#ff7a2a', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#wall)" />
      <Masonry seed={7} y0={-20} y1={c.hz + 40} color="#3a1a1e" light="#6a2a2a" line="#1a0a0c" rowH={40} />
      <Gloom id="gloom" y1={Math.max(160, c.hz - 430)} color="#0e0608" />
      <ellipse cx={gx} cy={gy - 150} rx="260" ry="200" fill="url(#glow)" />
      {/* la grande porte : un arc de pierre noire à cornes, la herse, l'œil gravé au-dessus */}
      <path d={`M${gx - 150} ${gy} V${gy - 200} Q${gx - 150} ${gy - 300} ${gx} ${gy - 310} Q${gx + 150} ${gy - 300} ${gx + 150} ${gy - 200} V${gy} H${gx + 110} V${gy - 196} Q${gx + 110} ${gy - 262} ${gx} ${gy - 270} Q${gx - 110} ${gy - 262} ${gx - 110} ${gy - 196} V${gy} Z`} fill="#1a0c0e" />
      <path d={`M${gx + 110} ${gy} V${gy - 196} Q${gx + 110} ${gy - 262} ${gx} ${gy - 270} L${gx} ${gy - 310} Q${gx + 150} ${gy - 300} ${gx + 150} ${gy - 200} V${gy} Z`} fill="#3a1a1c" />
      <path d={`M${gx - 150} ${gy - 220} Q${gx - 200} ${gy - 300} ${gx - 170} ${gy - 360} Q${gx - 168} ${gy - 300} ${gx - 128} ${gy - 270} Z M${gx + 150} ${gy - 220} Q${gx + 200} ${gy - 300} ${gx + 170} ${gy - 360} Q${gx + 168} ${gy - 300} ${gx + 128} ${gy - 270} Z`} fill="#2a1416" />
      <path d={`M${gx - 110} ${gy} V${gy - 196} Q${gx - 110} ${gy - 262} ${gx} ${gy - 270} Q${gx + 110} ${gy - 262} ${gx + 110} ${gy - 196} V${gy} Z`} fill="#0a0406" />
      {[-80, -40, 0, 40, 80].map((dx) => <path d={`M${gx + dx} ${gy - 254 + Math.abs(dx) * 0.4} V${gy - 10}`} stroke="#4a3434" stroke-width="7" />)}
      {[0.25, 0.55, 0.85].map((k) => <path d={`M${gx - 106} ${gy - 10 - 250 * k} H${gx + 106}`} stroke="#4a3434" stroke-width="6" />)}
      <path d={`M${gx - 22} ${gy - 290} Q${gx} ${gy - 310} ${gx + 22} ${gy - 290} Q${gx} ${gy - 270} ${gx - 22} ${gy - 290} Z`} fill="#ff6a2a" /><circle cx={gx} cy={gy - 290} r="6" fill="#1a0406" />
    </>
  );
}

function lairLand(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  return (
    <>
      <defs>
        <VGrad id="floor" y0={hz} y1={c.p0} stops={[[0, '#1a0a0c'], [1, '#2a1214']]} />
        <VGrad id="slab" y0={c.p0} y1={c.p1} stops={[[0, '#2a1e24'], [1, '#3a2a30']]} />
        <VGrad id="lava" y0={c.p1} y1={c.bottom} stops={[[0, '#ff6a1a'], [0.4, '#ffa83a'], [1, '#ff7a2a']]} />
        <VGrad id="pillar" y0={0} y1={1} stops={[[0, '#2a1a20'], [1, '#14080c']]} />
        <RGrad id="mouth" cy={0.7} stops={[[0, '#ffb040', 0.95], [0.5, '#ff6a1a', 0.6], [1, '#ff6a1a', 0]]} />
      </defs>
      {/* deux chutes de lave dans les coins du fond (le courant est animé) */}
      {[[68, 1], [652, -1]].map(([x, k]) => {
        const m = hz - 412;
        const fall = `M-20 ${m} Q-26 ${hz - 330} -18 ${hz - 250} Q-30 ${hz - 150} -24 ${hz - 60} Q-34 ${hz - 20} -40 ${hz - 6} H40 Q34 ${hz - 20} 26 ${hz - 60} Q34 ${hz - 150} 22 ${hz - 250} Q28 ${hz - 330} 20 ${m} Z`;
        return (
          <g transform={`translate(${x} 0) scale(${k} 1)`}>
            {/* la bouche : une arche de pierre dans le mur, le feu au fond, un rebord d'où la lave déborde */}
            <path d={`M-44 ${m + 6} V${m - 22} Q-44 ${m - 62} 0 ${m - 64} Q44 ${m - 62} 44 ${m - 22} V${m + 6} Z`} fill="#4a2226" />
            <path d={`M-44 ${m - 22} Q-44 ${m - 62} 0 ${m - 64} Q44 ${m - 62} 44 ${m - 22}`} fill="none" stroke="#8a4a4a" stroke-width="3" />
            <path d={`M-32 ${m} V${m - 20} Q-32 ${m - 50} 0 ${m - 52} Q32 ${m - 50} 32 ${m - 20} V${m} Z`} fill="#120608" />
            <ellipse cx="0" cy={m - 10} rx="28" ry="16" fill="url(#mouth)" />
            <path d={`M-40 ${m - 4} H40 L36 ${m + 8} H-36 Z`} fill="#2a1214" /><path d={`M-40 ${m - 4} H40`} stroke="#8a4a4a" stroke-width="2.4" />
            {/* la chute : plus large en bas, bords qui ondulent, croûte plus sombre sur les bords */}
            <path d={fall} transform="scale(1.22 1)" fill="#b8381a" />
            <path d={fall} fill="#ff7a2a" />
            <path d={`M-6 ${m} Q-10 ${hz - 300} -4 ${hz - 200} Q-12 ${hz - 100} -6 ${hz - 6} H8 Q12 ${hz - 100} 6 ${hz - 200} Q10 ${hz - 300} 6 ${m} Z`} fill="#ffd060" />
            <path d={`M12 ${m + 14} Q16 ${hz - 260} 10 ${hz - 130} Q14 ${hz - 60} 18 ${hz - 12}`} fill="none" stroke="#ffb040" stroke-width="3" opacity="0.8" />
            {/* le bassin où elle tombe */}
            <ellipse cx="0" cy={hz - 4} rx="64" ry="11" fill="#ff8a2a" /><ellipse cx="0" cy={hz - 5} rx="40" ry="6" fill="#ffe08a" />
          </g>
        );
      })}
      <rect y={hz - 4} width={W} height={p0 - hz + 4} fill="url(#floor)" />
      {/* deux piliers d'obsidienne, un brasero sur chacun */}
      {[176, 544].map((x) => (
        <g>
          <ellipse cx={x} cy={p0 - 1} rx="40" ry="6" fill="#000" opacity="0.4" />
          <rect x={x - 26} y={p0 - 150} width="52" height="148" fill="url(#pillar)" /><rect x={x + 8} y={p0 - 150} width="10" height="148" fill="#4a2a32" />
          <rect x={x - 34} y={p0 - 160} width="68" height="14" fill="#3a2028" /><rect x={x - 34} y={p0 - 160} width="68" height="3" fill="#8a4a4a" />
          <path d={RUNES[x === 176 ? 0 : 1]} fill="none" stroke="#ff6a2a" stroke-width="2.6" stroke-linecap="round" transform={`translate(${x} ${p0 - 80}) scale(2.4)`} opacity="0.8" />
          <Brazier x={x} y={p0 - 160} s={1.2} metal="#2a2028" lit="#5a4048" />
        </g>
      ))}
      {/* sous la dalle, le fleuve de lave */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#lava)" />
      {[60, 210, 380, 520, 660].map((x, i) => <ellipse cx={x} cy={p1 + 50 + (i % 2) * 6} rx={20 + (i % 3) * 8} ry="5" fill="#5a1a10" opacity="0.7" />)}
      {/* la dalle d'obsidienne, d'un bord à l'autre ; sa frise de signes qui luisent */}
      <Platform y0={p0} y1={p1} th={32} top="url(#slab)" face="#1a1014" faceDark="#2a1012" lip="#8a4a50" back="#000"
        faceArt={<>{Array.from({ length: 12 }, (_, i) => <path d={RUNES[(i * 3) % RUNES.length]} fill="none" stroke="#ff7a2a" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(30 + i * 60)} ${p1 + 16}) scale(1.5)`} />)}</>}>
        <Flagstones seed={42} y0={p0} y1={p1} rows={4} line="#1a1014" light="#6a4a50" lightOpacity={0.14} />
      </Platform>
    </>
  );
}

function lairFront(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <path d={`M-20 ${b + 10} L-8 ${b - 40} L28 ${b - 54} L62 ${b - 30} L84 ${b + 10} Z`} fill="#140a0c" />
      <path d={`M28 ${b - 54} L62 ${b - 30} L84 ${b + 10} H48 Z`} fill="#2a1418" />
      <path d={`M740 ${b + 10} L728 ${b - 44} L692 ${b - 58} L660 ${b - 28} L640 ${b + 10} Z`} fill="#140a0c" />
      <path d={`M692 ${b - 58} L728 ${b - 44} L740 ${b + 10} H700 Z`} fill="#2a1418" />
    </>
  );
}

function lairSprites(c: Ctx): Sprite[] {
  const fl = flameSprite(36, 56);
  const lavaTex = {
    w: 50, h: 140,
    draw: () => <><defs><RGrad id="l" stops={[[0, '#fff0a0', 0.9], [1, '#ffd060', 0]]} /></defs>{[[14, 20, 6, 18], [34, 64, 7, 22], [20, 104, 5, 16]].map(([x, y, rx, ry]) => <ellipse cx={x} cy={y} rx={rx} ry={ry} fill="url(#l)" />)}</>,
  };
  return [
    { id: 'lavaA', ...lavaTex, origin: [0.5, 0], at: [[68, c.hz - 410], [652, c.hz - 410]], depth: -18, anim: { k: 'flow', speed: 90 }, flowH: 400, add: true, alpha: 0.7, scale: [0.8, 0.8] },
    { id: 'pool', ...glowSprite(200, '#ffb040', 0.6), at: [[68, c.hz - 8], [652, c.hz - 8]], depth: -17, anim: { k: 'pulse', min: 0.4, period: 1.8 }, add: true },
    { id: 'flame', ...fl, origin: [0.5, 1], at: [[176, c.p0 - 160 - 34 * 1.2], [544, c.p0 - 160 - 34 * 1.2]], depth: -16, anim: { k: 'flicker', min: 0.75, period: 1.1 }, scale: [1.3, 1.3] },
    { id: 'bglow', ...glowSprite(220, '#ff8a2a', 0.6), at: [[176, c.p0 - 220], [544, c.p0 - 220]], depth: -17, anim: { k: 'flicker', min: 0.6, period: 1.5 }, add: true },
    { id: 'eye', ...glowSprite(120, '#ff5a1a', 0.8), at: [[360, c.hz - 294]], depth: -19, anim: { k: 'pulse', min: 0.3, period: 2.4 }, add: true },
    { id: 'lglow', ...glowSprite(300, '#ffd060', 0.55), at: [[120, c.p1 + 50], [420, c.p1 + 56], [660, c.p1 + 48]], depth: -13, anim: { k: 'pulse', min: 0.3, period: 2.6 }, add: true },
  ];
}

export const LAIR: Scene = {
  base: 0x2a1214,
  sky: lairSky, land: lairLand, front: lairFront, sprites: lairSprites,
  particles: (c) => [
    {
      id: 'ember', size: 12, area: [0, c.p1 + 20, W, c.bottom], depth: -11, vx: [-8, 12], vy: [-44, -22], life: [3000, 5200], count: 18, scale: [0.4, 1], alpha: [0.2, 1], add: true,
      draw: () => <><defs><RGrad id="e" stops={[[0, '#fff0b0'], [0.35, '#ff9a3a', 0.9], [1, '#ff5a1a', 0]]} /></defs><circle cx="6" cy="6" r="6" fill="url(#e)" /></>,
    },
  ],
};

// ---------------------------------------------------------------- l'arène

function arenaSky(c: Ctx) {
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#2264c8'], [0.5, '#62a8e8'], [1, '#d6ecfa']]} />
        <CloudGrad id="k-cloud" />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <g transform={`translate(-30 ${Math.max(140, c.hz * 0.3)}) scale(2)`}><Cloud lobes={CLOUD_C} w={126} /></g>
      <g transform={`translate(470 ${Math.max(110, c.hz * 0.2)}) scale(1.5)`}><Cloud lobes={CLOUD_A} w={90} /></g>
    </>
  );
}

/** L'arche n° i d'une rangée de n : son bord gauche x et sa largeur aw. */
const archOf = (i: number, n: number) => { const w = (W + 40) / n; return { x: -20 + i * w + w * 0.18, aw: w * 0.64, w }; };

/**
 * Les arcades de l'amphithéâtre : une rangée d'arches (pierre claire, creux d'ombre) sur une hauteur h ; `skip` = l'arche
 * remplacée par autre chose (la grande porte).
 */
function Arcade({ y, h, n, stone, shade, hole, skip = -1 }: { y: number; h: number; n: number; stone: string; shade: string; hole: string; skip?: number }) {
  return (
    <g>
      <rect x="-20" y={y - h} width={W + 40} height={h} fill={stone} />
      {Array.from({ length: n }, (_, i) => {
        if (i === skip) return null;
        const { x, aw, w } = archOf(i, n);
        return <g><path d={`M${f(x)} ${y} V${f(y - h * 0.55)} Q${f(x + aw / 2)} ${f(y - h * 0.95)} ${f(x + aw)} ${f(y - h * 0.55)} V${y} Z`} fill={hole} /><rect x={f(x + aw + w * 0.05)} y={y - h} width={f(w * 0.12)} height={h} fill={shade} opacity="0.35" /></g>;
      })}
      <rect x="-20" y={y - h} width={W + 40} height="6" fill="#fff6e0" opacity="0.7" />
    </g>
  );
}

/** Le public : couleurs des tuniques, des visages, des cheveux. */
const TUNICS = ['#a83a3a', '#2f5a9a', '#c8962e', '#3a7a4a', '#7a4a9a', '#b85a2a'];
const SKINS = ['#e8b890', '#c89068', '#8a5a3a', '#f0cca8'];
const HAIRS = ['#3a2a20', '#6a4a2a', '#1a1414', '#a87a3a', '#2a2020'];

/** Les pierres de la bordure de la piste : x, largeur. */
const ARENA_BLOCKS: [number, number][] = (() => { const r = rng(19); const o: [number, number][] = []; for (let x = -20; x < W + 20;) { const w = 90 + r() * 60; o.push([x, w]); x += w; } return o; })();

function arenaLand(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const r = rng(13);
  return (
    <>
      <defs>
        <VGrad id="sandBack" y0={hz} y1={c.p0} stops={[[0, '#c8a070'], [1, '#d8b080']]} />
        <VGrad id="track" y0={c.p0} y1={c.p1} stops={[[0, '#e2bc84'], [1, '#f0cc92']]} />
        <VGrad id="low" y0={c.p1} y1={c.bottom} stops={[[0, '#c89a64'], [1, '#d8aa70']]} />
      </defs>
      {/* l'amphithéâtre : deux étages d'arcades, le mur du bas et sa grande porte */}
      <Arcade y={hz - 150} h={110} n={9} stone="#e6d6b4" shade="#8a7a5a" hole="#7a5a40" />
      {/* le public aux arches du haut : têtes et épaules au-dessus du rebord (l'étage du bas, dessiné ensuite, cache le reste) */}
      {Array.from({ length: 9 }, (_, i) => {
        const { x, aw } = archOf(i, 9);
        return [0.3, 0.72].map((k, j) => {
          const cx = x + aw * k, n = i * 2 + j, top = hz - 160;
          const tunic = TUNICS[(n * 5) % TUNICS.length], skin = SKINS[(n * 3) % SKINS.length], hair = HAIRS[(n * 7) % HAIRS.length];
          return (
            <g>
              {n % 3 === 1 && <><path d={`M${f(cx + 7)} ${top - 8} L${f(cx + 12)} ${top - 25}`} stroke={tunic} stroke-width="4.5" stroke-linecap="round" /><circle cx={f(cx + 12.4)} cy={top - 27} r="2.6" fill={skin} /></>}
              <path d={`M${f(cx - 11)} ${top + 2} V${top - 6} Q${f(cx - 10)} ${top - 13} ${f(cx)} ${top - 13} Q${f(cx + 10)} ${top - 13} ${f(cx + 11)} ${top - 6} V${top + 2} Z`} fill={tunic} />
              <path d={`M${f(cx + 2)} ${top - 13} Q${f(cx + 10)} ${top - 13} ${f(cx + 11)} ${top - 6} V${top + 2} H${f(cx + 4)} Z`} fill="#000" opacity="0.18" />
              <circle cx={f(cx)} cy={top - 19} r="6.4" fill={skin} />
              <path d={`M${f(cx - 6.4)} ${top - 19} A6.4 6.4 0 0 1 ${f(cx + 6.4)} ${top - 19} Q${f(cx)} ${top - 23} ${f(cx - 6.4)} ${top - 19} Z`} fill={hair} />
            </g>
          );
        });
      })}
      <Arcade y={hz - 40} h={120} n={7} stone="#dcc8a0" shade="#8a7a5a" hole="#6a4a32" skip={3} />
      <rect x="-20" y={hz - 40} width={W + 40} height="44" fill="#c8b088" /><rect x="-20" y={hz - 40} width={W + 40} height="5" fill="#f2e2c0" />
      {/* la grande porte, à la place de l'arche du milieu : un arc de pierre claire et sa clé de voûte, la herse de fer */}
      <path d={`M286 ${hz + 4} V${hz - 84} Q360 ${hz - 156} 434 ${hz - 84} V${hz + 4} Z`} fill="#efe2c4" />
      <path d={`M286 ${hz + 4} V${hz - 84} Q360 ${hz - 156} 434 ${hz - 84} V${hz + 4}`} fill="none" stroke="#b8a074" stroke-width="2" />
      <path d={`M302 ${hz + 4} V${hz - 80} Q360 ${hz - 136} 418 ${hz - 80} V${hz + 4} Z`} fill="#3a2a1c" />
      {[318, 339, 360, 381, 402].map((x) => { const t = (x - 302) / 116; return <path d={`M${x} ${f(hz - 80 - 112 * t * (1 - t) + 4)} V${hz + 4}`} stroke="#22222a" stroke-width="5" />; })}
      {[0.32, 0.68].map((k) => <path d={`M302 ${f(hz - 76 * k - 6)} H418`} stroke="#22222a" stroke-width="5" />)}
      <path d={`M351 ${hz - 124} H369 L373 ${hz - 104} H347 Z`} fill="#fff6e0" /><path d={`M347 ${hz - 104} H373`} stroke="#b8a074" stroke-width="1.5" />
      {/* le sable devant le mur */}
      <rect y={hz + 4} width={W} height={p0 - hz} fill="url(#sandBack)" />
      {/* la piste : du sable damé d'un bord à l'autre, sur une bordure de pierre plaquée de bronze */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#low)" />
      <Platform y0={p0} y1={p1} th={30} top="url(#track)" face="#b89a70" faceDark="#9a7e58" lip="#fff0cc" back="#6a4a30"
        faceArt={<>{ARENA_BLOCKS.map(([x, w]) => <g><rect x={x + 2} y={p1 + 3} width={w - 4} height="24" rx="3" fill="#c8aa80" /><rect x={x + 2} y={p1 + 3} width={w - 4} height="5" rx="2.5" fill="#e8d0a8" /><circle cx={x + 12} cy={p1 + 16} r="3.4" fill="#c8963a" /><circle cx={x + w - 12} cy={p1 + 16} r="3.4" fill="#c8963a" /></g>)}</>}>
        {Array.from({ length: 14 }, () => <ellipse cx={r() * W} cy={p0 + 10 + r() * (p1 - p0 - 20)} rx={12 + r() * 30} ry="3" fill="#fff0c8" opacity="0.5" />)}
        <Pebbles seed={17} x={360} y={(p0 + p1) / 2} n={10} rx={360} ry={(p1 - p0) * 0.4} color="#b8966a" lit="#f2dcae" k={1} />
      </Platform>
    </>
  );
}

function arenaFront(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      {/* une épée et un bouclier plantés dans le sable, dans les coins */}
      <g transform={`translate(44 ${b - 2}) rotate(-8)`}>
        <ellipse cx="0" cy="2" rx="26" ry="5" fill="#000" opacity="0.3" />
        <path d="M-6 0 V-58 L0 -66 L6 -58 V0 Z" fill="#c8ced8" /><path d="M0 0 V-66 L6 -58 V0 Z" fill="#f0f4fa" />
        <rect x="-20" y="-6" width="40" height="7" rx="3" fill="#c8a040" transform="translate(0 -56)" />
        <rect x="-4" y="-84" width="8" height="24" rx="2" fill="#5a3a24" /><circle cx="0" cy="-86" r="5" fill="#c8a040" />
      </g>
      <g transform={`translate(680 ${b + 4})`}><ellipse cx="0" cy="-2" rx="28" ry="5" fill="#000" opacity="0.3" /><ellipse cx="0" cy="-30" rx="26" ry="32" fill="#8a8e98" /><ellipse cx="0" cy="-30" rx="21" ry="27" fill="#a8322e" /><g transform="translate(0 -30)"><Emblem kind={0} color="#ffd45c" /></g></g>
    </>
  );
}

function arenaSprites(c: Ctx): Sprite[] {
  const cA = cloudSprite(CLOUD_A, 90, 1.4), cB = cloudSprite(CLOUD_B, 62, 1.1);
  const flag = (color: string) => ({
    w: 60, h: 34,
    draw: () => <path d="M0 4 Q20 0 34 8 Q46 14 58 10 Q48 22 34 20 Q18 18 0 24 Z" fill={color} />,
  });
  return [
    { id: 'cloudA', ...cA, at: [[200, Math.max(100, c.hz * 0.16)]], depth: -28, anim: { k: 'drift', speed: 6, from: -300, to: 1020 } },
    { id: 'cloudB', ...cB, at: [[600, Math.max(170, c.hz * 0.4)]], depth: -28, anim: { k: 'drift', speed: 9, from: -300, to: 1020 }, alpha: 0.9 },
    // les mâts au sommet du mur et leurs fanions qui claquent
    {
      id: 'mast', w: 8, h: 90, origin: [0.5, 1], at: [[80, c.hz - 260], [280, c.hz - 260], [440, c.hz - 260], [640, c.hz - 260]], depth: -19, anim: { k: 'still' },
      draw: () => <g><rect x="2.5" y="0" width="3" height="90" fill="#6a4a30" /><circle cx="4" cy="2" r="3" fill="#ffd45c" /></g>,
    },
    // deux couleurs de fanions en alternance (pas quatre fanions identiques)
    { id: 'flagR', ...flag('#d23a3a'), origin: [0, 0.2], at: [[82, c.hz - 342], [442, c.hz - 342]], depth: -18, anim: { k: 'sway', deg: 7, period: 1.4 } },
    { id: 'flagB', ...flag('#2f5ab0'), origin: [0, 0.2], at: [[282, c.hz - 342], [642, c.hz - 342]], depth: -18, anim: { k: 'sway', deg: 7, period: 1.25 } },
    // les bannières, chacune sur un pilier de l'étage du bas (symétriques de part et d'autre de la porte)
    { id: 'banner', ...bannerSprite('#b8323a', '#7a1a26', 2, 70), origin: [0.5, 0], at: [[197, c.hz - 160], [523, c.hz - 160]], depth: -18, anim: { k: 'sway', deg: 2, period: 3 } },
  ];
}

export const ARENA: Scene = {
  base: 0xd8b080,
  sky: arenaSky, land: arenaLand, front: arenaFront, sprites: arenaSprites,
  particles: (c) => [
    {
      id: 'dust', size: 10, area: [-40, c.p0, -10, c.bottom], depth: -11, vx: [30, 60], vy: [-8, 2], life: [10000, 14000], count: 8, scale: [0.6, 1.4], alpha: [0.15, 0.45],
      draw: () => <><defs><RGrad id="d" stops={[[0, '#fff0c8'], [1, '#fff0c8', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#d)" /></>,
    },
  ],
};
