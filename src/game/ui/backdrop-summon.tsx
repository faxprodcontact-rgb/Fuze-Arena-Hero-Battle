// Le décor de l'onglet Invocation : un sanctuaire, la nuit. Tout en haut la lune et son cercle de signes, la voûte
// étoilée, une aurore qui ondule, une étoile filante ; au loin des pics noirs et des îles de roche qui flottent, coiffées
// de cristaux ; au sol, un plateau de pierre sombre fendu de lueurs, des pierres levées gravées, des gerbes de cristaux
// au premier plan. La lumière vient du centre (le portail, posé par-dessus par summon-stage.tsx) : chaque pierre a sa face
// claire tournée vers lui. Quatre dessins superposés, comme pour l'Aventure : le ciel ; ce qui bouge derrière (étoiles,
// lune, aurore) ; les reliefs ; ce qui bouge devant (signes qui s'allument, lucioles, brume).
import { GLYPHS } from './backdrop-adventure';
import { spark } from './portal';

const W = 390, H = 844;
/** L'horizon : là où le plateau commence. */
const GROUND = 392;

function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}
const f = (n: number) => n.toFixed(1);

/** Une chaîne de pics aigus, fermée en bas. */
function crags(seed: number, base: number, hMin: number, hMax: number, wMin: number, wMax: number): string {
  const r = rng(seed);
  let x = -14, d = `M-14 ${GROUND + 30} L-14 ${base}`;
  while (x < W + 14) {
    const w = wMin + r() * (wMax - wMin), h = hMin + r() * (hMax - hMin), lean = (r() - 0.5) * w * 0.3;
    d += ` L${f(x + w * 0.5 + lean)} ${f(base - h)} L${f(x + w)} ${f(base - h * 0.2 * r())}`;
    x += w;
  }
  return `${d} L${W + 14} ${GROUND + 30} Z`;
}

/** Une gerbe de cristaux : trois éclats, une face claire, une face sombre. */
function Shards({ x, y, s, c, light, dark }: { x: number; y: number; s: number; c: string; light: string; dark: string }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path d="M-13 4 L-17 -14 L-11 -22 L-5 -12 L-3 4 Z" fill={c} /><path d="M-11 -22 L-5 -12 L-3 4 L-7 4 L-9 -10 Z" fill={light} />
      <path d="M-3 4 L-4 -24 L3 -37 L9 -22 L8 4 Z" fill={c} /><path d="M3 -37 L9 -22 L8 4 L3 4 L4 -20 Z" fill={light} /><path d="M-3 4 L-4 -24 L3 -37 L1 -20 L0 4 Z" fill={dark} opacity="0.55" />
      <path d="M8 4 L9 -11 L15 -17 L19 -8 L17 4 Z" fill={c} /><path d="M15 -17 L19 -8 L17 4 L13 4 L14 -8 Z" fill={light} />
      <path d="M1 -30 L3 -35 L4.500 -28 Z" fill="#fff" opacity="0.9" />
    </g>
  );
}

/** Une île de roche qui flotte : dessus plat, dessous déchiqueté, des cristaux plantés dessus. `flip` = éclairée par la gauche. */
function Island({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d="M-34 0 H34 L26 12 L18 9 L12 26 L4 16 L-4 38 L-12 18 L-20 22 L-27 8 Z" fill="#33247a" />
      <path d="M-34 0 H-6 L-12 18 L-20 22 L-27 8 Z" fill="#1c1350" /><path d="M10 0 H34 L26 12 L18 9 L12 26 L6 14 Z" fill="#5a45b4" />
      <path d="M-34 0 Q0 -7 34 0 L32 3.500 Q0 -2 -32 3.500 Z" fill="#2f6f86" /><path d="M-34 0 Q0 -7 34 0 L33.500 1.200 Q0 -5 -33.500 1.200 Z" fill="#6fd0d6" />
      <Shards x={-8} y={-2} s={0.5} c="#3fb6e6" light="#c8f6ff" dark="#1f6aa8" /><Shards x={14} y={-1} s={0.34} c="#b06aff" light="#ecd6ff" dark="#6a2fc0" />
    </g>
  );
}

