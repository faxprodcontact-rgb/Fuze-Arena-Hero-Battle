// La forêt des ronciers : sous la voûte d'une vieille forêt. Au fond, des troncs pâles dans la brume et une trouée de
// lumière ; de part et d'autre, deux grands troncs qui encadrent l'arène ; des ronces à baies, des champignons géants, des
// fougères ; au sol, une clairière de mousse cerclée de petits champignons. Lucioles, feuilles qui tombent, lianes.
import { Bush, FaceStones, Flagstones, Overhang, Pebbles, Platform, RGrad, VGrad, W, canopy, tufts } from './kit';
import { Fern, Mushroom, Trunk, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

/** Le bas de la voûte de feuillage (en haut de l'écran). */
const roofOf = (c: Ctx) => c.hz * 0.22;
/** La trouée de lumière : sous la voûte, entre les troncs, à droite. */
const gapAt = (c: Ctx) => ({ x: 500, y: roofOf(c) + 140 });

/** Des ronces : un buisson sombre hérissé de vrilles à épines, des baies rouges. Pied en (x, y). */
function Bramble({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="2" rx="46" ry="6" fill="#0d1a10" opacity="0.3" />
      <path d="M-44 2 Q-50 -18 -32 -24 Q-30 -42 -10 -38 Q2 -52 20 -40 Q40 -40 42 -20 Q52 -10 44 2 Z" fill="#1f4a34" />
      <path d="M-20 2 Q-24 -16 -8 -20 Q0 -34 16 -26 Q34 -26 36 -10 Q42 -4 38 2 Z" fill="#2f6a48" />
      <path d="M8 -28 Q20 -34 30 -24 Q20 -22 14 -18 Z M-14 -16 Q-6 -24 4 -18 Q-4 -16 -8 -10 Z" fill="#4f9a5e" />
      <g fill="none" stroke="#3a5a2a" stroke-width="2.4" stroke-linecap="round">
        <path d="M-30 -22 Q-46 -40 -36 -54 Q-28 -60 -24 -50" /><path d="M24 -38 Q30 -60 48 -58 Q56 -54 50 -46" /><path d="M-4 -40 Q-2 -56 10 -60" />
      </g>
      <g fill="#3a5a2a"><path d="M-40 -46 l-5 -2 l4 -2 Z M-33 -56 l-2 -5 l4 2 Z M36 -58 l1 -5 l3 4 Z M48 -52 l5 -1 l-3 4 Z M4 -58 l-2 -4 l4 1 Z" /></g>
      <g fill="#d1323f">{[[-24, -14], [-16, -26], [6, -30], [22, -18], [30, -30], [-34, -6], [14, -8]].map(([bx, by]) => <circle cx={bx} cy={by} r="3.2" />)}</g>
      <g fill="#ff9aa0">{[[-25, -15], [5, -31], [21, -19], [29, -31]].map(([bx, by]) => <circle cx={bx! + 0.8} cy={by! - 0.8} r="1.1" />)}</g>
    </g>
  );
}

function sky(c: Ctx) {
  const { hz } = c;
  const g = gapAt(c);
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={hz} stops={[[0, '#123426'], [0.3, '#24583e'], [0.66, '#8fc48a'], [0.86, '#c9e8a8'], [1, '#a6d890']]} />
        <RGrad id="gap" stops={[[0, '#fffbe0', 0.95], [0.25, '#f8f2b0', 0.6], [0.6, '#d8eea0', 0.22], [1, '#d8eea0', 0]]} />
        <VGrad id="fog" y0={hz - 260} y1={hz} stops={[[0, '#dff2c8', 0], [1, '#dff2c8', 0.85]]} />
      </defs>
      <rect width={W} height={hz + 60} fill="url(#sky)" />
      <circle cx={g.x} cy={g.y} r="300" fill="url(#gap)" />
      {/* le fond de la forêt : des cimes rondes à peine dessinées dans la brume, puis quelques troncs inégaux, jamais alignés */}
      <path d={canopy(31, hz - 150, 40, 26)} fill="#b9dcb0" opacity="0.8" />
      <path d={canopy(37, hz - 96, 30, 20)} fill="#9cc898" opacity="0.85" />
      {[[60, 18, -2], [250, 12, 2.5], [418, 26, 0], [626, 15, -1.5]].map(([x, w, tilt], i) => {
        const base = hz - 20 + (i % 3) * 10;
        const col = i % 2 ? '#8fbc8e' : '#a6cda0';
        return (
          <g transform={`rotate(${tilt} ${x} ${base})`}>
            <path d={`M${x! - w! * 1.6} ${base} Q${x! - w! * 0.7} ${base - 14} ${x! - w! * 0.6} ${base - 60} L${x! - w! * 0.45} ${-20} H${x! + w! * 0.45} L${x! + w! * 0.6} ${base - 60} Q${x! + w! * 0.7} ${base - 14} ${x! + w! * 1.7} ${base} Z`} fill={col} />
            <path d={`M${x! + w! * 0.1} ${-20} H${x! + w! * 0.45} L${x! + w! * 0.6} ${base - 60} Q${x! + w! * 0.7} ${base - 14} ${x! + w! * 1.7} ${base} H${x! + w! * 0.5} Q${x! + w! * 0.3} ${base - 40} ${x! + w! * 0.1} ${base - 70} Z`} fill="#d6ecc8" opacity="0.5" />
          </g>
        );
      })}
      <rect y={hz - 260} width={W} height="270" fill="url(#fog)" />
      <rect y={hz - 420} width={W} height="420" fill="#cfe8bc" opacity="0.18" />
    </>
  );
}

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const g = gapAt(c);
  const top = roofOf(c);
  return (
    <>
      <defs>
        <VGrad id="floor" y0={hz - 10} y1={bottom} stops={[[0, '#2f6a44'], [0.18, '#4f9058'], [0.5, '#6aad66'], [1, '#5c9e5e']]} />
        <VGrad id="leaf" y0={-20} y1={top + 120} stops={[[0, '#0f2a1c'], [0.7, '#1f4a32'], [1, '#2f6a44']]} />
        {/* le même dégradé, retourné : la voûte est dessinée tête en bas (scale(1 -1)), et un dégradé suit le dessin qui
            l'utilise ; celui-ci retombe donc exactement sur le précédent à l'écran (aucune marche entre les deux) */}
        <VGrad id="leafFlip" y0={2 * top + 80} y1={top - 60} stops={[[0, '#0f2a1c'], [0.7, '#1f4a32'], [1, '#2f6a44']]} />
        <RGrad id="pool" stops={[[0, '#fff6c0', 0.55], [0.6, '#f0f0a0', 0.2], [1, '#f0f0a0', 0]]} />
        <VGrad id="path" y0={c.p0} y1={c.p1} stops={[[0, '#7f9a72'], [0.4, '#93ae84'], [1, '#a2bc90']]} />
      </defs>
      {/* les arbres du milieu : troncs moyens, leur pied dans l'ombre de la lisière ; dessinés avant la voûte, qui cache leur
          sommet (aucun tronc ne s'arrête dans le vide) */}
      <Trunk x={150} y={hz + 4} w={34} h={hz + 40} dark="#2c4a38" mid="#3f6450" lit="#5f8a6a" moss="#6fae62" band={false} />
      <Trunk x={566} y={hz + 6} w={30} h={hz + 40} dark="#2c4a38" mid="#3f6450" lit="#5f8a6a" moss="#6fae62" flip band={false} />
      <Trunk x={352} y={hz - 4} w={22} h={hz + 40} dark="#34584a" mid="#4a7060" lit="#6a927a" moss="#7fb86e" band={false} />
      {/* la voûte : un grand dais de feuilles en haut de l'écran, ourlé de lumière, troué à droite (même dégradé partout :
          aucun bord droit) */}
      <path d={`M-20 -20 H740 V${top - 30} H-20 Z`} fill="url(#leaf)" />
      <path d={canopy(4, top + 30, 34, 18)} transform={`scale(1 -1) translate(0 ${-2 * top - 60})`} fill="url(#leafFlip)" />
      <path d={canopy(4, top + 30, 34, 18, true)} transform={`scale(1 -1) translate(0 ${-2 * top - 60})`} fill="none" stroke="#5faa5a" stroke-width="3" opacity="0.45" />
      {Array.from({ length: 14 }, (_, i) => <ellipse cx={20 + i * 52} cy={top + 18 + (i % 3) * 9} rx="13" ry="7" fill={i % 2 ? '#3f8050' : '#2f6a44'} opacity="0.9" />)}
      {/* la lisière : des bosquets bas derrière l'arène */}
      <path d={canopy(13, hz + 2, 14, 10)} fill="#2f6a44" />
      <path d={canopy(13, hz + 2, 14, 10, true)} fill="none" stroke="#7fc47a" stroke-width="2.4" opacity="0.7" />
      {/* le sol de mousse, plus sombre sous les arbres */}
      <rect y={hz} width={W} height={bottom - hz} fill="url(#floor)" />
      <ellipse cx={g.x - 40} cy={p0 + 40} rx="300" ry="60" fill="url(#pool)" />
      {/* les grands troncs des bords, qui encadrent l'arène ; leurs racines plongent derrière la plateforme */}
      <Trunk x={18} y={p0 + 4} w={86} h={p0 + 30} band={false} />
      <Trunk x={708} y={p0 + 4} w={92} h={p0 + 30} flip band={false} />
      {/* ronces, champignons géants et fougères, juste derrière la plateforme */}
      <Bramble x={130} y={p0 - 2} s={1.1} /><Bramble x={596} y={p0 - 2} s={1.2} flip />
      <Mushroom x={84} y={p0 - 1} s={1.7} /><Mushroom x={110} y={p0 - 4} s={1} flip />
      <Mushroom x={640} y={p0 - 1} s={1.9} flip /><Mushroom x={614} y={p0 - 4} s={1.1} />
      <Fern x={226} y={p0 - 2} s={1.1} /><Fern x={486} y={p0 - 2} s={1.1} flip /><Fern x={300} y={p0 - 6} s={0.8} />
      <path d={tufts(4, p0 - 2, 3, 18)} fill="#3f8050" />
      {/* la plateforme : une vieille chaussée de dalles moussues, d'un bord à l'autre ; son mur de pierres devant */}
      <Platform y0={p0} y1={p1} th={30} top="url(#path)" face="#5f6a60" faceDark="#4a544c" lip="#c8d8b0" back="#0d2a18"
        faceArt={<>
          <FaceStones seed={51} y0={p1} y1={p1 + 30} color="#6a766a" lit="#a2ae9e" n={18} />
          <Overhang seed={53} y={p1 + 1} color="#4f8a40" light="#6fae5a" />
        </>}>
        <Flagstones seed={8} y0={p0} y1={p1} rows={4} line="#4f6a50" light="#c8dcb0" lightOpacity={0.18} />
        <Pebbles seed={6} x={360} y={(p0 + p1) / 2} n={14} rx={360} ry={(p1 - p0) * 0.42} color="#6a8a6a" lit="#b8d0a8" k={1.1} />
        <path d={tufts(27, p1 - 6, 4, 46, 1.6)} fill="#5f9a4a" /><path d={tufts(29, p0 + 10, 3, 52, 1.4)} fill="#5f9a4a" />
      </Platform>
      {/* sous la chaussée : fougères et petits champignons */}
      <Fern x={200} y={p1 + 64} s={0.9} /><Mushroom x={420} y={p1 + 60} s={0.6} /><Mushroom x={440} y={p1 + 64} s={0.45} flip />
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <Fern x={20} y={b + 8} s={2.1} dark="#1f5a3a" light="#3f8a50" /><Fern x={704} y={b + 6} s={2.3} dark="#1f5a3a" light="#3f8a50" flip />
      <Mushroom x={598} y={b + 4} s={1.2} flip /><Mushroom x={150} y={b + 6} s={0.9} />
      <path d={tufts(41, b + 2, 4, 26, 2.6)} fill="#2f6a44" />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const g = gapAt(c);
  const top = roofOf(c);
  const pool = glowSprite(260, '#fff6c0', 0.5);
  return [
    { id: 'gap', ...glowSprite(420, '#fff8d0', 0.55), at: [[g.x, g.y]], depth: -29, anim: { k: 'pulse', min: 0.55, period: 6 }, add: true },
    { id: 'pool', ...pool, at: [[g.x - 60, c.p0 + 50]], depth: -14, anim: { k: 'pulse', min: 0.4, period: 5 }, add: true, scale: [1.3] },
    // des lianes qui pendent de la voûte et se balancent
    {
      id: 'vine', w: 40, h: 190, origin: [0.5, 0], at: [[96, top + 24], [258, top + 30], [430, top + 26], [640, top + 28]], depth: -21, anim: { k: 'sway', deg: 3.5, period: 5.5 }, scale: [1.1, 0.8, 1, 1.15],
      draw: () => (
        <g>
          <path d="M20 0 Q14 50 22 100 Q28 150 18 186" fill="none" stroke="#2f6a44" stroke-width="4" stroke-linecap="round" />
          {[24, 52, 80, 108, 136, 162].map((y, i) => <path d={`M${21 + (i % 2 ? 2 : -2)} ${y} q${i % 2 ? 12 : -12} -4 ${i % 2 ? 16 : -16} 6 q${i % 2 ? -8 : 8} 2 ${i % 2 ? -16 : 16} -6 Z`} fill={i % 2 ? '#4f9a5e' : '#3f8050'} />)}
        </g>
      ),
    },
    // la lueur des champignons géants
    { id: 'shroom', ...glowSprite(110, '#ff9a7a', 0.45), at: [[84, c.p0 - 40], [640, c.p0 - 42]], depth: -12, anim: { k: 'pulse', min: 0.35, period: 3.8 }, add: true },
  ];
}

export const BRAMBLE: Scene = {
  base: 0x4f9058,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'firefly', size: 14, area: [0, c.hz - 120, W, c.cy + 80], depth: -11, vx: [-10, 10], vy: [-8, 6], life: [4000, 7000], count: 16, scale: [0.6, 1.1], alpha: [0.2, 1], add: true,
      draw: () => <><defs><RGrad id="f" stops={[[0, '#ffffe0'], [0.3, '#e8ff80', 0.8], [1, '#c8f060', 0]]} /></defs><circle cx="7" cy="7" r="7" fill="url(#f)" /></>,
    },
    {
      id: 'leaf', size: 16, area: [0, roofOf(c), W, roofOf(c) + 40], depth: 1295, vx: [-16, 22], vy: [26, 44], life: [9000, 13000], count: 7, scale: [0.8, 1.1], alpha: [0.6, 0.95], spin: 70,
      draw: () => <g><path d="M8 1 Q15 6 8 15 Q1 6 8 1 Z" fill="#7fbf4a" /><path d="M8 3 V13" stroke="#4f8a30" stroke-width="1.2" /></g>,
    },
  ],
};
