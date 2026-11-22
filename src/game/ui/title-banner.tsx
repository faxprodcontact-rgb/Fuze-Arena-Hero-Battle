// Le bandeau de titre d'une partie du jeu (ici « Aventure »), dessiné par le code dans le trait du décor :
// un ruban cramoisi aux bouts repliés, une plaque de bois sculpté sertie dans un cadre d'or, un fleuron en haut,
// une gemme de chaque côté, le titre en lettres d'or. Un reflet passe sur la plaque, les gemmes scintillent.
import type { ComponentChildren } from 'preact';
import './anim.css';
import { spark } from './portal';

/** `ribbon` = les deux tons du ruban et celui de son repli (cramoisi par défaut). Sans picto (`children`), le titre est centré. */
export function TitleBanner({ title, children, ribbon = ['#e2574c', '#9c2a2e', '#5e1418'] }: { title: string; children?: ComponentChildren; ribbon?: [string, string, string] }) {
  // la place du titre sur la plaque (moins large avec un picto à gauche) ; un titre long prend une taille plus petite, et
  // s'il dépasse encore, il est resserré pour tenir (jamais coupé)
  const tx = children ? 127 : 108, room = children ? 112 : 146;
  const size = Math.max(13, Math.min(23.5, room / (title.length * 0.5)));
  const ty = 27 + size * 0.32;
  const fit = title.length * 0.53 * size > room ? { textLength: room, lengthAdjust: 'spacingAndGlyphs' } : {};
  const gem = (x: number) => (
    <g>
      <path d={`M${x} 17 L${x + 8} 26 L${x} 35 L${x - 8} 26 Z`} fill="#2f1b0c" />
      <path d={`M${x} 18.800 L${x + 6.400} 26 L${x} 33.200 L${x - 6.400} 26 Z`} fill="url(#tb-gold)" />
      <path d={`M${x} 21.600 L${x + 3.900} 26 L${x} 30.400 L${x - 3.900} 26 Z`} fill="#2a5aa8" /><path d={`M${x} 21.600 L${x + 3.900} 26 H${x} Z`} fill="#8fc0ff" /><path d={`M${x} 26 H${x + 3.900} L${x} 30.400 Z`} fill="#4f8ae0" />
    </g>
  );
  return (
    <div class="title-banner">
      <svg viewBox="0 0 216 54" aria-hidden="true">
        <defs>
          <linearGradient id="tb-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
          <linearGradient id="tb-wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a97848" /><stop offset="0.5" stop-color="#7c5230" /><stop offset="1" stop-color="#55361a" /></linearGradient>
          <linearGradient id="tb-ribbon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2574c" /><stop offset="1" stop-color="#9c2a2e" /></linearGradient>
          <linearGradient id="tb-text" x1="0" y1="0" x2="0" y2="1"><stop offset="0.15" stop-color="#fffbe0" /><stop offset="0.55" stop-color="#ffd24a" /><stop offset="1" stop-color="#e08a12" /></linearGradient>
          <clipPath id="tb-clip"><rect x="26" y="9.500" width="164" height="35" rx="6" /></clipPath>
        </defs>
        {/* le ruban : deux bouts repliés derrière la plaque */}
        {[0, 1].map((i) => (
          <g transform={i ? 'translate(216 0) scale(-1 1)' : undefined}>
            <path d="M32 44 L22 51 V44 Z" fill={ribbon[2]} />
            <path d="M1 17 H33 V45 H1 L10 31 Z" fill="#2f1b0c" />
            <path d="M3.800 18.500 H31.500 V43.500 H3.800 L11.800 31 Z" fill={ribbon[1]} /><path d="M3.800 18.500 H31.500 V31 H11.800 Z" fill={ribbon[0]} />
            <path d="M3.800 18.500 H31.500 V21.200 H5.500 Z M5.500 40.800 H31.500 V43.500 H3.800 Z" fill="#ffd45c" />
            <path d="M24 21.200 H31.500 V40.800 H24 Z" fill="#000" opacity="0.2" />
          </g>
        ))}
        {/* la plaque : bord sombre, cadre d'or, filet, bois sculpté */}
        <rect x="20" y="3.500" width="176" height="47" rx="11" fill="#2f1b0c" />
        <rect x="21.800" y="5.300" width="172.400" height="43.400" rx="9.500" fill="url(#tb-gold)" />
        <path d="M24 12 Q24 7 30 6.800 H186 Q192 7 192 12" fill="none" stroke="#fffbe0" stroke-width="1" opacity="0.9" />
        <rect x="25" y="8.500" width="166" height="37" rx="7" fill="#2f1b0c" />
        <rect x="26" y="9.500" width="164" height="35" rx="6" fill="url(#tb-wood)" />
        <g clip-path="url(#tb-clip)">
          <rect x="26" y="9.500" width="164" height="13" fill="#fff" opacity="0.13" />
          <rect x="26" y="37" width="164" height="8" fill="#000" opacity="0.18" />
          {/* le reflet qui passe */}
          <path class="tb-sheen" d="M0 4 H16 L4 50 H-12 Z" fill="#fff" opacity="0.3" />
        </g>
        <rect x="29.500" y="13" width="157" height="28" rx="4" fill="none" stroke="#e9b84a" stroke-width="0.900" opacity="0.75" />
        {/* quatre clous d'or dans les angles */}
        {[[32.500, 16], [183.500, 16], [32.500, 38], [183.500, 38]].map(([x, y]) => <g><circle cx={x} cy={y} r="1.900" fill="#8a5206" /><circle cx={x! + 0.300} cy={y! - 0.300} r="1.200" fill="#fff3b0" /></g>)}
        {/* le fleuron du haut, la goutte d'or du bas */}
        <path d="M108 -3.500 L112.500 3 L122 3.500 L114 7.500 L108 12.500 L102 7.500 L94 3.500 L103.500 3 Z" fill="#2f1b0c" />
        <path d="M108 -1 L111.500 4.300 L118 4.800 L112.800 7.300 L108 10.800 L103.200 7.300 L98 4.800 L104.500 4.300 Z" fill="url(#tb-gold)" />
        <circle cx="108" cy="5.300" r="2.300" fill="#b81f2e" /><circle cx="108.600" cy="4.700" r="0.900" fill="#ff9a8a" />
        <path d="M108 47 L112 51 L108 55.500 L104 51 Z" fill="#2f1b0c" /><path d="M108 48.600 L110.500 51 L108 53.800 L105.500 51 Z" fill="url(#tb-gold)" />
        {/* une gemme de chaque côté */}
        {gem(20)}{gem(196)}
        {/* le titre, en lettres d'or cernées de brun */}
        <text {...fit} x={tx} y={ty + 1.500} text-anchor="middle" font-family="'Lilita One', 'Trebuchet MS', sans-serif" font-weight="400" font-size={size} fill="#1f1006" opacity="0.4" stroke="#1f1006" stroke-width="3.400" stroke-linejoin="round">{title}</text>
        <text {...fit} x={tx} y={ty} text-anchor="middle" font-family="'Lilita One', 'Trebuchet MS', sans-serif" font-weight="400" font-size={size} fill="url(#tb-text)" stroke="#2f1b0c" stroke-width="3.400" stroke-linejoin="round" paint-order="stroke">{title}</text>
        <path class="an-twinkle" style={{ transformOrigin: '20px 20px' }} d={spark(20, 20, 4)} fill="#fff" /><path class="an-twinkle an-late" style={{ transformOrigin: '196px 20px' }} d={spark(196, 20, 4)} fill="#fff" />
      </svg>
      {children}
    </div>
  );
}
