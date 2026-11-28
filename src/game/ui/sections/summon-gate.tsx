// Le portail d'invocation et l'estrade où il se pose (refait le 26/11/2026, vague 3 : « plus badass », même taille pour
// les deux portails, seule la couleur change). Tout est dessiné par le code, une seule lumière (en haut à droite) :
// - un grand anneau de pierre ancienne, posé sur son socle (il est posé au sol, sur l'estrade) : une couronne de trois
//   pointes serties de gemmes, des runes inventées gravées qui s'allument tour à tour, deux fissures ;
// - dedans, un tourbillon d'énergie en profondeur : trois couches de bras en spirale (plus petites et plus rapides vers
//   le fond), des anneaux qui filent vers le fond, des braises aspirées, un cœur blanc qui bat ;
// - des éclairs COURBES qui crépitent le long du bord et plongent vers le cœur (jamais de rayons droits) ;
// - des éclats de roche qui flottent autour et se balancent ; une onde de lumière qui part de l'anneau de temps en temps ;
// - `charging` : il s'emballe (tout tourne plus vite, les runes brûlent, les éclairs crépitent sans arrêt, la pierre
//   tremble) ; `open` : un éclair blanc, une onde, le tourbillon s'ouvre en grand ;
// - ses couleurs suivent --g-a / --g-b / --g-deep (posées par le CSS : violet, bleu pour l'invocation simple, ou la
//   couleur de la rareté pendant le tirage) ; la pierre, elle, ne change jamais.
// Repère du portail : viewBox « -150 -150 300 278 », centre de l'anneau en (0, 0), le sol (dessous du socle) en y = 128,
// c'est-à-dire tout en bas de la boîte : on pose la boîte sur le dessus de l'estrade.
import { FEATURED_BANNER, type SummonKind } from '../../../core/data/summon';
import { spark } from '../portal';

const f = (n: number) => n.toFixed(1);
const rad = (d: number) => (d * Math.PI) / 180;
type Pt = [number, number];
const pt = (r: number, a: number): Pt => [Math.cos(rad(a)) * r, Math.sin(rad(a)) * r];
const S = (p: Pt) => `${f(p[0])} ${f(p[1])}`;

/** Le repère du portail (pour le placer et retrouver le centre de l'anneau). */
export const GATE_VIEW = { w: 300, h: 278, cy: 150, ring: 110, hole: 80 } as const;

