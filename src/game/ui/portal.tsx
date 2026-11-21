// Le portail d'invocation : dessiné par le code et toujours en mouvement.
// Un anneau d'or serti de gemmes, un anneau de runes qui tourne à l'envers, un tourbillon de magie en spirale
// (trois couches à des vitesses différentes), un cœur qui bat, des étincelles qui s'échappent, deux pierres qui gravitent.
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
function spark(x: number, y: number, r: number): string {
  const q = r * 0.28;
  return `M${x} ${y - r} L${x + q} ${y - q} L${x + r} ${y} L${x + q} ${y + q} L${x} ${y + r} L${x - q} ${y + q} L${x - r} ${y} L${x - q} ${y - q} Z`;
}

/** Les runes : de petits signes faits de traits droits (aucune lettre réelle). */
const RUNES = [
  'M-4 -7 L-4 7 M-4 -7 L4 -1 L-4 3', 'M0 -7 L0 7 M-5 -2 L5 -6 M-5 4 L5 0', 'M-5 -7 L5 7 M5 -7 L-5 7 M0 -7 L0 -2',
  'M-4 7 L0 -7 L4 7 M-2 1 L2 1', 'M-5 -6 L5 -6 L0 0 L5 6 L-5 6', 'M0 -7 L0 7 M0 -7 L5 -2 M0 -1 L5 4',
  'M-5 0 L0 -7 L5 0 L0 7 Z', 'M-4 -7 L-4 7 L4 7 M-4 0 L3 0', 'M-5 -7 L0 0 L5 -7 M0 0 L0 7',
  'M-4 -7 L4 -7 L-4 7 L4 7', 'M0 -7 L0 7 M-5 -3 L0 2 L5 -3', 'M-5 7 L-5 -7 L5 7 L5 -7',
];

export function Portal({ kind = 'normal', size = 208 }: { kind?: 'normal' | 'basic'; size?: number }) {
  const id = `pt-${kind}`;
  const arms = (n: number, r0: number, r1: number, w: number, twist: number) =>
    Array.from({ length: n }, (_, i) => arm((i * Math.PI * 2) / n, r0, r1, w, twist));
  return (
    <div class={`portal portal-${kind}`} style={{ width: `${size}px`, height: `${size * 1.06}px` }} aria-hidden="true">
      <span class="pt-shadow" />
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
          <clipPath id={`${id}-clip`}><circle cx={C} cy={C} r="71" /></clipPath>
        </defs>

        {/* halo, ondes de magie et rayons derrière le portail */}
        <circle class="pt-halo" cx={C} cy={C} r="118" fill={`url(#${id}-glow)`} />
        <circle class="pt-wave" cx={C} cy={C} r="104" fill="none" stroke="var(--p-glow)" stroke-width="5" />
        <circle class="pt-wave pt-wave-2" cx={C} cy={C} r="104" fill="none" stroke="var(--p-glow)" stroke-width="5" />
        <g class="pt-rays">
          {Array.from({ length: 12 }, (_, i) => {
            const a = (i * Math.PI) / 6, w = i % 2 ? 0.085 : 0.05, r = i % 2 ? 116 : 104;
            return <path d={`M${C} ${C} L${C + Math.cos(a - w) * r} ${C + Math.sin(a - w) * r} L${C + Math.cos(a + w) * r} ${C + Math.sin(a + w) * r} Z`} fill="var(--p-glow)" opacity="0.5" />;
          })}
        </g>

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
          <circle class="pt-core" cx={C} cy={C} r="17" fill="#fff" />
          <circle class="pt-core pt-core-2" cx={C} cy={C} r="30" fill="var(--p-core)" opacity="0.55" />
          {/* reflet de verre en haut du tourbillon */}
          <path d="M62 96 Q84 58 126 54 Q96 66 78 104 Z" fill="#fff" opacity="0.28" />
          <circle cx={C} cy={C} r="69.5" fill="none" stroke="var(--p-arm-b)" stroke-width="3" opacity="0.8" />
        </g>

        {/* l'anneau de runes (tourne à l'envers) */}
        <g class="pt-runes">
          <circle cx={C} cy={C} r="84" fill="none" stroke={INK} stroke-width="19" />
          <circle cx={C} cy={C} r="84" fill="none" stroke="var(--p-band)" stroke-width="14" />
          {RUNES.map((d, i) => {
            const a = (i * 360) / RUNES.length;
            return <path class="pt-rune" d={d} transform={`rotate(${a} ${C} ${C}) translate(${C} ${C - 84}) scale(0.72)`} fill="none" stroke="var(--p-rune)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" style={{ animationDelay: `${-i * 0.3}s` }} />;
          })}
        </g>

        {/* l'anneau d'or et ses gemmes */}
        <g class="pt-ring">
          <circle cx={C} cy={C} r="99" fill="none" stroke={INK} stroke-width="15" />
          <circle cx={C} cy={C} r="99" fill="none" stroke={`url(#${id}-gold)`} stroke-width="10" />
          <circle cx={C} cy={C} r="101.5" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.7" stroke-dasharray="60 120 30 400" />
          {Array.from({ length: 6 }, (_, i) => {
            const a = (i * Math.PI) / 3 - Math.PI / 2, x = C + Math.cos(a) * 99, y = C + Math.sin(a) * 99;
            return (
              <g transform={`translate(${x} ${y}) rotate(${(a * 180) / Math.PI + 90})`}>
                <path d="M0 -10 L8 0 L0 10 L-8 0 Z" fill="var(--p-gem)" stroke={INK} stroke-width="2.6" stroke-linejoin="round" />
                <path d="M0 -6 L4 -1 L0 1 L-4 -1 Z" fill="#fff" opacity="0.8" />
              </g>
            );
          })}
        </g>

        {/* deux pierres qui gravitent autour du portail */}
        <g class="pt-orbit">
          <g transform={`translate(${C + 112} ${C})`}>
            <path d="M0 -9 L7 0 L0 9 L-7 0 Z" fill="var(--p-gem)" stroke={INK} stroke-width="2.4" stroke-linejoin="round" />
          </g>
          <g transform={`translate(${C - 112} ${C})`}>
            <path d="M0 -7 L5.5 0 L0 7 L-5.5 0 Z" fill="var(--p-ring-hi)" stroke={INK} stroke-width="2.2" stroke-linejoin="round" />
          </g>
        </g>

        {/* les étincelles qui s'échappent du tourbillon */}
        {Array.from({ length: 8 }, (_, i) => {
          const a = (i / 8) * Math.PI * 2 + 0.4;
          return (
            <path class="pt-spark" d={spark(C, C, i % 3 === 0 ? 10 : 7)} fill={i % 2 ? '#fff' : 'var(--p-spark)'} stroke={INK} stroke-width="1.4" stroke-linejoin="round"
              style={{ '--dx': `${Math.cos(a) * 112}px`, '--dy': `${Math.sin(a) * 112}px`, animationDelay: `${-i * 0.45}s` } as never} />
          );
        })}
      </svg>
    </div>
  );
}
