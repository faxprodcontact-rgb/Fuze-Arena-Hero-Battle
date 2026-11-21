// Le décor de la page d'un héros : un lieu par élément, dessiné par le code et animé.
//   Feu   : le pied d'un volcan, la nuit — cratère qui rougeoie, orgues de basalte, mares de lave, braises qui montent.
//   Vent  : un sanctuaire au-dessus des nuages — îles qui flottent, colonnes de marbre et leurs flammes d'étoffe, feuilles au vent.
//   Eau   : une grotte ouverte sur la mer — l'arche de roche, deux cascades, un bassin qui frissonne, des bulles.
//   Terre : un cirque de pierres au fond d'un canyon — mesas au loin, aiguilles de roche, pierres levées gravées, pollen.
// Le centre reste dégagé : c'est là que se tient le héros, sur son piédestal (`Pedestal`, posé par screens/hero-detail.tsx).
// Quatre dessins superposés, comme les autres décors : le fond ; ce qui bouge derrière ; les reliefs ; ce qui bouge devant.
import type { ComponentChildren } from 'preact';
import type { Element } from '../../core/types';
import './anim.css';
import { GLYPHS } from './backdrop-adventure';
import { spark } from './portal';

const W = 390, H = 844;
/** L'horizon : là où le sol commence. */
const HZ = 340;

function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}
const f = (n: number) => n.toFixed(1);

/** Une chaîne de reliefs fermée en bas : pics aigus (`flat` = 0) ou mesas à sommet plat (`flat` = part du sommet). */
function ridge(seed: number, base: number, hMin: number, hMax: number, wMin: number, wMax: number, flat = 0): string {
  const r = rng(seed);
  let x = -16, d = `M-16 ${base + 40} L-16 ${base}`;
  while (x < W + 16) {
    const w = wMin + r() * (wMax - wMin), h = hMin + r() * (hMax - hMin);
    if (flat) d += ` L${f(x + w * 0.12)} ${f(base - h)} L${f(x + w * (0.12 + flat))} ${f(base - h - 3 * r())} L${f(x + w * (0.3 + flat))} ${f(base - h * 0.25 * r())}`;
    else d += ` L${f(x + w * (0.4 + r() * 0.2))} ${f(base - h)} L${f(x + w)} ${f(base - h * 0.2 * r())}`;
    x += w;
  }
  return `${d} L${W + 16} ${base + 40} Z`;
}

/** Un nuage en volume : un seul contour bombé, le dessous ombré. */
function Cloud({ x, y, s, fill, shade }: { x: number; y: number; s: number; fill: string; shade: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M-46 0 Q-52 -15 -34 -17 Q-30 -34 -8 -29 Q6 -44 26 -31 Q46 -33 46 -15 Q58 -11 52 0 Z" fill={fill} />
      <path d="M-46 0 Q-50 -8 -40 -11 Q-16 -3 14 -7 Q40 -4 54 -8 Q56 -3 52 0 Z" fill={shade} opacity="0.55" />
    </g>
  );
}

/** Une gerbe de cristaux : trois éclats, une face claire, une face sombre. */
function Shards({ x, y, s, c, light, dark }: { x: number; y: number; s: number; c: string; light: string; dark: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M-13 4 L-17 -14 L-11 -22 L-5 -12 L-3 4 Z" fill={c} /><path d="M-11 -22 L-5 -12 L-3 4 L-7 4 L-9 -10 Z" fill={light} />
      <path d="M-3 4 L-4 -24 L3 -37 L9 -22 L8 4 Z" fill={c} /><path d="M3 -37 L9 -22 L8 4 L3 4 L4 -20 Z" fill={light} /><path d="M-3 4 L-4 -24 L3 -37 L1 -20 L0 4 Z" fill={dark} opacity="0.55" />
      <path d="M8 4 L9 -11 L15 -17 L19 -8 L17 4 Z" fill={c} /><path d="M15 -17 L19 -8 L17 4 L13 4 L14 -8 Z" fill={light} />
    </g>
  );
}

/** Des particules qui montent (braises, bulles, pollen) : `ring` = des bulles creuses. */
function Rise({ seed, n, colors, y0, y1, ring = false, rMin = 1, rMax = 2.4 }: { seed: number; n: number; colors: string[]; y0: number; y1: number; ring?: boolean; rMin?: number; rMax?: number }) {
  const r = rng(seed);
  return (
    <>
      {Array.from({ length: n }, (_, i) => {
        const x = 8 + r() * (W - 16), y = y0 + r() * (y1 - y0), k = rMin + r() * (rMax - rMin), c = colors[i % colors.length]!;
        const st = { animationDelay: `${(-r() * 9).toFixed(1)}s`, animationDuration: `${(5.5 + r() * 6).toFixed(1)}s` };
        return ring
          ? <circle class="bd-mote" style={st} cx={f(x)} cy={f(y)} r={f(k)} fill={c} fill-opacity="0.18" stroke={c} stroke-width="0.900" />
          : <circle class="bd-mote" style={st} cx={f(x)} cy={f(y)} r={f(k)} fill={c} />;
      })}
    </>
  );
}

type Layers = { Back: () => ComponentChildren; Mid: () => ComponentChildren; Front: () => ComponentChildren; Top: () => ComponentChildren };

// ---------------------------------------------------------------- Feu : le pied du volcan

/** Un orgue de basalte : un fût à pans, sa face tournée vers la lave éclairée. `side` = 1 si la lave est à sa droite. */
function Basalt({ x, y, w, h, side }: { x: number; y: number; w: number; h: number; side: number }) {
  const a = w * 0.34, e = w * 0.3;
  return (
    <g transform={`translate(${x} ${y}) scale(${side} 1)`}>
      <path d={`M${-w / 2} 0 V${-h + a * 0.5} L${-w / 2 + a} ${-h} H${w / 2 - a * 0.6} L${w / 2} ${-h + a * 0.7} V0 Z`} fill="#170810" />
      <path d={`M${w / 2 - e} ${-h + a * 0.9} L${w / 2} ${-h + a * 0.7} V0 H${w / 2 - e} Z`} fill="url(#hs-f-face)" />
      <path d={`M${-w / 2} ${-h + a * 0.5} L${-w / 2 + a} ${-h} H${w / 2 - a * 0.6} L${w / 2} ${-h + a * 0.7} L${w / 2 - e} ${-h + a * 0.9} H${-w / 2 + a * 0.5} Z`} fill="#3a1420" />
      <path d={`M${-w / 2 + a * 0.5} ${-h + a * 0.9} V0`} stroke="#000" stroke-width="1" opacity="0.35" />
      <path d={`M${w / 2 - 0.600} ${-h + a * 0.7} V0`} stroke="#ffa04a" stroke-width="1.200" opacity="0.9" />
    </g>
  );
}
const ORGANS: [number, number, number, number][] = [[14, 372, 30, 190], [42, 380, 26, 142], [66, 386, 22, 96], [-4, 392, 24, 120], [376, 372, 30, 204], [348, 380, 26, 150], [324, 386, 22, 104], [394, 392, 24, 130]];

