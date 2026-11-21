// Le décor de l'onglet Aventure : la route qui part vers le château. En haut (au-dessus des tuiles), le panorama : soleil
// et son cercle de runes, sommets enneigés, château sur son rocher, nuages, montgolfière, oiseaux. En dessous, la campagne :
// collines, sapins, le chemin qui serpente jusqu'au premier plan. Lumière venue de la droite (côté soleil) partout.
import { RUNES } from './portal';

const W = 390, H = 844;

function rng(seed: number) {
  let s = seed;
  return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}

/** Une ligne de collines douces, fermée en bas. */
function hills(seed: number, base: number, amp: number, step: number): string {
  const r = rng(seed);
  let d = `M-10 ${H} L-10 ${base}`;
  for (let x = -10; x <= W + 10; x += step) d += ` Q${x + step * 0.5} ${(base - amp * (0.4 + 0.6 * r())).toFixed(0)} ${x + step} ${(base - amp * 0.25 * r()).toFixed(0)}`;
  return `${d} L${W + 10} ${H} Z`;
}

/** Un sapin : trois étages, le côté droit éclairé. */
function Pine({ x, y, s, dark = '#2f7048', light = '#4f9a62' }: { x: number; y: number; s: number; dark?: string; light?: string }) {
  const tier = (top: number, w: number, h: number) => `M0 ${top} L${w} ${top + h} L${-w} ${top + h} Z`;
  const half = (top: number, w: number, h: number) => `M0 ${top} L${w} ${top + h} L0 ${top + h} Z`;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <rect x="-2.5" y="-6" width="5" height="8" fill="#6b4a2a" />
      <path d={`${tier(-52, 11, 18)} ${tier(-40, 15, 20)} ${tier(-26, 19, 22)}`} fill={dark} />
      <path d={`${half(-52, 11, 18)} ${half(-40, 15, 20)} ${half(-26, 19, 22)}`} fill={light} />
    </g>
  );
}

/** Un nuage aux bords ronds, plus bleu en dessous. */
function Cloud({ x, y, s, cls, opacity = 1 }: { x: number; y: number; s: number; cls: string; opacity?: number }) {
  return (
    <g class={cls}>
      <path transform={`translate(${x} ${y}) scale(${s})`} opacity={opacity} fill="url(#ad-cloud)"
        d="M4 34 a11 11 0 0 1 4 -21 a17 17 0 0 1 32 -5 a13 13 0 0 1 23 6 a11 11 0 0 1 3 20 Z" />
    </g>
  );
}

