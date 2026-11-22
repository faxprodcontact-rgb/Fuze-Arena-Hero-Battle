// La prairie (premières régions de la campagne) : un jour d'été. Le soleil à droite et son cercle de signes, les grands
// sommets enneigés, les collines boisées, le moulin sur sa colline et le hameau qui fume ; devant, la lisière de la forêt,
// une clôture, des meules, et la clairière de terre battue où l'on se bat. Lumière venue de la droite.
import { At, Bush, CLOUD_A, CLOUD_B, CLOUD_C, Cloud, CloudGrad, FaceStones, Flowers, GlyphRing, Oak, Overhang, Peak, Pebbles, Pine, Platform, RGrad, VGrad, W, bump, canopy, cloudSprite, curve, forest, rng, tufts } from './kit';
import type { Ctx, Scene, Sprite } from './core';

const sunAt = (c: Ctx) => ({ x: 566, y: Math.max(112, Math.min(c.hz * 0.31, c.hz - 290)) });

/** La colline du hameau (à gauche) et celle du moulin (à droite) : y de leur crête en chaque x. */
const hamletHill = (hz: number) => (x: number) => hz + 2 - bump(x, 120, 170, 66) - bump(x, 250, 80, 10);
const millHill = (hz: number) => (x: number) => hz + 2 - bump(x, 610, 150, 80) - bump(x, 720, 90, 20);
/** Le pied du moulin, sur la crête de sa colline. */
const millBase = (c: Ctx) => millHill(c.hz)(609) + 3;
/** Une maison large de w posée sur une pente : son pied au point le plus bas sous elle, pour qu'il ne flotte jamais. */
const onHill = (fn: (x: number) => number, x: number, w: number) => Math.max(fn(x), fn(x + w), fn(x + w / 2)) + 2;
const HOUSES: [number, number, string][] = [[52, 22, '#c9503f'], [86, 18, '#4a76b8'], [150, 22, '#d99a3a']];

/** Une maison du hameau : mur d'ombre à gauche, toit qui déborde, cheminée, porte. */
function House({ x, y, w, roof }: { x: number; y: number; w: number; roof: string }) {
  const h = w * 0.62;
  return (
    <g>
      <ellipse cx={x + w * 0.3} cy={y + 1} rx={w * 0.75} ry="2.6" fill="#123a2a" opacity="0.25" />
      <rect x={x + w * 0.62} y={y - h - w * 0.5} width={w * 0.13} height={w * 0.3} fill="#a99a80" />
      <rect x={x} y={y - h} width={w} height={h} fill="#f6efdc" /><rect x={x} y={y - h} width={w * 0.36} height={h} fill="#cdbfa3" />
      <path d={`M${x - w * 0.12} ${y - h + 1} L${x + w / 2} ${y - h - w * 0.5} L${x + w * 1.12} ${y - h + 1} Z`} fill={roof} />
      <path d={`M${x + w / 2} ${y - h - w * 0.5} L${x + w * 1.12} ${y - h + 1} H${x + w / 2 + 1} Z`} fill="#fff" opacity="0.22" />
      <rect x={x + w * 0.56} y={y - h * 0.62} width={w * 0.2} height={h * 0.62} fill="#5e4026" />
      <rect x={x + w * 0.12} y={y - h * 0.72} width={w * 0.16} height={w * 0.16} fill="#ffd98a" opacity="0.8" />
    </g>
  );
}

