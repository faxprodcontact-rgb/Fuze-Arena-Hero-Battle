// Le portail d'invocation (refait de zéro le 26/11/2026, style « moderne ») et l'estrade où il se tient.
// Tout est dessiné par le code, en formes courbes et lisses, une seule lumière (en haut à droite) :
// - le portail : une aura qui respire, un disque de magie qui tourne en spirale, des anneaux qui filent vers le fond
//   (on plonge dedans), un cœur blanc qui bat ; autour, trois croissants de lumière en orbite et une couronne de perles ;
// - `charging` : il s'emballe (tout tourne plus vite, il tremble et grossit) ; `open` : il éclate et s'ouvre en grand ;
// - ses couleurs suivent --g-a / --g-b / --g-deep (posées par le CSS : violet, bleu pour l'invocation simple, ou la
//   couleur de la rareté pendant le tirage) ;
// - l'estrade (Dais) : deux dalles arrondies posées au sol, un liseré de lumière, des cristaux posés aux coins.
import { spark } from '../portal';

const f = (n: number) => n.toFixed(1);

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

/** Un croissant : un arc épais de a0 à a1 (degrés) au rayon r. */
function arc(r: number, a0: number, a1: number): string {
  const p = (a: number) => `${f(Math.cos((a * Math.PI) / 180) * r)} ${f(Math.sin((a * Math.PI) / 180) * r)}`;
  return `M${p(a0)} A${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${p(a1)}`;
}

/** Le portail seul (boîte carrée, centre au milieu). `uid` rend ses dégradés uniques (deux portails peuvent coexister). */
export function Gate({ uid, charging = false, open = false, class: cls = '' }: { uid: string; charging?: boolean; open?: boolean; class?: string }) {
  const g = (n: string) => `sg-${n}-${uid}`;
  const sc = (c: string) => ({ stopColor: c });
  return (
    <div class={`sg${charging ? ' sg-charging' : ''}${open ? ' sg-open' : ''} ${cls}`} aria-hidden="true">
      <svg viewBox="-120 -120 240 240">
        <defs>
          <radialGradient id={g('aura')}><stop offset="0" style={sc('var(--g-a)')} stop-opacity="0.85" /><stop offset="0.45" style={sc('var(--g-a)')} stop-opacity="0.28" /><stop offset="1" style={sc('var(--g-a)')} stop-opacity="0" /></radialGradient>
          <radialGradient id={g('disc')}>
            <stop offset="0" stop-color="#ffffff" /><stop offset="0.16" style={sc('var(--g-b)')} /><stop offset="0.55" style={sc('var(--g-a)')} /><stop offset="1" style={sc('var(--g-deep)')} />
          </radialGradient>
          <linearGradient id={g('rim')} x1="1" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#ffffff" /><stop offset="0.45" style={sc('var(--g-b)')} /><stop offset="1" style={sc('var(--g-a)')} />
          </linearGradient>
          <linearGradient id={g('arm')} x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.9" /><stop offset="1" style={sc('var(--g-b)')} stop-opacity="0.2" /></linearGradient>
          <clipPath id={g('clip')}><circle r="73" /></clipPath>
        </defs>
        <circle class="sg-aura" r="119" fill={`url(#${g('aura')})`} />
        <g class="sg-body"><circle r="119" fill="none" />
          {/* la couronne de perles (elle tourne à l'envers), trois perles plus grosses */}
          <g class="sg-beads"><circle r="118" fill="none" />{Array.from({ length: 30 }, (_, i) => {
            const a = (i / 30) * Math.PI * 2;
            const big = i % 10 === 0;
            return <circle cx={f(Math.cos(a) * 106)} cy={f(Math.sin(a) * 106)} r={big ? 3.4 : 1.4} fill="#fff" opacity={big ? 1 : 0.55} />;
          })}</g>
          {/* les trois croissants de lumière, qui glissent sur leur piste */}
          <circle r="89" fill="none" style={{ stroke: 'var(--g-a)' }} stroke-width="10" opacity="0.2" />
          <g class="sg-crescents"><g class="sg-spin-x"><circle r="118" fill="none" />
            {[0, 120, 240].map((a) => (
              <g transform={`rotate(${a})`}>
                <path d={arc(89, -40, 52)} fill="none" style={{ stroke: 'var(--g-deep)' }} stroke-width="12" stroke-linecap="round" opacity="0.55" />
                <path d={arc(89, -40, 52)} fill="none" stroke={`url(#${g('rim')})`} stroke-width="8" stroke-linecap="round" />
                <path d={arc(90, -24, 30)} fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity="0.8" />
              </g>
            ))}
          </g></g>
          {/* le disque de magie */}
          <circle r="80" fill="none" style={{ stroke: 'var(--g-a)' }} stroke-width="6" opacity="0.45" />
          <circle class="sg-disc" r="75" fill={`url(#${g('disc')})`} />
          <g clip-path={`url(#${g('clip')})`}>
            {/* les anneaux qui filent vers le fond */}
            {[0, 1, 2, 3].map((i) => <circle class="sg-tunnel" r="72" fill="none" stroke="#fff" stroke-width="3" style={{ animationDelay: `${-i * 0.55}s` }} />)}
            <g class="sg-swirl"><g class="sg-spin-x"><circle r="118" fill="none" />{[0, 2.09, 4.19].map((k) => <path d={swirl(k, 78, 26)} fill={`url(#${g('arm')})`} />)}</g></g>
            <g class="sg-swirl-2"><g class="sg-spin-y"><circle r="118" fill="none" />{[1, 3.1, 5.2].map((k) => <path d={swirl(k, 70, 12)} fill="#fff" opacity="0.35" />)}</g></g>
          </g>
          <circle r="75.5" fill="none" stroke={`url(#${g('rim')})`} stroke-width="3" />
          {/* le cœur */}
          <circle class="sg-core" r="22" fill="#fff" opacity="0.5" />
          <circle class="sg-core sg-core-2" r="11" fill="#fff" />
          {/* le reflet de la lumière (en haut à droite) */}
          <path d={arc(68, -78, -18)} fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.6" />
          <path class="sg-glint" d={spark(48, -52, 7)} fill="#fff" />
        </g>
        {/* l'onde et l'éclair blanc de l'ouverture */}
        <circle class="sg-wave" r="80" fill="none" stroke="#fff" stroke-width="6" />
        <circle class="sg-flash" r="90" fill="#fff" />
      </svg>
    </div>
  );
}

