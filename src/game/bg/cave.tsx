// Deux décors sous la roche, pour les donjons.
//   La mine d'or : une galerie boisée ; au fond, l'entrée du tunnel et ses rails, un wagonnet plein d'or, des filons qui
//   scintillent, des lanternes pendues aux étais ; on se bat sur une passerelle de planches au-dessus d'un puits.
//   La source d'essence : une grotte bleue ; au fond, une cascade de lumière tombe dans un bassin, des cristaux poussent
//   sur les corniches ; on se bat sur une terrasse de pierre mouillée, le bassin luit dessous.
import { Flagstones, Platform, RGrad, VGrad, W, f, rng } from './kit';
import { Crystals, RockWall, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

// ---------------------------------------------------------------- la mine d'or

/** Les filons d'or (de x0, y0 à x1, y1, en y relatif à l'horizon). */
const VEINS: [number, number, number, number][] = [[30, -250, 150, -228], [550, -300, 700, -268], [196, -168, 268, -150]];

/** Un étai de mine : deux poteaux, une poutre, des contrefiches ; bois clair à droite. Pieds en (x0, y) et (x1, y). */
function Frame({ x0, x1, y, h, wood = '#8a5a34', dark = '#5a3a22', light = '#c08850' }: { x0: number; x1: number; y: number; h: number; wood?: string; dark?: string; light?: string }) {
  const t = 16;
  return (
    <g>
      <rect x={x0 - t / 2} y={y - h} width={t} height={h} fill={wood} /><rect x={x0 - t / 2} y={y - h} width={t * 0.4} height={h} fill={dark} />
      <rect x={x1 - t / 2} y={y - h} width={t} height={h} fill={wood} /><rect x={x1 + t * 0.1} y={y - h} width={t * 0.4} height={h} fill={light} />
      <rect x={x0 - t} y={y - h - t} width={x1 - x0 + t * 2} height={t + 2} fill={wood} /><rect x={x0 - t} y={y - h - t} width={x1 - x0 + t * 2} height="4" fill={light} />
      <path d={`M${x0 + t / 2} ${y - h + 34} L${x0 + 40} ${y - h + 2} L${x0 + 50} ${y - h + 2} L${x0 + t / 2} ${y - h + 46} Z M${x1 - t / 2} ${y - h + 34} L${x1 - 40} ${y - h + 2} L${x1 - 50} ${y - h + 2} L${x1 - t / 2} ${y - h + 46} Z`} fill={dark} />
      <ellipse cx={(x0 + x1) / 2} cy={y + 2} rx={(x1 - x0) / 2 + 20} ry="5" fill="#000" opacity="0.3" />
    </g>
  );
}

/** Un wagonnet plein d'or sur ses roues. Pied en (x, y). */
function Cart({ x, y, s }: { x: number; y: number; s: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx="0" cy="2" rx="50" ry="6" fill="#000" opacity="0.35" />
      <path d="M-44 -50 Q-30 -66 -10 -60 Q4 -74 22 -62 Q38 -66 46 -50 Z" fill="#e8b02a" />
      <path d="M-10 -60 Q4 -74 22 -62 Q14 -60 6 -54 Z M-30 -56 Q-24 -62 -14 -58 Z" fill="#fff0a0" />
      <path d="M-46 -50 H46 L38 -12 H-38 Z" fill="#6a5040" /><path d="M-46 -50 H-20 L-26 -12 H-38 Z" fill="#4a3628" />
      <rect x="-48" y="-54" width="96" height="6" rx="2" fill="#9a7a5a" /><path d="M-30 -48 V-14 M0 -48 V-12 M30 -48 V-14" stroke="#3a2a20" stroke-width="2.4" />
      {[-24, 24].map((wx) => <g><circle cx={wx} cy="-8" r="9" fill="#2a2420" /><circle cx={wx} cy="-8" r="4" fill="#8a7a6a" /></g>)}
    </g>
  );
}

function mineSky(c: Ctx) {
  const tx = 360, ty = c.hz - 4;
  return (
    <>
      <defs>
        <VGrad id="wall" y0={0} y1={c.hz} stops={[[0, '#1e140f'], [0.5, '#3a2618'], [1, '#5a3c24']]} />
        <RGrad id="deep" stops={[[0, '#ffd890', 0.9], [0.4, '#c88a40', 0.4], [1, '#c88a40', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#wall)" />
      <RockWall seed={5} y0={Math.max(40, c.hz - 520)} y1={c.hz + 40} dark="#3a2818" mid="#4e3622" light="#8a6440" edge="#9a7448" />
      {/* l'entrée du tunnel : un trou noir, une lueur au fond, les rails qui y entrent */}
      <path d={`M${tx - 80} ${ty} V${ty - 120} Q${tx} ${ty - 176} ${tx + 80} ${ty - 120} V${ty} Z`} fill="#0e0a08" />
      <ellipse cx={tx} cy={ty - 60} rx="40" ry="44" fill="url(#deep)" />
      {/* les filons d'or dans la roche : des pépites serrées le long d'une veine claire */}
      {VEINS.map(([x0, y0, x1, y1]) => <path d={`M${x0} ${c.hz + y0} Q${(x0 + x1) / 2} ${c.hz + (y0 + y1) / 2 - 14} ${x1} ${c.hz + y1}`} fill="none" stroke="#a8803a" stroke-width="5" stroke-linecap="round" opacity="0.6" />)}
      {VEINS.flatMap(([x0, y0, x1, y1], vi) => Array.from({ length: 6 }, (_, i) => {
        const t = (i + 0.5) / 6, x = x0 + (x1 - x0) * t, y = c.hz + y0 + (y1 - y0) * t - 14 * 4 * t * (1 - t) + ((vi + i) % 3) * 2 - 2;
        return <g><path d={`M${f(x - 5)} ${f(y)} L${f(x - 1)} ${f(y - 5)} L${f(x + 5)} ${f(y - 2)} L${f(x + 3)} ${f(y + 4)} L${f(x - 3)} ${f(y + 4)} Z`} fill="#e8b02a" /><path d={`M${f(x - 1)} ${f(y - 5)} L${f(x + 5)} ${f(y - 2)} L${f(x + 1)} ${f(y)} Z`} fill="#fff0a0" /></g>;
      }))}
    </>
  );
}

function mineLand(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const tx = 360, ty = hz - 4;
  const r = rng(7);
  return (
    <>
      <defs>
        <VGrad id="ground" y0={hz} y1={c.p0} stops={[[0, '#4a3220'], [1, '#5e4028']]} />
        <VGrad id="boards" y0={c.p0} y1={c.p1} stops={[[0, '#9a6a3e'], [1, '#b47c48']]} />
        <VGrad id="pit" y0={c.p1} y1={c.bottom} stops={[[0, '#120c08'], [1, '#2a1c12']]} />
      </defs>
      {/* le cadre de bois de l'entrée du tunnel, les rails qui en sortent */}
      <Frame x0={tx - 84} x1={tx + 84} y={ty} h={126} />
      <rect y={hz - 6} width={W} height={p0 - hz + 6} fill="url(#ground)" />
      <path d={`M${tx - 40} ${ty} L${tx - 150} ${p0} M${tx + 40} ${ty} L${tx - 60} ${p0}`} stroke="#8a8a90" stroke-width="4" />
      {Array.from({ length: 4 }, (_, i) => { const k = (i + 0.5) / 4, y = ty + (p0 - ty) * k; return <path d={`M${tx - 44 - 110 * k} ${y} H${tx + 44 - 100 * k}`} stroke="#5a3a22" stroke-width="5" />; })}
      {/* les étais de la galerie, à gauche et à droite */}
      <Frame x0={-20} x1={150} y={p0 - 2} h={hz * 0.6} /><Frame x0={570} x1={740} y={p0 - 2} h={hz * 0.6} />
      {/* le wagonnet, un tas de minerai, des caisses, une pioche */}
      <Cart x={200} y={p0 - 4} s={1} />
      <path d={`M470 ${p0 - 2} Q490 ${p0 - 46} 520 ${p0 - 40} Q546 ${p0 - 52} 560 ${p0 - 2} Z`} fill="#5a4030" />
      {Array.from({ length: 7 }, () => { const x = 480 + r() * 70, y = p0 - 6 - r() * 30; return <path d={`M${f(x)} ${f(y)} l4 -6 l4 6 l-4 4 Z`} fill="#ffd040" />; })}
      <g transform={`translate(646 ${p0 - 2})`}>
        <rect x="-26" y="-44" width="52" height="44" fill="#8a5a34" /><rect x="-26" y="-44" width="52" height="5" fill="#c08850" /><path d="M-26 -44 L26 0 M26 -44 L-26 0" stroke="#5a3a22" stroke-width="3" />
        <path d="M30 0 L52 -70" stroke="#6a4a30" stroke-width="5" stroke-linecap="round" /><path d="M36 -66 Q52 -84 72 -68 Q54 -74 44 -62 Z" fill="#9aa0a8" />
      </g>
      {/* la passerelle de planches au-dessus du puits, d'un bord à l'autre */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#pit)" />
      {[40, 180, 320, 460, 600].map((x) => <g><rect x={x - 9} y={p1 + 20} width="18" height="60" fill="#5a3a22" /><rect x={x - 9} y={p1 + 20} width="7" height="60" fill="#3a2414" /></g>)}
      <Platform y0={p0} y1={p1} th={24} top="url(#boards)" face="#6a4426" faceDark="#553620" lip="#e0a868" back="#1a100a">
        {Array.from({ length: 6 }, (_, i) => { const y = p0 + ((p1 - p0) * (i + 1)) / 6; return <rect x="-20" y={y - 2} width={W + 40} height="2.2" fill="#6a4426" opacity="0.6" />; })}
        {Array.from({ length: 12 }, (_, i) => <circle cx={30 + i * 60} cy={p0 + 14 + (i % 3) * 36} r="2" fill="#4a2e18" />)}
      </Platform>
    </>
  );
}

function mineFront(c: Ctx) {
  const b = c.bottom;
  const r = rng(11);
  return (
    <>
      <path d={`M-20 ${b + 10} Q30 ${b - 40} 100 ${b - 26} Q140 ${b - 14} 150 ${b + 10} Z`} fill="#c88a20" />
      {Array.from({ length: 16 }, () => { const x = r() * 130 - 10, y = b - r() * 26; return <ellipse cx={f(x)} cy={f(y)} rx="7" ry="3.4" fill={r() < 0.5 ? '#ffd040' : '#ffe890'} />; })}
      <g transform={`translate(680 ${b - 2})`}><rect x="-34" y="-40" width="68" height="40" fill="#8a5a34" /><rect x="-34" y="-40" width="68" height="5" fill="#c08850" /><path d="M-34 -20 H34" stroke="#5a3a22" stroke-width="3" /></g>
    </>
  );
}

function mineSprites(c: Ctx): Sprite[] {
  const lampY = c.p0 - 2 - c.hz * 0.6 + 24;
  return [
    {
      id: 'lantern', w: 30, h: 46, origin: [0.5, 0], at: [[136, lampY], [584, lampY]], depth: -18, anim: { k: 'sway', deg: 3, period: 3 },
      draw: () => <g><path d="M15 0 V10" stroke="#2a1c12" stroke-width="2" /><path d="M7 10 H23 L21 36 H9 Z" fill="#3a2c20" /><path d="M9 13 H21 L19.5 33 H10.5 Z" fill="#ffd77a" /><path d="M6 10 L15 4 L24 10 Z" fill="#2a1c12" /><rect x="8" y="36" width="14" height="4" fill="#2a1c12" /></g>,
    },
    { id: 'glow', ...glowSprite(180, '#ffc860', 0.7), at: [[136, lampY + 24], [584, lampY + 24]], depth: -17, anim: { k: 'flicker', min: 0.6, period: 2 }, add: true },
    { id: 'tunnel', ...glowSprite(120, '#ffd890', 0.6), at: [[360, c.hz - 64]], depth: -19, anim: { k: 'pulse', min: 0.5, period: 4 }, add: true },
    { id: 'sparkle', ...glowSprite(26, '#fff4c0', 0.95), at: [[70, c.hz - 248], [130, c.hz - 238], [600, c.hz - 294], [676, c.hz - 280], [236, c.hz - 166], [520, c.p0 - 30], [60, c.bottom - 20]], depth: -16, anim: { k: 'pulse', min: 0, period: 1.8 }, add: true },
  ];
}

export const MINE: Scene = {
  base: 0x4a3220,
  sky: mineSky, land: mineLand, front: mineFront, sprites: mineSprites,
  particles: (c) => [
    {
      id: 'dust', size: 10, area: [0, 0, W, c.p1], depth: -11, vx: [-5, 5], vy: [-4, 6], life: [6000, 10000], count: 14, scale: [0.4, 0.9], alpha: [0.15, 0.6], add: true,
      draw: () => <><defs><RGrad id="d" stops={[[0, '#fff0c8'], [0.4, '#e8b870', 0.5], [1, '#e8b870', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#d)" /></>,
    },
  ],
};

// ---------------------------------------------------------------- la source d'essence

function springSky(c: Ctx) {
  return (
    <>
      <defs>
        <VGrad id="wall" y0={0} y1={c.hz} stops={[[0, '#081a2a'], [0.5, '#123450'], [1, '#1e4e6e']]} />
        <RGrad id="halo" stops={[[0, '#bffcff', 0.8], [0.4, '#5ff0ff', 0.3], [1, '#5ff0ff', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#wall)" />
      <RockWall seed={9} y0={Math.max(40, c.hz - 520)} y1={c.hz + 40} dark="#14304a" mid="#1c4060" light="#4a8ab0" edge="#5aa0c8" />
      <ellipse cx="360" cy={c.hz - 160} rx="200" ry="220" fill="url(#halo)" />
    </>
  );
}

function springLand(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const top = Math.max(60, hz - 420);
  return (
    <>
      <defs>
        <VGrad id="fall" y0={top} y1={hz} stops={[[0, '#e8ffff'], [1, '#7ff0ff']]} />
        <VGrad id="pool" y0={c.p1} y1={c.bottom} stops={[[0, '#2ad8e8'], [1, '#5ff0ff']]} />
        <VGrad id="stone" y0={c.p0} y1={c.p1} stops={[[0, '#3a5a74'], [1, '#4e7090']]} />
        <VGrad id="ledge" y0={0} y1={1} stops={[[0, '#5f96b8'], [1, '#2a5a80']]} />
      </defs>
      {/* la cascade de lumière : elle sort d'une faille, tombe dans un bassin au fond */}
      <path d={`M330 ${top} Q326 ${hz - 200} 318 ${hz - 16} H402 Q394 ${hz - 200} 390 ${top} Z`} fill="url(#fall)" opacity="0.9" />
      <path d={`M350 ${top} Q348 ${hz - 200} 344 ${hz - 16} H360 Q362 ${hz - 200} 362 ${top} Z`} fill="#ffffff" opacity="0.7" />
      <path d={`M316 ${top - 10} Q360 ${top - 40} 404 ${top - 10} L396 ${top + 6} Q360 ${top - 14} 324 ${top + 6} Z`} fill="#0e2438" />
      <ellipse cx="360" cy={hz - 10} rx="130" ry="18" fill="#5ff0ff" opacity="0.8" /><ellipse cx="360" cy={hz - 12} rx="80" ry="9" fill="#e8ffff" />
      {/* deux corniches de roche, couvertes de cristaux */}
      <path d={`M-20 ${hz - 124} H170 Q190 ${hz - 120} 186 ${hz - 102} L160 ${hz - 64} Q120 ${hz - 44} 60 ${hz - 54} H-20 Z`} fill="url(#ledge)" />
      <path d={`M-20 ${hz - 124} H170 Q190 ${hz - 120} 186 ${hz - 102} L176 ${hz - 104} Q176 ${hz - 114} 160 ${hz - 116} H-20 Z`} fill="#8ac8e4" />
      <path d={`M740 ${hz - 154} H560 Q540 ${hz - 150} 544 ${hz - 132} L570 ${hz - 88} Q610 ${hz - 68} 670 ${hz - 78} H740 Z`} fill="url(#ledge)" />
      <path d={`M740 ${hz - 154} H560 Q540 ${hz - 150} 544 ${hz - 132} L554 ${hz - 134} Q556 ${hz - 144} 572 ${hz - 146} H740 Z`} fill="#8ac8e4" />
      <Crystals x={60} y={hz - 118} s={1.4} /><Crystals x={130} y={hz - 118} s={0.9} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" flip />
      <Crystals x={600} y={hz - 148} s={1.2} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" /><Crystals x={680} y={hz - 148} s={1.6} flip />
      {/* le sol de la grotte, des cristaux au pied des parois */}
      <rect y={hz - 4} width={W} height={p0 - hz + 4} fill="#1e3e58" />
      <Crystals x={40} y={p0 - 2} s={1.5} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" /><Crystals x={226} y={p0 - 4} s={0.9} />
      <Crystals x={500} y={p0 - 4} s={0.8} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" flip /><Crystals x={684} y={p0 - 2} s={1.7} flip />
      {/* la terrasse de pierre mouillée, d'un bord à l'autre ; le bassin qui luit dessous */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#pool)" />
      <Platform y0={p0} y1={p1} th={30} top="url(#stone)" face="#26465e" faceDark="#1e3a50" lip="#9fe8f8" back="#081a2a"
        faceArt={<>{[60, 250, 460, 650].map((x, i) => <g transform={`translate(${x} ${p1 + 30}) scale(${i % 2 ? 0.5 : 0.6}) rotate(180)`}><Crystals x={0} y={0} s={1} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" /></g>)}</>}>
        <Flagstones seed={32} y0={p0} y1={p1} rows={4} line="#26465e" light="#9fd8ec" lightOpacity={0.14} />
        {[[120, 0.4, 70], [400, 0.7, 90], [620, 0.3, 50]].map(([x, k, w]) => <ellipse cx={x} cy={p0 + (p1 - p0) * (k as number)} rx={w} ry="8" fill="#9ff0ff" opacity="0.25" />)}
      </Platform>
    </>
  );
}

function springFront(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <Crystals x={30} y={b + 4} s={1.8} /><Crystals x={96} y={b + 6} s={1} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" />
      <Crystals x={690} y={b + 4} s={1.9} color="#5ff0ff" light="#e8ffff" dark="#1a8aa8" flip /><Crystals x={630} y={b + 6} s={1.1} flip />
    </>
  );
}

function springSprites(c: Ctx): Sprite[] {
  const top = Math.max(60, c.hz - 420);
  return [
    // l'eau qui tombe : des traînées d'écume douces qui descendent (pas de rayures)
    {
      id: 'flow', w: 70, h: 120, origin: [0.5, 0], at: [[360, top]], depth: -18, anim: { k: 'flow', speed: 140 }, flowH: c.hz - 16 - top, add: true, alpha: 0.6,
      draw: () => <><defs><RGrad id="b" stops={[[0, '#ffffff', 0.55], [1, '#ffffff', 0]]} /></defs>{[[22, 30, 12, 40], [46, 84, 11, 46], [30, 108, 9, 30]].map(([x, y, rx, ry]) => <ellipse cx={x} cy={y} rx={rx} ry={ry} fill="url(#b)" />)}</>,
    },
    { id: 'splash', ...glowSprite(220, '#bffcff', 0.7), at: [[360, c.hz - 14]], depth: -17, anim: { k: 'pulse', min: 0.5, period: 1.6 }, add: true },
    { id: 'cglow', ...glowSprite(130, '#9a7aff', 0.6), at: [[60, c.hz - 140], [680, c.hz - 172], [684, c.p0 - 30], [40, c.p0 - 30]], depth: -16, anim: { k: 'pulse', min: 0.3, period: 3.2 }, add: true },
    { id: 'pglow', ...glowSprite(260, '#5ff0ff', 0.5), at: [[150, c.p1 + 40], [400, c.p1 + 46], [640, c.p1 + 40]], depth: -14, anim: { k: 'pulse', min: 0.3, period: 2.8 }, add: true },
  ];
}

export const SPRING: Scene = {
  base: 0x1e3e58,
  sky: springSky, land: springLand, front: springFront, sprites: springSprites,
  particles: (c) => [
    {
      id: 'essence', size: 14, area: [0, c.p1, W, c.bottom], depth: -11, vx: [-6, 6], vy: [-40, -20], life: [5000, 8000], count: 18, scale: [0.4, 1], alpha: [0.2, 0.9], add: true,
      draw: () => <><defs><RGrad id="e" stops={[[0, '#ffffff'], [0.3, '#7ff8ff', 0.8], [1, '#7ff8ff', 0]]} /></defs><circle cx="7" cy="7" r="7" fill="url(#e)" /></>,
    },
  ],
};