/** Une meule de foin, roulée : face ronde à droite (éclairée), dessus clair, spirale. */
function Bale({ x, y, s }: { x: number; y: number; s: number }) {
  return (
    <At x={x} y={y} s={s}>
      <ellipse cx="-4" cy="2" rx="34" ry="6" fill="#123a2a" opacity="0.3" />
      <path d="M-30 0 V-34 Q-30 -40 -22 -40 H14 V0 Z" fill="#c99a3a" />
      <path d="M-30 -30 Q-8 -36 14 -32 V-40 H-22 Q-30 -40 -30 -34 Z" fill="#f0cf6a" />
      <ellipse cx="14" cy="-20" rx="14" ry="20" fill="#e8c35a" />
      <path d="M14 -34 Q24 -26 20 -16 Q16 -8 10 -14 Q8 -22 15 -22" fill="none" stroke="#b8862a" stroke-width="2" stroke-linecap="round" />
      <path d="M-26 -12 H8 M-24 -22 H8" stroke="#a8802a" stroke-width="1.5" opacity="0.6" />
    </At>
  );
}

/** Un tronçon de clôture de bois : poteaux (ombre à gauche) et deux lisses. */
function Fence({ x0, x1, y, h = 40 }: { x0: number; x1: number; y: number; h?: number }) {
  const posts: number[] = [];
  for (let x = x0; x <= x1; x += 52) posts.push(x);
  return (
    <g>
      <path d={`M${x0 - 6} ${y + 2} H${x1 + 6}`} stroke="#123a2a" stroke-width="5" opacity="0.18" />
      {[0.32, 0.66].map((k) => (
        <g>
          <rect x={x0} y={y - h * k - 4} width={x1 - x0} height="8" fill="#9a6a3a" />
          <rect x={x0} y={y - h * k - 4} width={x1 - x0} height="2.6" fill="#d9a96a" />
        </g>
      ))}
      {posts.map((x) => (
        <g>
          <rect x={x - 5} y={y - h} width="10" height={h} fill="#b07a44" /><rect x={x - 5} y={y - h} width="4" height={h} fill="#7a5230" />
          <path d={`M${x - 6} ${y - h} L${x} ${y - h - 6} L${x + 6} ${y - h} Z`} fill="#d9a96a" />
        </g>
      ))}
    </g>
  );
}

function sky(c: Ctx) {
  const sun = sunAt(c);
  return (
    <>
      <defs>
        <VGrad id="sky" y0={0} y1={c.hz} stops={[[0, '#1a58bc'], [0.38, '#3b8ce0'], [0.76, '#a2d8f4'], [1, '#e6f6fc']]} />
        <RGrad id="bloom" stops={[[0, '#fffdf0', 0.92], [0.3, '#ffffff', 0.42], [0.65, '#ffffff', 0.13], [1, '#ffffff', 0]]} />
        <RGrad id="sun" stops={[[0, '#fffef4'], [0.5, '#fff7cf'], [0.82, '#ffeeb0'], [1, '#ffeeb0', 0]]} />
      </defs>
      <rect width={W} height={c.hz + 60} fill="url(#sky)" />
      <circle cx={sun.x} cy={sun.y} r="270" fill="url(#bloom)" />
      <circle cx={sun.x} cy={sun.y} r="46" fill="url(#sun)" />
      {/* un banc de cumulus qui monte derrière les montagnes */}
      <defs><CloudGrad id="k-cloud" top="#ffffff" mid="#eef5fc" low="#cfe0f2" /></defs>
      {[[-60, 2.6, CLOUD_C, 126], [170, 2.2, CLOUD_A, 90], [330, 2.9, CLOUD_C, 126], [560, 2.4, CLOUD_A, 90]].map(([x, k, lobes, w], i) => (
        <g transform={`translate(${x} ${c.hz - 120 - (i % 2) * 22 - liftOf(c) * 0.6}) scale(${k})`} opacity="0.95"><Cloud lobes={lobes as [number, number, number][]} w={w as number} /></g>
      ))}
    </>
  );
}

/** Sur un écran haut, le ciel s'allonge : les grands sommets montent avec lui (jusqu'à 120 px). */
const liftOf = (c: Ctx) => Math.max(0, Math.min(120, (c.hz - 480) * 0.4));