/** Une pierre levée : fût irrégulier, face claire tournée vers le portail (`side` = 1 si la pierre est à gauche de lui). */
function Menhir({ x, y, w, h, side }: { x: number; y: number; w: number; h: number; side: number }) {
  const t = w * 0.32;
  return (
    <g transform={`translate(${x} ${y}) scale(${side} 1)`}>
      <ellipse cx="0" cy="1" rx={w * 0.9} ry={w * 0.22} fill="#0b0722" opacity="0.5" />
      <path d={`M${-w / 2} 0 L${-w / 2 + t * 0.4} ${-h * 0.55} L${-w / 2 + t} ${-h * 0.92} L${-t * 0.2} ${-h} L${w / 2 - t * 0.5} ${-h * 0.9} L${w / 2 - t * 0.1} ${-h * 0.4} L${w / 2} 0 Z`} fill="#34267c" />
      <path d={`M${-w / 2} 0 L${-w / 2 + t * 0.4} ${-h * 0.55} L${-w / 2 + t} ${-h * 0.92} L${-t * 0.2} ${-h} L${-t * 0.3} ${-h * 0.5} L${-w * 0.12} 0 Z`} fill="#1a1150" />
      <path d={`M${w / 2 - t * 0.5} ${-h * 0.9} L${w / 2 - t * 0.1} ${-h * 0.4} L${w / 2} 0 H${w * 0.24} L${w * 0.2} ${-h * 0.45} Z`} fill="#6a55c8" />
      <path d={`M${w / 2 - t * 0.5} ${-h * 0.9} L${w / 2 - t * 0.1} ${-h * 0.4} L${w / 2} 0`} fill="none" stroke="#b9a8ff" stroke-width="1" opacity="0.8" />
    </g>
  );
}

/** Les pierres levées : place, taille, et le signe gravé sur chacune. */
const STONES: { x: number; y: number; w: number; h: number; g: number }[] = [
  { x: 26, y: 446, w: 30, h: 96, g: 1 }, { x: 74, y: 424, w: 22, h: 70, g: 4 }, { x: 116, y: 410, w: 16, h: 50, g: 2 },
  { x: 364, y: 446, w: 30, h: 96, g: 6 }, { x: 316, y: 424, w: 22, h: 70, g: 0 }, { x: 274, y: 410, w: 16, h: 50, g: 3 },
];

function Back() {
  return (
    <>
      <defs>
        <linearGradient id="sm-sky" x1="0" y1="0" x2="0" y2={GROUND} gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#0a0824" /><stop offset="0.4" stop-color="#1c1250" /><stop offset="0.78" stop-color="#43207a" /><stop offset="1" stop-color="#8a3596" /></linearGradient>
        <linearGradient id="sm-ground" x1="0" y1={GROUND} x2="0" y2="720" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#3a2878" /><stop offset="0.3" stop-color="#261a5c" /><stop offset="1" stop-color="#120c30" /></linearGradient>
        <radialGradient id="sm-neb-a"><stop offset="0" stop-color="#3fd6ff" stop-opacity="0.26" /><stop offset="1" stop-color="#3fd6ff" stop-opacity="0" /></radialGradient>
        <radialGradient id="sm-neb-b"><stop offset="0" stop-color="#c06aff" stop-opacity="0.34" /><stop offset="1" stop-color="#c06aff" stop-opacity="0" /></radialGradient>
        <radialGradient id="sm-neb-c"><stop offset="0" stop-color="#ff5ab0" stop-opacity="0.22" /><stop offset="1" stop-color="#ff5ab0" stop-opacity="0" /></radialGradient>
      </defs>
      <rect y="-40" width={W} height={GROUND + 40} fill="url(#sm-sky)" />
      <ellipse cx="96" cy="210" rx="150" ry="90" fill="url(#sm-neb-a)" /><ellipse cx="300" cy="110" rx="170" ry="110" fill="url(#sm-neb-b)" /><ellipse cx="220" cy="330" rx="200" ry="80" fill="url(#sm-neb-c)" />
      <rect y={GROUND} width={W} height={H} fill="url(#sm-ground)" />
    </>
  );
}