/** Un petit hasard fixe : le même dessin à chaque fois. */
function rnd(seed: number) {
  let s = (seed * 2654435761) >>> 0 || 1;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

/** Une spirale lisse du centre vers le bord (un bras du tourbillon). */
function swirl(turn: number, r: number, width: number): string {
  const pts: string[] = [];
  const back: string[] = [];
  const N = 16;
  for (let i = 0; i <= N; i++) {
    const k = i / N;
    const a = turn + k * 2.4;
    const rr = 4 + (r - 4) * k;
    const w = (width * Math.sin(Math.PI * Math.min(1, k * 1.1))) / Math.max(rr, 8);
    pts.push(`${f(Math.cos(a) * rr)} ${f(Math.sin(a) * rr)}`);
    back.unshift(`${f(Math.cos(a + w) * rr)} ${f(Math.sin(a + w) * rr)}`);
  }
  return `M${pts.join(' L')} L${back.join(' L')} Z`;
}

/** Un arc de a0 à a1 (degrés) au rayon r. */
function arc(r: number, a0: number, a1: number): string {
  return `M${S(pt(r, a0))} A${r} ${r} 0 ${Math.abs(a1 - a0) > 180 ? 1 : 0} 1 ${S(pt(r, a1))}`;
}

/** Un éclair : du rayon r0 au rayon r1, de l'angle a0 à a1, qui ondule (courbes lisses passant par les milieux). */
function bolt(seed: number, r0: number, r1: number, a0: number, a1: number, jit: number): string {
  const R = rnd(seed);
  const N = 7;
  const pts: Pt[] = [];
  for (let i = 0; i <= N; i++) {
    const k = i / N;
    const inner = i > 0 && i < N;
    pts.push(pt(r0 + (r1 - r0) * k + (inner ? (R() - 0.5) * jit : 0), a0 + (a1 - a0) * k + (inner ? (R() - 0.5) * jit * 0.7 : 0)));
  }
  let d = `M${S(pts[0]!)}`;
  for (let i = 1; i < N; i++) {
    const p = pts[i]!, n = pts[i + 1]!;
    d += ` Q${S(p)} ${S([(p[0] + n[0]) / 2, (p[1] + n[1]) / 2])}`;
  }
  return `${d} T${S(pts[N]!)}`;
}

/** Une pierre de la couronne : un bloc qui sort de l'anneau à l'angle a, du rayon r0 au rayon r1, finissant en pointe. */
function spike(a: number, r0: number, r1: number, w0: number, w1: number, tip: number): string {
  const u: Pt = [Math.cos(rad(a)), Math.sin(rad(a))], v: Pt = [-u[1], u[0]];
  const p = (r: number, w: number): Pt => [u[0] * r + v[0] * w, u[1] * r + v[1] * w];
  const apexL = p(r1 + tip * 0.72, -w1 * 0.16), apexR = p(r1 + tip * 0.72, w1 * 0.16);
  return `M${S(p(r0, -w0 / 2))} L${S(p(r1, -w1 / 2))} L${S(apexL)} Q${S(p(r1 + tip, 0))} ${S(apexR)} L${S(p(r1, w1 / 2))} L${S(p(r0, w0 / 2))} Z`;
}

/** Une gemme en amande, couchée le long du rayon (angle a, centre au rayon r). */
function gem(a: number, r: number, len: number, wid: number): string {
  const u: Pt = [Math.cos(rad(a)), Math.sin(rad(a))], v: Pt = [-u[1], u[0]];
  const p = (l: number, w: number): Pt => [u[0] * (r + l) + v[0] * w, u[1] * (r + l) + v[1] * w];
  return `M${S(p(-len, 0))} Q${S(p(0, wid * 1.6))} ${S(p(len, 0))} Q${S(p(0, -wid * 1.6))} ${S(p(-len, 0))} Z`;
}

/** Un éclat de roche : un caillou aux angles adoucis, autour de (cx, cy). */
function rock(seed: number, cx: number, cy: number, s: number): string {
  const R = rnd(seed);
  const n = 6;
  const pts: Pt[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * 360 + (R() - 0.5) * 34 - 90;
    const r = s * (0.72 + R() * 0.42) * (i % 2 ? 1 : 0.86);
    pts.push([cx + Math.cos(rad(a)) * r, cy + Math.sin(rad(a)) * r * 0.86]);
  }
  const mid = (a: Pt, b: Pt): Pt => [a[0] * 0.72 + b[0] * 0.28, a[1] * 0.72 + b[1] * 0.28];
  let d = '';
  for (let i = 0; i < n; i++) {
    const p = pts[i]!, prev = pts[(i + n - 1) % n]!, next = pts[(i + 1) % n]!;
    const a = mid(p, prev), b = mid(p, next);
    d += `${i ? ' L' : 'M'}${S(a)} Q${S(p)} ${S(b)}`;
  }
  return `${d} Z`;
}

/** Les runes : des signes inventés (jamais des lettres), tracés d'un trait ; « h0.01 » = un point. */
const RUNES = [
  'M-5 0 Q0 -5.5 5 0 Q0 5.5 -5 0 Z M0 0h0.01', // l'œil
  'M-4 4.5 C-5 -4 4.5 -5.5 4.2 0 C4 3 0.5 3.2 0.3 0.2', // la vrille
  'M0 -5.5 Q4 0 0 5.5 Q-4 0 0 -5.5 Z M-5.2 0h0.01 M5.2 0h0.01', // l'amande aux deux points
  'M-5 0 Q-2.5 -4.6 0 0 Q2.5 4.6 5 0 M-2.6 3.6h0.01 M2.6 -3.6h0.01', // la vague aux deux points
  'M0 -5.5 Q5.5 2 0 4.8 Q-5.5 2 0 -5.5 Z M-1.8 1.4 Q0 3 1.8 1.4', // la goutte
  'M-5 2.5 A5 5 0 0 1 5 2.5 M-2.4 2.5 A2.4 2.4 0 0 1 2.4 2.5 M0 5.2h0.01', // le double arc
];
/** Où sont gravées les runes, en degrés (en évitant la couronne et le socle), dans l'ordre où la lumière les parcourt. */
const RUNE_AT = [-170, -125, -108, -72, -55, -12, 12, 34, 146, 168];

/** Les éclats de roche qui flottent : [angle, rayon, taille, balancement (degrés), durée (s)]. */
const SHARDS: [number, number, number, number, number][] = [
  [-170, 133, 13, 5, 9.5], [-120, 138, 9.5, 7, 7.8], [-97, 140, 6.5, 6, 11], [-62, 136, 15, 5, 8.6],
  [-14, 134, 10.5, 6, 10.2], [17, 131, 7, 8, 7.2], [163, 131, 7.5, 7, 8.9],
];

/** Les éclairs : [graine, r0, r1, a0, a1, ondulation, durée (s), retard (s), sur la pierre ?]. */
const BOLTS: [number, number, number, number, number, number, number, number, boolean][] = [
  [1, 77, 73, -160, -112, 9, 3.1, 0.2, false],
  [2, 76, 77, -40, 18, 9, 3.7, 1.6, false],
  [3, 77, 74, 50, 104, 9, 4.3, 2.7, false],
  [4, 75, 78, 150, 204, 9, 3.4, 0.9, false],
  [5, 79, 20, -62, -18, 14, 4.9, 2.1, false],
  [6, 79, 24, 138, 186, 14, 4.1, 3.3, false],
  [7, 79, 18, 38, 92, 14, 5.3, 0.6, false],
  [8, 81, 113, -99, -90, 7, 5.9, 1.2, true],
  [9, 81, 106, -154, -145, 6, 6.7, 3.9, true],
  [10, 81, 106, -26, -35, 6, 6.1, 2.4, true],
];

/** Le portail seul. `uid` rend ses dégradés uniques (deux portails peuvent coexister). */
export function Gate({ uid, charging = false, open = false, class: cls = '' }: { uid: string; charging?: boolean; open?: boolean; class?: string }) {
  const g = (n: string) => `sg-${n}-${uid}`;
  const url = (n: string) => `url(#${g(n)})`;
  const sc = (c: string) => ({ stopColor: c });
  const stroke = (c: string) => ({ stroke: c });
  const ring = `M110 0 A110 110 0 1 1 -110 0 A110 110 0 1 1 110 0 Z M80 0 A80 80 0 1 0 -80 0 A80 80 0 1 0 80 0 Z`;
  const crown = spike(-90, 96, 124, 46, 32, 13);
  const hornL = spike(-145, 97, 121, 32, 18, 14);
  const hornR = spike(-35, 97, 121, 32, 18, 14);
  const base = 'M-58 93 L58 93 Q65 93 67 99 L77 121 Q79 128 72 128 L-72 128 Q-79 128 -77 121 L-67 99 Q-65 93 -58 93 Z';
  const baseTop = 'M-58 93 L58 93 Q65 93 67 99 L69 103 L-69 103 L-67 99 Q-65 93 -58 93 Z';
  const stones = [crown, hornL, hornR, base];
  const runeGlow = (d: string, w: number) => <path d={d} fill="none" style={stroke('var(--g-b)')} stroke-width={w} stroke-linecap="round" stroke-linejoin="round" />;
  return (
    <div class={`sg${charging ? ' sg-charging' : ''}${open ? ' sg-open' : ''} ${cls}`} aria-hidden="true">
      <svg viewBox="-150 -150 300 278">
        <defs>
          <radialGradient id={g('aura')}><stop offset="0" style={sc('var(--g-a)')} stop-opacity="0.75" /><stop offset="0.5" style={sc('var(--g-a)')} stop-opacity="0.22" /><stop offset="1" style={sc('var(--g-a)')} stop-opacity="0" /></radialGradient>
          {/* le tourbillon : un bord qui brille, une couronne sombre (la profondeur), un fond qui s'allume jusqu'au cœur blanc */}
          <radialGradient id={g('disc')}>
            <stop offset="0" stop-color="#ffffff" /><stop offset="0.08" stop-color="#ffffff" stop-opacity="0.95" /><stop offset="0.18" style={sc('var(--g-b)')} />
            <stop offset="0.36" style={sc('var(--g-a)')} /><stop offset="0.6" style={sc('var(--g-deep)')} />
            <stop offset="0.8" style={sc('color-mix(in srgb, var(--g-deep) 55%, #000)')} /><stop offset="0.93" style={sc('var(--g-a)')} /><stop offset="1" style={sc('var(--g-b)')} />
          </radialGradient>
          <linearGradient id={g('arm')} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.85" /><stop offset="1" style={sc('var(--g-b)')} stop-opacity="0.15" /></linearGradient>
          {/* la pierre : claire en haut à droite (la lumière), sombre en bas à gauche */}
          <linearGradient id={g('stone')} gradientUnits="userSpaceOnUse" x1="105" y1="-125" x2="-95" y2="125">
            <stop offset="0" stop-color="#c9c6d8" /><stop offset="0.3" stop-color="#8f8ca6" /><stop offset="0.62" stop-color="#5b5873" /><stop offset="1" stop-color="#33314a" />
          </linearGradient>
          <linearGradient id={g('rock')} x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c4c1d4" /><stop offset="0.45" stop-color="#7d7a95" /><stop offset="1" stop-color="#3a3852" /></linearGradient>
          {/* le bord intérieur de l'anneau : la face qui regarde la lumière est en bas à gauche */}
          <linearGradient id={g('bevel')} gradientUnits="userSpaceOnUse" x1="-60" y1="60" x2="60" y2="-60">
            <stop offset="0" stop-color="#e4e1f2" stop-opacity="0.75" /><stop offset="0.5" stop-color="#e4e1f2" stop-opacity="0" /><stop offset="1" stop-color="#000" stop-opacity="0.35" />
          </linearGradient>
          <radialGradient id={g('glow')}><stop offset="0" stop-color="#fff" stop-opacity="0.95" /><stop offset="0.35" style={sc('var(--g-b)')} stop-opacity="0.7" /><stop offset="1" style={sc('var(--g-a)')} stop-opacity="0" /></radialGradient>
          <clipPath id={g('hole')}><circle r="81" /></clipPath>
          <clipPath id={g('face')}><path d="M110 0 A110 110 0 1 1 -110 0 A110 110 0 1 1 110 0 Z M80 0 A80 80 0 1 0 -80 0 A80 80 0 1 0 80 0 Z" clip-rule="evenodd" /></clipPath>
        </defs>

        {/* derrière : la grande lueur qui respire, les ondes qui partent de l'anneau */}
        <circle class="sg-aura" r="150" fill={url('aura')} />
        <circle class="sg-pulse" r="96" fill="none" style={stroke('var(--g-b)')} stroke-width="3" />
        <circle class="sg-pulse sg-pulse-2" r="96" fill="none" style={stroke('var(--g-a)')} stroke-width="6" />

        <g class="sg-body">
          {/* les éclats de roche qui flottent et se balancent autour de l'anneau */}
          <g class="sg-shards"><circle r="150" fill="none" />
            {SHARDS.map(([a, r, s, sw, dur], i) => {
              const [x, y] = pt(r, a);
              return (
                <g class="sg-shard" style={{ '--sw': `${sw}deg`, animationDuration: `${dur}s`, animationDelay: `${-i * 1.3}s` } as never}><circle r="150" fill="none" />
                  <g class="sg-bob" style={{ animationDuration: `${(dur * 0.47).toFixed(2)}s`, animationDelay: `${-i * 0.7}s` }}>
                    <path d={rock(i + 3, x, y, s)} fill={url('rock')} stroke="#0b0820" stroke-width="1.8" stroke-linejoin="round" />
                    <path d={rock(i + 3, x + s * 0.12, y - s * 0.12, s * 0.62)} fill="#fff" opacity="0.18" />
                  </g>
                </g>
              );
            })}
          </g>

          {/* le tourbillon */}
          <g class="sg-hole"><circle r="82" fill="none" />
            <circle r="82" fill={url('disc')} />
            <g clip-path={url('hole')}>
              {[0, 1, 2, 3].map((i) => <circle class="sg-tunnel" r="78" fill="none" stroke="#fff" stroke-width="2.5" style={{ animationDelay: `${-i * 0.55}s` }} />)}
              <g class="sg-vortex"><circle r="82" fill="none" />
                <g class="sg-sw1"><circle r="82" fill="none" />{[0, 2.09, 4.19].map((k) => <path d={swirl(k, 84, 30)} fill={url('arm')} opacity="0.8" />)}</g>
                <g transform="scale(0.62)"><g class="sg-sw2"><circle r="82" fill="none" />{[0.6, 2.2, 3.8, 5.4].map((k) => <path d={swirl(k, 82, 20)} fill="#fff" opacity="0.38" />)}</g></g>
                <g transform="scale(0.34)"><g class="sg-sw3"><circle r="82" fill="none" />{[1.2, 3.3, 5.4].map((k) => <path d={swirl(k, 82, 24)} fill="#fff" opacity="0.55" />)}</g></g>
              </g>
              {/* les braises aspirées vers le fond */}
              {Array.from({ length: 9 }, (_, i) => (
                <g class="sg-ember" style={{ '--a': `${i * 40 + (i % 3) * 13}deg`, '--dur': `${2.6 + (i % 4) * 0.45}s`, animationDelay: `${-i * 0.43}s` } as never}>
                  <circle r="80" fill="none" /><circle cx="74" r={i % 3 ? 1.6 : 2.4} fill="#fff" />
                </g>
              ))}
              {/* les éclairs du dedans */}
              {BOLTS.filter((b) => !b[8]).map(([s, r0, r1, a0, a1, j, dur, del]) => {
                const d = bolt(s, r0, r1, a0, a1, j);
                return (
                  <g class="sg-bolt" style={{ '--dur': `${dur}s`, animationDelay: `${del}s` } as never}>
                    <path d={d} fill="none" style={stroke('var(--g-b)')} stroke-width="4.5" stroke-linecap="round" opacity="0.5" />
                    <path d={d} fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round" />
                  </g>
                );
              })}
            </g>
            {/* le cœur */}
            <circle class="sg-core" r="34" fill={url('glow')} opacity="0.6" />
            <circle class="sg-core sg-core-2" r="10" fill="#fff" />
            {/* l'invocation part : la lumière monte dans le portail, rien ne bouge (28/11) */}
            <circle class="sg-cast-light" r="81" fill={url('glow')} />
          </g>

          {/* la pierre : d'abord un seul contour pour tout (anneau, couronne, socle), puis les morceaux par-dessus */}
          <g fill="#0b0820" stroke="#0b0820" stroke-width="5" stroke-linejoin="round">
            <path d={ring} fill-rule="evenodd" />
            {stones.map((d) => <path d={d} />)}
          </g>
          <path d={ring} fill-rule="evenodd" fill={url('stone')} />
          {/* le grain de la vieille pierre : quelques taches douces, plus sombres en bas à gauche */}
          <g clip-path={url('face')}>
            {[[-70, 62, 30, 0.2], [-96, -18, 22, 0.16], [52, 84, 26, 0.12], [88, 30, 18, 0.1], [-30, -100, 18, 0.1]].map(([x, y, r, o]) => (
              <ellipse cx={x} cy={y} rx={r} ry={r! * 0.6} transform={`rotate(${f(Math.atan2(y!, x!) * 57.3 + 90)} ${x} ${y})`} fill="#0b0820" opacity={o} />
            ))}
            {[[70, -66, 20, 0.12], [24, -104, 16, 0.1]].map(([x, y, r, o]) => <ellipse cx={x} cy={y} rx={r} ry={r! * 0.55} transform={`rotate(${f(Math.atan2(y!, x!) * 57.3 + 90)} ${x} ${y})`} fill="#fff" opacity={o} />)}
          </g>
          {/* la bande gravée où sont les runes : deux sillons, chacun avec sa lèvre éclairée */}
          <circle r="103.2" fill="none" stroke="#0b0820" stroke-width="1.5" opacity="0.42" />
          <circle r="104.3" fill="none" stroke="#fff" stroke-width="0.9" opacity="0.2" />
          <circle r="87.4" fill="none" stroke="#0b0820" stroke-width="1.5" opacity="0.42" />
          <circle r="88.5" fill="none" stroke="#fff" stroke-width="0.9" opacity="0.2" />
          {/* les ombres douces que la couronne pose sur l'anneau, puis la couronne */}
          <path d={arc(101, -114, -66)} fill="none" stroke="#0b0820" stroke-width="5" stroke-linecap="round" opacity="0.28" />
          <path d={arc(102, -158, -132)} fill="none" stroke="#0b0820" stroke-width="4" stroke-linecap="round" opacity="0.25" />
          <path d={arc(102, -48, -22)} fill="none" stroke="#0b0820" stroke-width="4" stroke-linecap="round" opacity="0.25" />
          {[crown, hornL, hornR].map((d) => <path d={d} fill={url('stone')} />)}
          {/* le socle : l'anneau est pris dedans ; son dessus reçoit la lumière, son ombre douce sur l'anneau */}
          <path d="M-56 92 Q0 86 56 92" fill="none" stroke="#0b0820" stroke-width="4" stroke-linecap="round" opacity="0.3" />
          <path d={base} fill={url('stone')} />
          <path d={baseTop} fill="#fff" opacity="0.16" />
          <path d="M-56 93.6 L56 93.6" stroke="#fff" stroke-width="1.4" stroke-linecap="round" opacity="0.45" />
          <path d="M68 104 L76 122" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity="0.35" />

          {/* le bord intérieur : la face éclairée, la lueur du tourbillon sur la pierre */}
          <circle r="83" fill="none" stroke={url('bevel')} stroke-width="6" />
          <circle class="sg-lip" r="84" fill="none" style={stroke('var(--g-a)')} stroke-width="7" opacity="0.3" />
          <circle r="81.2" fill="none" style={stroke('var(--g-b)')} stroke-width="2" opacity="0.9" />
          {/* la lumière sur le bord de l'anneau et des pointes (en haut à droite), l'ombre en bas à gauche */}
          <path d={arc(107.5, -84, -6)} fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" opacity="0.5" />
          <path d={arc(107, 118, 212)} fill="none" stroke="#0b0820" stroke-width="5" stroke-linecap="round" opacity="0.22" />
          {/* deux fissures */}
          <path d={`M${S(pt(110, 152))} Q${S(pt(101, 158))} ${S(pt(97, 151))} T${S(pt(88, 157))}`} fill="none" stroke="#0b0820" stroke-width="1.4" stroke-linecap="round" opacity="0.55" />
          <path d={`M${S(pt(110, 24))} Q${S(pt(103, 18))} ${S(pt(99, 24))}`} fill="none" stroke="#0b0820" stroke-width="1.2" stroke-linecap="round" opacity="0.5" />

          {/* les runes gravées : un creux sombre, puis la lumière qui les parcourt l'une après l'autre */}
          {RUNE_AT.map((a, i) => {
            const [x, y] = pt(95.5, a);
            const d = RUNES[i % RUNES.length]!;
            return (
              <g transform={`translate(${f(x)} ${f(y)}) rotate(${a + 90}) scale(1.32)`}>
                <path d={d} fill="none" stroke="#0b0820" stroke-width="3.1" stroke-linecap="round" stroke-linejoin="round" opacity="0.5" />
                <g class="sg-rune" style={{ animationDelay: `${(i * 0.42).toFixed(2)}s` }}>
                  <g opacity="0.45">{runeGlow(d, 4.6)}</g>
                  {runeGlow(d, 1.5)}
                </g>
              </g>
            );
          })}
          {/* la rune du socle */}
          <g transform="translate(0 113) scale(1.45)">
            <path d={RUNES[0]} fill="none" stroke="#0b0820" stroke-width="3" stroke-linecap="round" opacity="0.5" />
            <g class="sg-rune sg-rune-base"><g opacity="0.35">{runeGlow(RUNES[0]!, 4)}</g>{runeGlow(RUNES[0]!, 1.4)}</g>
          </g>

          {/* les gemmes serties dans la couronne */}
          {[[-90, 112, 11, 4.6], [-145, 109, 7, 3], [-35, 109, 7, 3]].map(([a, r, l, w], i) => (
            <g>
              <circle class="sg-gem-glow" cx={f(pt(r!, a!)[0])} cy={f(pt(r!, a!)[1])} r={l! * 1.9} fill={url('glow')} style={{ animationDelay: `${-i * 0.7}s` }} />
              <path d={gem(a!, r!, l!, w!)} fill="#0b0820" stroke="#0b0820" stroke-width="2.4" stroke-linejoin="round" />
              <path d={gem(a!, r!, l!, w!)} style={{ fill: 'var(--g-a)' }} />
              <path d={gem(a!, r! + l! * 0.15, l! * 0.6, w! * 0.45)} fill="#fff" opacity="0.75" transform={`translate(${f(w! * 0.5)} ${f(-w! * 0.3)})`} />
            </g>
          ))}

          {/* les éclairs qui sautent du tourbillon sur la pierre, jusqu'aux gemmes */}
          {BOLTS.filter((b) => b[8]).map(([s, r0, r1, a0, a1, j, dur, del]) => {
            const d = bolt(s, r0, r1, a0, a1, j);
            return (
              <g class="sg-bolt" style={{ '--dur': `${dur}s`, animationDelay: `${del}s` } as never}>
                <path d={d} fill="none" style={stroke('var(--g-b)')} stroke-width="4" stroke-linecap="round" opacity="0.55" />
                <path d={d} fill="none" stroke="#fff" stroke-width="1.3" stroke-linecap="round" />
              </g>
            );
          })}
          <path class="sg-glint" d={spark(76, -79, 7)} fill="#fff" />
        </g>
        {/* l'onde et l'éclair blanc de l'ouverture */}
        <circle class="sg-wave" r="84" fill="none" stroke="#fff" stroke-width="6" />
        <circle class="sg-flash" r="96" fill="#fff" />
      </svg>
    </div>
  );
}

/** Une gerbe de cristaux posée au sol (pied en 0, 0) : trois éclats lisses, la face éclairée à droite. */
function Crystals({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <path d="M-14 1 Q-17 -10 -11 -19 Q-6 -10 -4 1 Z M-4 1 Q-6 -20 2 -34 Q10 -20 8 1 Z M8 1 Q9 -9 15 -15 Q20 -7 17 1 Z" fill="#0b0820" stroke="#0b0820" stroke-width="2.6" stroke-linejoin="round" />
      <path d="M-14 1 Q-17 -10 -11 -19 Q-6 -10 -4 1 Z" style={{ fill: 'var(--g-a)' }} />
      <path d="M-11 -19 Q-6 -10 -4 1 L-8 1 Q-9 -9 -11 -19 Z" fill="#fff" opacity="0.45" />
      <path d="M-4 1 Q-6 -20 2 -34 Q10 -20 8 1 Z" style={{ fill: 'var(--g-b)' }} />
      <path d="M2 -34 Q10 -20 8 1 L3 1 Q4 -18 2 -34 Z" fill="#fff" opacity="0.55" />
      <path d="M8 1 Q9 -9 15 -15 Q20 -7 17 1 Z" style={{ fill: 'var(--g-a)' }} />
      <path d="M15 -15 Q20 -7 17 1 L14 1 Q15 -8 15 -15 Z" fill="#fff" opacity="0.45" />
    </g>
  );
}

/**
 * L'estrade : deux dalles de pierre posées au sol, vues un peu de haut (repère 360 × 110, le dessus de la dalle haute est
 * centré en 180, 34 : c'est là que se pose le socle du portail, ou les pieds du héros). Un liseré de lumière de la couleur
 * du portail, la lumière du tourbillon qui se répand sur le dessus. `crystals` : des gerbes aux deux bouts.
 */
export function Dais({ uid, crystals = false, class: cls = '' }: { uid: string; crystals?: boolean; class?: string }) {
  const g = (n: string) => `sd-${n}-${uid}`;
  // une dalle : dessus (un rectangle arrondi aplati) et tranche, de demi-largeur w, au niveau y, d'épaisseur h
  const slab = (w: number, y: number, h: number, d: number) => {
    const top = `M${180 - w + d} ${y - d * 0.55} Q${180 - w} ${y - d * 0.55} ${180 - w} ${y} Q${180 - w} ${y + d * 0.55} ${180 - w + d} ${y + d * 0.55} L${180 + w - d} ${y + d * 0.55} Q${180 + w} ${y + d * 0.55} ${180 + w} ${y} Q${180 + w} ${y - d * 0.55} ${180 + w - d} ${y - d * 0.55} Z`;
    const side = `M${180 - w} ${y} Q${180 - w} ${y + d * 0.55} ${180 - w + d} ${y + d * 0.55} L${180 + w - d} ${y + d * 0.55} Q${180 + w} ${y + d * 0.55} ${180 + w} ${y} V${y + h} Q${180 + w} ${y + h + d * 0.55} ${180 + w - d} ${y + h + d * 0.55} L${180 - w + d} ${y + h + d * 0.55} Q${180 - w} ${y + h + d * 0.55} ${180 - w} ${y + h} Z`;
    return { top, side };
  };
  const low = slab(170, 62, 16, 26);
  const high = slab(118, 34, 14, 20);
  return (
    <svg class={`sd ${cls}`} viewBox="0 0 360 110" aria-hidden="true">
      <defs>
        <linearGradient id={g('top')} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#34324c" /><stop offset="0.62" stop-color="#5f5c78" /><stop offset="1" stop-color="#8d8aa4" /></linearGradient>
        <linearGradient id={g('side')} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#17152a" /><stop offset="0.7" stop-color="#2b2942" /><stop offset="1" stop-color="#3f3d59" /></linearGradient>
        <radialGradient id={g('pool')}><stop offset="0" stop-color="#fff" stop-opacity="0.9" /><stop offset="0.3" style={{ stopColor: 'var(--g-b)' }} stop-opacity="0.7" /><stop offset="1" style={{ stopColor: 'var(--g-a)' }} stop-opacity="0" /></radialGradient>
        <linearGradient id={g('seam')} x1="0" y1="0" x2="1" y2="0"><stop offset="0" style={{ stopColor: 'var(--g-b)' }} stop-opacity="0" /><stop offset="0.6" stop-color="#fff" /><stop offset="1" style={{ stopColor: 'var(--g-b)' }} stop-opacity="0" /></linearGradient>
      </defs>
      <path d={`M14 96 Q14 86 40 86 L320 86 Q346 86 346 96 Q346 106 320 106 L40 106 Q14 106 14 96 Z`} fill="#05021a" opacity="0.5" />
      {/* un seul contour pour les deux dalles */}
      <g fill="#0b0820" stroke="#0b0820" stroke-width="4" stroke-linejoin="round">
        <path d={low.side} /><path d={low.top} /><path d={high.side} /><path d={high.top} />
      </g>
      <path d={low.side} fill={`url(#${g('side')})`} /><path d={low.top} fill={`url(#${g('top')})`} />
      <path d={`M${180 - 150} ${62 + 9} L${180 + 150} ${62 + 9}`} stroke={`url(#${g('seam')})`} stroke-width="2" class="sd-seam" />
      <path d={`M${180 - 118} ${34 + 12} Q180 ${34 + 20} ${180 + 118} ${34 + 12}`} fill="none" stroke="#0b0820" stroke-width="5" opacity="0.25" />
      <path d={high.side} fill={`url(#${g('side')})`} /><path d={high.top} fill={`url(#${g('top')})`} />
      <path d={`M${180 - 100} ${34 + 7} L${180 + 100} ${34 + 7}`} stroke={`url(#${g('seam')})`} stroke-width="2.4" class="sd-seam" />
      <path d={`M${180 + 30} ${34 - 10.4} L${180 + 96} ${34 - 10.4}`} stroke="#fff" stroke-width="1.4" stroke-linecap="round" opacity="0.35" />
      {/* la lumière du tourbillon répandue sur le dessus */}
      <ellipse class="sd-pool" cx="180" cy="33" rx="96" ry="10" fill={`url(#${g('pool')})`} />
      {crystals && <><Crystals x={34} y={66} s={1.15} /><Crystals x={326} y={66} s={1.25} flip /></>}
    </svg>
  );
}

/** La scène de l'onglet : l'estrade, le portail posé dessus, des grains qui montent. Même taille et même place pour les
 * trois portails ; au repos chacun a sa lumière (couleurs posées par le CSS, ou par FEATURED_BANNER pour le spécial),
 * avec une onde de lumière au changement. Le portail spécial : quatre éclats des éléments tournent autour de l'anneau (ses
 * héros mis en avant ne se montrent que dans les chances, demande du propriétaire du 27/11).
 * `casting` : la lumière monte à l'intérieur du portail, sans aucun mouvement (le tirage s'ouvre ensuite par-dessus,
 * summon-reveal.tsx ; demande du 28/11). */
export function GateStage({ kind, casting }: { kind: SummonKind; casting: boolean }) {
  const featured = kind === 'featured';
  return (
    <div class={`sg-stage sg-kind-${kind}${casting ? ' sg-casting' : ''}`}>
      <Dais uid="tab" crystals class="sg-stage-dais" />
      <Gate uid="tab" class="sg-stage-gate" />
      {featured && (
        <span class="sg-orbit" aria-hidden="true">
          {FEATURED_BANNER.sparks.map((c, i) => <i style={{ '--c': c, '--i': i } as never}><b style={{ animationDelay: `${-i * 0.55}s` }} /></i>)}
        </span>
      )}
      <span class="sg-swap" key={kind} />
      <span class="sg-motes" aria-hidden="true">
        {Array.from({ length: 12 }, (_, i) => (
          <i style={{ left: `${10 + ((i * 37) % 80)}%`, animationDelay: `${-i * 0.47}s`, animationDuration: `${3.2 + (i % 4) * 0.6}s`,
            ...(featured ? { '--mote': FEATURED_BANNER.sparks[i % FEATURED_BANNER.sparks.length] } : {}) } as never} />
        ))}
      </span>
    </div>
  );
}
