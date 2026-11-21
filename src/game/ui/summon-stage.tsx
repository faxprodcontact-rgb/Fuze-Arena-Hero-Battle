// La scène du portail d'invocation : tout ce qui l'entoure, dessiné par le code et calé sur lui (le décor du fond, lui,
// est dans backdrop-summon.tsx). Derrière : le grand cercle de signes couché au sol qui tourne, l'estrade de pierre à trois
// marches, deux obélisques gravés coiffés d'un cristal, les arcs d'énergie qui relient les cristaux au portail. Devant :
// trois orbes en orbite, des étincelles aspirées vers le tourbillon. `casting` = l'invocation part : le portail enfle,
// un éclair blanc, une onde court sur le sol. `kind` change les couleurs (violet et or, ou bleu et argent).
import './anim.css';
import { GLYPHS } from './backdrop-adventure';
import { Portal, spark } from './portal';

const f = (n: number) => n.toFixed(1);
const CX = 180, CY = 162; // le centre du portail dans la scène (repère 360 × 400)

/** Un obélisque : socle, fût effilé, pointe, trois signes qui s'allument de bas en haut. `side` = 1 à gauche du portail. */
function Obelisk({ x, side }: { x: number; side: number }) {
  return (
    <g transform={`translate(${x} 0) scale(${side} 1)`}>
      <ellipse cx="0" cy="336" rx="30" ry="7" fill="#0b0722" opacity="0.55" />
      <path d="M-21 336 L-18 320 H18 L21 336 Z" fill="#3a2c86" /><path d="M-18 320 H18 L19 323.500 H-19 Z" fill="#8f7ae6" /><path d="M-21 336 L-18 320 H-6 L-8 336 Z" fill="#1c1350" />
      <path d="M-14 320 L-9 214 L0 192 L9 214 L14 320 Z" fill="#43349a" />
      <path d="M-14 320 L-9 214 L0 192 L-1 320 Z" fill="#1f1558" /><path d="M9 214 L14 320 H7 L4 216 L0 192 Z" fill="#7d68dc" />
      <path d="M0 192 L9 214 L14 320" fill="none" stroke="#c9b8ff" stroke-width="1.200" opacity="0.85" />
      <path d="M-9 214 H9" stroke="#1c1350" stroke-width="1.400" opacity="0.7" />
    </g>
  );
}