function Mid() {
  const r = rng(11);
  const moon = { x: 66, y: 92 };
  return (
    <>
      <defs>
        <radialGradient id="sm-moon"><stop offset="0" stop-color="#ffffff" /><stop offset="0.7" stop-color="#ece2ff" /><stop offset="1" stop-color="#c8b6f5" /></radialGradient>
        <radialGradient id="sm-halo"><stop offset="0" stop-color="#e6d8ff" stop-opacity="0.7" /><stop offset="0.45" stop-color="#b79cff" stop-opacity="0.22" /><stop offset="1" stop-color="#b79cff" stop-opacity="0" /></radialGradient>
        <linearGradient id="sm-aur" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5ff0d0" stop-opacity="0" /><stop offset="0.35" stop-color="#5ff0d0" stop-opacity="0.5" /><stop offset="1" stop-color="#7a6aff" stop-opacity="0" /></linearGradient>
        <linearGradient id="sm-aur2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff7ad0" stop-opacity="0" /><stop offset="0.4" stop-color="#c07aff" stop-opacity="0.42" /><stop offset="1" stop-color="#5ab0ff" stop-opacity="0" /></linearGradient>
        <linearGradient id="sm-shoot" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="1" stop-color="#fff" /></linearGradient>
      </defs>
      {/* la voûte étoilée */}
      <g fill="#fff">{Array.from({ length: 70 }, () => <circle class="bd-star" style={{ animationDelay: `${(-r() * 5).toFixed(1)}s` }} cx={f(r() * W)} cy={f(r() * (GROUND - 40))} r={f(0.500 + r() * 1.300)} />)}</g>
      {[[150, 46, 5], [338, 196, 4], [236, 150, 3.500], [24, 262, 3.500]].map(([x, y, k], i) => <path class={`an-twinkle ${i % 2 ? 'an-late' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
      {/* l'aurore : deux voiles qui ondulent */}
      <path class="sm-aurora" d="M96 70 C150 20 220 96 286 44 S388 60 420 16 L420 96 C384 132 332 104 296 128 C232 170 168 86 110 150 Z" fill="url(#sm-aur)" />
      <path class="sm-aurora sm-aurora-2" d="M-20 190 C40 150 100 210 170 170 S290 200 330 160 L336 220 C290 250 220 224 176 246 C110 280 50 220 -20 262 Z" fill="url(#sm-aur2)" />
      {/* la lune, son halo, son cercle de signes */}
      <circle class="bd-sun" cx={moon.x} cy={moon.y} r="96" fill="url(#sm-halo)" />
      <g class="bd-ring" style={{ transformOrigin: `${moon.x}px ${moon.y}px`, animationDuration: '120s' }} fill="none" stroke="#d9c8ff" opacity="0.6">
        <circle cx={moon.x} cy={moon.y} r="50" stroke-width="1.200" /><circle cx={moon.x} cy={moon.y} r="53.500" stroke-width="0.600" opacity="0.7" />
        {GLYPHS.map((d, i) => { const a = (i / GLYPHS.length) * Math.PI * 2; return <path d={d} stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(moon.x + Math.cos(a) * 43.500)} ${f(moon.y + Math.sin(a) * 43.500)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(0.560)`} />; })}
      </g>
      <circle cx={moon.x} cy={moon.y} r="31" fill="url(#sm-moon)" />
      <g fill="#b9a6ea" opacity="0.5"><circle cx={moon.x - 10} cy={moon.y - 8} r="6" /><circle cx={moon.x + 9} cy={moon.y + 4} r="4.500" /><circle cx={moon.x - 4} cy={moon.y + 13} r="3.500" /><circle cx={moon.x + 12} cy={moon.y - 13} r="2.500" /></g>
      <path d={`M${moon.x - 31} ${moon.y} A31 31 0 0 0 ${moon.x} ${moon.y + 31} A36 36 0 0 1 ${moon.x - 31} ${moon.y} Z`} fill="#7a62c8" opacity="0.3" />
      {/* une étoile filante, de temps en temps */}
      <path class="sm-shoot" d="M330 36 L270 84" stroke="url(#sm-shoot)" stroke-width="2.200" stroke-linecap="round" />
    </>
  );
}

