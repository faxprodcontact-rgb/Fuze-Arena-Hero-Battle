// Le fond animé d'une tuile de mode (onglet Aventure), dans le trait du portail : derrière le picto, une lueur qui respire
// et un anneau gravé qui tourne ; autour, un petit décor propre à chaque mode (nuages de la tour, route des missions,
// braises des donjons et du boss, fanions de l'arène, arcades et poussière du Colisée). Mouvements dans anim.css.
import './anim.css';
import { spark } from './portal';

const CX = 90, CY = 63.5; // centre du picto dans la tuile (repère 180 × 160)

const TICKS: Record<string, number> = { tower: 12, missions: 16, dungeons: 8, dailyBoss: 6, arena: 12, defense: 10 };

function Ring({ kind }: { kind: string }) {
  const n = TICKS[kind] ?? 12;
  return (
    <>
      <circle class="an-glow" cx={CX} cy={CY} r="56" fill="url(#ts-halo)" />
      <g class="ts-ring" fill="none" stroke="#fff">
        <circle cx={CX} cy={CY} r="45" stroke-width="1.2" opacity="0.42" />
        {Array.from({ length: n }, (_, i) => {
          const a = (i / n) * Math.PI * 2;
          return <path d={`M${(CX + Math.cos(a) * 41.500).toFixed(1)} ${(CY + Math.sin(a) * 41.500).toFixed(1)} L${(CX + Math.cos(a) * 45).toFixed(1)} ${(CY + Math.sin(a) * 45).toFixed(1)}`} stroke-width="1.1" opacity="0.42" />;
        })}
        {[0, 1, 2, 3].map((i) => {
          const a = (i / 4) * Math.PI * 2 + Math.PI / 4, x = CX + Math.cos(a) * 45, y = CY + Math.sin(a) * 45;
          return <path d={`M${x.toFixed(1)} ${(y - 5).toFixed(1)} L${(x + 1.800).toFixed(1)} ${y.toFixed(1)} L${x.toFixed(1)} ${(y + 5).toFixed(1)} L${(x - 1.800).toFixed(1)} ${y.toFixed(1)} Z`} transform={`rotate(${((a * 180) / Math.PI + 90).toFixed(0)} ${x.toFixed(1)} ${y.toFixed(1)})`} fill="#fff" stroke="none" opacity="0.6" />;
        })}
      </g>
      <circle class="ts-ring-2" cx={CX} cy={CY} r="53" fill="none" stroke="#fff" stroke-width="1" stroke-dasharray="1 8" stroke-linecap="round" opacity="0.35" />
    </>
  );
}

