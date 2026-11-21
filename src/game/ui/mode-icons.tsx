// Les pictos des six modes de l'Aventure, dessinés par le code et animés, dans le même trait que le décor de l'onglet :
// volumes en dégradés, lumière venue du haut à droite, un seul contour d'épaisseur constante autour de chaque objet
// (filtres `mi-out-c`, bleu nuit, pour les pictos froids et `mi-out-w`, brun, pour les chauds).
//   tour      : la tour des Épreuves, son cristal qui flotte, sa fenêtre allumée, ses bannières
//   missions  : la boussole, dont l'aiguille cherche le nord
//   dungeons  : la porte du donjon, sa herse, ses torches, la lueur du fond
//   dailyBoss : le crâne cornu, les yeux qui rougeoient
//   arena     : le bouclier et les deux épées croisées, l'éclat du choc
//   defense   : le Colisée, ses trois étages d'arcades, ses oriflammes
// Mouvements dans anim.css (classes mi-*).
import type { ComponentChildren } from 'preact';
import './anim.css';
import { spark } from './portal';

const f = (n: number) => n.toFixed(1);
const twinkle = (x: number, y: number, r: number, late = '', fill = '#fff') => <path class={`an-twinkle ${late}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x, y, r)} fill={fill} />;

function Defs() {
  return (
    <defs>
      <linearGradient id="mi-stone" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7f7a9c" /><stop offset="0.35" stop-color="#b9b4cc" /><stop offset="0.75" stop-color="#f1eef7" /><stop offset="1" stop-color="#cfcadc" /></linearGradient>
      <linearGradient id="mi-gold" x1="0.85" y1="0" x2="0.15" y2="1"><stop offset="0" stop-color="#fff6c2" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#c2760a" /></linearGradient>
      <linearGradient id="mi-wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a4a22" /><stop offset="0.7" stop-color="#c08448" /><stop offset="1" stop-color="#a06a34" /></linearGradient>
      <linearGradient id="mi-steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8794ad" /><stop offset="0.5" stop-color="#d6dfeb" /><stop offset="1" stop-color="#ffffff" /></linearGradient>
      <linearGradient id="mi-bone" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#bfa988" /><stop offset="0.45" stop-color="#eee0c4" /><stop offset="0.8" stop-color="#fffaec" /><stop offset="1" stop-color="#e6d6b6" /></linearGradient>
      <linearGradient id="mi-horn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4a3a34" /><stop offset="0.6" stop-color="#8f7458" /><stop offset="1" stop-color="#d9c29a" /></linearGradient>
      <linearGradient id="mi-sand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a87840" /><stop offset="0.4" stop-color="#dcb878" /><stop offset="0.75" stop-color="#f8e2ae" /><stop offset="1" stop-color="#d9b070" /></linearGradient>
      <linearGradient id="mi-cave" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#170f22" /><stop offset="0.55" stop-color="#3a1a20" /><stop offset="1" stop-color="#8a3414" /></linearGradient>
      <linearGradient id="mi-crystal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3fa0d8" /><stop offset="1" stop-color="#c8f6ff" /></linearGradient>
      <linearGradient id="mi-blue" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#274f9e" /><stop offset="1" stop-color="#5f93e6" /></linearGradient>
      <radialGradient id="mi-dial" cx="0.6" cy="0.4"><stop offset="0" stop-color="#fffdf2" /><stop offset="1" stop-color="#ecd9b0" /></radialGradient>
      <radialGradient id="mi-shield" cx="0.62" cy="0.36"><stop offset="0" stop-color="#7fb0f5" /><stop offset="0.7" stop-color="#3f74cc" /><stop offset="1" stop-color="#28509c" /></radialGradient>
      <radialGradient id="mi-fire"><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.95" /><stop offset="0.45" stop-color="#ff9a3d" stop-opacity="0.55" /><stop offset="1" stop-color="#ff9a3d" stop-opacity="0" /></radialGradient>
      <radialGradient id="mi-eye"><stop offset="0" stop-color="#fff6c2" /><stop offset="0.4" stop-color="#ff7a3a" /><stop offset="1" stop-color="#d1201a" stop-opacity="0" /></radialGradient>
      <radialGradient id="mi-cyan"><stop offset="0" stop-color="#d6fbff" stop-opacity="0.95" /><stop offset="0.5" stop-color="#6fd6f2" stop-opacity="0.45" /><stop offset="1" stop-color="#6fd6f2" stop-opacity="0" /></radialGradient>
      {[['c', '#2a2038'], ['w', '#4a2412']].map(([k, c]) => (
        <filter id={`mi-out-${k}`} x="-12%" y="-12%" width="124%" height="124%" color-interpolation-filters="sRGB">
          <feMorphology in="SourceAlpha" operator="dilate" radius="1.500" result="d" /><feFlood flood-color={c} result="c" /><feComposite in="c" in2="d" operator="in" result="o" />
          <feMerge><feMergeNode in="o" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      ))}
      <linearGradient id="mi-ivory" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a8927c" /><stop offset="0.4" stop-color="#e2d6c0" /><stop offset="0.78" stop-color="#fffaf0" /><stop offset="1" stop-color="#e6dac4" /></linearGradient>
      <linearGradient id="mi-inner" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f1e6d0" /><stop offset="0.55" stop-color="#c2a888" /><stop offset="1" stop-color="#7a5a48" /></linearGradient>
      <linearGradient id="mi-horn2" x1="44" y1="46" x2="18" y2="4" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#d2b78c" /><stop offset="0.55" stop-color="#86694e" /><stop offset="1" stop-color="#211816" /></linearGradient>
      <clipPath id="mi-ring"><path clip-rule="evenodd" d="M20 104 V56 Q20 17 60 17 Q100 17 100 56 V104 Z M38 104 V58 Q38 38 60 38 Q82 38 82 58 V104 Z" /></clipPath>
      <clipPath id="mi-colo"><path d="M13 38 A47 16.500 0 0 0 107 38 V84 A47 16.500 0 0 1 13 84 Z" /></clipPath>
      <clipPath id="mi-gate"><path d="M38 104 V58 Q38 38 60 38 Q82 38 82 58 V104 Z" /></clipPath>
    </defs>
  );
}

/** Une flamme de torche : deux langues qui dansent. */
function Flame({ x, y, s = 1, delay = 0 }: { x: number; y: number; s?: number; delay?: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <path class="ad-flame" style={{ animationDelay: `${-delay}s` }} d="M-5.500 0 C-8 -7 -2.500 -11 -0.500 -20 C3 -13 8 -8 5.500 0 Z" fill="#ff7a22" />
      <path class="ad-flame" style={{ animationDelay: `${-delay - 0.25}s` }} d="M-3.200 0 C-4.500 -4.500 -1.200 -7 0 -12.500 C1.800 -8 4.500 -5 3.200 0 Z" fill="#ffe27a" />
    </g>
  );
}

/** Un œil en feu : une flamme en goutte, arrondie en dessous (aucune coupure), à quatre couleurs emboîtées, qui tient dans
 *  l'orbite et dont seule la pointe dépasse en penchant vers l'extérieur ; la braise blanche au cœur, deux étincelles.
 *  `side` = -1 (œil gauche) ou 1 (œil droit). */
function EyeFire({ x, y, side }: { x: number; y: number; side: number }) {
  // la même goutte à quatre tailles : base ronde centrée sur l'œil, pointe vers le haut
  const drop = (k: number) => `M0 ${f(4.500 * k)} C${f(-5.500 * k)} ${f(4.500 * k)} ${f(-6.500 * k)} ${f(-0.500 * k)} ${f(-5 * k)} ${f(-4 * k)} C${f(-4 * k)} ${f(-6.500 * k)} ${f(-1.800 * k)} ${f(-8 * k)} ${f(-0.800 * k)} ${f(-14 * k)} C${f(1.800 * k)} ${f(-10 * k)} ${f(6 * k)} ${f(-7 * k)} ${f(6 * k)} ${f(-1.500 * k)} C${f(6 * k)} ${f(2.500 * k)} ${f(3.500 * k)} ${f(4.500 * k)} 0 ${f(4.500 * k)} Z`;
  return (
    <g>
      <circle class="an-glow" cx={x} cy={y - 1} r="11.500" fill="url(#mi-eye)" />
      <g transform={`translate(${x} ${y + 1.500}) rotate(${side * 12})`}>
        <path class="mi-drop mi-f1" d={drop(1)} fill="#e0281a" />
        <path class="mi-drop mi-f2" d={drop(0.760)} fill="#ff7a1e" />
        <path class="mi-drop mi-f3" d={drop(0.520)} fill="#ffd23a" />
        <path class="mi-drop mi-f2" d={drop(0.280)} fill="#fffbe0" />
      </g>
      {[0, 1].map((i) => <circle class="mi-eyespark" style={{ animationDelay: `${-i * 1.050 - (side > 0 ? 0.500 : 0)}s`, '--dx': `${side * (3 + i * 3)}px` } as never} cx={x + side * (i * 2 - 1)} cy={y - 11} r={1.100 - i * 0.200} fill={i ? '#fffbe0' : '#ffb347'} />)}
    </g>
  );
}

// ---------- la tour des Épreuves ----------
function TowerIcon() {
  const OUT = 'url(#mi-out-c)';
  return (
    <>
      <circle class="an-glow" cx="60" cy="11" r="19" fill="url(#mi-cyan)" />
      <g class="mi-bob mi-slow">
        <g transform="translate(60 118) scale(0.92) translate(-60 -118)">
          <g filter={OUT}>
            {/* l'île de roche qui porte la tour : trois facettes, la plus claire à droite */}
            <path d="M22 96 H98 L91 106 L82 104 L75 117 L65 111 L56 128 L46 110 L36 114 L29 102 Z" fill="#6a58a4" />
            <path d="M22 96 H50 L46 110 L36 114 L29 102 Z" fill="#4a3c80" /><path d="M72 96 H98 L91 106 L82 104 L75 117 L65 111 Z" fill="#9c8ad2" />
            <path d="M22 96 H98 L96.500 98.500 H24 Z" fill="#c4b4f0" />
            {/* le socle : deux marches, dessus clair et tranche plus sombre */}
            <path d="M24 97 L29 88 H91 L96 97 Z" fill="#b4afcc" /><path d="M29 88 H91 L93 91.500 H27 Z" fill="#eeebf6" /><path d="M24 97 L29 88 H40 L36 97 Z" fill="#332c58" opacity="0.2" />
            <path d="M32 88 L35 82 H85 L88 88 Z" fill="#b4afcc" /><path d="M35 82 H85 L86.200 84.500 H33.800 Z" fill="#eeebf6" /><path d="M32 88 L35 82 H44 L41.500 88 Z" fill="#332c58" opacity="0.2" />
            {/* le fût, quelques pierres */}
            <path d="M37 82 L40.500 44 H79.500 L83 82 Z" fill="url(#mi-stone)" />
            <g fill="#fff" opacity="0.5"><rect x="67" y="71" width="9" height="4.500" rx="0.800" /><rect x="70" y="50" width="7" height="4.500" rx="0.800" /></g>
            <g fill="#4a4470" opacity="0.2"><rect x="42.500" y="73" width="6" height="4.500" rx="0.800" /><rect x="71" y="57" width="8" height="4.500" rx="0.800" /></g>
            <path d="M37 82 L40.500 44 H53 L50.500 82 Z" fill="#332c58" opacity="0.26" />
            <path d="M79.500 44 L83 82" stroke="#fff" stroke-width="1.500" opacity="0.8" />
            {/* le bandeau d'or */}
            <path d="M39.300 63 H80.700 L81 66 H39 Z" fill="url(#mi-gold)" /><path d="M39.300 63 H80.700" stroke="#fff6c2" stroke-width="0.900" />
            {/* la porte, cerclée d'or */}
            <path d="M50 82 V73 Q50 64 60 64 Q70 64 70 73 V82 Z" fill="url(#mi-gold)" />
            <path d="M52.200 82 V73.200 Q52.200 66.200 60 66.200 Q67.800 66.200 67.800 73.200 V82 Z" fill="url(#mi-wood)" />
            <path d="M60 66.200 V82" stroke="#4a2a12" stroke-width="1.200" /><circle cx="63.200" cy="76" r="1.300" fill="#ffd45c" />
            {/* la fenêtre */}
            <path d="M55 60 V54 Q55 48 60 48 Q65 48 65 54 V60 Z" fill="#4a4470" />
            <path class="mi-flicker" d="M56.600 60 V54.200 Q56.600 49.800 60 49.800 Q63.400 49.800 63.400 54.200 V60 Z" fill="#ffe66a" />
            {/* les bannières : étroites, elles s'arrêtent au-dessus du bandeau */}
            {[42.500, 69.500].map((x, i) => (
              <g class="mi-sway" style={{ transformOrigin: `${x + 4}px 45px`, animationDelay: `${-i * 1.3}s` }}>
                <path d={`M${x} 45 H${x + 8} V60 L${x + 4} 56.500 L${x} 60 Z`} fill="url(#mi-blue)" />
                <path d={`M${x} 45 H${x + 8} V47.500 H${x} Z`} fill="#ffd45c" /><circle cx={x + 4} cy="52" r="1.700" fill="#ffd45c" />
              </g>
            ))}
            {/* l'encorbellement et ses petites arches */}
            <path d="M33 44.500 L35.500 37.500 H84.500 L87 44.500 Z" fill="#9f9abc" /><path d="M35.500 37.500 H84.500 L85.500 40 H34.500 Z" fill="#fff" opacity="0.45" />
            <g fill="#3a3358">{[38, 45.500, 53, 60.500, 68, 75.500].map((x) => <path d={`M${x} 44.500 v-2 q0 -2.200 2.300 -2.200 q2.300 0 2.300 2.200 v2 Z`} />)}</g>
            {/* les créneaux, coiffés d'or, bleuis par le cristal */}
            <path d="M31 38 V24 h10 v6 h7 v-6 h8.500 v6 h7 v-6 h8.500 v6 h7 v-6 h10 V38 Z" fill="url(#mi-stone)" />
            <path d="M31 38 V24 h10 v6 h4 V38 Z" fill="#332c58" opacity="0.26" />
            <path d="M48 30 h24 V38 H48 Z" fill="#6fd6f2" opacity="0.3" />
            <g fill="url(#mi-gold)"><rect x="30.300" y="22.300" width="11.400" height="3.200" rx="1" /><rect x="47.300" y="22.300" width="9.900" height="3.200" rx="1" /><rect x="62.800" y="22.300" width="9.900" height="3.200" rx="1" /><rect x="78.300" y="22.300" width="11.400" height="3.200" rx="1" /></g>
            <path d="M89 24 V38" stroke="#fff" stroke-width="1.400" opacity="0.8" />
          </g>
          <circle class="an-glow" cx="60" cy="54" r="11" fill="url(#mi-fire)" opacity="0.8" />
          {[[40, 116, 0], [80, 112, 1.1]].map(([x, y, d]) => <path class="mi-pebble" style={{ animationDelay: `${-d!}s` }} d={`M${x} ${y} l3 2 l-1 3 l-3 -1 Z`} fill="#6a58a4" />)}
        </g>
      </g>
      {/* le cristal, nettement détaché au-dessus des créneaux */}
      <g class="mi-bob">
        <g filter={OUT}>
          <path d="M60 -2 L68 9.500 L60 22 L52 9.500 Z" fill="url(#mi-crystal)" />
          <path d="M60 -2 L68 9.500 H60 Z" fill="#e9fdff" /><path d="M60 9.500 H68 L60 22 Z" fill="#7fdcf5" /><path d="M60 -2 L52 9.500 H60 Z" fill="#a6ecfb" /><path d="M52 9.500 H60 V22 Z" fill="#3fa0d8" />
          <path d="M62 2.500 L65.200 7.500" stroke="#fff" stroke-width="1.400" stroke-linecap="round" />
        </g>
      </g>
      {twinkle(42, 10, 5)}{twinkle(80, 15, 4, 'an-late')}{twinkle(74, 1, 3, 'an-later')}
    </>
  );
}

// ---------- la boussole des Missions ----------
function CompassIcon() {
  const OUT = 'url(#mi-out-w)';
  const C = { x: 60, y: 66 };
  return (
    <>
      <ellipse cx="60" cy="113" rx="34" ry="5" fill="#000" opacity="0.26" />
      <g transform="rotate(-10 60 66)">
        <g filter={OUT}>
          {/* l'anneau et son attache */}
          <circle cx="60" cy="13" r="7.500" fill="none" stroke="#c2760a" stroke-width="6" /><circle cx="60" cy="13" r="7.500" fill="none" stroke="#ffd45c" stroke-width="3.400" />
          <path d="M53 20 H67 L65.500 29 H54.500 Z" fill="url(#mi-gold)" /><path d="M53.500 23 H66.500" stroke="#a8650a" stroke-width="1.400" />
          {/* le boîtier : une lunette épaisse, quatre rivets */}
          <circle cx={C.x} cy={C.y} r="43" fill="url(#mi-gold)" />
          <path d="M60 23 A43 43 0 0 1 103 66 A44 44 0 0 0 60 26 Z" fill="#fff" opacity="0.35" />
          {[45, 135, 225, 315].map((a) => { const r = (a * Math.PI) / 180; return <g><circle cx={f(C.x + Math.cos(r) * 39.500)} cy={f(C.y + Math.sin(r) * 39.500)} r="2.200" fill="#a8650a" /><circle cx={f(C.x + Math.cos(r) * 39.500 + 0.500)} cy={f(C.y + Math.sin(r) * 39.500 - 0.500)} r="1.300" fill="#fff6c2" /></g>; })}
          <circle cx={C.x} cy={C.y} r="35.500" fill="#a8650a" /><circle cx={C.x} cy={C.y} r="34" fill="#ffe28a" />
          {/* le cadran, dans l'ombre de la lunette du côté de la lumière */}
          <circle cx={C.x} cy={C.y} r="32" fill="url(#mi-dial)" />
          <path d="M60 34 A32 32 0 0 1 92 66 A35 35 0 0 0 60 38.500 Z" fill="#6b4a22" opacity="0.2" />
          {/* la rose des vents */}
          <g fill="#dcc296">{[45, 135, 225, 315].map((a) => <path transform={`rotate(${a} 60 66)`} d="M60 50 L63 66 L60 82 L57 66 Z" />)}</g>
          <g>{[0, 90, 180, 270].map((a) => <g transform={`rotate(${a} 60 66)`}><path d="M60 41 L64 66 H60 Z" fill="#b8925a" /><path d="M60 41 L56 66 H60 Z" fill="#8f6c3c" /></g>)}</g>
          {Array.from({ length: 12 }, (_, i) => <path transform={`rotate(${i * 30} 60 66)`} d={i % 3 === 0 ? 'M60 35.500 V40.500' : 'M60 35.500 V38'} stroke="#6b4a22" stroke-width={i % 3 === 0 ? 2.200 : 1.400} stroke-linecap="round" />)}
        </g>
        {/* l'aiguille, qui cherche le nord : rouge d'un côté, bleu acier de l'autre */}
        <g class="mi-needle" style={{ transformOrigin: '60px 66px' }}>
          <path d="M61.500 46 L67 68 L61.500 90 L56 68 Z" fill="#3a2a1a" opacity="0.22" />
          <g filter={OUT}>
            <path d="M60 43 L65.500 66 H60 Z" fill="#f4705e" /><path d="M60 43 L54.500 66 H60 Z" fill="#b8352f" />
            <path d="M60 89 L65.500 66 H60 Z" fill="#8fb0dc" /><path d="M60 89 L54.500 66 H60 Z" fill="#4f74a8" />
          </g>
        </g>
        <circle cx={C.x} cy={C.y} r="4.800" fill="#a8650a" /><circle cx={C.x} cy={C.y} r="3.500" fill="url(#mi-gold)" /><circle cx="61" cy="65" r="1.200" fill="#fff" />
        {/* le verre */}
        <path d="M66 39 A28 28 0 0 1 87.500 60" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.5" />
      </g>
      {twinkle(98, 36, 5.500)}{twinkle(20, 94, 4, 'an-late')}
    </>
  );
}

// ---------- la porte des Donjons ----------
function GateIcon() {
  const OUT = 'url(#mi-out-c)';
  const cuts = [180, 205, 230, 256, 284, 310, 335, 360]; // limites des claveaux, en degrés
  const P = (a: number, rx: number, ry: number) => `${f(60 + Math.cos((a * Math.PI) / 180) * rx)} ${f(58 + Math.sin((a * Math.PI) / 180) * ry)}`;
  return (
    <>
      <ellipse cx="60" cy="113" rx="50" ry="5.500" fill="#000" opacity="0.28" />
      <g filter={OUT}>
        {/* le seuil */}
        <path d="M8 113 L16 103 H104 L112 113 Z" fill="#b4afcc" /><path d="M16 103 H104 L107 107 H13 Z" fill="#eeebf6" /><path d="M8 113 L16 103 H30 L24 113 Z" fill="#332c58" opacity="0.2" />
        {/* l'arche de pierre */}
        <path d="M20 104 V56 Q20 17 60 17 Q100 17 100 56 V104 Z" fill="url(#mi-stone)" />
        {/* les claveaux : des aplats de deux tons, un sur deux */}
        <g clip-path="url(#mi-ring)">
          {cuts.slice(0, -1).map((a, i) => i === 3 ? null : <path d={`M${P(a, 18, 16)} L${P(a, 52, 52)} L${P(cuts[i + 1]!, 52, 52)} L${P(cuts[i + 1]!, 18, 16)} Z`} fill={i % 2 ? '#fff' : '#3a3358'} opacity={i % 2 ? 0.3 : 0.14} />)}
          {/* les assises des jambages */}
          <g fill="#3a3358" opacity="0.14"><rect x="20" y="72" width="18" height="11" /><rect x="82" y="83" width="18" height="11" /><rect x="20" y="94" width="18" height="10" /></g>
          <g fill="#fff" opacity="0.3"><rect x="20" y="83" width="18" height="11" /><rect x="82" y="72" width="18" height="11" /></g>
          <rect x="82" y="58" width="18" height="46" fill="#3a3358" opacity="0.1" />
          {/* la chaleur des torches sur la pierre */}
          <circle cx="29" cy="48" r="17" fill="url(#mi-fire)" opacity="0.75" /><circle cx="91" cy="48" r="17" fill="url(#mi-fire)" opacity="0.75" />
        </g>
        <path d="M20 104 V56 Q20 28 42 19.500 L46 40 Q38 46 38 58 V104 Z" fill="#3a3358" opacity="0.2" />
        <path d="M100 104 V56 Q100 30 80 20.500" fill="none" stroke="#fff" stroke-width="1.600" opacity="0.75" />
        {/* le fond : du noir en haut au rougeoiement en bas, des marches en silhouette, la herse à demi levée */}
        <path d="M38 104 V58 Q38 38 60 38 Q82 38 82 58 V104 Z" fill="url(#mi-cave)" />
        <g clip-path="url(#mi-gate)">
          <ellipse class="an-glow" cx="60" cy="108" rx="28" ry="20" fill="url(#mi-fire)" />
          <path d="M38 104 V99 H45 V95 H52 V91 H68 V95 H75 V99 H82 V104 Z" fill="#170f22" opacity="0.92" />
          <path d="M52 91 H68 M45 95 H52 M68 95 H75" stroke="#ff9a3d" stroke-width="0.900" opacity="0.7" />
          <g fill="#2f2c3c">
            {[44.500, 52, 59.500, 67, 74.500].map((x) => <path d={`M${x - 1.700} 36 H${x + 1.700} V82 L${x} 87.500 L${x - 1.700} 82 Z`} />)}
            <rect x="38" y="50" width="44" height="3.400" /><rect x="38" y="64" width="44" height="3.400" /><rect x="38" y="77" width="44" height="3.400" />
          </g>
          <g stroke="#8a86a0" stroke-width="0.900" opacity="0.8">{[44.500, 52, 59.500, 67, 74.500].map((x) => <path d={`M${x + 1} 38 V81`} />)}</g>
        </g>
        <path d="M38 104 V58 Q38 38 60 38 Q82 38 82 58 V104" fill="none" stroke="#4f4a68" stroke-width="2.200" />
        {/* la clef de voûte et sa gemme */}
        <path d="M52.500 17.200 H67.500 L65 39 H55 Z" fill="#f6f3fb" /><path d="M52.500 17.200 H60 V39 H55 Z" fill="#3a3358" opacity="0.14" />
        <path d="M60 22 L64.800 29 L60 36 L55.200 29 Z" fill="#b81f2e" /><path class="mi-flicker" d="M60 22 L64.800 29 H60 Z" fill="#ff8a7a" /><path d="M60 29 H64.800 L60 36 Z" fill="#e23a44" />
        {/* les appliques de fer et leurs torches */}
        {[29, 91].map((x) => (
          <g>
            <path d={`M${x - 4.500} 72 H${x + 4.500} L${x + 3} 77 H${x - 3} Z`} fill="#3a3648" /><rect x={x - 1.700} y="60" width="3.400" height="13" rx="1" fill="#6b4420" />
            <path d={`M${x - 6} 53.500 H${x + 6} L${x + 4} 61 H${x - 4} Z`} fill="#3a3648" /><path d={`M${x - 6} 53.500 H${x + 6} L${x + 5.400} 55.700 H${x - 5.400} Z`} fill="#8a86a0" />
          </g>
        ))}
      </g>
      <circle class="an-glow" cx="29" cy="46" r="13" fill="url(#mi-fire)" /><circle class="an-glow an-late" cx="91" cy="46" r="13" fill="url(#mi-fire)" />
      <Flame x={29} y={54} s={1.1} /><Flame x={91} y={54} s={1.1} delay={0.4} />
      {[[50, 98, 0], [66, 100, 1.4], [58, 96, 2.6]].map(([x, y, d]) => <circle class="ts-ember" style={{ animationDelay: `${-d!}s` }} cx={x} cy={y} r="1.500" fill="#ffd27a" />)}
    </>
  );
}

// ---------- le crâne du Boss du jour ----------
function SkullIcon() {
  const OUT = 'url(#mi-out-w)';
  /** Une corne fine et pointue, de l'ivoire sombre au noir de la pointe ; `light` = le bord qui prend la lumière. */
  const horn = (light: string) => (
    <>
      <path d="M46 38 C34 33 21 37 18 25 C16 17 17.500 9 20.500 1 C8 11 3 27 10 39.500 C16.500 50.500 30 53 41 51 Z" fill="url(#mi-horn2)" />
      <path d={light} fill="none" stroke="#fff" stroke-width="1.800" stroke-linecap="round" opacity="0.5" />
    </>
  );
  return (
    <>
      <ellipse cx="60" cy="113" rx="32" ry="5" fill="#000" opacity="0.3" />
      <g class="mi-bob mi-slow">
        <g filter={OUT}>
          {horn('M43.500 38.500 C33 35 22 37 19.500 26 C18.500 21 18.500 16 19.500 11')}
          <g transform="translate(120 0) scale(-1 1)">{horn('M17.500 6 C8.500 15 5.500 28 11.500 38.500')}</g>
          {/* le crâne : voûte large, pommettes saillantes, mâchoire étroite */}
          <path d="M60 22 C82 22 95 36 94 55 C93.700 62 91 68 87 72 L90 78 L82.500 83 L81 93 H39 L37.500 83 L30 78 L33 72 C29 68 26.300 62 26 55 C25 36 38 22 60 22 Z" fill="url(#mi-bone)" />
          <path d="M60 22 C38 22 25 36 26 55 C26.300 62 29 68 33 72 L30 78 L37.500 83 L39 93 H47 C45.500 86 45 80 42 75 C38 68 36 61 36 53 C36 40 44 28 60 22 Z" fill="#5a3f4a" opacity="0.2" />
          <path d="M87 72 C91 68 93.700 62 94 55 C94.500 45 91 36 84 30" fill="none" stroke="#fff" stroke-width="1.500" opacity="0.75" />
          {/* le front accroche la lumière, à droite */}
          <path d="M62 27.500 C70 27 78 30 83 36" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity="0.6" />
          {/* les orbites, en colère */}
          <path d="M33 50 L56.500 59 L54.500 72.500 C47 76.500 38.500 74 35 65 Z" fill="#1f0e17" /><path d="M87 50 L63.500 59 L65.500 72.500 C73 76.500 81.500 74 85 65 Z" fill="#1f0e17" />
          <path d="M36.500 55 L54 61.500 L52.500 71 C47 73.500 40.500 71.500 38 65 Z" fill="#7a1418" opacity="0.85" /><path d="M83.500 55 L66 61.500 L67.500 71 C73 73.500 79.500 71.500 82 65 Z" fill="#7a1418" opacity="0.85" />
          {/* le nez, l'ombre sous les pommettes, une fêlure */}
          <path d="M60 71 L54 85 Q60 81.500 66 85 Z" fill="#1f0e17" />
          <path d="M31 78 L37.500 83 L43 81 Q38 81 31 78 Z M89 78 L82.500 83 L77 81 Q82 81 89 78 Z" fill="#5a3f4a" opacity="0.3" />
          <path d="M57 23.500 L54 31.500 L59 37 L56 44" fill="none" stroke="#8a7658" stroke-width="1.400" stroke-linecap="round" stroke-linejoin="round" />
          {/* les dents : quatre incisives entre deux crocs, sous l'ombre courbe de la mâchoire */}
          <path d="M39 89 Q60 94 81 89 V93 H39 Z" fill="#4a3438" opacity="0.5" />
          <path d="M40.500 92 h7.500 l-3.800 15 Z M72 92 h7.500 l-3.700 15 Z" fill="#fffaec" /><path d="M40.500 92 h3.700 v15 Z M72 92 h3.700 v15 Z" fill="#bfa988" opacity="0.6" />
          {[49, 54.700, 60.400, 66.100].map((x) => <g><rect x={x} y="92" width="4.900" height="9" rx="1.800" fill="#fffaec" /><rect x={x} y="92" width="1.700" height="9" rx="0.800" fill="#bfa988" opacity="0.6" /></g>)}
        </g>
        {/* les yeux : deux brasiers qui débordent des orbites */}
        <EyeFire x={45} y={66} side={-1} /><EyeFire x={75} y={66} side={1} />
      </g>
      {[[30, 104, 0, '#ffb09a'], [90, 102, 1.2, '#ffd27a'], [50, 110, 2.3, '#ffd27a'], [72, 108, 3.1, '#ffb09a']].map(([x, y, d, c]) => <circle class="ts-ember" style={{ animationDelay: `${-(d as number)}s` }} cx={x} cy={y} r="1.700" fill={c as string} />)}
    </>
  );
}

// ---------- le bouclier et les épées de l'Arène ----------
/** Une épée dessinée pointe en haut, autour du point où les deux lames se croisent. */
function Sword({ angle, reverse }: { angle: number; reverse?: boolean }) {
  return (
    <g class="mi-clash" style={{ transformOrigin: '60px 56px', animationDirection: reverse ? 'reverse' : 'normal' }}>
      <g transform={`translate(60 56) rotate(${angle})`}>
        <g filter="url(#mi-out-c)">
          {/* la lame : pointe en losange, pan clair du côté de la lumière */}
          <path d="M-5.500 -40 L0 -53 L5.500 -40 V25 H-5.500 Z" fill="#8c9bb5" />
          <path d="M0 -53 L5.500 -40 V25 H0 Z" fill="#ffffff" />
          <path d="M-1 -36 H1 V21 H-1 Z" fill="#5f6c86" opacity="0.5" />
          {/* la garde : courte et fine */}
          <rect x="-11" y="24" width="22" height="5" rx="2.500" fill="url(#mi-gold)" /><path d="M-9 25.300 H9" stroke="#fff6c2" stroke-width="1" stroke-linecap="round" />
          <circle cx="0" cy="26.500" r="2.300" fill="#b81f2e" /><circle cx="0.600" cy="25.900" r="0.900" fill="#ff8a7a" />
          {/* la fusée et son anneau, le pommeau */}
          <rect x="-3.400" y="29" width="6.800" height="13" rx="1.500" fill="url(#mi-wood)" /><rect x="-3.800" y="34.500" width="7.600" height="2.200" rx="1" fill="url(#mi-gold)" />
          <circle cx="0" cy="45.500" r="4.800" fill="url(#mi-gold)" /><circle cx="1.200" cy="44.400" r="1.400" fill="#fff" opacity="0.85" />
        </g>
        <path class="mi-glint" d={spark(0, 10, 5.500)} fill="#fff" />
      </g>
    </g>
  );
}

function SwordsIcon() {
  return (
    <>
      <ellipse cx="60" cy="114" rx="38" ry="5" fill="#000" opacity="0.26" />
      <g filter="url(#mi-out-c)">
        {/* le bouclier : cerclé d'or, bombé (clair en haut à droite, sombre en bas à gauche), six rivets, un emblème */}
        <circle cx="60" cy="62" r="42" fill="url(#mi-gold)" /><circle cx="60" cy="62" r="35.500" fill="#a8650a" /><circle cx="60" cy="62" r="34" fill="url(#mi-shield)" />
        <path d="M30 76 A34 34 0 0 0 78 91 A40 40 0 0 1 28 68 Z" fill="#16306e" opacity="0.35" />
        <path d="M66 31 A31 31 0 0 1 90.500 54" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.4" />
        {[0, 60, 120, 180, 240, 300].map((a) => { const r = ((a + 30) * Math.PI) / 180; return <g><circle cx={f(60 + Math.cos(r) * 38.800)} cy={f(62 + Math.sin(r) * 38.800)} r="2.400" fill="#a8650a" /><circle cx={f(60 + Math.cos(r) * 38.800 + 0.500)} cy={f(62 + Math.sin(r) * 38.800 - 0.500)} r="1.500" fill="#fff6c2" /></g>; })}
        <path d="M60 78 l7 8 l-7 8 l-7 -8 Z" fill="url(#mi-gold)" /><path d="M60 81.500 l3.800 4.500 l-3.800 4.500 l-3.800 -4.500 Z" fill="#28509c" />
      </g>
      <Sword angle={-32} /><Sword angle={32} reverse />
      {/* l'éclat du choc, là où les lames se croisent */}
      <g class="mi-spark" style={{ transformOrigin: '60px 56px' }}><path d={spark(60, 56, 13)} fill="#fff" /><path d={spark(60, 56, 7)} fill="#ffe27a" /></g>
    </>
  );
}

// ---------- le Colisée ----------
function ColosseumIcon() {
  const E = { x: 60, rx: 47, ry: 16.500 };
  const rows: [number, number][] = [[50, 9.500], [65.500, 10.500], [82, 11.500]]; // base de l'arcade (au centre), hauteur
  const flags: [number, number][] = [[27, 0], [60, 0.6], [93, 1.2]];
  const backY = (x: number) => 38 - E.ry * Math.sqrt(Math.max(0, 1 - ((x - E.x) / E.rx) ** 2));
  const front = (y: number, rx = E.rx, ry = E.ry) => `M${E.x - rx} ${y} A${rx} ${ry} 0 0 0 ${E.x + rx} ${y}`;
  return (
    <>
      <ellipse cx="60" cy="108" rx="54" ry="7" fill="#000" opacity="0.26" />
      <g filter="url(#mi-out-w)">
        {/* le socle : deux marches */}
        <path d={`${front(92, 55, 19)} V97 A55 19 0 0 1 5 97 Z`} fill="#b8a48c" /><path d={`${front(92, 55, 19)}`} fill="none" stroke="#e9ddc8" stroke-width="2" />
        <path d={`${front(87, 51, 17.800)} V92 A51 17.800 0 0 1 9 92 Z`} fill="#d2c2a8" /><path d={`${front(87, 51, 17.800)}`} fill="none" stroke="#fffaf0" stroke-width="2" />
        {/* l'intérieur, creusé : la paroi du fond (claire à gauche, dans l'ombre à droite), deux gradins, la piste */}
        <ellipse cx={E.x} cy="38" rx={E.rx} ry={E.ry} fill="#fffaf0" />
        <ellipse cx={E.x} cy="39" rx="41" ry="13.500" fill="url(#mi-inner)" />
        <ellipse cx={E.x} cy="43.500" rx="35" ry="10.500" fill="#b89a78" /><path d="M25 43.500 A35 10.500 0 0 1 95 43.500" fill="none" stroke="#f1e6d0" stroke-width="1.400" />
        <ellipse cx={E.x} cy="46.500" rx="29" ry="8.500" fill="#9c7e60" /><path d="M31 46.500 A29 8.500 0 0 1 89 46.500" fill="none" stroke="#e2d2b6" stroke-width="1.400" />
        <ellipse cx={E.x} cy="49" rx="23" ry="6.500" fill="#f3dfa6" /><ellipse cx="55" cy="49.500" rx="12" ry="3.200" fill="#fff6d2" opacity="0.8" />
        {/* les oriflammes, plantées sur le rebord du fond */}
        {flags.map(([x, d]) => (
          <g><path d={`M${x} ${f(backY(x) + 3)} V${f(backY(x) - 14)}`} stroke="#5a3418" stroke-width="1.800" stroke-linecap="round" /><path class="bd-flag" style={{ transformOrigin: `${x}px ${f(backY(x) - 10)}px`, animationDelay: `${-d}s` }} d={`M${x} ${f(backY(x) - 14)} q8 -1 14 3.500 q-6 4 -14 4.500 Z`} fill="#e0463c" /></g>
        ))}
        {/* la façade : trois étages, sept grandes arcades chacun, une porte au milieu */}
        <path d={`${front(38)} V84 A${E.rx} ${E.ry} 0 0 1 ${E.x - E.rx} 84 Z`} fill="url(#mi-ivory)" />
        <g clip-path="url(#mi-colo)">
          {[55.500, 71].map((y) => <g><path d={front(y)} fill="none" stroke="#8a6248" stroke-width="1.600" opacity="0.55" /><path d={front(y + 1.800)} fill="none" stroke="#fffaf0" stroke-width="1.200" opacity="0.7" /></g>)}
          {rows.map(([base, h], row) => Array.from({ length: 7 }, (_, i) => {
            const door = row === 2 && i === 3;
            const t = (Math.PI * (i + 1)) / 8, x = E.x - E.rx * Math.cos(t), yb = base + E.ry * Math.sin(t) + (door ? 2 : 0);
            const w = Math.max(3, (door ? 12 : 9) * Math.sin(t)), hh = door ? h + 4 : h, top = yb - hh + w / 2;
            return (
              <g>
                <path d={`M${f(x - w / 2)} ${f(yb)} V${f(top)} A${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(x + w / 2)} ${f(top)} V${f(yb)} Z`} fill="#3f2218" />
                <path d={`M${f(x - w / 2)} ${f(yb)} V${f(top)} A${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(x)} ${f(top - w / 2)} A${f(w * 0.34)} ${f(w / 2)} 0 0 0 ${f(x - w * 0.16)} ${f(top)} V${f(yb)} Z`} fill="#8a5a40" opacity="0.8" />
              </g>
            );
          }))}
          {/* le côté gauche dans l'ombre */}
          <path d="M13 38 H40 V104 H13 Z" fill="#6b3a2a" opacity="0.14" />
        </g>
        {/* le rebord du haut, épais et clair */}
        <path d={`${front(38)} L${E.x + E.rx} 42 A${E.rx} ${E.ry} 0 0 1 ${E.x - E.rx} 42 Z`} fill="#fffaf0" />
        <path d={front(42)} fill="none" stroke="#8a6248" stroke-width="1" opacity="0.45" />
      </g>
      {[[52, 49, 0], [68, 50, 1.6], [60, 47, 3]].map(([x, y, d]) => <circle class="ts-dust" style={{ animationDelay: `${-d!}s` }} cx={x} cy={y} r="1.500" fill="#fff" />)}
      {twinkle(102, 30, 5)}{twinkle(16, 64, 3.500, 'an-late')}
    </>
  );
}

const ICONS: Record<string, () => ComponentChildren> = { tower: TowerIcon, missions: CompassIcon, dungeons: GateIcon, dailyBoss: SkullIcon, arena: SwordsIcon, defense: ColosseumIcon };

export function hasModeIcon(kind: string): boolean {
  return kind in ICONS;
}

/** Le picto animé d'un mode. `class` s'ajoute à `icon mode-icon` (les tuiles règlent la taille par le style). */
export function ModeIcon({ kind, size = 86, class: cls = '' }: { kind: string; size?: number; class?: string }) {
  const Draw = ICONS[kind];
  if (!Draw) return null;
  return (
    <svg class={`icon mode-icon mode-icon-${kind} ${cls}`} width={size} height={size} viewBox="0 0 120 120" aria-hidden="true">
      <Defs />
      <Draw />
    </svg>
  );
}
