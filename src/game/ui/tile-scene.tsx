// Le fond animé d'une tuile de mode (onglet Aventure), dans le trait du portail : derrière le picto, une lueur qui respire
// et un anneau gravé qui tourne ; autour, un petit décor propre à chaque mode (nuages de la tour, route des missions,
// braises des donjons et du boss, fanions de l'arène, arcades et poussière du Colisée). Mouvements dans anim.css.
import './anim.css';
import { spark } from './portal';

const CX = 90, CY = 63.5; // centre du picto dans la tuile (repère 180 × 160)

function Ring() {
  return (
    <>
      <circle class="an-glow" cx={CX} cy={CY} r="56" fill="url(#ts-halo)" />
      <g class="ts-ring" fill="none" stroke="#fff">
        <circle cx={CX} cy={CY} r="47" stroke-width="1.4" opacity="0.5" />
        {Array.from({ length: 12 }, (_, i) => {
          const a = (i / 12) * Math.PI * 2, r0 = i % 3 === 0 ? 41 : 43.5;
          return <path d={`M${(CX + Math.cos(a) * r0).toFixed(1)} ${(CY + Math.sin(a) * r0).toFixed(1)} L${(CX + Math.cos(a) * 47).toFixed(1)} ${(CY + Math.sin(a) * 47).toFixed(1)}`} stroke-width="1.4" opacity="0.5" />;
        })}
        {[0, 1, 2, 3].map((i) => {
          const a = (i / 4) * Math.PI * 2 + Math.PI / 4, x = CX + Math.cos(a) * 47, y = CY + Math.sin(a) * 47;
          return <path d={`M${x} ${y - 3.5} L${x + 3.5} ${y} L${x} ${y + 3.5} L${x - 3.5} ${y} Z`} fill="#fff" stroke="none" opacity="0.8" />;
        })}
      </g>
      <circle class="ts-ring-2" cx={CX} cy={CY} r="57" fill="none" stroke="#fff" stroke-width="1.2" stroke-dasharray="2 7" opacity="0.32" />
    </>
  );
}

