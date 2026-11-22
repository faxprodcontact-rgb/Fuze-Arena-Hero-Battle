// Les fonds des menus : dessinés par le code dans le trait du portail, épurés mais vivants.
// Un décor par onglet (salle des héros, nuit d'invocation, route de l'aventure, forteresse de la guilde) et un décor
// pour les pages (crépuscule sur les montagnes) : un dégradé, quelques silhouettes, un grand cercle de runes qui tourne
// très lentement, des poussières de lumière qui montent. Les mouvements sont dans anim.css.
import type { ComponentChildren } from 'preact';
import './anim.css';
import { AdventureBackdrop } from './backdrop-adventure';
import { SummonBackdrop } from './backdrop-summon';
import { HeroesBackdrop } from './backdrop-heroes';
import { GuildBackdrop } from './backdrop-guild';
import { RUNES, spark } from './portal';

export type BackdropKind = 'heroes' | 'summon' | 'adventure' | 'guild' | 'page';
const W = 390, H = 844;

/** Hasard fixe (toujours le même dessin). */
function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}

/** Une crête de montagnes, de gauche à droite, fermée en bas. */
function ridge(seed: number, base: number, amp: number, step: number): string {
  const r = rng(seed);
  let d = `M-10 ${H} L-10 ${base}`;
  for (let x = -10; x <= W + 10; x += step) {
    const peak = base - amp * (0.35 + 0.65 * r());
    d += ` L${x + step * 0.5} ${peak.toFixed(0)} L${x + step} ${(base - amp * 0.15 * r()).toFixed(0)}`;
  }
  return `${d} L${W + 10} ${H} Z`;
}

/** Des collines douces. */
function hills(seed: number, base: number, amp: number, step: number): string {
  const r = rng(seed);
  let d = `M-10 ${H} L-10 ${base}`;
  for (let x = -10; x <= W + 10; x += step) d += ` Q${x + step * 0.5} ${(base - amp * (0.4 + 0.6 * r())).toFixed(0)} ${x + step} ${(base - amp * 0.2 * r()).toFixed(0)}`;
  return `${d} L${W + 10} ${H} Z`;
}

