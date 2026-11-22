// Le portail d'invocation : dessiné par le code et toujours en mouvement.
// Posé sur un socle de pierre gravé : un anneau d'or serti de gemmes, un anneau de runes qui tourne à l'envers et
// s'allume tour à tour, un tourbillon de magie en spirale (trois couches à des vitesses différentes), un cœur qui bat,
// des ondes et des étincelles de lumière. `scene` l'installe dans son décor (rayons doux, lueur au sol).
import './portal.css';

const INK = '#2f2244';
const C = 120; // centre du dessin (240 × 240)

/** Un bras de spirale : une bande qui s'élargit en s'éloignant du centre (spirale logarithmique). */
function arm(turn: number, r0: number, r1: number, width: number, twist: number): string {
  const pts: [number, number][] = [];
  const back: [number, number][] = [];
  const N = 22;
  for (let i = 0; i <= N; i++) {
    const k = i / N;
    const r = r0 + (r1 - r0) * k;
    const a = turn + twist * k;
    const w = width * (0.25 + 0.75 * Math.sin(Math.PI * Math.min(1, k * 1.15))) * (r / r1 + 0.25);
    pts.push([C + Math.cos(a) * r, C + Math.sin(a) * r]);
    back.push([C + Math.cos(a + w / Math.max(r, 12)) * r, C + Math.sin(a + w / Math.max(r, 12)) * r]);
  }
  const f = (p: [number, number]) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`;
  return `M${pts.map(f).join(' L')} L${back.reverse().map(f).join(' L')} Z`;
}

/** Une étoile à quatre branches (étincelle). */
export function spark(x: number, y: number, r: number): string {
  const q = r * 0.28;
  return `M${x} ${y - r} L${x + q} ${y - q} L${x + r} ${y} L${x + q} ${y + q} L${x} ${y + r} L${x - q} ${y + q} L${x - r} ${y} L${x - q} ${y - q} Z`;
}

/** Les signes : inventés (chevrons, arcs, points, losanges), jamais une forme de lettre. */
export const RUNES = [
  'M-5 5 L0 -5 L5 5', 'M0 -6 L5 0 L0 6 L-5 0 Z', 'M-5 3 Q0 -8 5 3', 'M-3 -6 V6 M3 -6 V6',
  'M0 -6 L5.500 5 H-5.500 Z', 'M-4.500 0 h0.010 M0 0 h0.010 M4.500 0 h0.010', 'M-5 -3 Q0 3 5 -3 M-5 3 Q0 9 5 3', 'M-4.500 0 A4.500 4.500 0 1 0 4.500 0 A4.500 4.500 0 1 0 -4.500 0',
  'M-5 -4 Q0 -9 5 -4 M0 -2 V6', 'M-5 5 L0 0 L-5 -5 M1 5 L6 0 L1 -5', 'M0 -6 V6 M-5 0 h0.010 M5 0 h0.010', 'M-5 -2 L0 -6 L5 -2 M-5 4 L0 0 L5 4',
];

export function Portal({ kind = 'normal', size = 208, base = true, claws = false }: { kind?: 'normal' | 'basic'; size?: number; base?: boolean; claws?: boolean }) {
  const id = `pt-${kind}`;
  const arms = (n: number, r0: number, r1: number, w: number, twist: number) =>
    Array.from({ length: n }, (_, i) => arm((i * Math.PI * 2) / n, r0, r1, w, twist));
  return (
    <div class={`portal portal-${kind}`} style={{ width: `${size}px`, height: `${size * (base ? 1.23 : 1)}px` }} aria-hidden="true">
      {base && (
        <svg class="pt-base" viewBox="0 0 240 70" width="100%" height={size * 0.292}>
          {/* le socle : deux marches de pierre, un cercle de runes qui luit, deux cristaux */}
          <ellipse cx="120" cy="50" rx="104" ry="17" fill={INK} opacity="0.18" />
          <path d="M26 34 L26 46 A94 15 0 0 0 214 46 L214 34 Z" fill="#a79cc0" stroke={INK} stroke-width="3.5" stroke-linejoin="round" />
          <ellipse cx="120" cy="34" rx="94" ry="15" fill="#d9d2e6" stroke={INK} stroke-width="3.5" />
          <path d="M48 22 L48 31 A72 11.5 0 0 0 192 31 L192 22 Z" fill="#b9afd0" stroke={INK} stroke-width="3.5" stroke-linejoin="round" />
          <ellipse cx="120" cy="22" rx="72" ry="11.5" fill="#eeeaf6" stroke={INK} stroke-width="3.5" />
          <ellipse class="pt-seal" cx="120" cy="22" rx="52" ry="7.5" fill="none" stroke="var(--p-arm-b)" stroke-width="3" />
          <ellipse class="pt-seal" cx="120" cy="22" rx="30" ry="4" fill="var(--p-glow)" opacity="0.7" />
          {[[70, 41], [96, 46], [146, 46], [172, 41]].map(([x, y]) => <path d={`M${x! - 4} ${y} l4 -5 l4 5 l-4 5 Z`} fill="var(--p-arm-b)" stroke={INK} stroke-width="1.6" />)}
          <path d="M22 40 L30 18 L40 34 L36 48 Z" fill="var(--p-gem)" stroke={INK} stroke-width="3" stroke-linejoin="round" />
          <path d="M28 30 L31 22 L35 30 Z" fill="#fff" opacity="0.7" />
          <path d="M218 42 L210 22 L201 36 L205 49 Z" fill="var(--p-arm-b)" stroke={INK} stroke-width="3" stroke-linejoin="round" />
          <path d="M209 33 L211 26 L214 33 Z" fill="#fff" opacity="0.7" />
        </svg>
      )}
      <svg class="pt-float" viewBox="0 0 240 240" width="100%" height={size}>
        <defs>
          <radialGradient id={`${id}-deep`} cx="50%" cy="50%" r="50%">
            <stop offset="0" stop-color="var(--p-core)" />
            <stop offset="0.35" stop-color="var(--p-mid)" />
            <stop offset="0.8" stop-color="var(--p-deep)" />
            <stop offset="1" stop-color="var(--p-edge)" />
          </radialGradient>
          <radialGradient id={`${id}-glow`} cx="50%" cy="50%" r="50%">
            <stop offset="0" stop-color="var(--p-glow)" stop-opacity="0.95" />
            <stop offset="0.55" stop-color="var(--p-glow)" stop-opacity="0.35" />
            <stop offset="1" stop-color="var(--p-glow)" stop-opacity="0" />
          </radialGradient>
          <linearGradient id={`${id}-gold`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="var(--p-ring-hi)" />
            <stop offset="0.5" stop-color="var(--p-ring)" />
            <stop offset="1" stop-color="var(--p-ring-lo)" />
          </linearGradient>
          <radialGradient id={`${id}-rim`} cx="50%" cy="50%" r="50%">
            <stop offset="0.68" stop-color="#1b1040" stop-opacity="0" />
            <stop offset="1" stop-color="#1b1040" stop-opacity="0.6" />
          </radialGradient>
          <clipPath id={`${id}-clip`}><circle cx={C} cy={C} r="71" /></clipPath>
        </defs>

        {/* halo, ondes de magie et rayons derrière le portail */}
        <circle class="pt-halo" cx={C} cy={C} r="118" fill={`url(#${id}-glow)`} />
        <circle class="pt-wave" cx={C} cy={C} r="104" fill="none" stroke="var(--p-glow)" stroke-width="5" />
        <circle class="pt-wave pt-wave-2" cx={C} cy={C} r="104" fill="none" stroke="var(--p-glow)" stroke-width="5" />
        {/* le tourbillon : fond profond, puis trois couches de bras en spirale */}
        <circle cx={C} cy={C} r="73" fill={INK} />
        <g clip-path={`url(#${id}-clip)`}>
          <circle cx={C} cy={C} r="72" fill={`url(#${id}-deep)`} />
          <g class="pt-swirl pt-swirl-a">{arms(5, 14, 76, 30, 2.6).map((d) => <path d={d} fill="var(--p-arm-a)" opacity="0.85" />)}</g>
          <g class="pt-swirl pt-swirl-b">{arms(4, 8, 70, 20, 3.4).map((d) => <path d={d} fill="var(--p-arm-b)" opacity="0.9" />)}</g>
          <g class="pt-swirl pt-swirl-c">{arms(3, 4, 46, 12, 4.2).map((d) => <path d={d} fill="#ffffff" opacity="0.85" />)}</g>
          <g class="pt-swirl pt-swirl-b">{arms(4, 16, 66, 4, 3.4).map((d) => <path d={d} fill="#fff" opacity="0.75" />)}</g>
          {[[84, 150, 5], [158, 92, 4], [150, 162, 3.5], [92, 100, 3], [128, 70, 3.5]].map(([x, y, r], i) => (
            <path class="pt-twinkle" d={spark(x!, y!, r!)} fill="#fff" style={{ animationDelay: `${-i * 0.55}s`, transformOrigin: `${x}px ${y}px` } as never} />
          ))}
          {/* le tunnel : trois anneaux de lumière aspirés vers le cœur, l'un après l'autre */}
          {[0, 1, 2].map((i) => <circle class="pt-tunnel" cx={C} cy={C} r="64" fill="none" stroke="#fff" stroke-width="3" style={{ animationDelay: `${-i * 0.8}s` }} />)}
          <circle class="pt-core" cx={C} cy={C} r="17" fill="#fff" />
          <circle class="pt-core pt-core-2" cx={C} cy={C} r="30" fill="var(--p-core)" opacity="0.55" />
          <path class="pt-flare" d={spark(C, C, 30)} fill="#fff" opacity="0.85" />
          {/* reflet de verre en haut du tourbillon */}
          <path d="M62 96 Q84 58 126 54 Q96 66 78 104 Z" fill="#fff" opacity="0.28" />
          <circle cx={C} cy={C} r="72" fill={`url(#${id}-rim)`} />
          <circle cx={C} cy={C} r="69.5" fill="none" stroke="var(--p-arm-b)" stroke-width="3" opacity="0.8" />
        </g>

        {/* l'anneau de runes (tourne à l'envers) */}
        <g class="pt-runes">
          <circle cx={C} cy={C} r="84" fill="none" stroke={INK} stroke-width="19" />
          <circle cx={C} cy={C} r="84" fill="none" stroke="var(--p-band)" stroke-width="14" />
          <circle cx={C} cy={C} r="77.5" fill="none" stroke={`url(#${id}-gold)`} stroke-width="1.6" opacity="0.9" />
          <circle cx={C} cy={C} r="90.5" fill="none" stroke={`url(#${id}-gold)`} stroke-width="1.6" opacity="0.9" />
          {RUNES.map((d, i) => {
            const a = (i * 360) / RUNES.length;
            return <path class="pt-rune" d={d} transform={`rotate(${a} ${C} ${C}) translate(${C} ${C - 84}) scale(0.72)`} fill="none" stroke="var(--p-rune)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" style={{ animationDelay: `${-i * 0.3}s` }} />;
          })}
        </g>

        {/* derrière l'anneau : la couronne de pointes et d'ailes d'or (rien vers le bas : le portail flotte au-dessus de l'estrade) */}
        {claws && (
          <g class="pt-claws">
            {/* la grande flèche du haut, ses deux volutes, sa gemme */}
            <path d={`M${C - 15} 24 Q${C - 13} 10 ${C - 6} 2 L${C} -30 L${C + 6} 2 Q${C + 13} 10 ${C + 15} 24 Z`} fill={`url(#${id}-gold)`} stroke={INK} stroke-width="3" stroke-linejoin="round" />
            <path d={`M${C} -30 L${C + 6} 2 Q${C + 13} 10 ${C + 15} 24 H${C + 4} Q${C + 4} 8 ${C} -30 Z`} fill="#fff" opacity="0.3" />
            <path d={`M${C - 15} 14 Q${C - 28} 12 ${C - 30} 2 Q${C - 22} 8 ${C - 13} 6 Z M${C + 15} 14 Q${C + 28} 12 ${C + 30} 2 Q${C + 22} 8 ${C + 13} 6 Z`} fill={`url(#${id}-gold)`} stroke={INK} stroke-width="2.4" stroke-linejoin="round" />
            <path d={`M${C} -6 L${C + 7} 5 L${C} 16 L${C - 7} 5 Z`} fill="var(--p-gem)" stroke={INK} stroke-width="2.4" stroke-linejoin="round" />
            <path d={`M${C} -3 L${C + 4} 4 H${C} Z`} fill="#fff" opacity="0.8" />
            {/* les ailes d'or : de chaque côté, trois plumes qui partent d'un même point de l'anneau et montent en éventail
                (elles se chevauchent, la plus longue au milieu) : des ailes, pas des rayons */}
            {[1, -1].map((side) => {
              const ra = (-20 * Math.PI) / 180, rx = C + side * Math.cos(ra) * 97, ry = C + Math.sin(ra) * 97;
              return (
                <g transform={`translate(${rx.toFixed(1)} ${ry.toFixed(1)}) scale(${side} 1)`}>
                  {[[-62, 40, 11], [-18, 44, 12], [-40, 58, 15]].map(([deg, len, w]) => (
                    <g transform={`rotate(${deg})`}>
                      <path d={`M0 ${-w! / 2} Q${len! * 0.55} ${-w! * 1.05} ${len!} ${-w! * 0.12} Q${len! * 0.62} ${w! * 0.55} 0 ${w! / 2} Z`} fill={`url(#${id}-gold)`} stroke={INK} stroke-width="2.6" stroke-linejoin="round" />
                      <path d={`M3 ${-w! * 0.12} Q${len! * 0.55} ${-w! * 0.5} ${len! * 0.9} ${-w! * 0.14}`} fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity="0.6" />
                    </g>
                  ))}
                  <circle r="7" fill={INK} /><circle r="5.4" fill={`url(#${id}-gold)`} /><path d="M0 -3.2 L2.6 0 L0 3.2 L-2.6 0 Z" fill="var(--p-gem)" />
                </g>
              );
            })}
          </g>
        )}

        {/* l'anneau d'or : double, perlé sur son bord, six gemmes serties dans des chatons d'or */}
        <g class="pt-ring">
          <circle cx={C} cy={C} r="100" fill="none" stroke={INK} stroke-width="17" />
          <circle cx={C} cy={C} r="100" fill="none" stroke={`url(#${id}-gold)`} stroke-width="12" />
          <circle cx={C} cy={C} r="95" fill="none" stroke="var(--p-ring-lo)" stroke-width="2" opacity="0.9" />
          <circle cx={C} cy={C} r="102.5" fill="none" stroke="#fff" stroke-width="2.2" opacity="0.85" stroke-dasharray="70 110 34 60 16 400" stroke-linecap="round" />
          {Array.from({ length: 30 }, (_, i) => {
            const a = (i / 30) * Math.PI * 2, x = C + Math.cos(a) * 109.5, y = C + Math.sin(a) * 109.5;
            return <g><circle cx={x} cy={y} r="2.9" fill={INK} /><circle cx={x} cy={y} r="2" fill="var(--p-ring-hi)" /></g>;
          })}
          {Array.from({ length: 6 }, (_, i) => {
            const a = (i * Math.PI) / 3 - Math.PI / 2 + Math.PI / 6, x = C + Math.cos(a) * 100, y = C + Math.sin(a) * 100;
            return (
              <g transform={`translate(${x} ${y}) rotate(${(a * 180) / Math.PI + 90})`}>
                <circle r="11.5" fill={INK} /><circle r="9.5" fill={`url(#${id}-gold)`} />
                <path d="M0 -8.5 L6.5 0 L0 8.5 L-6.5 0 Z" fill="var(--p-gem)" stroke={INK} stroke-width="1.8" stroke-linejoin="round" />
                <path d="M0 -6 L3.6 -0.5 L0 1 L-3.6 -0.5 Z" fill="#fff" opacity="0.85" />
                <path class="pt-gemglint" d={spark(3, -6, 4)} fill="#fff" style={{ animationDelay: `${-i * 0.6}s` }} />
              </g>
            );
          })}
        </g>

        {/* les étincelles qui s'échappent du tourbillon */}
        {Array.from({ length: 8 }, (_, i) => {
          const a = (i / 8) * Math.PI * 2 + 0.4;
          return (
            <path class="pt-spark" d={spark(C, C, i % 3 === 0 ? 10 : 7)} fill={i % 2 ? '#fff' : 'var(--p-spark)'}
              style={{ '--dx': `${Math.cos(a) * 112}px`, '--dy': `${Math.sin(a) * 112}px`, animationDelay: `${-i * 0.45}s` } as never} />
          );
        })}
      </svg>
    </div>
  );
}
