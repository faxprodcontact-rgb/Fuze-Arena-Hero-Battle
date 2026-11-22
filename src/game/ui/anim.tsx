// Petits dessins animés des menus, dans le trait du portail d'invocation : dessinés par le code, toujours en mouvement.
// Sablier (le sable coule puis il se retourne), coffre de butin (fermé, entrouvert, plein), halo de runes (derrière un
// trophée, un héros fusionné…). Les mouvements sont dans anim.css.
import './anim.css';
import { RUNES, spark } from './portal';

/** Le contour des dessins : le même brun sombre que les pièces de l'interface (chrome.tsx). */
const INK = '#2f1b0c';

/**
 * Le sablier du butin rapide : deux socles d'or ciselés (une gemme sur chacun), trois colonnes de bois tourné baguées d'or
 * (celle du fond dans l'ombre), une ampoule de verre bleuté avec ses reflets ; le sable descend, puis le sablier se
 * retourne et recommence (dessin symétrique : la boucle ne se voit pas).
 */
export function Hourglass({ size = 54, class: cls = '' }: { size?: number; class?: string }) {
  const glass = 'M31 19 H69 C69 38 54 44 54 50 C54 56 69 62 69 81 H31 C31 62 46 56 46 50 C46 44 31 38 31 19 Z';
  // une colonne de bois tourné : renflée au milieu, une bague d'or en haut, au milieu et en bas
  const pillar = (x: number, back = false) => (
    <g opacity={back ? 0.9 : 1}>
      <path d={`M${x - 3.2} 19 C${x - 4.6} 30 ${x - 2.4} 40 ${x - 3.6} 50 C${x - 2.4} 60 ${x - 4.6} 70 ${x - 3.2} 81 H${x + 3.2} C${x + 4.6} 70 ${x + 2.4} 60 ${x + 3.6} 50 C${x + 2.4} 40 ${x + 4.6} 30 ${x + 3.2} 19 Z`} fill={back ? '#3a2414' : 'url(#hg-wood)'} stroke={INK} stroke-width="2" stroke-linejoin="round" />
      {!back && <path d={`M${x + 0.8} 22 C${x + 2} 32 ${x + 0.6} 42 ${x + 1.6} 50 C${x + 0.6} 58 ${x + 2} 68 ${x + 0.8} 78`} fill="none" stroke="#fff" stroke-width="1.1" opacity="0.45" stroke-linecap="round" />}
      {[24, 50, 76].map((y) => <rect x={x - 4.6} y={y - 2} width="9.2" height="4" rx="1.6" fill="url(#hg-gold)" stroke={INK} stroke-width="1.4" />)}
    </g>
  );
  // un socle : plateau d'or biseauté, sa tranche plus sombre, une gemme au milieu
  const cap = (y: number, gem: string) => (
    <g>
      <rect x="16" y={y} width="68" height="11" rx="4" fill="url(#hg-gold)" stroke={INK} stroke-width="2.6" />
      <rect x="18" y={y + 6.5} width="64" height="3" rx="1.5" fill="#9a5a06" opacity="0.55" />
      <path d={`M21 ${y + 2.6} H79`} stroke="#fffbe0" stroke-width="1.6" stroke-linecap="round" opacity="0.85" />
      <path d={`M50 ${y + 1.2} L54.5 ${y + 5.5} L50 ${y + 9.8} L45.5 ${y + 5.5} Z`} fill={gem} stroke={INK} stroke-width="1.4" />
      <path d={`M50 ${y + 2.4} L52.6 ${y + 5.5} H50 Z`} fill="#fff" opacity="0.6" />
      {[24, 76].map((x) => <circle cx={x} cy={y + 5.5} r="1.6" fill="#7a4406" />)}
    </g>
  );
  return (
    <span class={`anim hourglass-anim ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <svg viewBox="0 0 100 100" width={size} height={size} aria-hidden="true">
        <defs>
          <linearGradient id="hg-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
          <linearGradient id="hg-wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5a3418" /><stop offset="0.55" stop-color="#9a6234" /><stop offset="1" stop-color="#6e4020" /></linearGradient>
          <linearGradient id="hg-glass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#bfe8ff" stop-opacity="0.75" /><stop offset="0.5" stop-color="#eaf8ff" stop-opacity="0.35" /><stop offset="1" stop-color="#9fd4f5" stop-opacity="0.7" /></linearGradient>
          <linearGradient id="hg-sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe89a" /><stop offset="1" stop-color="#ee9420" /></linearGradient>
          <radialGradient id="hg-glow"><stop offset="0" stop-color="#ffe58a" stop-opacity="0.85" /><stop offset="1" stop-color="#ffe58a" stop-opacity="0" /></radialGradient>
          <clipPath id="hg-top"><path d="M31 19 H69 C69 38 54 44 54 50 H46 C46 44 31 38 31 19 Z" /></clipPath>
          <clipPath id="hg-bot"><path d="M46 50 H54 C54 56 69 62 69 81 H31 C31 62 46 56 46 50 Z" /></clipPath>
        </defs>
        <circle class="an-glow" cx="50" cy="50" r="48" fill="url(#hg-glow)" />
        <ellipse cx="50" cy="97" rx="30" ry="3.5" fill="#000" opacity="0.28" />
        <g class="hg-turn">
          {pillar(50, true)}
          <path d={glass} fill="url(#hg-glass)" />
          <g clip-path="url(#hg-top)"><rect class="hg-sand-top" x="28" y="24" width="44" height="30" fill="url(#hg-sand)" /><ellipse class="hg-sand-top" cx="50" cy="24" rx="20" ry="2.4" fill="#fff3c0" opacity="0.8" /></g>
          <g clip-path="url(#hg-bot)"><path class="hg-sand-bot" d="M28 84 V70 Q38 63 50 61 Q62 63 72 70 V84 Z" fill="url(#hg-sand)" /></g>
          <rect class="hg-stream" x="49.2" y="50" width="1.6" height="28" rx="0.8" fill="#ffd45c" />
          <path d={glass} fill="none" stroke={INK} stroke-width="2.6" stroke-linejoin="round" />
          <path d="M35 23 C36 32 40 38 44.5 42" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity="0.9" />
          <path d="M35.5 77 C36.5 69 40 63.5 44.5 59.5" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" opacity="0.55" />
          <path d="M64 26 C63.5 31 61.5 35 59 38" fill="none" stroke="#fff" stroke-width="1.3" stroke-linecap="round" opacity="0.5" />
          {pillar(24)}{pillar(76)}
          {cap(8, '#ff6fb5')}{cap(81, '#6fe3ff')}
        </g>
        <path class="an-twinkle" style={{ transformOrigin: '10px 30px' }} d={spark(10, 30, 6)} fill="#fff" />
        <path class="an-twinkle an-late" style={{ transformOrigin: '91px 64px' }} d={spark(91, 64, 5)} fill="#fff" />
      </svg>
    </span>
  );
}

/**
 * Le coffre de butin, en bois cerclé d'or : `closed` (il respire), `ready` (le couvercle se soulève, la lumière filtre
 * dessous), `full` (grand ouvert, débordant de pièces et de gemmes). Planches de bois, deux bandes d'or rivetées, coins
 * ferrés, serrure ciselée avec sa gemme ; couvercle bombé ; lumière venue de la droite.
 */
export function Chest({ size = 64, state = 'closed', class: cls = '' }: { size?: number; state?: 'closed' | 'ready' | 'full'; class?: string }) {
  const lifted = state !== 'closed';
  const band = (x: number) => (
    <g>
      <rect x={x} y="57" width="10" height="38" fill="url(#ch-gold)" stroke={INK} stroke-width="2.2" />
      <path d={`M${x + 2} 59 V93`} stroke="#fffbe0" stroke-width="1.2" opacity="0.7" />
      {[63, 87].map((y) => <g><circle cx={x + 5} cy={y} r="2" fill={INK} /><circle cx={x + 4.6} cy={y - 0.4} r="1.1" fill="#fff3b0" /></g>)}
    </g>
  );
  const coin = (x: number, y: number, r: number) => (
    <g><ellipse cx={x} cy={y} rx={r} ry={r * 0.82} fill="url(#ch-gold)" stroke={INK} stroke-width="1.6" /><ellipse cx={x} cy={y} rx={r * 0.58} ry={r * 0.45} fill="none" stroke="#b8720a" stroke-width="1" /><path d={`M${x - r * 0.4} ${y - r * 0.35} Q${x} ${y - r * 0.7} ${x + r * 0.4} ${y - r * 0.35}`} fill="none" stroke="#fff" stroke-width="1" opacity="0.8" /></g>
  );
  const gem = (x: number, y: number, r: number, c: [string, string]) => (
    <g><path d={`M${x} ${y - r} L${x + r} ${y} L${x} ${y + r} L${x - r} ${y} Z`} fill={c[1]} stroke={INK} stroke-width="1.6" /><path d={`M${x} ${y - r} L${x + r} ${y} H${x} Z`} fill={c[0]} /><path d={`M${x - r * 0.35} ${y - r * 0.2} L${x} ${y - r * 0.6}`} stroke="#fff" stroke-width="1" opacity="0.9" /></g>
  );
  return (
    <span class={`anim chest-anim chest-${state} ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <svg viewBox="0 0 120 110" width={size} height={size} aria-hidden="true">
        <defs>
          <linearGradient id="ch-wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a4520" /><stop offset="0.5" stop-color="#b77838" /><stop offset="1" stop-color="#d09050" /></linearGradient>
          <linearGradient id="ch-lid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dc9a58" /><stop offset="1" stop-color="#9a5e2a" /></linearGradient>
          <linearGradient id="ch-in" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a3216" /><stop offset="1" stop-color="#2a160a" /></linearGradient>
          <linearGradient id="ch-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
          <radialGradient id="ch-glow"><stop offset="0" stop-color="#fff6c2" stop-opacity="0.95" /><stop offset="0.45" stop-color="#ffd45c" stop-opacity="0.5" /><stop offset="1" stop-color="#ffd45c" stop-opacity="0" /></radialGradient>
        </defs>
        <ellipse cx="60" cy="101" rx="48" ry="6.5" fill="#000" opacity="0.3" />
        {lifted && <ellipse class="an-glow" cx="60" cy="46" rx="60" ry="40" fill="url(#ch-glow)" />}
        {/* grand ouvert : l'intérieur du couvercle rabattu en arrière, puis le trésor qui déborde */}
        {state === 'full' && (
          <g>
            <path d="M15 58 L7 20 Q60 6 113 20 L105 58 Z" fill={INK} />
            <path d="M17.5 56 L10.5 22.5 Q60 9.5 109.5 22.5 L102.5 56 Z" fill="url(#ch-in)" />
            <path d="M10.5 22.5 Q60 9.5 109.5 22.5 L108.5 27 Q60 14.5 11.5 27 Z" fill="url(#ch-gold)" stroke={INK} stroke-width="1.6" />
            {[28, 82].map((x) => <path d={`M${x} ${x < 60 ? 16.5 : 16.5} L${x + 9} ${x < 60 ? 14.6 : 14.6} L${x + 7.5} 56 H${x + 1.5} Z`} fill="url(#ch-gold)" stroke={INK} stroke-width="1.6" opacity="0.9" />)}
            <ellipse class="ch-light" cx="60" cy="56" rx="44" ry="12" fill="url(#ch-glow)" />
            {gem(31, 46, 6, ['#bfe0ff', '#3a78d8'])}{coin(44, 48, 7)}{coin(58, 42, 8)}{coin(73, 46, 7)}{gem(87, 45, 6.5, ['#ffc0e0', '#d83a8a'])}
            {coin(36, 54, 6.5)}{coin(51, 52, 7)}{gem(62, 50, 5.5, ['#c8ffd8', '#2fae5a'])}{coin(68, 55, 6.5)}{coin(83, 54, 6.5)}
            <path d="M40 40 Q48 34 56 37" fill="none" stroke="#fff6e0" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="0.1 4" />
          </g>
        )}
        {/* fermé ou entrouvert : l'intérieur sombre sous le couvercle, la lumière qui filtre */}
        {state !== 'full' && <path d="M16 56 H104 V62 H16 Z" fill="#2a160a" />}
        {state === 'ready' && <ellipse class="ch-light" cx="60" cy="57" rx="40" ry="5" fill="url(#ch-glow)" />}
        {/* la caisse */}
        <g class="ch-body">
          <path d="M13 55 H107 V93 Q107 99 101 99 H19 Q13 99 13 93 Z" fill={INK} />
          <path d="M15.5 57.5 H104.5 V92.5 Q104.5 96.5 100.5 96.5 H19.5 Q15.5 96.5 15.5 92.5 Z" fill="url(#ch-wood)" />
          <path d="M15.5 71 H104.5 M15.5 84 H104.5" stroke="#4a2810" stroke-width="1.4" opacity="0.45" />
          <path d="M15.5 72.4 H104.5 M15.5 85.4 H104.5" stroke="#ffe0b0" stroke-width="0.9" opacity="0.25" />
          <rect x="15.5" y="57.5" width="14" height="39" fill="#000" opacity="0.14" />
          {band(25)}{band(85)}
          {/* coins ferrés */}
          {[[13, 99, 1], [107, 99, -1]].map(([x, y, k]) => <path d={`M${x} ${y! - 13} V${y! - 6} Q${x} ${y} ${x! + k! * 6} ${y} H${x! + k! * 13} V${y! - 4} H${x! + k! * 6} Q${x! + k! * 4} ${y! - 4} ${x! + k! * 4} ${y! - 6} V${y! - 13} Z`} fill="url(#ch-gold)" stroke={INK} stroke-width="1.8" stroke-linejoin="round" />)}
          {/* la serrure ciselée, sa gemme, le trou de la clé */}
          <path d="M49 57 H71 V72 Q71 82 60 86 Q49 82 49 72 Z" fill="url(#ch-gold)" stroke={INK} stroke-width="2.4" stroke-linejoin="round" />
          <path d="M52 60 H68 V71 Q68 79 60 82.4 Q52 79 52 71 Z" fill="none" stroke="#b8720a" stroke-width="1.2" />
          <path d="M60 61 L64 65.5 L60 70 L56 65.5 Z" fill="#c8283a" stroke={INK} stroke-width="1.4" /><path d="M60 62.2 L62.6 65.5 H60 Z" fill="#ffb0b0" />
          <circle cx="60" cy="74" r="2.6" fill={INK} /><path d="M58.8 75 L58 80 H62 L61.2 75 Z" fill={INK} />
        </g>
        {/* le couvercle bombé (fermé ou entrouvert) */}
        {state !== 'full' && (
          <g class="ch-lid">
            <path d="M11 58 V45 Q11 23 36 23 H84 Q109 23 109 45 V58 Z" fill={INK} />
            <path d="M13.5 55.5 V45 Q13.5 25.5 36 25.5 H84 Q106.5 25.5 106.5 45 V55.5 Z" fill="url(#ch-lid)" />
            <path d="M14 42 Q60 34 106 42" fill="none" stroke="#6a3a16" stroke-width="1.3" opacity="0.5" />
            <path d="M20 34 Q24 28 34 28 H66" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity="0.5" />
            <path d="M25 25.5 H35 V56 H25 Z M85 25.5 H95 V56 H85 Z" fill="url(#ch-gold)" stroke={INK} stroke-width="2.2" />
            <rect x="11" y="50" width="98" height="8" rx="2.5" fill="url(#ch-gold)" stroke={INK} stroke-width="2.2" />
            <path d="M14 52 H106" stroke="#fffbe0" stroke-width="1.1" opacity="0.8" />
            <path d="M55 53 H65 V62 Q60 65 55 62 Z" fill="url(#ch-gold)" stroke={INK} stroke-width="1.8" />
          </g>
        )}
        {lifted && <path class="an-twinkle" style={{ transformOrigin: '18px 24px' }} d={spark(18, 24, 6)} fill="#fff" />}
        {lifted && <path class="an-twinkle an-late" style={{ transformOrigin: '102px 16px' }} d={spark(102, 16, 5)} fill="#fff" />}
        {state === 'full' && <path class="an-twinkle an-later" style={{ transformOrigin: '60px 8px' }} d={spark(60, 8, 7)} fill="#fff6c2" />}
        {state === 'closed' && <path class="an-twinkle an-later" style={{ transformOrigin: '96px 62px' }} d={spark(96, 62, 4.5)} fill="#fff" />}
      </svg>
    </span>
  );
}

/** Un halo de runes qui tourne, à poser derrière quelque chose de précieux (trophée, héros fusionné). */
export function Halo({ size = 150, color = '#ffc531', class: cls = '' }: { size?: number; color?: string; class?: string }) {
  return (
    <span class={`anim halo-anim ${cls}`} style={{ width: `${size}px`, height: `${size}px`, color }}>
      <svg viewBox="0 0 240 240" width={size} height={size} aria-hidden="true">
        <defs><radialGradient id="ha-glow"><stop offset="0" stop-color="currentColor" stop-opacity="0.75" /><stop offset="0.6" stop-color="currentColor" stop-opacity="0.22" /><stop offset="1" stop-color="currentColor" stop-opacity="0" /></radialGradient></defs>
        <circle class="an-glow" cx="120" cy="120" r="118" fill="url(#ha-glow)" />
        <g class="ha-ring">
          <circle cx="120" cy="120" r="104" fill="none" stroke="currentColor" stroke-width="2.5" opacity="0.9" />
          <circle cx="120" cy="120" r="84" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.7" />
          {RUNES.map((d, i) => {
            const a = (i / RUNES.length) * Math.PI * 2;
            return <path d={d} transform={`translate(${(120 + Math.cos(a) * 94).toFixed(1)} ${(120 + Math.sin(a) * 94).toFixed(1)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(0.8)`} fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />;
          })}
        </g>
        <g class="ha-ring-2">
          <circle cx="120" cy="120" r="70" fill="none" stroke="#fff" stroke-width="1.5" stroke-dasharray="3 9" opacity="0.8" />
          {[0, 1, 2, 3].map((i) => <path d={spark(120 + Math.cos((i * Math.PI) / 2) * 70, 120 + Math.sin((i * Math.PI) / 2) * 70, 7)} fill="#fff" />)}
        </g>
      </svg>
    </span>
  );
}