const FIRE: Layers = {
  Back: () => (
    <>
      <defs>
        <linearGradient id="hs-f-sky" x1="0" y1="0" x2="0" y2={HZ} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#10050c" /><stop offset="0.45" stop-color="#3a0e16" /><stop offset="0.8" stop-color="#8a2416" /><stop offset="1" stop-color="#ff7a2a" /></linearGradient>
        <linearGradient id="hs-f-ground" x1="0" y1={HZ} x2="0" y2="640" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#8a2a18" /><stop offset="0.12" stop-color="#4a1614" /><stop offset="0.45" stop-color="#260a10" /><stop offset="1" stop-color="#12050a" /></linearGradient>
        <linearGradient id="hs-f-cone" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a1018" /><stop offset="0.5" stop-color="#1c0810" /><stop offset="1" stop-color="#2a0c14" /></linearGradient>
        <radialGradient id="hs-f-ash"><stop offset="0" stop-color="#5a1a1c" stop-opacity="0.8" /><stop offset="1" stop-color="#5a1a1c" stop-opacity="0" /></radialGradient>
      </defs>
      <rect y="-40" width={W} height={HZ + 40} fill="url(#hs-f-sky)" />
      <ellipse cx="80" cy="96" rx="150" ry="60" fill="url(#hs-f-ash)" /><ellipse cx="330" cy="150" rx="140" ry="56" fill="url(#hs-f-ash)" /><ellipse cx="200" cy="30" rx="190" ry="50" fill="url(#hs-f-ash)" />
      {/* le volcan : décentré, flancs inégaux, lèvre ébréchée ; son flanc gauche prend la lueur de la coulée */}
      <path d="M-30 346 L26 268 L58 236 L80 196 L98 166 L110 158 L120 166 L132 154 L146 160 L156 150 L168 164 L186 196 L214 228 L236 262 L262 286 L306 346 Z" fill="url(#hs-f-cone)" />
      <path d="M-30 346 L26 268 L58 236 L80 196 L98 166 L110 158 L120 166 L112 196 L92 240 L60 290 L36 346 Z" fill="#5a1a1e" opacity="0.85" />
      <path d="M168 164 L186 196 L214 228 L236 262 L262 286 L306 346 H250 L222 290 L196 240 L176 200 Z" fill="#12050a" opacity="0.6" />
      <path d="M98 166 L110 158 L120 166 L132 154 L146 160 L156 150 L168 164" fill="none" stroke="#ffa04a" stroke-width="2.200" stroke-linejoin="round" stroke-linecap="round" />
      <path d={ridge(3, HZ, 22, 64, 30, 60)} fill="#1c0810" /><path d={ridge(9, HZ + 4, 10, 34, 22, 44)} fill="#12050a" />
      <rect y={HZ} width={W} height={H} fill="url(#hs-f-ground)" />
    </>
  ),
  Mid: () => (
    <>
      <defs>
        <radialGradient id="hs-f-crater"><stop offset="0" stop-color="#fff3b0" stop-opacity="0.95" /><stop offset="0.35" stop-color="#ff8a2a" stop-opacity="0.6" /><stop offset="1" stop-color="#ff5a1a" stop-opacity="0" /></radialGradient>
        <radialGradient id="hs-f-smoke"><stop offset="0" stop-color="#6a2a24" stop-opacity="0.55" /><stop offset="1" stop-color="#6a2a24" stop-opacity="0" /></radialGradient>
        <linearGradient id="hs-f-flow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe08a" /><stop offset="0.35" stop-color="#ff9a2a" /><stop offset="1" stop-color="#d8401a" /></linearGradient>
      </defs>
      {/* le cratère rougeoie ; son panache monte et dérive, en volume */}
      <ellipse class="bd-sun" cx="134" cy="158" rx="84" ry="62" fill="url(#hs-f-crater)" />
      <g class="bd-cloud bd-slow"><Cloud x={150} y={118} s={0.800} fill="#5a2026" shade="#2a0c14" /><Cloud x={186} y={78} s={1.150} fill="#4a181e" shade="#22080e" /><Cloud x={236} y={34} s={1.500} fill="#3a1218" shade="#1a060c" /></g>
      {[[128, 150, 0], [142, 140, -2], [134, 132, -4]].map(([x, y, d]) => <circle class="ad-smoke" style={{ animationDelay: `${d}s`, animationDuration: '6s' }} cx={x} cy={y} r="15" fill="url(#hs-f-smoke)" />)}
      {/* la coulée : large, elle s'étale en descendant le flanc gauche, loin du héros */}
      <path d="M112 164 L124 166 L118 196 Q110 228 92 256 Q72 290 66 346 H22 Q40 292 70 250 Q96 214 104 188 Z" fill="url(#hs-f-flow)" />
      <path class="ts-pulse" d="M118 168 Q112 204 98 234 Q76 272 52 344" fill="none" stroke="#fff3b0" stroke-width="3" stroke-linecap="round" opacity="0.9" />
      <path d="M124 166 L118 196 Q110 228 92 256 Q72 290 66 346" fill="none" stroke="#5a1410" stroke-width="1.600" opacity="0.7" />
    </>
  ),
  Front: () => (
    <>
      <defs>
        <linearGradient id="hs-f-face" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1018" /><stop offset="0.55" stop-color="#6a1e16" /><stop offset="1" stop-color="#b8401a" /></linearGradient>
        <radialGradient id="hs-f-pool"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.4" stop-color="#ffa02a" /><stop offset="0.85" stop-color="#d8401a" /><stop offset="1" stop-color="#5a1410" /></radialGradient>
        <radialGradient id="hs-f-lit" cx="195" cy="420" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(195 420) scale(210 70) translate(-195 -420)"><stop offset="0" stop-color="#ff9a4a" stop-opacity="0.42" /><stop offset="1" stop-color="#ff9a4a" stop-opacity="0" /></radialGradient>
      </defs>
      <rect y={HZ} width={W} height="200" fill="url(#hs-f-lit)" />
      {/* les mares de lave, cernées de croûte noire */}
      {[[44, 420, 62, 11], [352, 432, 70, 12], [118, 366, 30, 5], [286, 362, 26, 4.500]].map(([x, y, rx, ry]) => (
        <g><ellipse cx={x} cy={y! + 1.500} rx={rx! + 5} ry={ry! + 2.500} fill="#14060a" /><ellipse cx={x} cy={y} rx={rx} ry={ry} fill="url(#hs-f-pool)" /></g>
      ))}
      {/* les orgues de basalte, de chaque côté */}
      {ORGANS.map(([x, y, w, h]) => <Basalt x={x} y={y} w={w} h={h} side={x < 195 ? 1 : -1} />)}
      <path d="M-10 640 L-10 520 L22 500 L52 526 L70 560 L96 640 Z M400 640 L400 512 L370 494 L338 524 L318 566 L296 640 Z" fill="#0c0408" />
      <path d="M22 500 L52 526 L70 560 L60 566 L44 536 Z M370 494 L338 524 L318 566 L328 570 L346 534 Z" fill="#5a1a14" opacity="0.8" />
    </>
  ),
  Top: () => (
    <>
      <defs><radialGradient id="hs-f-glow"><stop offset="0" stop-color="#ffb04a" stop-opacity="0.7" /><stop offset="1" stop-color="#ff7a1a" stop-opacity="0" /></radialGradient></defs>
      <ellipse class="an-glow" cx="44" cy="414" rx="74" ry="26" fill="url(#hs-f-glow)" /><ellipse class="an-glow an-late" cx="352" cy="426" rx="82" ry="28" fill="url(#hs-f-glow)" />
      <Rise seed={5} n={22} colors={['#ffd24a', '#ff8a2a', '#fff3b0']} y0={240} y1={520} rMin={0.900} rMax={2.200} />
      {[[70, 250, 4], [318, 228, 3.500], [250, 120, 3]].map(([x, y, k], i) => <path class={`an-twinkle ${i % 2 ? 'an-late' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, k!)} fill="#ffe08a" />)}
    </>
  ),
};

// ---------------------------------------------------------------- Vent : le sanctuaire des cimes

/** Une île qui flotte : herbe dessus, roche claire dessous. */
function SkyIsland({ x, y, s }: { x: number; y: number; s: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M-34 0 H34 L26 12 L18 9 L12 26 L4 16 L-4 36 L-12 18 L-20 22 L-27 8 Z" fill="#5f8f9c" /><path d="M-34 0 H-6 L-12 18 L-20 22 L-27 8 Z" fill="#3f6f80" /><path d="M10 0 H34 L26 12 L18 9 L12 26 L6 14 Z" fill="#9fd0d0" />
      <path d="M-36 0 Q-20 -9 0 -7 Q22 -10 36 0 L33 4 Q0 -2 -33 4 Z" fill="#4fae6a" /><path d="M-36 0 Q-20 -9 0 -7 Q22 -10 36 0 L35 1.500 Q0 -5 -35 1.500 Z" fill="#b8f09a" />
      <path d="M-10 -7 Q-9 -20 0 -22 Q9 -20 10 -8 Z" fill="#3f9a5a" /><path d="M0 -22 Q9 -20 10 -8 L4 -8 Q5 -16 0 -22 Z" fill="#8fe08a" />
    </g>
  );
}

/** Une colonne de marbre brisée, sa flamme d'étoffe qui claque au vent. `side` = 1 si le soleil est à sa droite. */
function Marble({ x, y, h, side }: { x: number; y: number; h: number; side: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${side} 1)`}>
      <ellipse cx="2" cy="1" rx="22" ry="5" fill="#1f5a48" opacity="0.5" />
      <path d={`M-13 0 V${-h + 8} L-7 ${-h} L2 ${-h + 5} L9 ${-h - 2} L13 ${-h + 6} V0 Z`} fill="#eaf8f2" />
      <path d={`M-13 0 V${-h + 8} L-7 ${-h} L-4 ${-h + 3} V0 Z`} fill="#8fbcb4" /><path d={`M7 0 V${-h + 1} L9 ${-h - 2} L13 ${-h + 6} V0 Z`} fill="#fffbe6" />
      <path d={`M-13 ${-h * 0.36} H13 M-13 ${-h * 0.68} H13`} stroke="#7fb0a8" stroke-width="1" opacity="0.7" />
      <path d="M-17 0 H17 V-7 H-17 Z" fill="#cfe8e0" /><path d="M-17 -7 H17 V-9 H-17 Z" fill="#fff" /><path d="M-17 0 H-8 V-7 H-17 Z" fill="#8fbcb4" />
    </g>
  );
}

const WIND: Layers = {
  Back: () => (
    <>
      <defs>
        <linearGradient id="hs-w-sky" x1="0" y1="0" x2="0" y2={HZ} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#1c6480" /><stop offset="0.45" stop-color="#3fa8a8" /><stop offset="0.82" stop-color="#a8e8c0" /><stop offset="1" stop-color="#f4ffd8" /></linearGradient>
        <linearGradient id="hs-w-ground" x1="0" y1={HZ} x2="0" y2="640" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#b8f09a" /><stop offset="0.1" stop-color="#6fc878" /><stop offset="0.45" stop-color="#3a8a5e" /><stop offset="1" stop-color="#1c4a44" /></linearGradient>
        <radialGradient id="hs-w-sun"><stop offset="0" stop-color="#fffbe0" stop-opacity="0.95" /><stop offset="0.3" stop-color="#f4ffd8" stop-opacity="0.5" /><stop offset="1" stop-color="#f4ffd8" stop-opacity="0" /></radialGradient>
      </defs>
      <rect y="-40" width={W} height={HZ + 40} fill="url(#hs-w-sky)" />
      <circle cx="300" cy="150" r="150" fill="url(#hs-w-sun)" />
      {/* une grande lune de jour, pâle */}
      <g opacity="0.75"><circle cx="300" cy="150" r="34" fill="#f4fff4" /><path d="M300 116 A34 34 0 0 1 300 184 A44 44 0 0 0 300 116 Z" fill="#a8dcd0" opacity="0.5" /><g fill="#b8e4d8" opacity="0.7"><circle cx="288" cy="140" r="6" /><circle cx="306" cy="162" r="4.500" /><circle cx="294" cy="166" r="2.600" /></g></g>
      {/* la mer de nuages, au loin */}
      <Cloud x={40} y={318} s={1.300} fill="#d8f6e0" shade="#8fd0c0" /><Cloud x={150} y={330} s={1.600} fill="#eafcec" shade="#9fd8c8" /><Cloud x={290} y={322} s={1.500} fill="#d8f6e0" shade="#8fd0c0" /><Cloud x={380} y={334} s={1.200} fill="#eafcec" shade="#9fd8c8" />
      <rect y={HZ} width={W} height={H} fill="url(#hs-w-ground)" />
    </>
  ),
  Mid: () => (
    <>
      <g class="bd-cloud"><Cloud x={60} y={120} s={0.900} fill="#f4fff0" shade="#a8dcd0" /><Cloud x={330} y={250} s={0.700} fill="#f4fff0" shade="#a8dcd0" /></g>
      <g class="bd-cloud bd-slow"><Cloud x={250} y={64} s={1.100} fill="#e4f8ec" shade="#8fd0c8" /><Cloud x={20} y={236} s={0.800} fill="#f4fff0" shade="#a8dcd0" /></g>
      {/* les îles qui flottent */}
      <g class="mi-bob mi-slow"><SkyIsland x={70} y={196} s={0.900} /></g><g class="mi-bob"><SkyIsland x={338} y={104} s={0.600} /></g><g class="mi-bob mi-slow" style={{ animationDelay: '-1.4s' }}><SkyIsland x={130} y={86} s={0.440} /></g>
    </>
  ),
  Front: () => (
    <>
      <defs><radialGradient id="hs-w-lit" cx="195" cy="420" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(195 420) scale(210 64) translate(-195 -420)"><stop offset="0" stop-color="#f4ffd8" stop-opacity="0.5" /><stop offset="1" stop-color="#f4ffd8" stop-opacity="0" /></radialGradient></defs>
      <rect y={HZ} width={W} height="190" fill="url(#hs-w-lit)" />
      {/* le bord de la terrasse : une frange d'herbe claire sur l'horizon */}
      <path d={`M-10 ${HZ + 3} Q60 ${HZ - 5} 130 ${HZ + 1} T260 ${HZ - 1} T400 ${HZ + 2} V${HZ + 9} Q300 ${HZ + 4} 195 ${HZ + 8} T-10 ${HZ + 10} Z`} fill="#d8ffb0" opacity="0.9" />
      <Marble x={34} y={404} h={196} side={1} /><Marble x={86} y={376} h={96} side={1} /><Marble x={358} y={404} h={176} side={1} /><Marble x={308} y={376} h={110} side={1} />
      <Cloud x={24} y={566} s={1.700} fill="#f4fff0" shade="#9fd8c8" /><Cloud x={372} y={560} s={1.800} fill="#eafcec" shade="#9fd8c8" /><Cloud x={110} y={600} s={1.300} fill="#d8f6e0" shade="#8fd0c0" /><Cloud x={290} y={604} s={1.400} fill="#d8f6e0" shade="#8fd0c0" />
    </>
  ),
  Top: () => {
    const r = rng(23);
    return (
      <>
        {/* les flammes d'étoffe, en haut des grandes colonnes */}
        {[[34, 214, '#3fd68a', '#1f9a6a'], [358, 234, '#ffd45c', '#d89a1a']].map(([x, y, c, d]) => (
          <g transform={`translate(${x} ${y})`}>
            <path d="M0 6 V-30" stroke="#5a3a1a" stroke-width="2.400" stroke-linecap="round" />
            <g class="bd-flag" style={{ transformOrigin: '0px -22px' }}><path d="M0 -30 Q18 -34 30 -27 Q42 -20 56 -24 L46 -17 L54 -10 Q40 -8 30 -14 Q18 -20 0 -15 Z" fill={c as string} /><path d="M0 -22 Q18 -27 30 -20 Q42 -14 54 -10 Q40 -8 30 -14 Q18 -20 0 -15 Z" fill={d as string} /></g>
          </g>
        ))}
        {/* les volutes du vent : deux rubans qui filent */}
        <g fill="none" stroke="#fff" stroke-linecap="round" opacity="0.6"><path class="hs-gust" d="M-30 300 C40 270 110 290 130 262 C142 244 122 232 112 246" stroke-width="2.600" /><path class="hs-gust hs-gust-2" d="M420 196 C350 170 290 190 270 164 C258 148 276 136 286 148" stroke-width="2.200" /></g>
        {/* les feuilles emportées */}
        {Array.from({ length: 11 }, (_, i) => {
          const y = 90 + r() * 400, k = 0.700 + r() * 0.800;
          return <g class="hs-leaf" style={{ animationDelay: `${(-r() * 9).toFixed(1)}s`, animationDuration: `${(6 + r() * 5).toFixed(1)}s` }}><path d="M0 0 Q5 -6 12 -3 Q7 3 0 0 Z" transform={`translate(-20 ${f(y)}) scale(${f(k)})`} fill={i % 3 ? '#7fe08a' : '#d8ffb0'} /></g>;
        })}
      </>
    );
  },
};

// ---------------------------------------------------------------- Eau : la grotte des marées

const WATER: Layers = {
  Back: () => (
    <>
      <defs>
        <linearGradient id="hs-a-out" x1="0" y1="60" x2="0" y2="270" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#2a6ac8" /><stop offset="0.55" stop-color="#6fc8f0" /><stop offset="1" stop-color="#eafcff" /></linearGradient>
        <linearGradient id="hs-a-sea" x1="0" y1="268" x2="0" y2={HZ} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#9fe8f8" /><stop offset="0.25" stop-color="#4fb8e6" /><stop offset="1" stop-color="#1f7ac8" /></linearGradient>
        <linearGradient id="hs-a-rock" x1="0" y1="0" x2="0" y2={HZ} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#030c22" /><stop offset="1" stop-color="#0a2c5a" /></linearGradient>
        <linearGradient id="hs-a-ground" x1="0" y1={HZ} x2="0" y2="640" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#2a8ad0" /><stop offset="0.1" stop-color="#14508c" /><stop offset="0.45" stop-color="#0a2850" /><stop offset="1" stop-color="#04122a" /></linearGradient>
        <radialGradient id="hs-a-sun"><stop offset="0" stop-color="#fff" stop-opacity="0.95" /><stop offset="0.3" stop-color="#eafcff" stop-opacity="0.55" /><stop offset="1" stop-color="#eafcff" stop-opacity="0" /></radialGradient>
      </defs>
      {/* dehors : le ciel, le soleil qui touche l'horizon (décalé à droite), son reflet sur la mer */}
      <rect y="-40" width={W} height={HZ + 40} fill="url(#hs-a-out)" />
      <circle cx="252" cy="262" r="110" fill="url(#hs-a-sun)" /><circle cx="252" cy="262" r="19" fill="#fff" />
      <rect x="-10" y="268" width={W + 20} height={HZ - 266} fill="url(#hs-a-sea)" />
      <path d="M236 274 H268 M228 284 H276 M238 295 H270 M224 307 H282 M234 320 H274 M218 332 H288" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.8" />
      <path d="M96 288 H132 M150 300 H176 M110 314 H150 M300 296 H326 M316 322 H344" stroke="#eafcff" stroke-width="1.500" stroke-linecap="round" opacity="0.55" />
      {/* la voûte de la grotte : une arche de roche large et dissymétrique, ses stalactites */}
      <path d={`M-20 -40 H${W + 20} V${HZ + 2} H344 L336 300 L346 262 L322 214 L330 168 L304 122 L290 128 L266 88 L246 82 L238 124 L228 78 L204 66 L178 74 L170 108 L160 80 L132 92 L118 86 L92 118 L66 150 L74 196 L48 246 L60 298 L50 ${HZ + 2} H-20 Z`} fill="url(#hs-a-rock)" />
      <path d={`M50 ${HZ + 2} L60 298 L48 246 L74 196 L66 150 L92 118 L118 86 L132 92 L160 80 L170 108 L178 74 L204 66 L228 78 L238 124 L246 82 L266 88 L290 128 L304 122 L330 168 L322 214 L346 262 L336 300 L344 ${HZ + 2}`} fill="none" stroke="#4fa8ee" stroke-width="1.800" stroke-linejoin="round" opacity="0.9" />
      <path d="M66 150 L92 118 L118 86 L112 124 L90 160 L96 204 L74 250 L84 300 L60 298 L48 246 L74 196 Z" fill="#1c5aa0" opacity="0.5" />
      <rect y={HZ} width={W} height={H} fill="url(#hs-a-ground)" />
    </>
  ),
  Mid: () => (
    <>
      {/* la mer scintille */}
      {[[252, 290, 3.200], [238, 314, 2.600], [268, 326, 2.400], [120, 304, 2.200], [312, 310, 2]].map(([x, y, k], i) => <path class={`an-twinkle ${i % 2 ? 'an-late' : i % 3 ? 'an-later' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
    </>
  ),
  Front: () => (
    <>
      <defs>
        <linearGradient id="hs-a-fall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eafcff" stop-opacity="0.95" /><stop offset="1" stop-color="#7fd8f5" stop-opacity="0.8" /></linearGradient>
        <radialGradient id="hs-a-basin" cx="195" cy="408" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(195 408) scale(200 54) translate(-195 -408)"><stop offset="0" stop-color="#bff2ff" stop-opacity="0.75" /><stop offset="0.6" stop-color="#3fb6e6" stop-opacity="0.25" /><stop offset="1" stop-color="#3fb6e6" stop-opacity="0" /></radialGradient>
      </defs>
      {/* le bassin : la lumière du dehors s'y reflète */}
      <rect y={HZ} width={W} height="170" fill="url(#hs-a-basin)" />
      {/* les rochers des cascades, et leurs cristaux */}
      <path d="M-10 420 V150 L18 132 L44 150 L58 200 L50 268 L66 330 L74 400 L40 424 Z" fill="#06183a" /><path d="M44 150 L58 200 L50 268 L66 330 L74 400 L60 396 L54 330 L40 268 L46 204 Z" fill="#1c5aa0" />
      <path d="M400 420 V140 L372 124 L348 146 L334 198 L342 262 L326 326 L318 400 L352 424 Z" fill="#06183a" /><path d="M348 146 L334 198 L342 262 L326 326 L318 400 L332 396 L338 326 L352 262 L346 200 Z" fill="#1c5aa0" />
      <Shards x={70} y={414} s={1.100} c="#3fb6e6" light="#d8f8ff" dark="#14609a" /><Shards x={322} y={414} s={1} c="#4fd6c8" light="#d8fff6" dark="#1a7a80" />
      <path d="M-10 640 V528 L18 506 L46 528 L62 566 L80 640 Z M400 640 V520 L372 500 L344 524 L326 566 L308 640 Z" fill="#030c1e" /><path d="M18 506 L46 528 L62 566 L52 568 L38 534 Z M372 500 L344 524 L326 566 L336 568 L352 532 Z" fill="#14508c" opacity="0.85" />
    </>
  ),
  Top: () => (
    <>
      <defs><radialGradient id="hs-a-mist"><stop offset="0" stop-color="#eafcff" stop-opacity="0.7" /><stop offset="1" stop-color="#eafcff" stop-opacity="0" /></radialGradient></defs>
      {/* les deux cascades : un filet large qui s'évase, deux filets fins inégaux, la brume et l'écume au pied */}
      {[[26, 148, 398, 1], [364, 140, 400, -1]].map(([x, y0, y1, k]) => (
        <g>
          <path d={`M${x! - 4} ${y0} Q${x! - 9} ${y0! + 110} ${x! - 12} ${y1} H${x! + 11} Q${x! + 8} ${y0! + 120} ${x! + 5} ${y0} Z`} fill="url(#hs-a-fall)" />
          <path d={`M${x! + 12 * k!} ${y0! + 26} Q${x! + 15 * k!} ${y0! + 130} ${x! + 19 * k!} ${y1! - 6}`} fill="none" stroke="#bff2ff" stroke-width="2.600" stroke-linecap="round" opacity="0.75" />
          <path d={`M${x! - 14 * k!} ${y0! + 70} Q${x! - 16 * k!} ${y0! + 160} ${x! - 18 * k!} ${y1! - 20}`} fill="none" stroke="#bff2ff" stroke-width="1.600" stroke-linecap="round" opacity="0.55" />
          <path class="ad-fall" d={`M${x! - 2} ${y0} Q${x! - 5} ${y0! + 110} ${x! - 6} ${y1} M${x! + 3} ${y0! + 8} Q${x! + 4} ${y0! + 120} ${x! + 5} ${y1}`} fill="none" stroke="#fff" stroke-width="1.600" stroke-dasharray="14 20 6 11" stroke-linecap="round" opacity="0.9" />
          <ellipse cx={x} cy={y1! - 6} rx="34" ry="16" fill="url(#hs-a-mist)" />
          <ellipse class="ad-foam" cx={x} cy={y1! + 2} rx="22" ry="6" fill="#fff" /><ellipse class="ad-foam" style={{ animationDelay: '-1s' }} cx={x! + 8 * k!} cy={y1! + 5} rx="14" ry="4" fill="#eafcff" />
        </g>
      ))}
      {/* le bassin frissonne : des ronds qui s'élargissent */}
      {[[150, 430, 0], [250, 452, -1.600], [196, 486, -3]].map(([x, y, d]) => <ellipse class="hs-ripple" style={{ animationDelay: `${d}s`, transformOrigin: `${x}px ${y}px` }} cx={x} cy={y} rx="26" ry="5" fill="none" stroke="#bff2ff" stroke-width="1.300" />)}
      <Rise seed={31} n={16} colors={['#bff2ff', '#7fe0f0']} y0={280} y1={540} ring rMin={1.600} rMax={3.600} />
    </>
  ),
};

// ---------------------------------------------------------------- Terre : le cirque de pierres

/** Une aiguille de roche : deux pans (l'un au soleil, l'autre à l'ombre), une corniche d'herbe. `side` = 1 si le soleil est à sa droite. */
function Spire({ x, y, w, h, side }: { x: number; y: number; w: number; h: number; side: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${side} 1)`}>
      <path d={`M${-w / 2} 0 L${-w * 0.4} ${-h * 0.34} L${-w * 0.3} ${-h * 0.4} L${-w * 0.24} ${-h * 0.62} L${-w * 0.1} ${-h * 0.7} L${-w * 0.04} ${-h * 0.93} L${w * 0.05} ${-h} L${w * 0.13} ${-h * 0.86} L${w * 0.22} ${-h * 0.6} L${w * 0.34} ${-h * 0.52} L${w * 0.4} ${-h * 0.3} L${w / 2} 0 Z`} fill="#7a4a2a" />
      <path d={`M${w * 0.05} ${-h} L${w * 0.13} ${-h * 0.86} L${w * 0.22} ${-h * 0.6} L${w * 0.34} ${-h * 0.52} L${w * 0.4} ${-h * 0.3} L${w / 2} 0 H${w * 0.1} L${w * 0.14} ${-h * 0.44} L${w * 0.06} ${-h * 0.7} Z`} fill="#e6ae6c" />
      <path d={`M${w * 0.05} ${-h} L${w * 0.06} ${-h * 0.7} L${w * 0.14} ${-h * 0.44} L${w * 0.1} 0 H${-w * 0.14} L${-w * 0.08} ${-h * 0.5} L${-w * 0.04} ${-h * 0.93} Z`} fill="#a86c3c" />
      {/* les strates : deux lits plus sombres, brisés aux arêtes */}
      <path d={`M${-w * 0.36} ${-h * 0.25} L${-w * 0.12} ${-h * 0.29} L${w * 0.12} ${-h * 0.25} L${w * 0.42} ${-h * 0.22} M${-w * 0.26} ${-h * 0.53} L${-w * 0.07} ${-h * 0.57} L${w * 0.13} ${-h * 0.52} L${w * 0.3} ${-h * 0.5}`} fill="none" stroke="#5a3418" stroke-width="2" stroke-linejoin="round" opacity="0.45" />
      <path d={`M${-w * 0.42} ${-h * 0.33} Q${-w * 0.36} ${-h * 0.4} ${-w * 0.29} ${-h * 0.41} L${-w * 0.3} ${-h * 0.36} Q${-w * 0.36} ${-h * 0.35} ${-w * 0.4} ${-h * 0.29} Z`} fill="#7fbe4a" />
      <path d={`M${w * 0.2} ${-h * 0.6} Q${w * 0.28} ${-h * 0.58} ${w * 0.35} ${-h * 0.51} L${w * 0.33} ${-h * 0.47} Q${w * 0.27} ${-h * 0.53} ${w * 0.2} ${-h * 0.55} Z`} fill="#a8e06a" />
    </g>
  );
}

/** Les pierres levées du cirque : place, taille, signe gravé. */
const MENHIRS: { x: number; y: number; w: number; h: number; g: number }[] = [{ x: 98, y: 392, w: 28, h: 78, g: 1 }, { x: 292, y: 392, w: 28, h: 82, g: 4 }, { x: 138, y: 362, w: 17, h: 46, g: 2 }, { x: 252, y: 362, w: 17, h: 48, g: 6 }];

const EARTH: Layers = {
  Back: () => (
    <>
      <defs>
        <linearGradient id="hs-e-sky" x1="0" y1="0" x2="0" y2={HZ} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#3f7ab0" /><stop offset="0.4" stop-color="#8fbcd0" /><stop offset="0.78" stop-color="#f6dca0" /><stop offset="1" stop-color="#ffc878" /></linearGradient>
        <linearGradient id="hs-e-ground" x1="0" y1={HZ} x2="0" y2="640" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#c8e070" /><stop offset="0.1" stop-color="#86b848" /><stop offset="0.45" stop-color="#4c7a2c" /><stop offset="1" stop-color="#24401a" /></linearGradient>
        <radialGradient id="hs-e-sun"><stop offset="0" stop-color="#fffbe0" stop-opacity="0.95" /><stop offset="0.3" stop-color="#ffe9a8" stop-opacity="0.5" /><stop offset="1" stop-color="#ffe9a8" stop-opacity="0" /></radialGradient>
      </defs>
      <rect y="-40" width={W} height={HZ + 40} fill="url(#hs-e-sky)" />
      <circle cx="92" cy="170" r="150" fill="url(#hs-e-sun)" /><circle cx="92" cy="170" r="19" fill="#fffdf0" />
      {/* les mesas, de plus en plus pâles vers le fond */}
      <path d={ridge(11, HZ - 6, 60, 110, 70, 120, 0.56)} fill="#e8bc8a" /><path d={ridge(19, HZ - 2, 34, 76, 60, 100, 0.5)} fill="#cc9060" /><path d={ridge(27, HZ + 2, 16, 44, 46, 84, 0.44)} fill="#a8683c" />
      <rect y={HZ} width={W} height={H} fill="url(#hs-e-ground)" />
    </>
  ),
  Mid: () => (
    <>
      <g class="bd-cloud"><Cloud x={250} y={96} s={1} fill="#fff6e0" shade="#e8c8a0" /><Cloud x={40} y={60} s={0.700} fill="#fff6e0" shade="#e8c8a0" /></g>
      <g class="bd-cloud bd-slow"><Cloud x={340} y={176} s={0.700} fill="#fffaf0" shade="#ecd0a8" /></g>
      <g class="bd-birds" fill="none" stroke="#5a3a24" stroke-width="1.500" stroke-linecap="round"><path d="M-40 130 q5 -5 10 0 q5 -5 10 0 M-66 144 q4 -4 8 0 q4 -4 8 0" /></g>
    </>
  ),
  Front: () => (
    <>
      <defs><radialGradient id="hs-e-lit" cx="195" cy="420" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(195 420) scale(210 64) translate(-195 -420)"><stop offset="0" stop-color="#f6ffb0" stop-opacity="0.5" /><stop offset="1" stop-color="#f6ffb0" stop-opacity="0" /></radialGradient></defs>
      <rect y={HZ} width={W} height="190" fill="url(#hs-e-lit)" />
      {/* les aiguilles de roche, de chaque côté */}
      <Spire x={26} y={410} w={96} h={250} side={-1} /><Spire x={72} y={384} w={54} h={120} side={-1} /><Spire x={366} y={410} w={100} h={270} side={-1} /><Spire x={318} y={384} w={52} h={128} side={-1} />
      {/* les pierres levées : l'ombre courte à droite (le soleil est à gauche) */}
      {MENHIRS.map((m) => (
        <g transform={`translate(${m.x} ${m.y})`}>
          <ellipse cx={m.w * 0.5} cy="1" rx={m.w * 0.9} ry={m.w * 0.2} fill="#24401a" opacity="0.5" />
          <path d={`M${-m.w / 2} 0 L${-m.w * 0.42} ${-m.h * 0.7} L${-m.w * 0.16} ${-m.h} L${m.w * 0.3} ${-m.h * 0.94} L${m.w * 0.46} ${-m.h * 0.5} L${m.w / 2} 0 Z`} fill="#6e4426" />
          <path d={`M${-m.w / 2} 0 L${-m.w * 0.42} ${-m.h * 0.7} L${-m.w * 0.16} ${-m.h} L${-m.w * 0.22} ${-m.h * 0.6} L${-m.w * 0.3} 0 Z`} fill="#d8a066" />
          <path d={`M${m.w * 0.3} ${-m.h * 0.94} L${m.w * 0.46} ${-m.h * 0.5} L${m.w / 2} 0 H${m.w * 0.3} L${m.w * 0.26} ${-m.h * 0.5} Z`} fill="#4a2c16" opacity="0.6" />
          <path d={`M${-m.w * 0.46} 0 Q0 -5 ${m.w * 0.46} 0 Z`} fill="#86b848" />
        </g>
      ))}
      <path d="M-10 640 V536 L14 516 L40 524 L58 548 L74 590 L92 640 Z M400 640 V528 L376 508 L350 518 L332 546 L318 590 L300 640 Z" fill="#8a5632" />
      <path d="M-10 536 L14 516 L40 524 L58 548 L40 544 L20 536 Z" fill="#b87a48" /><path d="M376 508 L350 518 L332 546 L318 590 L336 568 L352 536 Z" fill="#e6ae6c" />
      <path d="M-10 540 L14 518 L40 526 Q22 524 8 540 Z M400 532 L376 510 L350 520 Q368 518 384 534 Z" fill="#a8e06a" />
    </>
  ),
  Top: () => (
    <>
      <defs><radialGradient id="hs-e-glow"><stop offset="0" stop-color="#ffe08a" stop-opacity="0.85" /><stop offset="1" stop-color="#ffb84a" stop-opacity="0" /></radialGradient></defs>
      {/* les signes des pierres s'allument tour à tour */}
      {MENHIRS.map((m, i) => (
        <g class="sm-glyph" style={{ animationDelay: `${-i * 1.300}s` }}>
          <circle cx={m.x + m.w * 0.04} cy={m.y - m.h * 0.5} r={m.w * 0.42} fill="url(#hs-e-glow)" />
          <path d={GLYPHS[m.g]} transform={`translate(${f(m.x + m.w * 0.04)} ${f(m.y - m.h * 0.5)}) scale(${f(m.w / 15)})`} fill="none" stroke="#ffe08a" stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round" />
        </g>
      ))}
      <Rise seed={41} n={16} colors={['#fff6c8', '#ffe08a', '#d8ffa0']} y0={300} y1={540} rMin={0.900} rMax={2} />
    </>
  ),
};

const SCENES: Record<Element, Layers> = { fire: FIRE, wind: WIND, water: WATER, earth: EARTH };

export function HeroScene({ element }: { element: Element }) {
  const box = { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMin slice' };
  const { Back, Mid, Front, Top } = SCENES[element];
  // la clé force le navigateur à redessiner les quatre calques quand on passe d'un héros à un autre élément
  return (
    <div class={`backdrop hero-scene hs-${element}`} aria-hidden="true" key={element}>
      <svg {...box}><Back /></svg>
      <svg {...box}><Mid /></svg>
      <svg {...box}><Front /></svg>
      <svg {...box}><Top /></svg>
    </div>
  );
}

// ---------------------------------------------------------------- le piédestal

/** Les teintes du piédestal par élément : dessus (clair, bord), contremarche (bords, centre), filet, lueur. */
const STONE: Record<Element, { top: [string, string]; side: [string, string]; inlay: string; glow: string }> = {
  fire: { top: ['#6a3a3a', '#2a1218'], side: ['#12060a', '#4a1a1c'], inlay: '#ffb04a', glow: '#ff7a2a' },
  wind: { top: ['#ffffff', '#b8dcd0'], side: ['#5f9a8c', '#d8f0e8'], inlay: '#3fd68a', glow: '#8ff0b8' },
  water: { top: ['#d8f4ff', '#5f9ad0'], side: ['#0f3a70', '#4f8ad0'], inlay: '#7fe8ff', glow: '#5fd0ff' },
  earth: { top: ['#f6e0b0', '#b8885a'], side: ['#5a3a20', '#b88a58'], inlay: '#ffd45c', glow: '#ffd45c' },
};

/**
 * Le piédestal du héros : deux marches rondes de pierre (teintes de l'élément), un filet de métal, un cercle de signes
 * gravé qui tourne à plat et luit, une gemme de la couleur de la rareté sur le devant. Repère 300 × 104 : le héros pose
 * les pieds au point (150, 30).
 */
export function Pedestal({ element, rarity }: { element: Element; rarity: string }) {
  const c = STONE[element];
  const cx = 150, cy = 30, rx = 104, ry = 19, h = 15, rx2 = 128, ry2 = 23, cy2 = cy + h + 6, h2 = 15;
  return (
    <svg class="pedestal" viewBox="0 0 300 104" aria-hidden="true">
      <defs>
        <radialGradient id="pd-top" cx={cx} cy={cy - 4} r="1" gradientUnits="userSpaceOnUse" gradientTransform={`translate(${cx} ${cy - 4}) scale(${rx} ${ry * 1.500}) translate(${-cx} ${-(cy - 4)})`}><stop offset="0" stop-color={c.top[0]} /><stop offset="1" stop-color={c.top[1]} /></radialGradient>
        <linearGradient id="pd-side" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color={c.side[0]} /><stop offset="0.5" stop-color={c.side[1]} /><stop offset="1" stop-color={c.side[0]} /></linearGradient>
        <linearGradient id="pd-seam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="0.5" stop-color="#fff" stop-opacity="0.9" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></linearGradient>
        <radialGradient id="pd-glow"><stop offset="0" stop-color={c.glow} stop-opacity="0.85" /><stop offset="0.5" stop-color={c.glow} stop-opacity="0.25" /><stop offset="1" stop-color={c.glow} stop-opacity="0" /></radialGradient>
        <linearGradient id="pd-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.5" stop-color="#ffc531" /><stop offset="1" stop-color="#a8690c" /></linearGradient>
      </defs>
      <ellipse cx={cx} cy={cy2 + h2 + 6} rx={rx2 + 14} ry={ry2 + 3} fill="#000" opacity="0.4" />
      {/* la marche du bas */}
      <path d={`M${cx - rx2} ${cy2} V${cy2 + h2} A${rx2} ${ry2} 0 0 0 ${cx + rx2} ${cy2 + h2} V${cy2} Z`} fill="url(#pd-side)" />
      <ellipse cx={cx} cy={cy2} rx={rx2} ry={ry2} fill={c.top[1]} />
      <path d={`M${cx - rx2} ${cy2 + 1} A${rx2} ${ry2} 0 0 0 ${cx + rx2} ${cy2 + 1}`} fill="none" stroke="url(#pd-seam)" stroke-width="1.600" />
      {/* la marche du haut */}
      <path d={`M${cx - rx} ${cy} V${cy + h} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + h} V${cy} Z`} fill="url(#pd-side)" />
      <path d={`M${cx - rx} ${cy + h - 4} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + h - 4}`} fill="none" stroke={c.inlay} stroke-width="1.400" opacity="0.8" />
      <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="url(#pd-top)" />
      <path d={`M${cx - rx} ${cy + 1} A${rx} ${ry} 0 0 0 ${cx + rx} ${cy + 1}`} fill="none" stroke="url(#pd-seam)" stroke-width="2" />
      <ellipse cx={cx} cy={cy} rx={rx - 8} ry={ry - 2.400} fill="none" stroke="url(#pd-gold)" stroke-width="1.800" />
      {/* le cercle de signes : il tourne à plat et luit */}
      <ellipse class="an-glow" cx={cx} cy={cy} rx={rx - 12} ry={ry - 3} fill="url(#pd-glow)" />
      <g transform={`translate(${cx} ${cy}) scale(1 ${(ry / rx).toFixed(3)})`}>
        <g class="pd-ring" fill="none" stroke={c.inlay}>
          <circle r={rx - 22} stroke-width="1.300" opacity="0.9" /><circle r={rx - 48} stroke-width="1" stroke-dasharray="3 8" opacity="0.7" />
          {Array.from({ length: 12 }, (_, i) => { const a = (i / 12) * Math.PI * 2, d = rx - 35; return <path d={GLYPHS[i % GLYPHS.length]} stroke-width="1.500" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(Math.cos(a) * d)} ${f(Math.sin(a) * d)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(1.800)`} />; })}
        </g>
      </g>
      {/* la gemme du devant : la couleur de la rareté, sertie d'or */}
      <g transform={`translate(${cx} ${cy2 + ry2 + h2 * 0.5 - 1})`}>
        <path d="M0 -11 L11 0 L0 11 L-11 0 Z" fill="#2f1b0c" /><path d="M0 -9 L9 0 L0 9 L-9 0 Z" fill="url(#pd-gold)" />
        <path d="M0 -5.600 L5.600 0 L0 5.600 L-5.600 0 Z" fill={rarity} /><path d="M0 -5.600 L5.600 0 H0 Z" fill="#fff" opacity="0.55" /><path d="M0 0 H5.600 L0 5.600 Z" fill="#000" opacity="0.22" />
      </g>
    </svg>
  );
}