export function AdventureScene() {
  const sun = { x: 314, y: 136 };
  return (
    <>
      <defs>
        <linearGradient id="ad-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a62b4" /><stop offset="0.17" stop-color="#4b90d6" /><stop offset="0.31" stop-color="#b4dcf2" /><stop offset="1" stop-color="#b4dcf2" /></linearGradient>
        <radialGradient id="ad-sun"><stop offset="0" stop-color="#fffbe0" /><stop offset="0.3" stop-color="#ffe58a" stop-opacity="0.85" /><stop offset="1" stop-color="#ffe58a" stop-opacity="0" /></radialGradient>
        <linearGradient id="ad-cloud" x1="0" y1="0" x2="0" y2="1"><stop offset="0.35" stop-color="#ffffff" /><stop offset="1" stop-color="#c4def3" /></linearGradient>
        <linearGradient id="ad-peak" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c2d9f0" /><stop offset="1" stop-color="#93b6de" /></linearGradient>
        <linearGradient id="ad-crag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d9fcc" /><stop offset="1" stop-color="#6088b8" /></linearGradient>
        <linearGradient id="ad-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset="0.6" stop-color="#fff" stop-opacity="0.6" /><stop offset="1" stop-color="#fff" stop-opacity="0" /></linearGradient>
        <linearGradient id="ad-h1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a5d99a" /><stop offset="1" stop-color="#7cc083" /></linearGradient>
        <linearGradient id="ad-h2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#86c98a" /><stop offset="0.5" stop-color="#63b074" /></linearGradient>
        <linearGradient id="ad-h3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6bb878" /><stop offset="0.5" stop-color="#4c9c64" /></linearGradient>
        <linearGradient id="ad-h4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f9f66" /><stop offset="0.6" stop-color="#357a50" /></linearGradient>
        <linearGradient id="ad-path" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6ecc8" /><stop offset="1" stop-color="#e2c98c" /></linearGradient>
      </defs>
      <rect width={W} height={H} fill="url(#ad-sky)" />

      {/* le soleil et son cercle de runes */}
      <circle class="bd-sun" cx={sun.x} cy={sun.y} r="118" fill="url(#ad-sun)" />
      <g class="bd-ring" style={{ transformOrigin: `${sun.x}px ${sun.y}px`, animationDuration: '90s' }} fill="none" stroke="#fff" opacity="0.5">
        <circle cx={sun.x} cy={sun.y} r="52" stroke-width="1.4" />
        <circle cx={sun.x} cy={sun.y} r="40" stroke-width="1" stroke-dasharray="2 6" />
        {RUNES.map((d, i) => {
          const a = (i / RUNES.length) * Math.PI * 2;
          return <path d={d} stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" transform={`translate(${(sun.x + Math.cos(a) * 46).toFixed(1)} ${(sun.y + Math.sin(a) * 46).toFixed(1)}) rotate(${((a * 180) / Math.PI + 90).toFixed(0)}) scale(0.42)`} />;
        })}
      </g>
      <circle cx={sun.x} cy={sun.y} r="23" fill="#fff6c4" /><circle cx={sun.x - 6} cy={sun.y - 6} r="12" fill="#fff" opacity="0.5" />

      <g transform="translate(0 28)">
        <Cloud x={250} y={170} s={1.5} cls="bd-cloud bd-slow" opacity={0.6} />
        {/* les sommets au loin, coiffés de neige */}
        <path d="M118 236 L168 150 L186 168 L214 104 L246 158 L262 144 L296 196 L330 150 L352 176 L372 140 L400 190 V236 Z" fill="url(#ad-peak)" />
        <path d="M214 104 L186 168 L168 150 L118 236 H204 Z M372 140 L352 176 L330 150 L296 196 L318 236 H360 Z" fill="#7da3d2" opacity="0.4" />
        <g fill="#fff">
          <path d="M214 104 L201 134 L207 130 L213 138 L219 129 L225 137 L231 134 Z" />
          <path d="M372 140 L361 160 L367 157 L372 164 L378 157 L383 160 Z" />
          <path d="M168 150 L159 166 L164 164 L169 170 L175 164 L181 165 Z" />
          <path d="M330 150 L322 163 L327 161 L331 166 L336 161 L340 163 Z" />
        </g>
        {/* le rocher et le château */}
        <path d="M-10 240 L8 206 L30 190 L52 160 L74 150 L112 150 L130 172 L150 198 L170 212 L198 240 Z" fill="url(#ad-crag)" />
        <path d="M112 150 L130 172 L150 198 L170 212 L198 240 H150 L128 200 L104 172 Z" fill="#a8c4e4" opacity="0.55" />
        <g>
          {/* murs : pierre claire, côté gauche à l'ombre */}
          <path d="M62 152 V126 h5 v-5 h6 v5 h6 v-5 h6 v5 h20 v-5 h6 v5 h6 v-5 h6 v5 V152 Z" fill="#efe6d0" />
          <path d="M62 152 V126 h5 v-5 h6 v5 h6 v-5 h6 v5 h3 V152 Z" fill="#cfc4ac" />
          <rect x="54" y="106" width="18" height="46" fill="#efe6d0" /><rect x="54" y="106" width="8" height="46" fill="#cfc4ac" />
          <rect x="80" y="90" width="22" height="62" fill="#f4ecd8" /><rect x="80" y="90" width="9" height="62" fill="#d6cbb4" />
          <rect x="106" y="112" width="16" height="40" fill="#efe6d0" /><rect x="106" y="112" width="6" height="40" fill="#cfc4ac" />
          {/* toits */}
          <path d="M50 106 L63 82 L76 106 Z" fill="#c9584c" /><path d="M50 106 L63 82 L63 106 Z" fill="#a4443c" />
          <path d="M76 90 L91 58 L106 90 Z" fill="#d1604f" /><path d="M76 90 L91 58 L91 90 Z" fill="#a4443c" />
          <path d="M102 112 L114 92 L126 112 Z" fill="#c9584c" /><path d="M102 112 L114 92 L114 112 Z" fill="#a4443c" />
          {/* porte et fenêtres */}
          <path d="M86 152 V141 Q86 135 91 135 Q96 135 96 141 V152 Z" fill="#5a4636" />
          <g fill="#ffd98a">
            <rect class="bd-star" x="89" y="102" width="4" height="7" rx="2" /><rect class="bd-star" style={{ animationDelay: '-1.4s' }} x="61" y="118" width="3.5" height="6" rx="1.7" />
            <rect class="bd-star" style={{ animationDelay: '-2.6s' }} x="112" y="124" width="3.5" height="6" rx="1.7" /><rect class="bd-star" style={{ animationDelay: '-0.7s' }} x="89" y="118" width="4" height="7" rx="2" />
          </g>
          {/* fanions */}
          <path d="M91 58 v-18 M63 82 v-12" stroke="#5a4636" stroke-width="1.4" />
          <path class="bd-flag" style={{ transformOrigin: '91px 45px' }} d="M91 40 l15 4.5 l-15 5 Z" fill="#e0564e" />
          <path class="bd-flag" style={{ transformOrigin: '63px 74px', animationDelay: '-0.6s' }} d="M63 70 l10 3.5 l-10 4 Z" fill="#ffd45c" />
        </g>
        {/* nuages, montgolfière, oiseaux */}
        <Cloud x={14} y={70} s={1.15} cls="bd-cloud" />
        <Cloud x={200} y={196} s={0.85} cls="bd-cloud bd-slow" opacity={0.9} />
        <Cloud x={150} y={62} s={0.55} cls="bd-cloud bd-slow" opacity={0.85} />
        <g class="ad-balloon">
          <g transform="translate(252 92)">
            <path d="M-4.5 19 L-3 24 M4.5 19 L3 24" stroke="#5a4636" stroke-width="1" />
            <rect x="-3.5" y="24" width="7" height="5.5" rx="1.2" fill="#8a5a30" />
            <path d="M0 -17 C13 -17 17 -6 15 2 C13 10 7 15 4.5 19 H-4.5 C-7 15 -13 10 -15 2 C-17 -6 -13 -17 0 -17 Z" fill="#e0564e" />
            <path d="M0 -17 C6 -17 8 -6 7 2 C6 10 3 15 2 19 H-2 C-3 15 -6 10 -7 2 C-8 -6 -6 -17 0 -17 Z" fill="#f4b05a" />
            <path d="M0 -17 C13 -17 17 -6 15 2 C13 10 7 15 4.5 19 H1 C6 12 10 6 10 -2 C10 -10 6 -17 0 -17 Z" fill="#fff" opacity="0.22" />
            <path d="M-14.6 4 Q0 9 14.6 4" fill="none" stroke="#ffd45c" stroke-width="2" />
          </g>
        </g>
        <g class="bd-birds" fill="none" stroke="#2f4a6a" stroke-width="1.6" stroke-linecap="round"><path d="M70 150 q5 -5 8 0 q3 -5 8 0" /><path d="M94 164 q4 -4 7 0 q3 -4 7 0" /><path d="M52 170 q3.5 -3.5 6 0 q2.5 -3.5 6 0" /></g>
        <rect y="196" width={W} height="70" fill="url(#ad-haze)" />
      </g>

      {/* la campagne : quatre plans de collines, de plus en plus proches */}
      <path d={hills(7, 276, 22, 120)} fill="url(#ad-h1)" />
      <Pine x={232} y={272} s={0.36} dark="#5aa070" light="#7cc083" /><Pine x={246} y={274} s={0.42} dark="#5aa070" light="#7cc083" /><Pine x={346} y={276} s={0.4} dark="#5aa070" light="#7cc083" /><Pine x={28} y={280} s={0.44} dark="#5aa070" light="#7cc083" />
      <path d={hills(19, 372, 46, 150)} fill="url(#ad-h2)" />
      <path d={hills(29, 520, 56, 170)} fill="url(#ad-h3)" />
      {/* le chemin : il part du premier plan et monte en serpentant vers le château */}
      <path d="M150 844 C120 716 306 642 256 508 C220 412 96 376 122 272 L129 272 C108 372 246 410 288 508 C344 640 196 716 252 844 Z" fill="url(#ad-path)" />
      <Pine x={52} y={400} s={0.75} dark="#3f8a58" light="#62b074" /><Pine x={76} y={412} s={0.62} dark="#3f8a58" light="#62b074" /><Pine x={340} y={452} s={0.85} dark="#3f8a58" light="#62b074" /><Pine x={316} y={464} s={0.68} dark="#3f8a58" light="#62b074" />
      <Pine x={30} y={600} s={1.15} /><Pine x={58} y={624} s={0.95} /><Pine x={364} y={650} s={1.25} /><Pine x={336} y={672} s={1} />
      <path d={hills(41, 742, 44, 190)} fill="url(#ad-h4)" />
      {/* premier plan : le poteau indicateur et le campement */}
      <g transform="translate(330 768)">
        <rect x="-2.5" y="-46" width="5" height="48" fill="#6b4a2a" />
        <path d="M-2 -44 H24 L30 -38 L24 -32 H-2 Z" fill="#c99556" /><path d="M2 -28 H-22 L-28 -22 L-22 -16 H2 Z" fill="#b5803f" />
      </g>
      <g transform="translate(70 780)">
        <path d="M-30 0 L0 -40 L30 0 Z" fill="#e9dcc0" /><path d="M0 -40 L30 0 H8 Z" fill="#fff" opacity="0.5" /><path d="M-7 0 L0 -18 L7 0 Z" fill="#6b4a2a" />
        <path d="M0 -40 v-14" stroke="#6b4a2a" stroke-width="1.6" /><path class="bd-flag" style={{ transformOrigin: '0px -50px' }} d="M0 -54 l12 4 l-12 4 Z" fill="#e0564e" />
      </g>
      <Pine x={14} y={790} s={1.5} dark="#255c3c" light="#3a8050" /><Pine x={380} y={812} s={1.6} dark="#255c3c" light="#3a8050" />
    </>
  );
}
