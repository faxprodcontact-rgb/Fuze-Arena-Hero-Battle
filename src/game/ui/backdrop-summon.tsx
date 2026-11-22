// Le décor de l'onglet Invocation : un sanctuaire, la nuit. Tout en haut la lune, la voûte étoilée, une aurore qui
// ondule, une étoile filante ; au loin des pics (trois chaînes) et deux îles de roche qui flottent dans les coins du ciel ;
// au sol, un plateau de pierre sombre où le portail se reflète. La lumière vient du centre (le portail, posé par-dessus
// par summon-stage.tsx) : les pics les plus proches sont ourlés de sa lueur. Tout ce qui se tient debout près du portail
// (obélisques, estrade, cristaux du premier plan) est dans summon-stage.tsx, dans un seul dessin rangé du fond vers
// l'avant : rien ici ne doit croiser la scène (une pierre du fond devant un obélisque, un cercle au sol qui passe devant
// une pierre…). Quatre dessins superposés : le ciel ; ce qui bouge derrière (étoiles, lune, aurore) ; les reliefs ; ce
// qui bouge devant (lucioles, brume).
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

/** La ligne de crête d'une chaîne de `crags` (mêmes tirages), sans ses bords : pour l'ourler de lumière. */
function crest(seed: number, base: number, hMin: number, hMax: number, wMin: number, wMax: number): string {
  const r = rng(seed);
  let x = -14, d = `M-14 ${base}`;
  while (x < W + 14) {
    const w = wMin + r() * (wMax - wMin), h = hMin + r() * (hMax - hMin), lean = (r() - 0.5) * w * 0.3;
    d += ` L${f(x + w * 0.5 + lean)} ${f(base - h)} L${f(x + w)} ${f(base - h * 0.2 * r())}`;
    x += w;
  }
  return d;
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
  const moon = { x: 302, y: 118 };
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
      {[[150, 46, 5], [346, 232, 4], [236, 150, 3.500], [24, 262, 3.500]].map(([x, y, k], i) => <path class={`an-twinkle ${i % 2 ? 'an-late' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x!, y!, k!)} fill="#fff" />)}
      {/* l'aurore : deux voiles qui ondulent */}
      <path class="sm-aurora" d="M-60 96 C10 40 90 110 170 60 S330 80 450 30 L450 110 C380 150 300 110 240 140 C150 180 60 110 -60 176 Z" fill="url(#sm-aur)" />
      <path class="sm-aurora sm-aurora-2" d="M-60 200 C20 150 110 216 190 172 S340 206 450 150 L450 220 C370 262 280 226 210 250 C130 284 40 224 -60 272 Z" fill="url(#sm-aur2)" />
      {/* la lune : petite et discrète, pour ne pas voler la vedette au portail */}
      <circle class="bd-sun" cx={moon.x} cy={moon.y} r="52" fill="url(#sm-halo)" opacity="0.6" />
      <g opacity="0.8">
        <circle cx={moon.x} cy={moon.y} r="20" fill="url(#sm-moon)" />
        <g fill="#b9a6ea" opacity="0.5"><circle cx={moon.x - 6} cy={moon.y - 5} r="4" /><circle cx={moon.x + 6} cy={moon.y + 3} r="3" /><circle cx={moon.x - 2} cy={moon.y + 9} r="2.200" /></g>
        <path d={`M${moon.x + 20} ${moon.y} A20 20 0 0 1 ${moon.x} ${moon.y + 20} A23 23 0 0 0 ${moon.x + 20} ${moon.y} Z`} fill="#7a62c8" opacity="0.3" />
      </g>
      {/* une étoile filante, de temps en temps */}
      <path class="sm-shoot" d="M150 30 L90 78" stroke="url(#sm-shoot)" stroke-width="2.200" stroke-linecap="round" />
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
      {/* les pics : une chaîne lointaine pâle dans la brume, puis deux chaînes noires ; la plus proche est ourlée de la
          lueur du portail (le trait suit sa crête, sans les bords) */}
      <path d={crags(31, GROUND - 14, 30, 70, 34, 60)} fill="#4a3290" opacity="0.7" />
      <path d={crags(5, GROUND, 40, 96, 26, 52)} fill="#2a1c66" />
      <path d={crags(13, GROUND + 4, 18, 58, 18, 40)} fill="#1c1250" />
      <path d={crest(13, GROUND + 4, 18, 58, 18, 40)} fill="none" stroke="#9a7aff" stroke-width="1.2" stroke-linejoin="round" opacity="0.45" />
      <rect y={GROUND - 46} width={W} height="70" fill="url(#sm-mist)" />
      {/* les îles qui flottent, loin, dans les coins du ciel (jamais près du portail) */}
      <Island x={112} y={112} s={0.46} /><Island x={372} y={156} s={0.56} flip />
      {/* le plateau : la lueur du portail sur la pierre, et son reflet qui descend vers nous */}
      <ellipse cx="195" cy="462" rx="190" ry="56" fill="url(#sm-pool)" />
      <ellipse cx="195" cy="520" rx="46" ry="110" fill="url(#sm-pool)" opacity="0.55" />
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
      {/* les cristaux des îles luisent */}
      <circle class="an-glow" cx="110" cy="104" r="12" fill="url(#sm-glow-c)" /><circle class="an-glow an-late" cx="374" cy="146" r="14" fill="url(#sm-glow-v)" />
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