/** Le grand cercle de runes, à peine visible, qui tourne très lentement. */
function RuneCircle({ cx, cy, r, color, opacity = 0.2 }: { cx: number; cy: number; r: number; color: string; opacity?: number }) {
  return (
    <g class="bd-ring" style={{ transformOrigin: `${cx}px ${cy}px` }} opacity={opacity} stroke={color} fill="none">
      <circle cx={cx} cy={cy} r={r} stroke-width="2" />
      <circle cx={cx} cy={cy} r={r * 0.82} stroke-width="1.2" />
      <circle cx={cx} cy={cy} r={r * 0.56} stroke-width="1" stroke-dasharray="2 8" />
      {RUNES.map((d, i) => {
        const a = (i / RUNES.length) * Math.PI * 2;
        return <path d={d} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${(cx + Math.cos(a) * r * 0.91).toFixed(1)} ${(cy + Math.sin(a) * r * 0.91).toFixed(1)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(${(r / 150).toFixed(2)})`} />;
      })}
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const a = (i / 6) * Math.PI * 2;
        const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r, q = r * 0.04;
        return <path d={`M${x} ${y - q} L${x + q} ${y} L${x} ${y + q} L${x - q} ${y} Z`} fill={color} stroke="none" />;
      })}
    </g>
  );
}

/** Des poussières de lumière qui montent. */
function Motes({ seed, color, n = 14 }: { seed: number; color: string; n?: number }) {
  const r = rng(seed);
  return (
    <g fill={color}>
      {Array.from({ length: n }, (_, i) => {
        const x = 12 + r() * (W - 24), y = 200 + r() * 600, s = 1.4 + r() * 2.4;
        return i % 3 === 0
          ? <path class="bd-mote" style={{ animationDelay: `${(-r() * 9).toFixed(1)}s`, animationDuration: `${(7 + r() * 6).toFixed(1)}s`, transformOrigin: `${x}px ${y}px` }} d={spark(x, y, s * 2.2)} />
          : <circle class="bd-mote" style={{ animationDelay: `${(-r() * 9).toFixed(1)}s`, animationDuration: `${(7 + r() * 6).toFixed(1)}s` }} cx={x} cy={y} r={s} />;
      })}
    </g>
  );
}

function Stars({ seed, n = 40 }: { seed: number; n?: number }) {
  const r = rng(seed);
  return <g fill="#fff">{Array.from({ length: n }, () => <circle class="bd-star" style={{ animationDelay: `${(-r() * 5).toFixed(1)}s` }} cx={r() * W} cy={r() * 520} r={0.6 + r() * 1.5} />)}</g>;
}

/** Une tour avec son toit pointu et son fanion qui flotte. */
function Tower({ x, y, w, h, fill, flag }: { x: number; y: number; w: number; h: number; fill: string; flag?: string }) {
  return (
    <g>
      <path d={`M${x} ${y + h} V${y} L${x + w / 2} ${y - w * 0.9} L${x + w} ${y} V${y + h} Z`} fill={fill} />
      {flag && <path class="bd-flag" style={{ transformOrigin: `${x + w / 2}px ${y - w * 0.9 - 16}px` }} d={`M${x + w / 2} ${y - w * 0.9 - 22} l18 5 l-18 6 Z`} fill={flag} />}
      {flag && <path d={`M${x + w / 2} ${y - w * 0.9} v-24`} stroke={fill} stroke-width="1.6" />}
    </g>
  );
}

/** Une bannière suspendue qui se balance. */
function Banner({ x, len, w, fill, trim }: { x: number; len: number; w: number; fill: string; trim: string }) {
  return (
    <g class="bd-banner" style={{ transformOrigin: `${x}px 0px`, animationDelay: `${-(x % 5)}s` }}>
      <path d={`M${x - w / 2} -4 H${x + w / 2} V${len} L${x} ${len - w * 0.45} L${x - w / 2} ${len} Z`} fill={fill} />
      <path d={`M${x - w / 2 + 4} -4 V${len - 8} M${x + w / 2 - 4} -4 V${len - 8}`} stroke={trim} stroke-width="1.5" opacity="0.8" />
      <path d={`M${x} ${len * 0.42 - 11} l9 11 l-9 11 l-9 -11 Z`} fill="none" stroke={trim} stroke-width="1.8" />
      <circle cx={x} cy={len * 0.42} r="3" fill={trim} />
    </g>
  );
}

function Scene({ kind }: { kind: BackdropKind }): ComponentChildren {
  if (kind === 'summon') {
    return (
      <>
        <defs>
          <linearGradient id="bd-s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2670" /><stop offset="0.55" stop-color="#5440a8" /><stop offset="1" stop-color="#8f6ad6" /></linearGradient>
          <radialGradient id="bd-moon"><stop offset="0" stop-color="#d9c8ff" stop-opacity="0.7" /><stop offset="1" stop-color="#d9c8ff" stop-opacity="0" /></radialGradient>
        </defs>
        <rect width={W} height={H} fill="url(#bd-s)" />
        <Stars seed={7} />
        <circle class="bd-sun" cx="70" cy="150" r="90" fill="url(#bd-moon)" />
        <path d="M70 118 a32 32 0 1 0 22 54 a26 26 0 1 1 -22 -54 Z" fill="#efe6ff" />
        <g stroke="#ffe58a" stroke-width="1" opacity="0.5" fill="#ffe58a">
          <path d="M250 120 L290 90 L330 130 L316 180 L262 172 Z" fill="none" />
          <circle cx="250" cy="120" r="2.5" /><circle cx="290" cy="90" r="3" /><circle cx="330" cy="130" r="2.5" /><circle cx="316" cy="180" r="2" /><circle cx="262" cy="172" r="2.5" />
        </g>
        <RuneCircle cx={195} cy={470} r={230} color="#c9a8ff" opacity={0.2} />
        <g>
          <path d="M-10 844 V690 L24 600 L52 700 L80 640 L104 730 V844 Z" fill="#2a1c66" />
          <path d="M400 844 V670 L364 590 L340 690 L312 650 L290 740 V844 Z" fill="#2a1c66" />
          <path d="M24 600 L36 700 L52 700 Z M364 590 L352 690 L340 690 Z" fill="#6f52d6" opacity="0.7" />
          <path d="M80 640 L88 720 L104 730 Z M312 650 L304 730 L290 740 Z" fill="#8f6fe8" opacity="0.5" />
          <path d="M-10 844 V780 Q100 740 195 770 Q300 800 400 760 V844 Z" fill="#221656" />
        </g>
        <Motes seed={12} color="#e6d6ff" n={10} />
      </>
    );
  }
  if (kind === 'guild') {
    return (
      <>
        <defs>
          <linearGradient id="bd-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f2a5c" /><stop offset="0.45" stop-color="#9a4a62" /><stop offset="0.75" stop-color="#eea45e" /><stop offset="1" stop-color="#5a2c3a" /></linearGradient>
          <radialGradient id="bd-gs"><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.9" /><stop offset="1" stop-color="#ffb060" stop-opacity="0" /></radialGradient>
        </defs>
        <rect width={W} height={H} fill="url(#bd-g)" />
        <circle class="bd-sun" cx="195" cy="600" r="210" fill="url(#bd-gs)" />
        <RuneCircle cx={195} cy={360} r={170} color="#ffe2a8" opacity={0.2} />
        <g fill="none" stroke="#ffe2a8" stroke-width="2" opacity="0.22" stroke-linejoin="round">
          <path d="M195 268 L262 292 V362 Q262 420 195 452 Q128 420 128 362 V292 Z" />
          <path d={spark(195, 356, 34)} />
        </g>
        <path d={ridge(31, 640, 80, 70)} fill="#8a3f58" opacity="0.8" />
        <g fill="#4a2440">
          <Tower x={36} y={560} w={40} h={200} fill="#4a2440" flag="#ffd45c" />
          <Tower x={314} y={560} w={40} h={200} fill="#4a2440" flag="#ffd45c" />
          <path d="M-10 844 V660 h22 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h20 v-14 h20 v14 h30 V844 Z" />
          <path d="M165 844 V730 Q165 696 195 696 Q225 696 225 730 V844 Z" fill="#2c1428" />
        </g>
        <Motes seed={21} color="#ffe9a0" n={7} />
      </>
    );
  }
  return (
    <>
      <defs><linearGradient id="bd-p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#27356a" /><stop offset="0.5" stop-color="#58649e" /><stop offset="0.8" stop-color="#d99a86" /><stop offset="1" stop-color="#2c3560" /></linearGradient></defs>
      <rect width={W} height={H} fill="url(#bd-p)" />
      <Stars seed={4} n={24} />
      <RuneCircle cx={300} cy={230} r={150} color="#ffe2c8" opacity={0.18} />
      <path d={ridge(41, 640, 150, 66)} fill="#6a6aa0" />
      <rect y="520" width={W} height="180" fill="url(#bd-mist)" />
      <path d={ridge(47, 700, 120, 50)} fill="#4a4f88" />
      <rect y="620" width={W} height="160" fill="url(#bd-mist)" />
      <path d={hills(13, 780, 50, 100)} fill="#2c3560" />
      <Motes seed={8} color="#ffe2c8" n={6} />
    </>
  );
}

/** Le fond d'un écran. `dim` l'assombrit un peu (pages chargées en panneaux). */
export function Backdrop({ kind }: { kind: BackdropKind }) {
  if (kind === 'adventure') return <div class="backdrop backdrop-adventure" aria-hidden="true"><AdventureBackdrop /></div>;
  if (kind === 'summon') return <div class="backdrop backdrop-summon" aria-hidden="true"><SummonBackdrop /></div>;
  if (kind === 'heroes') return <div class="backdrop backdrop-heroes" aria-hidden="true"><HeroesBackdrop /></div>;
  if (kind === 'guild') return <div class="backdrop backdrop-guild" aria-hidden="true"><GuildBackdrop /></div>;
  return (
    <div class={`backdrop backdrop-${kind}`} aria-hidden="true">
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid slice">
        <defs><linearGradient id="bd-mist" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="1" stop-color="#fff" stop-opacity="0.3" /></linearGradient></defs>
        <Scene kind={kind} />
      </svg>
    </div>
  );
}
