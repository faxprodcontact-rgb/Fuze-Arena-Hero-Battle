// Petits dessins animés des menus, dans le trait du portail d'invocation : dessinés par le code, toujours en mouvement.
// Sablier (le sable coule puis il se retourne), coffre de butin (fermé, entrouvert, plein), halo de runes (derrière un
// trophée, un héros fusionné…). Les mouvements sont dans anim.css.
import './anim.css';
import { RUNES, spark } from './portal';

const INK = '#2f2244';

/** Le sablier du butin rapide : le sable descend, puis le sablier se retourne et recommence. */
export function Hourglass({ size = 54, class: cls = '' }: { size?: number; class?: string }) {
  const glass = 'M31 19 H69 C69 38 54 44 54 50 C54 56 69 62 69 81 H31 C31 62 46 56 46 50 C46 44 31 38 31 19 Z';
  return (
    <span class={`anim hourglass-anim ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <svg viewBox="0 0 100 100" width={size} height={size} aria-hidden="true">
        <defs>
          <linearGradient id="hg-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0a8" /><stop offset="0.5" stop-color="#ffc531" /><stop offset="1" stop-color="#d98a0b" /></linearGradient>
          <linearGradient id="hg-sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe58a" /><stop offset="1" stop-color="#f09a1e" /></linearGradient>
          <radialGradient id="hg-glow"><stop offset="0" stop-color="#ffe58a" stop-opacity="0.85" /><stop offset="1" stop-color="#ffe58a" stop-opacity="0" /></radialGradient>
          <clipPath id="hg-top"><path d="M31 19 H69 C69 38 54 44 54 50 H46 C46 44 31 38 31 19 Z" /></clipPath>
          <clipPath id="hg-bot"><path d="M46 50 H54 C54 56 69 62 69 81 H31 C31 62 46 56 46 50 Z" /></clipPath>
        </defs>
        <circle class="an-glow" cx="50" cy="50" r="48" fill="url(#hg-glow)" />
        <g class="hg-turn">
          <path d={glass} fill="#dff4ff" fill-opacity="0.62" />
          <g clip-path="url(#hg-top)"><rect class="hg-sand-top" x="28" y="24" width="44" height="30" fill="url(#hg-sand)" /></g>
          <g clip-path="url(#hg-bot)"><path class="hg-sand-bot" d="M28 84 V68 Q50 60 72 68 V84 Z" fill="url(#hg-sand)" /></g>
          <rect class="hg-stream" x="49" y="50" width="2" height="28" rx="1" fill="#ffd45c" />
          <path d={glass} fill="none" stroke={INK} stroke-width="3" stroke-linejoin="round" />
          <path d="M36 24 C37 33 41 38 45 42" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity="0.85" />
          <path d="M36 76 C37 68 41 63 45 59" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.5" />
          <rect x="24" y="17" width="5" height="66" rx="2" fill="#d98a0b" stroke={INK} stroke-width="2.5" />
          <rect x="71" y="17" width="5" height="66" rx="2" fill="#d98a0b" stroke={INK} stroke-width="2.5" />
          <rect x="19" y="7" width="62" height="12" rx="4.5" fill="url(#hg-gold)" stroke={INK} stroke-width="3" />
          <rect x="19" y="81" width="62" height="12" rx="4.5" fill="url(#hg-gold)" stroke={INK} stroke-width="3" />
          <path d="M24 11 H76" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.7" />
          <path d="M24 85 H76" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity="0.7" />
          <path d="M50 9.5 L53 13 L50 16.5 L47 13 Z" fill="#ff6fb5" stroke={INK} stroke-width="1.5" />
          <path d="M50 83.5 L53 87 L50 90.5 L47 87 Z" fill="#6fe3ff" stroke={INK} stroke-width="1.5" />
        </g>
        <path class="an-twinkle" style={{ transformOrigin: '14px 30px' }} d={spark(14, 30, 6)} fill="#fff" />
        <path class="an-twinkle an-late" style={{ transformOrigin: '88px 62px' }} d={spark(88, 62, 5)} fill="#fff" />
      </svg>
    </span>
  );
}

/** Le coffre de butin : `closed` (il respire), `ready` (le couvercle se soulève, une lueur s'échappe), `full` (ouvert, il déborde). */
export function Chest({ size = 64, state = 'closed', class: cls = '' }: { size?: number; state?: 'closed' | 'ready' | 'full'; class?: string }) {
  const open = state !== 'closed';
  return (
    <span class={`anim chest-anim chest-${state} ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <svg viewBox="0 0 100 100" width={size} height={size} aria-hidden="true">
        <defs>
          <linearGradient id="ch-wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c98a48" /><stop offset="1" stop-color="#8a5426" /></linearGradient>
          <linearGradient id="ch-lid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e0a35c" /><stop offset="1" stop-color="#a86a30" /></linearGradient>
          <linearGradient id="ch-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0a8" /><stop offset="0.5" stop-color="#ffc531" /><stop offset="1" stop-color="#d98a0b" /></linearGradient>
          <radialGradient id="ch-glow"><stop offset="0" stop-color="#fff6c2" stop-opacity="0.95" /><stop offset="0.5" stop-color="#ffd45c" stop-opacity="0.5" /><stop offset="1" stop-color="#ffd45c" stop-opacity="0" /></radialGradient>
        </defs>
        <ellipse cx="50" cy="90" rx="38" ry="6" fill="#000" opacity="0.28" />
        {open && <ellipse class="an-glow" cx="50" cy="44" rx="48" ry="34" fill="url(#ch-glow)" />}
        {/* l'intérieur, visible quand le couvercle se lève */}
        <path d="M15 52 H85 V60 H15 Z" fill="#3a2414" stroke={INK} stroke-width="3" stroke-linejoin="round" />
        {open && <path class="ch-light" d="M20 54 L10 18 H90 L80 54 Z" fill="url(#ch-glow)" />}
        {state === 'full' && (
          <g stroke={INK} stroke-width="2">
            <circle cx="34" cy="50" r="7" fill="url(#ch-gold)" /><circle cx="48" cy="46" r="8" fill="url(#ch-gold)" /><circle cx="63" cy="50" r="7" fill="url(#ch-gold)" />
            <path d="M72 40 L78 47 L72 54 L66 47 Z" fill="#ff6fb5" /><path d="M26 39 L31 45 L26 51 L21 45 Z" fill="#6fe3ff" />
          </g>
        )}
        {/* la caisse */}
        <g class="ch-body">
          <path d="M13 56 H87 V82 Q87 88 81 88 H19 Q13 88 13 82 Z" fill="url(#ch-wood)" stroke={INK} stroke-width="3" stroke-linejoin="round" />
          <path d="M13 68 H87" stroke="#6b3d18" stroke-width="2" opacity="0.6" /><path d="M13 78 H87" stroke="#6b3d18" stroke-width="2" opacity="0.6" />
          <rect x="21" y="56" width="9" height="32" fill="url(#ch-gold)" stroke={INK} stroke-width="2.5" />
          <rect x="70" y="56" width="9" height="32" fill="url(#ch-gold)" stroke={INK} stroke-width="2.5" />
          <path d="M42 56 H58 V68 Q58 75 50 75 Q42 75 42 68 Z" fill="url(#ch-gold)" stroke={INK} stroke-width="2.5" stroke-linejoin="round" />
          <circle cx="50" cy="63" r="2.6" fill={INK} /><path d="M50 64 V70" stroke={INK} stroke-width="2.4" stroke-linecap="round" />
        </g>
        {/* le couvercle */}
        <g class="ch-lid">
          <path d="M11 56 V42 Q11 24 29 24 H71 Q89 24 89 42 V56 Z" fill="url(#ch-lid)" stroke={INK} stroke-width="3" stroke-linejoin="round" />
          <path d="M18 34 Q22 28 30 28 H56" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity="0.55" />
          <rect x="21" y="24" width="9" height="32" fill="url(#ch-gold)" stroke={INK} stroke-width="2.5" />
          <rect x="70" y="24" width="9" height="32" fill="url(#ch-gold)" stroke={INK} stroke-width="2.5" />
          <rect x="11" y="48" width="78" height="8" rx="2" fill="url(#ch-gold)" stroke={INK} stroke-width="2.5" />
        </g>
        {open && <path class="an-twinkle" style={{ transformOrigin: '20px 22px' }} d={spark(20, 22, 6)} fill="#fff" />}
        {open && <path class="an-twinkle an-late" style={{ transformOrigin: '82px 16px' }} d={spark(82, 16, 5)} fill="#fff" />}
        {state === 'full' && <path class="an-twinkle an-later" style={{ transformOrigin: '52px 12px' }} d={spark(52, 12, 7)} fill="#fff6c2" />}
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