const twinkle = (x: number, y: number, r: number, late = '') => <path class={`an-twinkle ${late}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x, y, r)} fill="#fff" />;
const ember = (x: number, y: number, r: number, delay: number, color: string) => <circle class="ts-ember" style={{ animationDelay: `${-delay}s` }} cx={x} cy={y} r={r} fill={color} />;

/** Une colonne de l'arène : fût éclairé à droite, chapiteau et base. */
function Pillar({ x }: { x: number }) {
  return (
    <g>
      <rect x={x} y="-4" width="15" height="130" fill="url(#ts-pillar)" />
      <rect x={x - 3} y="8" width="21" height="5" rx="1.5" fill="#8fb4ee" /><rect x={x - 2} y="13" width="19" height="2.4" fill="#16356e" opacity="0.4" />
      <rect x={x - 3} y="112" width="21" height="6" rx="1.5" fill="#6f9be0" />
    </g>
  );
}

/** Une bannière suspendue, frangée d'or. */
function Banner({ x, delay }: { x: number; delay: number }) {
  return (
    <g class="bd-banner" style={{ transformOrigin: `${x}px 0px`, animationDelay: `${-delay}s` }}>
      <path d={`M${x - 10} -2 H${x + 10} V54 L${x} 46 L${x - 10} 54 Z`} fill="#c8453f" />
      <path d={`M${x} -2 H${x + 10} V54 L${x} 46 Z`} fill="#e86a5a" />
      <path d={`M${x - 10} -2 H${x + 10} V2 H${x - 10} Z`} fill="#ffd45c" />
      <path d={`M${x - 10} 54 L${x} 46 L${x + 10} 54`} fill="none" stroke="#ffd45c" stroke-width="1.6" />
      <path d={`M${x} 14 l5.500 7 l-5.500 7 l-5.500 -7 Z`} fill="#ffd45c" /><path d={`M${x} 17.500 l2.800 3.500 l-2.800 3.500 l-2.800 -3.500 Z`} fill="#c8453f" />
    </g>
  );
}

/** Un bouquet de cristaux qui luit. */
function Crystals({ x, y, c, light, flip = false }: { x: number; y: number; c: string; light: string; flip?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -1 : 1} 1)`}>
      <ellipse class="an-glow" cx="0" cy="-8" rx="24" ry="20" fill={`url(#ts-glow-${c === '#4fc3ff' ? 'b' : 'a'})`} />
      <path d="M-10 4 L-14 -12 L-9 -18 L-4 -10 L-2 4 Z" fill={c} /><path d="M-9 -18 L-4 -10 L-2 4 L-6 4 L-8 -8 Z" fill={light} />
      <path d="M-2 4 L-3 -18 L3 -28 L8 -16 L7 4 Z" fill={c} /><path d="M3 -28 L8 -16 L7 4 L3 4 L4 -14 Z" fill={light} />
      <path d="M7 4 L8 -8 L13 -13 L16 -6 L14 4 Z" fill={c} /><path d="M13 -13 L16 -6 L14 4 L11 4 L12 -6 Z" fill={light} />
      <path d="M1 -22 L3 -26 L4 -20 Z" fill="#fff" opacity="0.9" />
    </g>
  );
}

