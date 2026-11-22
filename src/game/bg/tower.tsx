// Le sommet de la tour infinie : au-dessus d'une mer de nuages, en plein ciel. Des îles flottent (leurs cascades se
// perdent dans le vide), une arche en ruine se dresse au fond avec son cristal suspendu ; on se bat sur la terrasse de
// marbre du sommet, ses signes luisent de bleu. Les îles montent et descendent, le cristal respire, des nuages filent.
import { CLOUD_A, CLOUD_B, CLOUD_C, Cloud, CloudGrad, Flagstones, GLYPHS, Oak, Platform, RGrad, VGrad, W, cloudSprite, f } from './kit';
import { Column, glowSprite } from './props';
import type { Ctx, Scene, Sprite } from './core';

function sky(c: Ctx) {
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#2462c8'], [0.45, '#6aaee8'], [0.82, '#c4e6fa'], [1, '#e6f4ff']]} />
        <RGrad id="sun" stops={[[0, '#ffffff', 0.95], [0.3, '#fff8e0', 0.5], [1, '#fff8e0', 0]]} />
        <CloudGrad id="k-cloud" top="#ffffff" mid="#eef6fd" low="#c8dcf0" />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <circle cx="600" cy={Math.max(110, c.hz * 0.22)} r="220" fill="url(#sun)" />
      {/* la mer de nuages, sous l'horizon : on est plus haut qu'eux */}
      {[[-80, 3.4, CLOUD_C, 126], [180, 2.8, CLOUD_A, 90], [330, 3.6, CLOUD_C, 126], [580, 3, CLOUD_A, 90]].map(([x, s, lobes, w], i) => (
        <g transform={`translate(${x} ${c.hz + 30 - (i % 2) * 18}) scale(${s})`}><Cloud lobes={lobes as [number, number, number][]} w={w as number} /></g>
      ))}
    </>
  );
}

