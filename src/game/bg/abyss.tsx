// Les abysses : sous la mer, au milieu de ruines englouties. La lumière tombe de la surface, très haut ; au loin, des
// arches de roche et une épave couchée ; de part et d'autre, des rochers couverts de coraux. On se bat sur une vieille
// chaussée de pierre engloutie, ses signes luisent encore. Algues qui ondulent, méduses, bancs de poissons, bulles.
import { Flagstones, GLYPHS, Platform, RGrad, VGrad, W, bump, curve, f, rng } from './kit';
import { glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

/** Un corail en éventail (rose, orangé) : un éventail plein, puis des nervures plus claires. Pied en (x, y). */
function Fan({ x, y, s, color, light, flip = false }: { x: number; y: number; s: number; color: string; light: string; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d="M0 0 Q-34 -20 -40 -56 Q-30 -76 -6 -80 Q16 -84 36 -66 Q44 -40 0 0 Z" fill={color} />
      <path d="M0 0 L-24 -60 M0 0 L-4 -74 M0 0 L20 -66 M0 0 L32 -46" fill="none" stroke={light} stroke-width="3" stroke-linecap="round" opacity="0.8" />
      <path d="M-6 -80 Q16 -84 36 -66 Q20 -70 4 -72 Z" fill={light} opacity="0.7" />
    </g>
  );
}

/** Des coraux en tubes qui luisent : trois à cinq tuyaux de hauteurs inégales. Pied en (x, y). */
function Tubes({ x, y, s, color = '#3ad8c8', light = '#bfffef' }: { x: number; y: number; s: number; color?: string; light?: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      {[[-14, 30, 6], [-4, 46, 7], [8, 36, 6], [18, 22, 5]].map(([dx, h, w]) => (
        <g><rect x={dx! - w!} y={-h!} width={w! * 2} height={h} rx={w} fill={color} /><ellipse cx={dx} cy={-h! + 2} rx={w! * 0.8} ry="3" fill="#0e3a40" /><rect x={dx! + w! * 0.2} y={-h! + 6} width={w! * 0.5} height={h! - 10} rx="2" fill={light} opacity="0.6" /></g>
      ))}
    </g>
  );
}

/** Un rocher couvert de coraux, sur un côté de la scène : roche éclairée par le haut, coraux plantés sur ses replats. */
function Reef({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="2" rx="80" ry="8" fill="#061a30" opacity="0.4" />
      <path d="M-74 0 Q-84 -50 -60 -86 L-34 -96 Q-20 -130 12 -132 Q48 -128 58 -92 Q74 -50 72 0 Z" fill="#2a5e86" />
      <path d="M12 -132 Q48 -128 58 -92 Q74 -50 72 0 H34 Q44 -60 12 -132 Z" fill="#3c7aa2" />
      <path d="M-60 -86 L-34 -96 Q-20 -130 12 -132 Q40 -130 52 -110 Q20 -118 -4 -112 Q-30 -100 -60 -86 Z" fill="#6aa8cc" />
      <path d="M-74 0 Q-84 -50 -60 -86 Q-62 -40 -48 0 Z" fill="#1c4468" />
      <Fan x={-30} y={-104} s={0.7} color="#e8607a" light="#ffb0c0" /><Fan x={30} y={-122} s={0.55} color="#ff9a50" light="#ffd0a0" flip />
      <Tubes x={-52} y={-78} s={0.7} /><Tubes x={52} y={-96} s={0.6} color="#9a7aff" light="#e0d0ff" />
    </g>
  );
}

function sky(c: Ctx) {
  const r = rng(3);
  return (
    <>
      <defs>
        <VGrad id="sea" y0={0} y1={c.hz} stops={[[0, '#3a96d8'], [0.22, '#1e66aa'], [0.6, '#0f3c78'], [1, '#0c2c5c']]} />
        <RGrad id="light" stops={[[0, '#c8f0ff', 0.7], [0.5, '#8ad0f8', 0.2], [1, '#8ad0f8', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sea)" />
      {/* la surface, très haut : une lumière qui ondule */}
      <path d={curve((x) => 18 + Math.sin(x / 40) * 6 + Math.sin(x / 17) * 2, -20, 740, -10)} fill="#d8f6ff" opacity="0.45" />
      <ellipse cx="460" cy="40" rx="320" ry="160" fill="url(#light)" />
      {/* au loin, des arches de roche bleutées */}
      <path d={`M-20 ${c.hz} V${c.hz - 160} Q40 ${c.hz - 240} 110 ${c.hz - 200} Q150 ${c.hz - 120} 170 ${c.hz} Z M130 ${c.hz} Q160 ${c.hz - 150} 230 ${c.hz - 150} Q290 ${c.hz - 150} 300 ${c.hz} H270 Q262 ${c.hz - 110} 230 ${c.hz - 112} Q196 ${c.hz - 110} 170 ${c.hz} Z`} fill="#1a4a80" opacity="0.8" />
      <path d={`M740 ${c.hz} V${c.hz - 190} Q680 ${c.hz - 250} 620 ${c.hz - 214} Q580 ${c.hz - 140} 560 ${c.hz} Z`} fill="#1a4a80" opacity="0.8" />
      {Array.from({ length: 20 }, () => <circle cx={r() * W} cy={40 + r() * (c.hz - 120)} r={0.8 + r() * 1.6} fill="#bfefff" opacity={0.3 + r() * 0.4} />)}
    </>
  );
}

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  return (
    <>
      <defs>
        <VGrad id="sand" y0={hz - 40} y1={bottom} stops={[[0, '#2a5a8a'], [0.25, '#3a6a96'], [1, '#2a5280']]} />
        <VGrad id="road" y0={c.p0} y1={c.p1} stops={[[0, '#4a6a8a'], [1, '#5f80a0']]} />
      </defs>
      {/* le fond de la mer : du sable bleuté, des dunes douces */}
      <path d={curve((x) => hz - 30 - bump(x, 200, 200, 26) - bump(x, 560, 180, 30), -20, 740, bottom)} fill="url(#sand)" />
      {/* l'épave, couchée sur le flanc, à droite au fond */}
      <g transform={`translate(520 ${hz - 34}) rotate(-8)`}>
        <path d="M-100 0 Q-90 -40 -40 -46 H90 Q120 -46 130 -20 L110 0 Z" fill="#3a3a4a" />
        <path d="M-100 0 Q-90 -40 -40 -46 H-20 L-36 0 Z" fill="#26283a" />
        <path d="M-60 -30 H100 M-70 -16 H110" stroke="#4a4a5e" stroke-width="3" opacity="0.7" />
        <circle cx="-20" cy="-24" r="5" fill="#16182a" /><circle cx="20" cy="-24" r="5" fill="#16182a" /><circle cx="60" cy="-24" r="5" fill="#16182a" />
        <path d="M30 -46 L46 -170" stroke="#3a3a4a" stroke-width="7" /><path d="M46 -170 L40 -120 L80 -140 Z" fill="#6a7088" opacity="0.6" />
        <path d="M36 -110 H74" stroke="#3a3a4a" stroke-width="5" />
      </g>
      {/* les rochers à coraux des deux côtés, posés sur le sable */}
      <Reef x={40} y={p0 + 2} s={1.1} /><Reef x={690} y={p0 + 4} s={1.2} flip />
      <Tubes x={200} y={p0 - 2} s={0.8} /><Tubes x={510} y={p0 - 2} s={0.7} color="#9a7aff" light="#e0d0ff" />
      {/* la chaussée engloutie, d'un bord à l'autre : dalles moussues de bleu, signes qui luisent sur son flanc */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="#1e4270" />
      <Platform y0={p0} y1={p1} th={34} top="url(#road)" face="#2e4e72" faceDark="#243e60" lip="#9fd0ea" back="#0a1e3a"
        faceArt={<>{Array.from({ length: 12 }, (_, i) => <path d={GLYPHS[(i * 5) % GLYPHS.length]} fill="none" stroke="#5ff0ff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(30 + i * 60)} ${p1 + 17}) scale(1.5)`} opacity="0.85" />)}</>}>
        <Flagstones seed={22} y0={p0} y1={p1} rows={4} line="#2e4a68" light="#9fc0d8" lightOpacity={0.15} />
        {Array.from({ length: 9 }, (_, i) => <ellipse cx={40 + i * 82} cy={p0 + 20 + (i % 3) * 40} rx="40" ry="10" fill="#a8e8ff" opacity="0.12" />)}
      </Platform>
      {/* sous la chaussée : coquillages et étoiles de mer */}
      {[[90, p1 + 56, '#ff9a6a'], [380, p1 + 60, '#ffd06a'], [600, p1 + 54, '#ff7a9a']].map(([x, y, col]) => <path d={`M${x} ${(y as number) - 8} L${(x as number) + 2.5} ${(y as number) - 2} L${(x as number) + 9} ${(y as number) - 1} L${(x as number) + 3.5} ${(y as number) + 3} L${(x as number) + 5.5} ${(y as number) + 9} L${x} ${(y as number) + 5} L${(x as number) - 5.5} ${(y as number) + 9} L${(x as number) - 3.5} ${(y as number) + 3} L${(x as number) - 9} ${(y as number) - 1} L${(x as number) - 2.5} ${(y as number) - 2} Z`} fill={col as string} />)}
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <Fan x={30} y={b + 6} s={1.3} color="#e8607a" light="#ffb0c0" /><Tubes x={90} y={b + 4} s={1} />
      <Fan x={690} y={b + 6} s={1.4} color="#ff9a50" light="#ffd0a0" flip /><Tubes x={636} y={b + 4} s={0.9} color="#9a7aff" light="#e0d0ff" />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  /** Une algue : un ruban qui ondule (ancrée en bas). */
  const kelp = (h: number, color: string) => ({
    w: 40, h,
    draw: () => (
      <g>
        <path d={`M20 ${h} Q8 ${h * 0.75} 22 ${h * 0.5} Q34 ${h * 0.25} 18 0 Q26 ${h * 0.25} 28 ${h * 0.5} Q16 ${h * 0.75} 26 ${h} Z`} fill={color} />
        {[0.2, 0.42, 0.64, 0.84].map((k, i) => <path d={`M${i % 2 ? 26 : 16} ${h * k} q${i % 2 ? 12 : -12} -8 ${i % 2 ? 10 : -10} -18 q${i % 2 ? -6 : 6} 6 ${i % 2 ? -10 : 10} 14 Z`} fill={color} />)}
      </g>
    ),
  });
  /** Une méduse : cloche lumineuse, filaments. */
  const jelly = (color: string) => ({
    w: 60, h: 90,
    draw: () => (
      <>
        <defs><RGrad id="j" stops={[[0, '#ffffff', 0.9], [0.5, color, 0.7], [1, color, 0.2]]} cy={0.3} /></defs>
        <path d="M6 30 Q6 4 30 4 Q54 4 54 30 Q46 26 38 32 Q30 26 22 32 Q14 26 6 30 Z" fill="url(#j)" />
        <path d="M14 32 Q10 52 16 70 M24 32 Q22 56 26 84 M36 32 Q40 54 34 80 M46 32 Q50 50 44 66" fill="none" stroke={color} stroke-width="2.4" stroke-linecap="round" opacity="0.7" />
      </>
    ),
  });
  return [
    { id: 'kelpA', ...kelp(170, '#2a8a6a'), origin: [0.5, 1], at: [[150, c.p0], [258, c.p0 - 4], [470, c.p0 - 4]], depth: -16, anim: { k: 'sway', deg: 6, period: 4.4 }, scale: [1, 0.8, 0.9] },
    { id: 'kelpB', ...kelp(220, '#1f7058'), origin: [0.5, 1], at: [[110, c.p0 + 2], [580, c.p0], [626, c.p0 + 2]], depth: -16, anim: { k: 'sway', deg: 5, period: 5.2 }, scale: [1.1, 0.85, 1] },
    { id: 'jellyA', ...jelly('#ff8ad8'), at: [[150, Math.max(200, c.hz * 0.32)], [560, Math.max(180, c.hz * 0.24)]], depth: -27, anim: { k: 'bob', amp: 16, period: 5 }, scale: [1, 0.8], add: true },
    { id: 'jellyB', ...jelly('#9a8aff'), at: [[420, Math.max(260, c.hz * 0.48)]], depth: -27, anim: { k: 'bob', amp: 12, period: 6 }, scale: [0.7], add: true },
    {
      id: 'fish', w: 150, h: 70, at: [[100, Math.max(220, c.hz - 230)], [600, Math.max(260, c.hz - 150)]], depth: -26, anim: { k: 'drift', speed: 20, from: -180, to: 920 }, scale: [1, 0.75],
      draw: () => (
        <g>
          {[[30, 24, 1], [62, 14, 0.8], [58, 40, 0.9], [96, 28, 1], [124, 16, 0.75], [118, 48, 0.85]].map(([x, y, k]) => (
            <g transform={`translate(${x} ${y}) scale(${k})`}>
              <path d="M-14 0 Q-4 -9 10 -3 L16 -8 L15 0 L16 8 L10 3 Q-4 9 -14 0 Z" fill="#ffb84a" />
              <path d="M-14 0 Q-4 -9 10 -3 L8 0 Q-4 -4 -14 0 Z" fill="#ffe08a" />
              <path d="M-2 -6 Q0 0 -2 6" fill="none" stroke="#e8743a" stroke-width="1.6" />
              <circle cx="-9" cy="-1.5" r="1.4" fill="#2a1a10" />
            </g>
          ))}
        </g>
      ),
    },
    { id: 'glow', ...glowSprite(120, '#5ff0ff', 0.5), at: [[60, c.p1 + 17], [300, c.p1 + 17], [540, c.p1 + 17], [690, c.p1 + 17]], depth: -14, anim: { k: 'pulse', min: 0.2, period: 3.6 }, add: true },
    { id: 'light', ...glowSprite(500, '#bfefff', 0.35), at: [[460, 60]], depth: -29, anim: { k: 'pulse', min: 0.5, period: 6 }, add: true },
    {
      id: 'frontKelp', ...kelp(130, '#2a8a6a'), origin: [0.5, 1], at: [[56, c.bottom + 8], [664, c.bottom + 8]], depth: 1301, anim: { k: 'sway', deg: 7, period: 4 }, scale: [1, 1.1],
    },
  ];
}

export const ABYSS: Scene = {
  base: 0x2a5a8a,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'bubble', size: 14, area: [0, c.bottom - 10, W, c.bottom], depth: -11, vx: [-6, 6], vy: [-60, -30], life: [9000, 14000], count: 16, scale: [0.3, 1], alpha: [0.3, 0.8],
      draw: () => <g><circle cx="7" cy="7" r="6" fill="none" stroke="#d8f8ff" stroke-width="1.6" /><circle cx="5" cy="5" r="1.6" fill="#ffffff" /></g>,
    },
    {
      id: 'mote', size: 10, area: [0, 0, W, c.hz], depth: -27, vx: [-4, 4], vy: [-6, 6], life: [6000, 10000], count: 14, scale: [0.4, 0.9], alpha: [0.2, 0.7], add: true,
      draw: () => <><defs><RGrad id="m" stops={[[0, '#e8ffff'], [0.4, '#8ae8ff', 0.6], [1, '#8ae8ff', 0]]} /></defs><circle cx="5" cy="5" r="5" fill="url(#m)" /></>,
    },
  ],
};