function Motif({ kind }: { kind: string }) {
  switch (kind) {
    case 'tower': return ( // la nuit, au-dessus d'une mer de nuages
      <>
        <defs><radialGradient id="ts-moon"><stop offset="0" stop-color="#f3e9ff" stop-opacity="0.8" /><stop offset="1" stop-color="#f3e9ff" stop-opacity="0" /></radialGradient></defs>
        <rect width="180" height="160" fill="#2a1466" opacity="0.28" />
        <circle class="an-glow" cx="30" cy="28" r="26" fill="url(#ts-moon)" />
        <path transform="translate(60 0) scale(-1 1)" d="M30 15 a13 13 0 1 0 10 21.500 a10.500 10.500 0 1 1 -10 -21.500 Z" fill="#f6efff" />
        <g fill="#fff">
          <circle class="bd-star" cx="62" cy="14" r="1.2" /><circle class="bd-star" style={{ animationDelay: '-1.2s' }} cx="150" cy="20" r="1.5" /><circle class="bd-star" style={{ animationDelay: '-2.3s' }} cx="166" cy="56" r="1.1" />
          <circle class="bd-star" style={{ animationDelay: '-0.6s' }} cx="14" cy="66" r="1.3" /><circle class="bd-star" style={{ animationDelay: '-1.8s' }} cx="128" cy="10" r="1" /><circle class="bd-star" style={{ animationDelay: '-2.9s' }} cx="46" cy="50" r="0.9" />
        </g>
        {twinkle(152, 44, 4.500)}{twinkle(20, 92, 3.500, 'an-late')}
        {/* les sommets qui percent les nuages */}
        <path d="M-4 124 V104 L14 86 L26 100 L42 80 L58 106 L74 96 L92 112 L112 92 L128 108 L146 82 L162 102 L184 88 V124 Z" fill="#4a2c98" opacity="0.7" />
        <path d="M42 80 L58 106 L48 104 L44 92 Z M146 82 L162 102 L152 100 L148 92 Z M14 86 L26 100 L18 100 Z M112 92 L128 108 L118 106 Z" fill="#b9a2f2" opacity="0.75" />
        {/* la mer de nuages, sur deux plans */}
        <g class="ts-cloud ts-back" fill="#9a7ee0" opacity="0.85">{[-6, 22, 50, 80, 110, 140, 170].map((x, i) => <circle cx={x} cy={116 + (i % 2) * 3} r={15 + (i % 3) * 2} />)}<rect x="-40" y="116" width="260" height="20" /></g>
        <g class="ts-cloud" fill="#c7b2f6">{[-20, 8, 38, 66, 96, 126, 156].map((x, i) => <circle cx={x} cy={124 + (i % 2) * 2} r={12 + (i % 3) * 2} />)}<rect x="-40" y="124" width="260" height="16" /></g>
        <g class="ts-cloud" fill="#fff" opacity="0.5">{[-20, 38, 96, 156].map((x) => <ellipse cx={x + 2} cy="115" rx="8" ry="3.500" />)}</g>
      </>
    );
    case 'missions': return ( // la route des missions, de colline en colline jusqu'au fanion
      <>
        <defs><linearGradient id="ts-hill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fd0b4" /><stop offset="1" stop-color="#1c8a74" /></linearGradient></defs>
        <circle class="an-glow" cx="156" cy="22" r="22" fill="url(#ts-halo)" opacity="0.6" />
        <path d="M-4 124 V92 Q20 70 48 86 Q74 100 100 84 Q130 66 158 80 Q172 86 184 78 V124 Z" fill="#157868" opacity="0.6" />
        <path d="M-4 124 V104 Q24 84 56 100 Q88 114 118 100 Q150 86 184 102 V124 Z" fill="url(#ts-hill)" opacity="0.85" />
        <path d="M-4 104 Q24 84 56 100 Q88 114 118 100 Q150 86 184 102" fill="none" stroke="#b8f5e0" stroke-width="1.4" opacity="0.8" />
        {/* sapins */}
        {[[14, 98, 0.8], [26, 96, 0.6], [164, 96, 0.7]].map(([x, y, k]) => <g transform={`translate(${x} ${y}) scale(${k})`}><path d="M0 -20 L7 -8 H3 L9 2 H-9 L-3 -8 H-7 Z" fill="#0f5a4c" /><path d="M0 -20 L7 -8 H3 L9 2 H1 Z" fill="#4fc4a4" /></g>)}
        {/* la route en pointillés */}
        <path class="ts-route" d="M4 122 C30 112 34 98 60 102 S104 110 124 96 S142 78 154 74" fill="none" stroke="#fff" stroke-width="2.4" stroke-dasharray="5 6" stroke-linecap="round" opacity="0.85" />
        <circle cx="8" cy="120" r="3.600" fill="#fff" /><circle cx="8" cy="120" r="1.6" fill="#1c8a74" />
        {/* l'arrivée : la croix de la carte au trésor */}
        <g class="ts-pulse" stroke-linecap="round"><path d="M149 68 l11 11 M160 68 l-11 11" stroke="#7a1d18" stroke-width="5" /><path d="M149 68 l11 11 M160 68 l-11 11" stroke="#ff6a5a" stroke-width="3" /></g>
        {twinkle(28, 26, 4.500)}{twinkle(40, 60, 3.500, 'an-late')}
      </>
    );
    case 'dungeons': return ( // la grotte : stalactites, cristaux qui luisent, braises
      <>
        <defs>
          <radialGradient id="ts-glow-b"><stop offset="0" stop-color="#7fe3ff" stop-opacity="0.75" /><stop offset="1" stop-color="#7fe3ff" stop-opacity="0" /></radialGradient>
          <radialGradient id="ts-glow-a"><stop offset="0" stop-color="#ffd27a" stop-opacity="0.8" /><stop offset="1" stop-color="#ffd27a" stop-opacity="0" /></radialGradient>
        </defs>
        <rect width="180" height="160" fill="#2a1408" opacity="0.22" />
        {/* la voûte */}
        <path d="M-4 -4 H184 V10 L176 34 L168 12 L158 26 L150 8 L140 20 L130 6 L118 14 L108 4 H72 L62 16 L52 6 L44 28 L34 10 L24 22 L16 8 L6 38 L-4 14 Z" fill="#4a2a14" opacity="0.8" />
        <path d="M176 34 L168 12 L172 10 Z M158 26 L150 8 L155 8 Z M44 28 L34 10 L40 9 Z M6 38 L-4 14 L2 12 Z M24 22 L16 8 L21 8 Z M140 20 L130 6 L136 6 Z" fill="#b07a4a" opacity="0.8" />
        {/* le sol */}
        <path d="M-4 124 V96 L8 80 L18 100 L28 92 L40 112 L56 118 H124 L140 110 L152 90 L162 102 L172 78 L184 98 V124 Z" fill="#4a2a14" opacity="0.8" />
        <path d="M8 80 L18 100 L12 100 Z M172 78 L184 98 L176 98 Z M152 90 L162 102 L155 102 Z M28 92 L40 112 L32 110 Z" fill="#b07a4a" opacity="0.8" />
        <Crystals x={30} y={112} c="#4fc3ff" light="#b8ecff" /><Crystals x={150} y={114} c="#ffb347" light="#ffe2a8" flip />
        {ember(46, 104, 2, 0, '#ffd27a')}{ember(64, 112, 1.5, 1.3, '#ffb347')}{ember(128, 108, 1.9, 0.7, '#ffd27a')}{ember(112, 116, 1.4, 2.1, '#ffe2a8')}{ember(90, 120, 1.6, 2.8, '#ffd27a')}
      </>
    );
    case 'dailyBoss': return ( // l'antre du boss : rochers noirs, fissures de lave, braises
      <>
        <defs><radialGradient id="ts-lava"><stop offset="0" stop-color="#ffd27a" stop-opacity="0.95" /><stop offset="0.5" stop-color="#ff7a3d" stop-opacity="0.55" /><stop offset="1" stop-color="#ff7a3d" stop-opacity="0" /></radialGradient></defs>
        <rect width="180" height="160" fill="#3a0a10" opacity="0.2" />
        <ellipse class="an-glow" cx="90" cy="126" rx="96" ry="26" fill="url(#ts-lava)" />
        <path d="M-4 124 V70 L8 86 L16 54 L26 82 L36 72 L44 100 L58 110 L52 124 Z" fill="#3a0c14" opacity="0.88" />
        <path d="M184 124 V64 L174 84 L164 50 L154 80 L144 70 L138 98 L124 110 L130 124 Z" fill="#3a0c14" opacity="0.88" />
        <path d="M16 54 L26 82 L20 84 Z M36 72 L44 100 L38 98 Z M164 50 L174 84 L168 82 Z M-4 70 L8 86 L2 90 Z" fill="#e8776a" opacity="0.6" />
        {/* la lave dans les fissures : larges en bas, effilées en haut */}
        <g class="ts-pulse">
          <g fill="#ff8a3d"><path d="M8 124 L15 104 L11 95 L17 86 L15 98 L20 106 L18 124 Z" /><path d="M30 124 L31 110 L36 100 L35 111 L38 124 Z" /><path d="M172 124 L165 106 L170 95 L163 84 L166 98 L160 108 L162 124 Z" /><path d="M150 124 L151 111 L146 101 L148 112 L143 124 Z" /></g>
          <g fill="#ffe08a"><path d="M11 124 L15.500 108 L13 98 L16 104 L17.500 110 L15 124 Z" /><path d="M169 124 L164.500 108 L167 98 L164 104 L162.500 110 L165 124 Z" /></g>
        </g>
        <path d="M-4 124 Q30 112 60 118 Q90 124 120 118 Q150 112 184 122 V130 H-4 Z" fill="#ff9a3d" opacity="0.6" />
        {ember(28, 100, 2.2, 0, '#ffd27a')}{ember(50, 112, 1.6, 1.1, '#ffb09a')}{ember(132, 108, 2.2, 0.5, '#ffd27a')}{ember(156, 98, 1.6, 1.9, '#ffb09a')}{ember(90, 120, 1.9, 2.6, '#ffe2a8')}{ember(72, 116, 1.4, 3.3, '#ffd27a')}{ember(108, 118, 1.5, 3.8, '#ffc9b8')}
      </>
    );
    case 'arena': return ( // l'arène : colonnes, bannières, piste éclairée
      <>
        <defs><linearGradient id="ts-pillar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1f4a94" /><stop offset="0.6" stop-color="#5a8ad8" /><stop offset="1" stop-color="#3f6fc0" /></linearGradient></defs>
        <ellipse cx="90" cy="126" rx="104" ry="20" fill="#16356e" opacity="0.45" />
        <ellipse cx="90" cy="124" rx="88" ry="14" fill="#a9c8f5" opacity="0.4" /><ellipse cx="90" cy="124" rx="64" ry="9" fill="none" stroke="#fff" stroke-width="1.2" opacity="0.5" />
        <Pillar x={2} /><Pillar x={163} />
        <path d="M14 1.500 H48 M132 1.500 H166" stroke="#ffd45c" stroke-width="2.4" stroke-linecap="round" /><circle cx="48" cy="1.500" r="2" fill="#ffd45c" /><circle cx="132" cy="1.500" r="2" fill="#ffd45c" />
        <Banner x={34} delay={0} /><Banner x={146} delay={1.7} />
        {twinkle(56, 98, 4.500)}{twinkle(128, 96, 3.500, 'an-late')}{twinkle(90, 12, 4, 'an-later')}
      </>
    );
    default: return ( // le Colisée : deux étages d'arcades sous le soleil
      <>
        <defs><linearGradient id="ts-sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9c874" /><stop offset="1" stop-color="#a87422" /></linearGradient></defs>
        <circle class="an-glow" cx="152" cy="22" r="34" fill="url(#ts-halo)" /><circle cx="152" cy="22" r="9" fill="#fff8d6" opacity="0.9" />
        {/* les gradins : un mur à deux étages d'arcades */}
        <path d="M-4 124 V68 Q90 56 184 68 V124 Z" fill="url(#ts-sand)" opacity="0.85" />
        <path d="M-4 68 Q90 56 184 68" fill="none" stroke="#fff3c4" stroke-width="1.8" opacity="0.85" />
        <path d="M-4 88 Q90 78 184 88" fill="none" stroke="#7a5210" stroke-width="1.2" opacity="0.45" />
        <g fill="#6b4408" opacity="0.5">{[4, 26, 48, 70, 96, 118, 140, 162].map((x, i) => { const y = 77 - Math.sin(((i + 0.5) / 8) * Math.PI) * 5; return <path d={`M${x} ${y + 9} v-6 q0 -4.500 5 -4.500 q5 0 5 4.500 v6 Z`} />; })}</g>
        <g fill="#5a3806" opacity="0.55">{[-2, 28, 58, 108, 138, 168].map((x, i) => { const y = 96 - Math.sin(((i + 0.5) / 6) * Math.PI) * 4; return <path d={`M${x} ${y + 18} v-10 q0 -7 7.500 -7 q7.500 0 7.500 7 v10 Z`} />; })}</g>
        {/* les oriflammes du sommet */}
        {[[22, 65], [158, 65]].map(([x, y], i) => (
          <g><path d={`M${x} ${y} v-16`} stroke="#6b4408" stroke-width="1.4" stroke-linecap="round" /><path class="bd-flag" style={{ transformOrigin: `${x}px ${y! - 12}px`, animationDelay: `${-i * 0.7}s` }} d={`M${x} ${y! - 16} q7 -1 12 3 q-5 4 -12 4.500 Z`} fill="#d1493f" /></g>
        ))}
        {[52, 76, 104, 126].map((x, i) => <circle class="ts-dust" style={{ animationDelay: `${-i * 1.4}s` }} cx={x} cy={30 - (i % 2) * 14} r="1.4" fill="#fff" />)}
      </>
    );
  }
}

export function TileScene({ kind }: { kind: string }) {
  return (
    <svg class="tile-scene" viewBox="0 0 180 160" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs><radialGradient id="ts-halo"><stop offset="0" stop-color="#fff" stop-opacity="0.75" /><stop offset="0.55" stop-color="#fff" stop-opacity="0.22" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></radialGradient></defs>
      <Ring kind={kind} />
      <Motif kind={kind} />
    </svg>
  );
}
