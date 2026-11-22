// Les terres de cendre : une savane brûlée au crépuscule. Au fond, le volcan crache sa fumée, des coulées descendent ses
// flancs ; des acacias à cime plate se découpent sur le ciel rouge ; on se bat sur une dalle de basalte fendue, ses
// fissures luisent de lave. Braises qui montent, cendre qui tombe.
import { CLOUD_A, CLOUD_C, Cloud, CloudGrad, Flagstones, Pebbles, Platform, flagJoints, RGrad, VGrad, W, ridge, rng, tufts } from './kit';
import { glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

const volcanoAt = (c: Ctx) => ({ x: 520, top: Math.max(150, c.hz - 300) });

/** Un acacia : tronc fourchu, cime plate en deux étages, liseré de lumière du côté du couchant. Pied en (x, y). */
function Acacia({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d="M-3 0 L-2 -30 Q-14 -44 -30 -52 L-27 -55 Q-12 -48 0 -38 Q8 -50 26 -58 L28 -55 Q12 -46 4 -32 L4 0 Z" fill="#2a1418" />
      <path d="M-58 -54 Q-40 -68 -6 -66 Q30 -72 62 -60 Q40 -50 0 -52 Q-36 -48 -58 -54 Z" fill="#2a1418" />
      <path d="M-36 -66 Q-14 -78 14 -76 Q36 -78 48 -68 Q24 -64 -2 -66 Q-24 -62 -36 -66 Z" fill="#3a1c20" />
      <path d="M14 -76 Q36 -78 48 -68 Q36 -70 20 -73 Z M30 -70 Q48 -68 62 -60 Q50 -62 38 -64 Z" fill="#ff8a4a" opacity="0.8" />
    </g>
  );
}

function sky(c: Ctx) {
  const v = volcanoAt(c);
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#22091a'], [0.38, '#5a1626'], [0.72, '#c4462a'], [0.9, '#f07a3a'], [1, '#ffa050']]} />
        <RGrad id="glow" stops={[[0, '#ffb060', 0.8], [0.4, '#ff7030', 0.3], [1, '#ff7030', 0]]} />
        <CloudGrad id="k-cloud" top="#5a2a34" mid="#3a1a26" low="#2a1220" />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <circle cx={v.x} cy={v.top} r="260" fill="url(#glow)" />
      {/* des nuages de fumée lourds, éclairés par-dessous */}
      {[[-40, 0.2, CLOUD_C, 126, 2.4], [300, 0.12, CLOUD_A, 90, 2], [480, 0.28, CLOUD_C, 126, 1.8]].map(([x, k, lobes, w, s]) => (
        <g transform={`translate(${x} ${Math.max(90, c.hz * (k as number) + 60)}) scale(${s})`}><Cloud lobes={lobes as [number, number, number][]} w={w as number} light="#7a3a3a" /></g>
      ))}
    </>
  );
}