const twinkle = (x: number, y: number, r: number, late = '') => <path class={`an-twinkle ${late}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x, y, r)} fill="#fff" />;
const ember = (x: number, y: number, r: number, delay: number, color: string) => <circle class="ts-ember" style={{ animationDelay: `${-delay}s` }} cx={x} cy={y} r={r} fill={color} />;

function Motif({ kind }: { kind: string }) {
  switch (kind) {
    case 'tower': return (
      <>
        <g fill="#fff">
          <path class="ts-cloud" opacity="0.3" d="M-4 44 q3 -10 14 -7 q4 -9 15 -4 q11 -3 12 7 q7 1 6 6 H-6 q-4 -3 2 -2 Z" />
          <path class="ts-cloud ts-back" opacity="0.22" d="M132 112 q3 -9 13 -6 q4 -8 14 -3 q10 -3 11 6 q6 1 5 5 H130 q-4 -3 2 -2 Z" />
          <circle class="bd-star" cx="30" cy="16" r="1.3" /><circle class="bd-star" style={{ animationDelay: '-1.2s' }} cx="152" cy="24" r="1.6" /><circle class="bd-star" style={{ animationDelay: '-2.3s' }} cx="164" cy="70" r="1.2" /><circle class="bd-star" style={{ animationDelay: '-0.6s' }} cx="16" cy="84" r="1.4" />
        </g>
        {twinkle(148, 46, 5)}{twinkle(26, 112, 4, 'an-late')}
      </>
    );
    case 'missions': return (
      <>
        <path class="ts-route" d="M-6 118 C30 96 34 44 76 30 S150 46 186 14" fill="none" stroke="#fff" stroke-width="2.2" stroke-dasharray="5 7" stroke-linecap="round" opacity="0.45" />
        <g stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity="0.7"><path d="M157 21 l9 9 M166 21 l-9 9" /></g>
        <circle cx="14" cy="108" r="3.5" fill="#fff" opacity="0.7" />
        {twinkle(150, 96, 5)}{twinkle(34, 26, 4, 'an-late')}
      </>
    );
    case 'dungeons': return (
      <>
        <g fill="#2a1408" opacity="0.3">
          <path d="M0 0 H180 V8 L168 30 L160 10 L148 22 L138 6 L126 16 L112 4 L60 4 L50 20 L40 8 L28 26 L18 8 L8 34 L0 12 Z" />
          <path d="M0 128 V104 L10 86 L20 108 L30 98 L38 128 Z M180 128 V100 L168 82 L158 110 L150 100 L142 128 Z" />
        </g>
        {ember(30, 96, 2.2, 0, '#ffd27a')}{ember(52, 110, 1.6, 1.3, '#ffb347')}{ember(140, 100, 2, 0.7, '#ffd27a')}{ember(158, 88, 1.5, 2.1, '#ffb347')}{ember(120, 116, 1.8, 2.8, '#ffe2a8')}
      </>
    );
    case 'dailyBoss': return (
      <>
        <g fill="#3a0a10" opacity="0.34">
          <path d="M0 128 V86 L12 104 L20 70 L30 100 L42 90 L48 128 Z M180 128 V80 L170 102 L160 66 L150 98 L138 92 L132 128 Z" />
        </g>
        {ember(26, 100, 2.2, 0, '#ffb09a')}{ember(44, 112, 1.6, 1.1, '#ffd27a')}{ember(146, 104, 2.2, 0.5, '#ffb09a')}{ember(162, 94, 1.6, 1.9, '#ffd27a')}{ember(90, 120, 1.8, 2.6, '#ffc9b8')}{ember(70, 116, 1.4, 3.3, '#ffd27a')}
      </>
    );
    case 'arena': return (
      <>
        {[22, 158].map((x, i) => (
          <g class="bd-banner" style={{ transformOrigin: `${x}px 0px`, animationDelay: `${-i * 1.7}s` }}>
            <path d={`M${x - 11} -2 H${x + 11} V58 L${x} 49 L${x - 11} 58 Z`} fill="#1f3f7a" opacity="0.55" />
            <path d={`M${x - 8} -2 V50 M${x + 8} -2 V50`} stroke="#ffd45c" stroke-width="1.2" opacity="0.7" />
            <path d={`M${x} 16 l5 6 l-5 6 l-5 -6 Z`} fill="#ffd45c" opacity="0.85" />
          </g>
        ))}
        {twinkle(40, 104, 5)}{twinkle(142, 100, 4, 'an-late')}{twinkle(90, 14, 4, 'an-later')}
      </>
    );
    default: return ( // Colisée
      <>
        <circle class="an-glow" cx="150" cy="24" r="30" fill="url(#ts-halo)" />
        <g fill="#5a3a08" opacity="0.26">
          <path d="M-4 128 V84 H184 V128 Z" />
        </g>
        <g fill="#fff" opacity="0.16">
          {[6, 34, 62, 90, 118, 146].map((x) => <path d={`M${x} 128 V104 Q${x} 92 ${x + 12} 92 Q${x + 24} 92 ${x + 24} 104 V128 Z`} />)}
        </g>
        <path d="M-4 84 H184" stroke="#fff" stroke-width="1.4" opacity="0.3" />
        {[24, 60, 124, 160].map((x, i) => <circle class="ts-dust" style={{ animationDelay: `${-i * 1.4}s` }} cx={x} cy={70 - (i % 2) * 22} r="1.6" fill="#fff" />)}
      </>
    );
  }
}

export function TileScene({ kind }: { kind: string }) {
  return (
    <svg class="tile-scene" viewBox="0 0 180 160" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs><radialGradient id="ts-halo"><stop offset="0" stop-color="#fff" stop-opacity="0.75" /><stop offset="0.55" stop-color="#fff" stop-opacity="0.22" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></radialGradient></defs>
      <Motif kind={kind} />
      <Ring />
    </svg>
  );
}