function land(c: Ctx) {
  const { hz, bottom, cx, p0, p1 } = c;
  const L = liftOf(c);
  return (
    <>
      <defs>
        <VGrad id="mist" y0={hz - 150} y1={hz - 70} stops={[[0, '#ffffff', 0], [1, '#ffffff', 0.7]]} />
        <VGrad id="stone" y0={0} y1={1} stops={[[0, '#fdf6e4'], [1, '#d6cab6']]} />
        <VGrad id="wood1" y0={hz - 92} y1={hz - 40} stops={[[0, '#9cc4c8'], [1, '#6fa7a6']]} />
        <VGrad id="wood2" y0={hz - 70} y1={hz - 30} stops={[[0, '#7fb8a6'], [1, '#4f9584']]} />
        <VGrad id="wood3" y0={hz - 30} y1={hz + 10} stops={[[0, '#6fc47a'], [0.5, '#4fa466'], [1, '#3a8656']]} />
        <VGrad id="floor" y0={hz} y1={bottom} stops={[[0, '#3f8a52'], [0.1, '#5aa868'], [0.5, '#7cc47e'], [1, '#6cb874']]} />
        <VGrad id="roof" y0={0} y1={1} stops={[[0, '#c9503f'], [1, '#8a3040']]} />
        <VGrad id="dirt" y0={c.p0} y1={c.p1} stops={[[0, '#c9a46c'], [0.35, '#dcbc84'], [1, '#e6c992']]} />
      </defs>
      {/* la chaîne lointaine, pâle, et ses neiges à peine marquées */}
      <path d={`M-20 ${hz - 50} L-20 ${hz - 120} L40 ${hz - 156} L84 ${hz - 128} L132 ${hz - 170} L180 ${hz - 132} L246 ${hz - 150} L300 ${hz - 118} L360 ${hz - 160} L420 ${hz - 124} L470 ${hz - 146} L530 ${hz - 116} L590 ${hz - 150} L650 ${hz - 120} L740 ${hz - 154} V${hz - 50} Z`} fill="#bcd3ee" />
      <path d={`M132 ${hz - 170} L180 ${hz - 132} L156 ${hz - 128} L152 ${hz - 150} Z M360 ${hz - 160} L420 ${hz - 124} L388 ${hz - 126} Z M590 ${hz - 150} L650 ${hz - 120} L620 ${hz - 124} Z M40 ${hz - 156} L84 ${hz - 128} L60 ${hz - 130} Z`} fill="#eef4fc" />
      {/* les grands sommets : face gauche bleu-violet, face droite tiédie par le soleil */}
      <Peak a={[176, hz - 262 - L]} l={52 - L * 0.4} r={300 + L * 0.3} by={hz - 56} ridge={[[186, hz - 228 - L * 0.9], [170, hz - 190 - L * 0.7], [192, hz - 144 - L * 0.45], [178, hz - 100 - L * 0.2], [196, hz - 56]]} snow={58 + L * 0.3} shade="#7c8fcc" lit="#d3ddf2" snowShade="#c6d4f0" />
      <Peak a={[318, hz - 200 - L * 0.5]} l={236} r={404} by={hz - 56} ridge={[[326, hz - 170 - L * 0.42], [312, hz - 134 - L * 0.3], [330, hz - 96 - L * 0.12], [320, hz - 56]]} snow={36 + L * 0.15} shade="#8698d2" lit="#dbe3f4" snowShade="#c6d4f0" />
      <Peak a={[668, hz - 236 - L * 0.8]} l={548 - L * 0.3} r={790} by={hz - 56} ridge={[[676, hz - 204 - L * 0.7], [660, hz - 166 - L * 0.5], [680, hz - 118 - L * 0.25], [668, hz - 56]]} snow={48 + L * 0.25} shade="#7c8fcc" lit="#d3ddf2" snowShade="#c6d4f0" />
      <Peak a={[28, hz - 196 - L * 0.6]} l={-70} r={128} by={hz - 56} ridge={[[36, hz - 166 - L * 0.5], [22, hz - 130 - L * 0.35], [40, hz - 92 - L * 0.15], [30, hz - 56]]} snow={38 + L * 0.2} shade="#8698d2" lit="#dbe3f4" snowShade="#c6d4f0" />
      {/* contreforts plus proches, quelques strates sur les grandes faces */}
      <path d={`M250 ${hz - 56} L300 ${hz - 150} L342 ${hz - 90} L336 ${hz - 56} Z`} fill="#6f84c2" /><path d={`M300 ${hz - 150} L342 ${hz - 90} L336 ${hz - 56} H380 Z`} fill="#b9c8e8" />
      <path d={`M560 ${hz - 56} L596 ${hz - 130} L626 ${hz - 84} L620 ${hz - 56} Z`} fill="#6f84c2" /><path d={`M596 ${hz - 130} L626 ${hz - 84} L620 ${hz - 56} H650 Z`} fill="#b9c8e8" />
      <g fill="#aebfe6" opacity="0.7"><path d={`M206 ${hz - 186} L228 ${hz - 158} L212 ${hz - 152} Z M690 ${hz - 170} L712 ${hz - 140} L696 ${hz - 136} Z M110 ${hz - 120} L126 ${hz - 98} L114 ${hz - 96} Z`} /></g>
      <rect y={hz - 150} width={W} height="90" fill="url(#mist)" opacity="0.65" />
      {/* les collines boisées et la forêt du fond : c'est elles qui donnent la profondeur */}
      <path d={canopy(2, hz - 60, 22, 8)} fill="url(#wood1)" />
      <path d={canopy(2, hz - 60, 22, 8, true)} fill="none" stroke="#c6e0de" stroke-width="2" opacity="0.8" />
      <path d={forest(5, hz - 44, 10, 24, 12, 20)} fill="url(#wood2)" />

      {/* la colline du moulin, à droite : le moulin, les champs et les arbres sont posés sur sa crête */}
      <path d={curve(millHill(hz), 430, 740, hz)} fill="#8fcf8c" />
      <path d={curve(millHill(hz), 430, 740, hz, true)} fill="none" stroke="#d3f2bc" stroke-width="2.4" />
      <path d={`M520 ${millHill(hz)(520) + 10} Q556 ${millHill(hz)(556) + 2} 590 ${millHill(hz)(590) + 6} L594 ${millHill(hz)(594) + 14} Q560 ${millHill(hz)(560) + 12} 530 ${millHill(hz)(530) + 20} Z`} fill="#e2d36c" />
      <path d={`M652 ${millHill(hz)(652) + 6} Q690 ${millHill(hz)(690) + 2} 724 ${millHill(hz)(724) + 8} L726 ${millHill(hz)(726) + 15} Q690 ${millHill(hz)(690) + 9} 654 ${millHill(hz)(654) + 13} Z`} fill="#c9dc6c" />
      {/* le moulin : tour de pierre qui s'affine, toit conique, porte ; ses ailes tournent (élément animé) */}
      <g transform={`translate(0 ${millBase(c) - (hz - 77)})`}>
        <ellipse cx="606" cy={hz - 76} rx="26" ry="4.5" fill="#123a2a" opacity="0.25" />
        <path d={`M592 ${hz - 75} L598 ${hz - 134} H620 L626 ${hz - 75} Z`} fill="url(#stone)" />
        <path d={`M592 ${hz - 75} L598 ${hz - 134} H605 L602 ${hz - 75} Z`} fill="#b8aa94" />
        <path d={`M594 ${hz - 134} L609 ${hz - 156} L624 ${hz - 134} Z`} fill="url(#roof)" /><path d={`M609 ${hz - 156} L624 ${hz - 134} H610 Z`} fill="#fff" opacity="0.2" />
        <path d={`M604 ${hz - 75} V${hz - 92} Q609 ${hz - 98} 614 ${hz - 92} V${hz - 75} Z`} fill="#4a3f36" />
        <rect x="606" y={hz - 120} width="6" height="8" rx="3" fill="#4a3f36" />
      </g>
      <Oak x={566} y={millHill(hz)(566) + 4} s={0.9} /><Oak x={668} y={millHill(hz)(668) + 4} s={0.7} />

      {/* la colline du hameau, à gauche : chaque maison a le pied dans l'herbe de la crête */}
      <path d={curve(hamletHill(hz), -20, 330, hz)} fill="#86c987" />
      <path d={curve(hamletHill(hz), -20, 330, hz, true)} fill="none" stroke="#cdeeb6" stroke-width="2.2" />
      {HOUSES.map(([x, w, roof]) => <House x={x} y={onHill(hamletHill(hz), x, w)} w={w} roof={roof} />)}
      <Oak x={128} y={hamletHill(hz)(128) + 4} s={0.7} /><Pine x={196} y={hamletHill(hz)(196) + 4} s={0.75} dark="#2f6d55" light="#4c9a6a" />

      {/* la lisière de la forêt, juste derrière l'arène : elle cache le pied des collines */}
      <path d={canopy(7, hz - 4, 10, 7)} fill="url(#wood3)" />
      <path d={canopy(7, hz - 4, 10, 7, true)} fill="none" stroke="#b6eaa0" stroke-width="2.4" opacity="0.85" />

      {/* le sol : la bande d'herbe derrière la plateforme, dans l'ombre des arbres */}
      <rect y={hz} width={W} height={bottom - hz} fill="url(#floor)" />
      {/* des arbres en avant de la lisière, les pieds dans l'herbe, derrière la plateforme */}
      <Pine x={22} y={p0 - 2} s={1.25} dark="#2f7a52" light="#58b070" /><Pine x={58} y={p0 - 8} s={0.95} dark="#2f7a52" light="#58b070" />
      <Oak x={250} y={p0 - 10} s={1} /><Pine x={474} y={p0 - 8} s={0.9} dark="#2f7a52" light="#58b070" />
      <Oak x={664} y={p0 - 6} s={1.1} /><Pine x={704} y={p0 - 2} s={1.2} dark="#2f7a52" light="#58b070" />
      <path d={tufts(4, hz + 12, 4, 16)} fill="#3f9058" />
      {/* la clôture et les meules, juste derrière la plateforme */}
      <Fence x0={92} x1={250} y={p0 - 1} h={36} /><Fence x0={482} x1={640} y={p0 - 1} h={36} />
      <Bale x={300} y={p0 - 2} s={0.75} /><Bale x={430} y={p0 - 3} s={0.68} />
      {/* la plateforme : une longue terrasse de terre battue, d'un bord à l'autre ; son talus de terre et de pierres devant */}
      <Platform y0={p0} y1={p1} th={28} top="url(#dirt)" face="#9a6a3a" faceDark="#7a5230" lip="#f2dcaa" back="#3a5a2a"
        faceArt={<>
          <FaceStones seed={41} y0={p1} y1={p1 + 28} color="#8a7a68" lit="#c2b49c" n={13} />
          <Overhang seed={37} y={p1 + 1} color="#5aa866" light="#7cc47e" />
        </>}>
        <Pebbles seed={3} x={cx} y={(p0 + p1) / 2 + 6} n={34} rx={360} ry={(p1 - p0) * 0.42} color="#a8916a" lit="#e8d6ae" k={1.25} />
      </Platform>
      {/* sous la plateforme, l'herbe : fleurs et touffes */}
      <path d={tufts(23, p1 + 48, 6, 22, 2.2)} fill="#4f9a5e" />
      <Flowers x={60} y={p1 + 52} s={1.5} /><Flowers x={250} y={p1 + 58} s={1.3} colors={['#ff9fb5', '#fff', '#ffd45c']} /><Flowers x={480} y={p1 + 54} s={1.4} />
    </>
  );
}