/** Une gerbe de cristaux posée au sol (pied en 0, 0) : trois éclats lisses, la face éclairée à droite. */
function Crystals({ x, y, s, flip = false }: { x: number; y: number; s: number; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ellipse cx="0" cy="1" rx="20" ry="3.5" fill="#05021a" opacity="0.45" />
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
 * L'estrade : deux dalles arrondies posées au sol, vues un peu de haut (repère 360 × 110, le dessus de la dalle haute est
 * centré en 180, 34). Un liseré de lumière sur le dessus, une lueur qui monte. `crystals` : des gerbes aux deux bouts.
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
        <linearGradient id={g('top')} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2b2170" /><stop offset="0.62" stop-color="#5a48c4" /><stop offset="1" stop-color="#8c7cf0" /></linearGradient>
        <linearGradient id={g('side')} x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#140d40" /><stop offset="0.7" stop-color="#2e2380" /><stop offset="1" stop-color="#4536a8" /></linearGradient>
        <radialGradient id={g('pool')}><stop offset="0" stop-color="#fff" stop-opacity="0.95" /><stop offset="0.3" style={{ stopColor: 'var(--g-b)' }} stop-opacity="0.75" /><stop offset="1" style={{ stopColor: 'var(--g-a)' }} stop-opacity="0" /></radialGradient>
        <linearGradient id={g('seam')} x1="0" y1="0" x2="1" y2="0"><stop offset="0" style={{ stopColor: 'var(--g-b)' }} stop-opacity="0" /><stop offset="0.6" stop-color="#fff" /><stop offset="1" style={{ stopColor: 'var(--g-b)' }} stop-opacity="0" /></linearGradient>
      </defs>
      <ellipse cx="180" cy="96" rx="178" ry="14" fill="#05021a" opacity="0.5" />
      <path d={low.side} fill={`url(#${g('side')})`} /><path d={low.top} fill={`url(#${g('top')})`} />
      <path d={`M${180 - 150} ${62 + 9} L${180 + 150} ${62 + 9}`} stroke={`url(#${g('seam')})`} stroke-width="2" class="sd-seam" />
      <path d={high.side} fill={`url(#${g('side')})`} /><path d={high.top} fill={`url(#${g('top')})`} />
      <path d={`M${180 - 100} ${34 + 7} L${180 + 100} ${34 + 7}`} stroke={`url(#${g('seam')})`} stroke-width="2.4" class="sd-seam" />
      {/* la flaque de lumière sur le dessus */}
      <ellipse class="sd-pool" cx="180" cy="33" rx="92" ry="11" fill={`url(#${g('pool')})`} />
      {crystals && <><Crystals x={34} y={66} s={1.15} /><Crystals x={326} y={66} s={1.25} flip /></>}
    </svg>
  );
}

/** La scène de l'onglet : l'estrade, une colonne de lumière, le portail qui flotte au-dessus, des grains qui montent. */
export function GateStage({ kind, casting }: { kind: 'normal' | 'basic'; casting: boolean }) {
  return (
    <div class={`sg-stage sg-kind-${kind}${casting ? ' sg-casting' : ''}`}>
      <span class="sg-column" />
      <Dais uid="tab" crystals class="sg-stage-dais" />
      <Gate uid="tab" charging={casting} class="sg-stage-gate" />
      <span class="sg-motes" aria-hidden="true">
        {Array.from({ length: 10 }, (_, i) => <i style={{ left: `${12 + ((i * 37) % 76)}%`, animationDelay: `${-i * 0.47}s`, animationDuration: `${3.2 + (i % 4) * 0.6}s` }} />)}
      </span>
    </div>
  );
}