export function SummonStage({ kind, casting }: { kind: 'normal' | 'basic'; casting: boolean }) {
  const c = kind === 'normal' ? { a: '#8fe6ff', b: '#d09aff', seam: '#c9a2ff' } : { a: '#bfeaff', b: '#8fb8ff', seam: '#9fdcff' };
  const OB = [28, 332]; // les deux obélisques, bien écartés du portail
  return (
    <div class={`sum-art sum-${kind}${casting ? ' casting' : ''}`}>
      <svg class="sum-back" viewBox="0 0 360 400" aria-hidden="true">
        <defs>
          <radialGradient id="ss-floor"><stop offset="0" stop-color={c.b} stop-opacity="0.85" /><stop offset="0.5" stop-color={c.b} stop-opacity="0.3" /><stop offset="1" stop-color={c.b} stop-opacity="0" /></radialGradient>
          <radialGradient id="ss-gl-a"><stop offset="0" stop-color={c.a} stop-opacity="0.9" /><stop offset="1" stop-color={c.a} stop-opacity="0" /></radialGradient>
          <radialGradient id="ss-gl-b"><stop offset="0" stop-color={c.b} stop-opacity="0.9" /><stop offset="1" stop-color={c.b} stop-opacity="0" /></radialGradient>
          <radialGradient id="ss-pool"><stop offset="0" stop-color="#fff" stop-opacity="0.9" /><stop offset="0.35" stop-color={c.b} stop-opacity="0.75" /><stop offset="1" stop-color={c.b} stop-opacity="0" /></radialGradient>
          <linearGradient id="ss-top" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#33267e" /><stop offset="0.5" stop-color="#9a86f0" /><stop offset="1" stop-color="#33267e" /></linearGradient>
          <linearGradient id="ss-side" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#170f46" /><stop offset="0.5" stop-color="#4f3fa8" /><stop offset="1" stop-color="#170f46" /></linearGradient>
          <linearGradient id="ss-seam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color={c.seam} stop-opacity="0" /><stop offset="0.5" stop-color="#fff" /><stop offset="1" stop-color={c.seam} stop-opacity="0" /></linearGradient>
        </defs>
        <ellipse class="an-glow" cx={CX} cy="334" rx="176" ry="46" fill="url(#ss-floor)" />
        {/* le grand cercle de signes, couché sur le sol, qui tourne */}
        <g transform={`translate(${CX} 336) scale(1 0.250)`}>
          <g class="ss-floor-ring" fill="none" stroke={c.a}>
            <circle r="170" stroke-width="3" opacity="0.85" /><circle r="160" stroke-width="1.400" opacity="0.6" /><circle r="134" stroke-width="2" stroke-dasharray="4 14" opacity="0.7" />
            {GLYPHS.map((d, i) => { const a = (i / GLYPHS.length) * Math.PI * 2; return <path d={d} stroke-width="1.700" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${f(Math.cos(a) * 147)} ${f(Math.sin(a) * 147)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(2.200)`} />; })}
            {[0, 1, 2, 3, 4, 5].map((i) => { const a = (i / 6) * Math.PI * 2; return <path d={spark(Math.cos(a) * 170, Math.sin(a) * 170, 11)} fill={c.a} stroke="none" />; })}
          </g>
        </g>
        {/* les obélisques et leurs signes */}
        <Obelisk x={OB[0]!} side={1} /><Obelisk x={OB[1]!} side={-1} />
        {OB.map((x, k) => [298, 268, 238].map((y, i) => (
          <g class="ss-rune" style={{ animationDelay: `${-(2 - i) * 0.5 - k * 0.25}s` }}>
            <circle cx={x} cy={y} r="11" fill="url(#ss-gl-a)" opacity="0.7" />
            <path d={GLYPHS[(i * 3 + k * 5) % GLYPHS.length]} transform={`translate(${x} ${y}) scale(1.300)`} fill="none" stroke={c.a} stroke-width="1.500" stroke-linecap="round" stroke-linejoin="round" />
          </g>
        )))}
        {/* l'estrade : trois marches de pierre ; le nez de chaque marche s'allume au centre et s'éteint vers les bords */}
        {[[338, 122, 25, 13], [323, 96, 19.500, 12], [309, 70, 14, 11]].map(([y, rx, ry, h]) => (
          <g>
            <path d={`M${CX - rx!} ${y} V${y! + h!} A${rx} ${ry} 0 0 0 ${CX + rx!} ${y! + h!} V${y} Z`} fill="url(#ss-side)" />
            <ellipse cx={CX} cy={y} rx={rx} ry={ry} fill="url(#ss-top)" />
            <path d={`M${CX - rx!} ${y! + 1.500} A${rx} ${ry} 0 0 0 ${CX + rx!} ${y! + 1.500}`} fill="none" stroke="url(#ss-seam)" stroke-width="2" />
          </g>
        ))}
        {/* la lumière du portail : une flaque sur le dessus de l'estrade, un halo qui monte vers lui */}
        <ellipse class="an-glow" cx={CX} cy="309" rx="58" ry="11" fill="url(#ss-pool)" />
        <ellipse class="ss-beam" cx={CX} cy="282" rx="46" ry="40" fill="url(#ss-gl-b)" opacity="0.5" />
        {/* les cristaux des obélisques (de la couleur du portail), et l'arc d'énergie qui file de chacun vers lui */}
        {OB.map((x, k) => {
          const s = k ? -1 : 1;
          return (
            <g>
              <circle class="an-glow" cx={x} cy="166" r="24" fill="url(#ss-gl-a)" />
              <path class="ss-arc" d={`M${x + s * 8} 166 q${s * 10} -12 ${s * 20} -3 t${s * 16} 5`} fill="none" stroke={c.a} stroke-width="2.200" stroke-linecap="round" stroke-linejoin="round" />
              <path class="ss-arc ss-arc-2" d={`M${x + s * 8} 167 q${s * 8} 9 ${s * 19} 2 t${s * 17} -3`} fill="none" stroke="#fff" stroke-width="1.100" stroke-linecap="round" stroke-linejoin="round" />
              <g class="mi-bob">
                <path d={`M${x} 144 L${x + 9} 166 L${x} 188 L${x - 9} 166 Z`} fill="#150e3c" />
                <path d={`M${x} 147 L${x + 7} 166 L${x} 185 L${x - 7} 166 Z`} fill={c.a} />
                <path d={`M${x} 147 L${x + s * 7} 166 H${x} Z`} fill="#fff" opacity="0.75" /><path d={`M${x - s * 7} 166 H${x} V185 Z`} fill="#000" opacity="0.25" />
              </g>
            </g>
          );
        })}
        {/* l'onde qui court sur le sol quand l'invocation part */}
        <g transform={`translate(${CX} 336) scale(1 0.250)`}><circle class="ss-shock" r="60" fill="none" stroke="#fff" stroke-width="10" /></g>
      </svg>

      {/* quand l'invocation part : des traits de lumière jaillissent du portail, juste derrière lui */}
      <svg class="sum-burst" viewBox="0 0 360 400" aria-hidden="true">
        <g class="ss-rays" style={{ transformOrigin: `${CX}px ${CY}px` }}>
          {Array.from({ length: 12 }, (_, i) => <path transform={`rotate(${i * 30 + (i % 2) * 9} ${CX} ${CY})`} d={`M${CX - (i % 2 ? 4 : 6)} ${CY - 96} L${CX} ${CY - (i % 2 ? 190 : 240)} L${CX + (i % 2 ? 4 : 6)} ${CY - 96} Z`} fill={i % 3 ? '#fff' : c.a} />)}
        </g>
      </svg>

      <div class="sum-portal"><Portal kind={kind} size={224} base={false} claws /></div>

      <svg class="sum-front" viewBox="0 0 360 400" aria-hidden="true">
        <defs><radialGradient id="ss-white"><stop offset="0" stop-color="#fff" /><stop offset="0.55" stop-color="#fff" stop-opacity="0.9" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></radialGradient></defs>
        {/* trois comètes en orbite autour du portail : une tête blanche, une traîne qui s'efface */}
        <g transform={`translate(${CX} ${CY}) scale(1 0.340)`}>
          <g class="ss-orbit">
            {[[0, c.a], [120, '#ffe58a'], [240, c.b]].map(([a, col]) => (
              <g transform={`rotate(${a})`}>
                <path d="M134 0 A134 134 0 0 0 123.800 -51.300" fill="none" stroke={col as string} stroke-width="4" stroke-linecap="round" opacity="0.4" />
                <path d="M134 0 A134 134 0 0 0 131.400 -26.100" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.7" />
                <g transform="translate(134 0) scale(1 2.940)"><circle r="4.600" fill={col as string} /><circle r="2.600" fill="#fff" /></g>
              </g>
            ))}
          </g>
        </g>
        {/* des étincelles aspirées vers le tourbillon */}
        {Array.from({ length: 9 }, (_, i) => {
          const a = (i / 9) * Math.PI * 2 + 0.3, r = 150 + (i % 3) * 14;
          return <path class="ss-pull" style={{ '--dx': `${f(Math.cos(a) * r)}px`, '--dy': `${f(Math.sin(a) * r)}px`, animationDelay: `${-i * 0.33}s`, transformOrigin: `${CX}px ${CY}px` } as never} d={spark(CX, CY, i % 2 ? 5 : 7)} fill={i % 3 === 0 ? '#fff' : i % 3 === 1 ? c.a : c.b} />;
        })}
        {/* l'éclat du cœur et l'anneau d'onde de l'invocation */}
        <circle class="ss-wave" cx={CX} cy={CY} r="70" fill="none" stroke="#fff" stroke-width="5" />
        <circle class="ss-flash" cx={CX} cy={CY} r="60" fill="url(#ss-white)" />
      </svg>
    </div>
  );
}