/** Le premier plan : buissons dans les coins du bas, herbes hautes, fleurs. Rien au-dessus des pieds du rang de devant. */
function front(c: Ctx) {
  const b = c.bottom;
  return (
    <>
      <Bush x={8} y={b - 6} s={2.3} /><Bush x={716} y={b - 2} s={2.5} flip />
      <Bush x={84} y={b + 10} s={1.5} dark="#2a6a46" mid="#3a8656" light="#62b070" />
      <path d={tufts(31, b - 4, 6, 22, 3)} fill="#3f9058" /><path d={tufts(33, b + 2, 6, 34, 3.6)} fill="#62b070" />
      <Flowers x={160} y={b - 14} s={2} /><Flowers x={566} y={b - 12} s={2} colors={['#ff9fb5', '#fff', '#ffd45c']} />
    </>
  );
}

function sprites(c: Ctx): Sprite[] {
  const sun = sunAt(c);
  const cA = cloudSprite(CLOUD_C, 126, 2.1), cB = cloudSprite(CLOUD_A, 90, 1.5), cC = cloudSprite(CLOUD_B, 62, 1.2);
  const hz = c.hz;
  return [
    { id: 'ring', w: 190, h: 190, draw: () => <g transform="translate(95 95)"><GlyphRing r={74} /></g>, at: [[sun.x, sun.y]], depth: -29, anim: { k: 'spin', period: 110 }, alpha: 0.7 },
    { id: 'cloudA', ...cA, at: [[40, Math.max(150, hz - 300)]], depth: -28, anim: { k: 'drift', speed: 5, from: -300, to: 1020 } },
    { id: 'cloudB', ...cB, at: [[420, Math.max(110, hz - 380)], [880, Math.max(170, hz - 230)]], depth: -28, anim: { k: 'drift', speed: 7.5, from: -300, to: 1020 }, scale: [1, 0.8], alpha: 0.92 },
    { id: 'cloudC', ...cC, at: [[260, Math.max(200, hz - 210)], [640, Math.max(90, hz * 0.18)]], depth: -28, anim: { k: 'drift', speed: 10, from: -300, to: 1020 }, alpha: 0.85, scale: [1, 0.7] },
    {
      id: 'balloon', w: 60, h: 92, at: [[300, Math.max(150, hz * 0.42)]], depth: -27, anim: { k: 'drift', speed: 3.2, from: -120, to: 860 },
      draw: () => (
        <g transform="translate(30 42)">
          <defs><linearGradient id="bl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a8322e" /><stop offset="0.45" stop-color="#e0564e" /><stop offset="0.8" stop-color="#f58a72" /><stop offset="1" stop-color="#d94f47" /></linearGradient></defs>
          <path d="M-9 31 L-5 41 M9 31 L5 41 M0 33 V41" stroke="#5e4026" stroke-width="1.4" />
          <path d="M-7 41 H7 L5.6 50 H-5.6 Z" fill="#9a6a38" /><path d="M-7 41 H7 L6.6 44 H-6.6 Z" fill="#c99556" />
          <path d="M0 -30 C23 -30 30 -12 26 3 C23 15 13 24 9 31 H-9 C-13 24 -23 15 -26 3 C-30 -12 -23 -30 0 -30 Z" fill="url(#bl)" />
          <path d="M-26 4 Q0 13 26 4 Q25 9 22.5 13 Q0 21 -22.5 13 Q-25 9 -26 4 Z" fill="#ffd45c" />
          <path d="M0 -3 l4.5 6 l-4.5 6 l-4.5 -6 Z" fill="#fff6c4" opacity="0.9" />
          <path d="M9 -26 C18 -20 22 -9 19.5 1.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" opacity="0.38" />
        </g>
      ),
    },
    {
      // le moyeu au sommet de la tour, juste sous le toit ; ailes assez courtes pour laisser voir la tour
      id: 'sails', w: 132, h: 132, origin: [0.5, 0.5], at: [[609, millBase(c) - 52]], scale: [0.74], depth: -19, anim: { k: 'spin', period: 14 },
      draw: () => (
        <g transform="translate(66 66)">
          {[0, 90, 180, 270].map((a) => (
            <g transform={`rotate(${a})`}>
              <path d="M0 0 V-60" stroke="#5e4026" stroke-width="3" stroke-linecap="round" />
              <path d="M2 -8 H16 V-58 H2 Z" fill="#f6efdc" stroke="#8f8068" stroke-width="1.2" />
              <path d="M2 -22 H16 M2 -36 H16 M2 -48 H16 M9 -8 V-58" stroke="#8f8068" stroke-width="1" />
            </g>
          ))}
          <circle r="4.5" fill="#5e4026" /><circle r="1.8" fill="#d9a96a" />
        </g>
      ),
    },
    {
      id: 'birds', w: 90, h: 40, at: [[180, Math.max(130, hz - 330)]], depth: -27, anim: { k: 'drift', speed: 16, from: -150, to: 900 },
      draw: () => (
        <g fill="none" stroke="#2f4a6a" stroke-linecap="round">
          <path d="M20 14 q7 -7 12 0 q5 -7 12 0" stroke-width="2.2" /><path d="M52 24 q5 -5 9 0 q4 -5 9 0" stroke-width="1.8" /><path d="M6 28 q5 -5 9 0 q4 -5 9 0" stroke-width="1.8" /><path d="M64 8 q4 -4 7 0 q3 -4 7 0" stroke-width="1.5" />
        </g>
      ),
    },
    // de l'herbe haute qui ondule devant, dans les coins
    {
      id: 'grass', w: 60, h: 70, origin: [0.5, 1], at: [[44, c.bottom + 4], [676, c.bottom + 6], [126, c.bottom + 8]], depth: 1301, anim: { k: 'sway', deg: 4, period: 3.6 }, scale: [1.2, 1.3, 0.9],
      draw: () => (
        <g>
          <path d="M30 70 Q24 40 8 10 Q30 36 34 70 Z" fill="#3f9058" /><path d="M32 70 Q36 34 52 4 Q42 40 38 70 Z" fill="#62b070" />
          <path d="M26 70 Q18 50 4 38 Q24 48 32 70 Z" fill="#58a868" /><path d="M36 70 Q44 48 58 34 Q46 50 40 70 Z" fill="#3f9058" />
        </g>
      ),
    },
  ];
}