/** Les croûtes sombres qui flottent sur la lave. */
const CRUST: [number, number][] = (() => { const r = rng(61); const o: [number, number][] = []; for (let x = 20; x < W; x += 70 + r() * 80) o.push([x, 16 + r() * 22]); return o; })();

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const v = volcanoAt(c);
  return (
    <>
      <defs>
        <VGrad id="cone" y0={v.top} y1={hz} stops={[[0, '#3a2026'], [1, '#22141a']]} />
        <VGrad id="plain" y0={hz - 40} y1={hz + 20} stops={[[0, '#6a2a26'], [1, '#3a1c20']]} />
        <VGrad id="floor" y0={hz} y1={bottom} stops={[[0, '#2e1c20'], [0.3, '#3a2628'], [1, '#2a1a1e']]} />
        <RGrad id="crater" stops={[[0, '#fff0a0'], [0.3, '#ffa040'], [1, '#ff6020', 0]]} />
        <VGrad id="slab" y0={c.p0} y1={c.p1} stops={[[0, '#3e3034'], [1, '#4c3c40']]} />
        <VGrad id="seam" y0={c.p0} y1={c.p1} stops={[[0, '#ff7a2a', 0.12], [0.6, '#ff8a3a', 0.45], [1, '#ffb050', 0.85]]} />
        <VGrad id="lava" y0={c.p1} y1={c.bottom} stops={[[0, '#ff7a1a'], [0.4, '#ffb03a'], [1, '#ff8a2a']]} />
      </defs>
      {/* les crêtes lointaines */}
      <path d={ridge(3, hz - 40, 30, 80, 60, 120)} fill="#5a2228" />
      {/* le volcan : deux faces, le cratère qui rougeoie, deux coulées de lave */}
      <path d={`M${v.x - 330} ${hz - 30} Q${v.x - 140} ${v.top + 120} ${v.x - 46} ${v.top} H${v.x + 50} Q${v.x + 150} ${v.top + 120} ${v.x + 330} ${hz - 30} Z`} fill="url(#cone)" />
      <path d={`M${v.x + 6} ${v.top} H${v.x + 50} Q${v.x + 150} ${v.top + 120} ${v.x + 330} ${hz - 30} H${v.x + 150} Q${v.x + 60} ${v.top + 140} ${v.x + 6} ${v.top} Z`} fill="#5a2c30" />
      <ellipse cx={v.x + 2} cy={v.top + 2} rx="48" ry="9" fill="url(#crater)" />
      <path d={`M${v.x - 20} ${v.top + 4} Q${v.x - 44} ${v.top + 70} ${v.x - 34} ${v.top + 120} Q${v.x - 48} ${v.top + 170} ${v.x - 86} ${hz - 52} Q${v.x - 40} ${v.top + 166} ${v.x - 22} ${v.top + 118} Q${v.x - 30} ${v.top + 64} ${v.x - 6} ${v.top + 4} Z`} fill="#ff7a2a" />
      <path d={`M${v.x - 16} ${v.top + 4} Q${v.x - 34} ${v.top + 60} ${v.x - 28} ${v.top + 100} Q${v.x - 22} ${v.top + 60} ${v.x - 9} ${v.top + 4} Z`} fill="#ffd060" />
      <path d={`M${v.x + 22} ${v.top + 4} Q${v.x + 44} ${v.top + 70} ${v.x + 96} ${v.top + 140} Q${v.x + 54} ${v.top + 82} ${v.x + 34} ${v.top + 4} Z`} fill="#ffb04a" />
      {/* la savane : une plaine sombre, des acacias, des rochers */}
      <path d={`M-20 ${hz + 20} V${hz - 34} Q180 ${hz - 50} 360 ${hz - 40} Q540 ${hz - 30} 740 ${hz - 44} V${hz + 20} Z`} fill="url(#plain)" />
      <Acacia x={96} y={hz - 26} s={1.5} /><Acacia x={250} y={hz - 34} s={0.9} flip /><Acacia x={668} y={hz - 22} s={1.3} flip />
      <path d={tufts(5, hz - 30, 6, 14, 2)} fill="#8a3a28" />
      {/* le sol de cendre derrière la chaussée, des herbes brûlées, des rochers */}
      <rect y={hz} width={W} height={bottom - hz} fill="url(#floor)" />
      {[[40, p0 - 2, 70, 50], [690, p0 - 2, 80, 56]].map(([x, y, w, h], i) => (
        <g transform={`translate(${x} ${y})`}>
          <ellipse cx="0" cy="2" rx={w! * 0.6} ry="6" fill="#000" opacity="0.4" />
          <path d={`M${-w! / 2} 0 L${-w! * 0.4} ${-h! * 0.6} L${-w! * 0.05} ${-h!} L${w! * 0.3} ${-h! * 0.8} L${w! / 2} 0 Z`} fill="#3a2a2e" />
          <path d={`M${-w! * 0.05} ${-h!} L${w! * 0.3} ${-h! * 0.8} L${w! / 2} 0 H${w! * 0.1} Z`} fill="#5a4246" />
          <path d={`M${-w! * 0.3} ${-h! * 0.3} L${-w! * 0.1} ${-h! * 0.6} L${w! * 0.1} ${-h! * 0.5}`} fill="none" stroke="#ff7a2a" stroke-width="2" opacity={i % 2 ? 0.9 : 0.6} />
        </g>
      ))}
      <path d={tufts(15, p0 - 2, 6, 30, 2, 70, 200)} fill="#7a3424" /><path d={tufts(17, p0 - 2, 6, 30, 2, 520, 650)} fill="#7a3424" />
      {/* sous la chaussée, une rivière de lave */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#lava)" />
      {CRUST.map(([x, w]) => <ellipse cx={x} cy={p1 + 44} rx={w} ry="5" fill="#5a2216" opacity="0.7" />)}
      {/* la chaussée de basalte, d'un bord à l'autre : dalles sombres, fissures de lave ; son flanc rougeoie par-dessous */}
      <Platform y0={p0} y1={p1} th={30} top="url(#slab)" face="#2a1a1e" faceDark="#3a1a16" lip="#8a6a6e" back="#000"
        faceArt={<rect x="-20" y={p1 + 22} width={W + 40} height="8" fill="#ff6a2a" opacity="0.55" />}>
        <Flagstones seed={12} y0={p0} y1={p1} rows={4} line="#241418" light="#6a5458" lightOpacity={0.2} />
        {/* la lave luit sous la chaussée, à travers les joints : à peine au fond, plus fort devant (la rivière est dessous) */}
        <path d={flagJoints(12, p0, p1, 4, true)} fill="none" stroke="url(#seam)" stroke-width="2.4" stroke-linecap="round" />
        <Pebbles seed={9} x={360} y={(p0 + p1) / 2} n={16} rx={360} ry={(p1 - p0) * 0.42} color="#2a1e22" lit="#5a4448" k={1.3} />
      </Platform>
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <path d={`M-20 ${b + 10} L-10 ${b - 34} L26 ${b - 48} L58 ${b - 26} L80 ${b + 10} Z`} fill="#24161a" />
      <path d={`M26 ${b - 48} L58 ${b - 26} L80 ${b + 10} H44 Z`} fill="#3a2a2e" />
      <path d={`M740 ${b + 10} L730 ${b - 40} L694 ${b - 52} L660 ${b - 24} L642 ${b + 10} Z`} fill="#24161a" />
      <path d={`M694 ${b - 52} L730 ${b - 40} L740 ${b + 10} H704 Z`} fill="#3a2a2e" />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const v = volcanoAt(c);
  return [
    { id: 'crater', ...glowSprite(220, '#ff9a40', 0.8), at: [[v.x, v.top]], depth: -19, anim: { k: 'pulse', min: 0.5, period: 2.8 }, add: true },
    // la fumée du volcan : de gros nuages sombres qui montent et s'étirent
    {
      id: 'plume', w: 200, h: 120, at: [[v.x + 30, v.top - 54], [v.x + 110, v.top - 140]], depth: -21, anim: { k: 'bob', amp: 6, period: 6 }, scale: [1, 1.3], alpha: 0.9,
      draw: () => <><defs><CloudGrad id="k-cloud" top="#5a3a40" mid="#3a2228" low="#2a161c" /></defs><g transform="translate(6 110) scale(1.5)"><Cloud lobes={CLOUD_A} w={90} light="#a85a40" /></g></>,
    },
    // les fissures de la dalle respirent
    {
      // (4 px de marge en haut et en bas : le trait déborde des joints)
      id: 'crack', w: W + 80, h: Math.ceil(c.p1 - c.p0) + 8, origin: [0, 0], at: [[-40, c.p0 - 4]], depth: -14, anim: { k: 'pulse', min: 0.2, period: 3.2 }, add: true,
      draw: () => <><defs><VGrad id="s" y0={0} y1={c.p1 - c.p0} stops={[[0, '#ffb050', 0], [0.5, '#ffb050', 0.3], [1, '#ffc870', 0.9]]} /></defs><path transform="translate(40 4)" d={flagJoints(12, 0, c.p1 - c.p0, 4, true)} fill="none" stroke="url(#s)" stroke-width="5" stroke-linecap="round" /></>,
    },
    { id: 'lavaGlow', ...glowSprite(300, '#ffd060', 0.6), at: [[120, c.p1 + 50], [420, c.p1 + 56], [660, c.p1 + 48]], depth: -13, anim: { k: 'pulse', min: 0.3, period: 2.6 }, add: true, scale: [1.2, 1, 1.1] },
    { id: 'lava', ...glowSprite(160, '#ff7a2a', 0.6), at: [[v.x - 50, v.top + 120], [v.x + 60, v.top + 100]], depth: -18, anim: { k: 'pulse', min: 0.4, period: 2.2 }, add: true },
  ];
}

export const ASH: Scene = {
  base: 0x3a2628,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'ember', size: 12, area: [0, c.p1 + 20, W, c.bottom], depth: -11, vx: [-8, 12], vy: [-40, -20], life: [3000, 5200], count: 18, scale: [0.4, 1], alpha: [0.2, 1], add: true,
      draw: () => <><defs><RGrad id="e" stops={[[0, '#fff0b0'], [0.35, '#ff9a3a', 0.9], [1, '#ff5a1a', 0]]} /></defs><circle cx="6" cy="6" r="6" fill="url(#e)" /></>,
    },
    {
      id: 'ash', size: 8, area: [0, 0, W, c.hz], depth: -27, vx: [-6, 6], vy: [10, 22], life: [9000, 14000], count: 16, scale: [0.6, 1], alpha: [0.2, 0.6],
      draw: () => <circle cx="4" cy="4" r="3" fill="#c8b0b0" />,
    },
    {
      id: 'smoke', size: 40, area: [volcanoAt(c).x - 20, volcanoAt(c).top - 6, volcanoAt(c).x + 20, volcanoAt(c).top + 2], depth: -21, vx: [4, 14], vy: [-24, -14], life: [5000, 7000], count: 8, scale: [0.8, 2.4], alpha: [0, 0.55],
      draw: () => <><defs><RGrad id="s" stops={[[0, '#4a2a30', 0.9], [1, '#4a2a30', 0]]} /></defs><circle cx="20" cy="20" r="20" fill="url(#s)" /></>,
    },
  ],
};