function Front() {
  return (
    <>
      <defs>
        <linearGradient id="sm-mist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c8a6ff" stop-opacity="0" /><stop offset="0.55" stop-color="#c8a6ff" stop-opacity="0.32" /><stop offset="1" stop-color="#c8a6ff" stop-opacity="0" /></linearGradient>
        <radialGradient id="sm-pool"><stop offset="0" stop-color="#b98aff" stop-opacity="0.75" /><stop offset="0.5" stop-color="#7a52e8" stop-opacity="0.3" /><stop offset="1" stop-color="#7a52e8" stop-opacity="0" /></radialGradient>
      </defs>
      {/* les pics du fond : deux chaînes noires, la plus proche ourlée de lumière */}
      <path d={crags(5, GROUND, 40, 96, 26, 52)} fill="#2a1c66" />
      <path d={crags(13, GROUND + 4, 18, 58, 18, 40)} fill="#1c1250" />
      <rect y={GROUND - 46} width={W} height="70" fill="url(#sm-mist)" />
      {/* les îles qui flottent */}
      <Island x={46} y={262} s={0.9} flip /><Island x={346} y={214} s={0.78} /><Island x={300} y={318} s={0.42} /><Island x={104} y={338} s={0.36} flip />
      {/* le plateau : de grandes dalles en arcs autour du centre, des fissures où court la lueur */}
      <g fill="none" stroke="#5a48b4" opacity="0.5"><ellipse cx="195" cy="470" rx="150" ry="32" stroke-width="1.400" /><ellipse cx="195" cy="486" rx="230" ry="52" stroke-width="1.200" /><ellipse cx="195" cy="510" rx="320" ry="80" stroke-width="1" /></g>
      <ellipse cx="195" cy="452" rx="170" ry="46" fill="url(#sm-pool)" />
      <g fill="none" stroke="#8fe6ff" stroke-linecap="round" stroke-linejoin="round" opacity="0.5">
        <path d="M150 470 L118 484 L104 478 L70 500 L52 496" stroke-width="1.400" /><path d="M240 470 L270 486 L290 480 L322 502 L346 498" stroke-width="1.400" />
        <path d="M170 494 L150 520 L156 540 L132 566" stroke-width="1.200" /><path d="M222 494 L244 522 L236 544 L262 570" stroke-width="1.200" /><path d="M104 478 L96 462 M290 480 L300 464" stroke-width="1" />
      </g>
      {/* les pierres levées */}
      {STONES.map((st) => <Menhir x={st.x} y={st.y} w={st.w} h={st.h} side={st.x < 195 ? 1 : -1} />)}
      {/* au premier plan : des gerbes de cristaux sombres, de chaque côté */}
      <Shards x={18} y={540} s={1.500} c="#2f2478" light="#6f5ae0" dark="#150e3c" /><Shards x={372} y={546} s={1.700} c="#2f2478" light="#6f5ae0" dark="#150e3c" />
      <Shards x={52} y={560} s={0.900} c="#3fb6e6" light="#c8f6ff" dark="#1f6aa8" /><Shards x={338} y={566} s={1} c="#b06aff" light="#ecd6ff" dark="#6a2fc0" />
    </>
  );
}

function Top() {
  const r = rng(29);
  return (
    <>
      <defs>
        <radialGradient id="sm-glow-c"><stop offset="0" stop-color="#8fe6ff" stop-opacity="0.8" /><stop offset="1" stop-color="#8fe6ff" stop-opacity="0" /></radialGradient>
        <radialGradient id="sm-glow-v"><stop offset="0" stop-color="#d09aff" stop-opacity="0.8" /><stop offset="1" stop-color="#d09aff" stop-opacity="0" /></radialGradient>
      </defs>
      {/* les signes gravés sur les pierres s'allument tour à tour */}
      {STONES.map((st, i) => (
        <g class="sm-glyph" style={{ animationDelay: `${-i * 0.9}s` }}>
          <circle cx={st.x} cy={st.y - st.h * 0.52} r={st.w * 0.6} fill="url(#sm-glow-c)" />
          <path d={GLYPHS[st.g]} transform={`translate(${st.x} ${f(st.y - st.h * 0.52)}) scale(${f(st.w / 13)})`} fill="none" stroke="#c8f6ff" stroke-width="1.600" stroke-linecap="round" stroke-linejoin="round" />
        </g>
      ))}
      {/* les cristaux des îles et du premier plan luisent */}
      <circle class="an-glow" cx="42" cy="246" r="20" fill="url(#sm-glow-c)" /><circle class="an-glow an-late" cx="350" cy="200" r="18" fill="url(#sm-glow-v)" />
      <circle class="an-glow an-late" cx="52" cy="540" r="26" fill="url(#sm-glow-c)" /><circle class="an-glow" cx="338" cy="544" r="28" fill="url(#sm-glow-v)" />
      {/* la brume du plateau glisse */}
      <rect class="sm-mist" x="-60" y={GROUND + 10} width={W + 120} height="60" fill="url(#sm-mist)" opacity="0.8" />
      {/* des lucioles montent du sol */}
      {Array.from({ length: 16 }, (_, i) => {
        const x = 10 + r() * (W - 20), y = GROUND + r() * 170, k = 1 + r() * 1.600;
        return <circle class="bd-mote" style={{ animationDelay: `${(-r() * 9).toFixed(1)}s`, animationDuration: `${(6 + r() * 6).toFixed(1)}s` }} cx={f(x)} cy={f(y)} r={f(k)} fill={i % 3 ? '#c8f6ff' : '#e6c8ff'} />;
      })}
    </>
  );
}

export function SummonBackdrop() {
  const box = { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMin slice' };
  return (
    <>
      <svg {...box}><Back /></svg>
      <svg {...box}><Mid /></svg>
      <svg {...box}><Front /></svg>
      <svg {...box}><Top /></svg>
    </>
  );
}