export const MEADOW: Scene = {
  base: 0x7cc586,
  sky, land, front, sprites,
  particles: (c) => [
    // la fumée d'une cheminée du hameau
    {
      id: 'smoke', size: 16, area: [86 + 18 * 0.62, onHill(hamletHill(c.hz), 86, 18) - 18 * 0.62 - 9 - 4, 86 + 18 * 0.62 + 2, onHill(hamletHill(c.hz), 86, 18) - 18 * 0.62 - 9], depth: -19, vx: [2, 6], vy: [-14, -9], life: [3200, 4600], count: 7, scale: [0.6, 1.8], alpha: [0, 0.5],
      draw: () => <><defs><RGrad id="s" stops={[[0, '#ffffff', 0.9], [1, '#ffffff', 0]]} /></defs><circle cx="8" cy="8" r="8" fill="url(#s)" /></>,
    },
    // des papillons au-dessus de l'herbe, sur les côtés
    {
      id: 'fly', size: 12, area: [0, c.hz + 30, W, c.hz + 210], depth: -11, vx: [-18, 18], vy: [-8, 4], life: [5000, 8000], count: 6, scale: [0.8, 1], alpha: [0.3, 0.95],
      draw: () => <g><path d="M6 6 Q1 0 1 4 Q1 8 6 6 Z M6 6 Q11 0 11 4 Q11 8 6 6 Z" fill="#fff6c8" /><path d="M6 6 Q3 11 5 11 Z M6 6 Q9 11 7 11 Z" fill="#ffd45c" /></g>,
    },
  ],
};