function land(c: Ctx) {
  const { hz, bottom, p0, p1 } = c;
  const ax = 360, ay = p0 - 4;
  return (
    <>
      <defs>
        <VGrad id="marble" y0={c.p0} y1={c.p1} stops={[[0, '#d6e2f2'], [1, '#f2f6fc']]} />
        <VGrad id="below" y0={c.p1} y1={c.bottom} stops={[[0, '#c8dcf0'], [1, '#e6f2fc']]} />
        <VGrad id="arch" y0={0} y1={1} stops={[[0, '#f6f2e8'], [1, '#c8c2b4']]} />
      </defs>
      {/* l'arche en ruine au fond : deux piliers, un arc brisé */}
      <Column x={ax - 92} y={ay} w={30} h={190} lit="#ffffff" mid="#e6e2d6" dark="#b0aa9c" ivy />
      <Column x={ax + 92} y={ay} w={30} h={150} broken lit="#ffffff" mid="#e6e2d6" dark="#b0aa9c" />
      <path d={`M${ax - 114} ${ay - 186} Q${ax - 100} ${ay - 270} ${ax - 10} ${ay - 278} L${ax + 4} ${ay - 262} L${ax - 8} ${ay - 250} Q${ax - 80} ${ay - 244} ${ax - 72} ${ay - 186} Z`} fill="url(#arch)" />
      <path d={`M${ax - 114} ${ay - 186} Q${ax - 100} ${ay - 270} ${ax - 10} ${ay - 278}`} fill="none" stroke="#ffffff" stroke-width="3" />
      <path d={`M${ax - 72} ${ay - 186} Q${ax - 80} ${ay - 244} ${ax - 8} ${ay - 250}`} fill="none" stroke="#a8a294" stroke-width="2" />
      {/* la terrasse : marbre clair, signes bleus gravés sur son flanc ; sous elle, le vide et les nuages */}
      <rect y={p1} width={W} height={bottom - p1 + 20} fill="url(#below)" />
      <Platform y0={p0} y1={p1} th={34} top="url(#marble)" face="#b8c6dc" faceDark="#9aaac4" lip="#ffffff" back="#6a8ab0"
        faceArt={<>{Array.from({ length: 12 }, (_, i) => <path d={GLYPHS[(i * 7) % GLYPHS.length]} fill="none" stroke="#3aa8ff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(30 + i * 60)} ${p1 + 17}) scale(1.5)`} />)}</>}>
        <Flagstones seed={26} y0={p0} y1={p1} rows={4} line="#b8c8dc" light="#ffffff" lightOpacity={0.4} />
        <path d={`M-20 ${(p0 + p1) / 2} H${W + 20}`} stroke="#5ab8ff" stroke-width="3" opacity="0.5" />
      </Platform>
      {/* deux colonnes cassées sur les bords de la terrasse, posées sur sa marge du fond */}
      <Column x={36} y={p0 + 6} w={36} h={150} broken ivy lit="#ffffff" mid="#e6e2d6" dark="#b0aa9c" />
      <Column x={690} y={p0 + 6} w={38} h={120} broken lit="#ffffff" mid="#e6e2d6" dark="#b0aa9c" />
      <Oak x={110} y={p0 + 2} s={0.9} /><Oak x={612} y={p0 + 2} s={0.8} />
    </>
  );
}

function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <defs><CloudGrad id="k-cloud" top="#ffffff" mid="#f2f8fe" low="#d8e8f6" /></defs>
      <g transform={`translate(-60 ${b + 14}) scale(1.8)`}><Cloud lobes={CLOUD_A} w={90} /></g>
      <g transform={`translate(560 ${b + 18}) scale(2)`}><Cloud lobes={CLOUD_B} w={62} /></g>
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  /** Une île flottante : dessus herbeux, une ruine, un arbre ; dessous de roche en pointe ; une cascade qui tombe et se perd. */
  const island = (w: number, ruin: boolean) => ({
    w: w + 40, h: w * 1.1,
    draw: () => {
      const cx = (w + 40) / 2, top = w * 0.32;
      return (
        <g>
          <defs><linearGradient id="fall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" /><stop offset="1" stop-color="#ffffff" stop-opacity="0" /></linearGradient></defs>
          <path d={`M${cx - w / 2} ${top} Q${cx - w * 0.3} ${top + w * 0.5} ${cx - w * 0.06} ${top + w * 0.72} Q${cx + w * 0.05} ${top + w * 0.6} ${cx + w * 0.16} ${top + w * 0.66} Q${cx + w * 0.34} ${top + w * 0.36} ${cx + w / 2} ${top} Z`} fill="#8a7a6a" />
          <path d={`M${cx + w * 0.05} ${top + w * 0.6} Q${cx + w * 0.16} ${top + w * 0.66} ${cx + w * 0.16} ${top + w * 0.66} Q${cx + w * 0.34} ${top + w * 0.36} ${cx + w / 2} ${top} H${cx + w * 0.1} Z`} fill="#b8a690" />
          <path d={`M${cx - w / 2 - 4} ${top + 2} Q${cx} ${top - 14} ${cx + w / 2 + 4} ${top + 2} Q${cx} ${top + 12} ${cx - w / 2 - 4} ${top + 2} Z`} fill="#5aa860" />
          <path d={`M${cx - w / 2 - 4} ${top + 2} Q${cx} ${top - 14} ${cx + w / 2 + 4} ${top + 2} Q${cx} ${top - 6} ${cx - w / 2 - 4} ${top + 2} Z`} fill="#8ad08a" />
          <rect x={cx + w * 0.28} y={top + 4} width="7" height={w * 0.7} fill="url(#fall)" opacity="0.9" />
          {ruin
            ? <g><rect x={cx - w * 0.3} y={top - 46} width="12" height="46" fill="#f2eee2" /><rect x={cx - w * 0.3 - 3} y={top - 50} width="18" height="6" fill="#ffffff" /><rect x={cx - w * 0.1} y={top - 30} width="12" height="30" fill="#e2ddd0" /></g>
            : <g><circle cx={cx - w * 0.1} cy={top - 22} r="16" fill="#3f8a50" /><circle cx={cx - w * 0.04} cy={top - 28} r="11" fill="#6ab872" /><rect x={cx - w * 0.12} y={top - 10} width="4" height="10" fill="#6a4a30" /></g>}
        </g>
      );
    },
  });
  const iA = island(150, true), iB = island(100, false), iC = island(70, true);
  const cA = cloudSprite(CLOUD_A, 90, 1.6), cB = cloudSprite(CLOUD_B, 62, 1.2);
  const ay = c.p0 - 4;
  return [
    { id: 'islandA', ...iA, at: [[120, Math.max(250, c.hz * 0.42)]], depth: -27, anim: { k: 'bob', amp: 10, period: 7 } },
    { id: 'islandB', ...iB, at: [[610, Math.max(200, c.hz * 0.32)]], depth: -27, anim: { k: 'bob', amp: 8, period: 6 } },
    { id: 'islandC', ...iC, at: [[430, Math.max(240, c.hz * 0.24)]], depth: -28, anim: { k: 'bob', amp: 6, period: 8 }, alpha: 0.8 },
    { id: 'cloudA', ...cA, at: [[300, Math.max(200, c.hz * 0.52)], [800, Math.max(170, c.hz * 0.2)]], depth: -26, anim: { k: 'drift', speed: 9, from: -300, to: 1020 } },
    { id: 'cloudB', ...cB, at: [[40, Math.max(170, c.hz * 0.16)]], depth: -28, anim: { k: 'drift', speed: 6, from: -300, to: 1020 }, alpha: 0.85 },
    // le cristal suspendu sous l'arche, et sa lueur
    {
      id: 'crystal', w: 40, h: 70, at: [[340, ay - 150]], depth: -18, anim: { k: 'bob', amp: 8, period: 4 },
      draw: () => <g><path d="M20 0 L36 26 L20 70 L4 26 Z" fill="#7ad0ff" /><path d="M20 0 L36 26 L20 70 Z" fill="#c8f0ff" /><path d="M20 0 L4 26 L20 30 Z" fill="#ffffff" opacity="0.7" /></g>,
    },
    { id: 'cglow', ...glowSprite(180, '#7ad0ff', 0.6), at: [[340, ay - 150]], depth: -19, anim: { k: 'pulse', min: 0.4, period: 4 }, add: true },
    { id: 'runes', ...glowSprite(110, '#3aa8ff', 0.45), at: [[90, c.p1 + 17], [330, c.p1 + 17], [570, c.p1 + 17]], depth: -14, anim: { k: 'pulse', min: 0.2, period: 3 }, add: true },
    { id: 'wisp', ...cloudSprite(CLOUD_C, 126, 1.5), at: [[200, c.bottom - 6]], depth: 1301, anim: { k: 'drift', speed: 10, from: -300, to: 1020 }, alpha: 0.85 },
  ];
}

export const TOWER: Scene = {
  base: 0xc8dcf0,
  sky, land, front, sprites,
  particles: (c) => [
    {
      id: 'mote', size: 12, area: [0, c.p0 - 40, W, c.p1], depth: -11, vx: [-4, 4], vy: [-26, -12], life: [5000, 8000], count: 12, scale: [0.4, 0.9], alpha: [0.2, 0.9], add: true,
      draw: () => <><defs><RGrad id="m" stops={[[0, '#ffffff'], [0.35, '#8ad8ff', 0.7], [1, '#8ad8ff', 0]]} /></defs><circle cx="6" cy="6" r="6" fill="url(#m)" /></>,
    },
  ],
};
