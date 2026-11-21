// Les pictos des six modes de l'Aventure, dessinés par le code et animés, dans le même trait que le décor de l'onglet :
// volumes en dégradés, lumière venue du haut à droite, un seul contour autour de chaque objet (filtre de `.mi-body`).
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

// ---------- la tour des Épreuves ----------
function TowerIcon() {
  return (
    <>
      <circle class="an-glow" cx="60" cy="13" r="21" fill="url(#mi-cyan)" />
      <g class="mi-bob mi-slow">
        <g class="mi-body">
          {/* le rocher qui porte la tour, suspendu au-dessus des nuages */}
          <path d="M22 96 H98 L88 104 L80 102 L72 112 L62 106 L54 117 L46 105 L36 108 L30 100 Z" fill="#5a4a8c" />
          <path d="M98 96 L88 104 L80 102 L72 112 L62 106 L62 96 Z" fill="#8f7fc4" /><path d="M22 96 H98 L96 98.500 H25 Z" fill="#b9a8ea" />
          {/* le socle, en deux marches */}
          <path d="M24 97 L29 88 H91 L96 97 Z" fill="url(#mi-stone)" /><path d="M29 88 H91 L93 91.500 H27 Z" fill="#fff" opacity="0.55" />
          <path d="M32 88 L35 82 H85 L88 88 Z" fill="url(#mi-stone)" /><path d="M35 82 H85 L86.200 84.500 H33.800 Z" fill="#fff" opacity="0.55" />
          {/* le fût, ses pierres */}
          <path d="M37 82 L40.500 44 H79.500 L83 82 Z" fill="url(#mi-stone)" />
          <g fill="#fff" opacity="0.5"><rect x="66" y="70" width="9" height="4.500" rx="0.800" /><rect x="70" y="52" width="7" height="4.500" rx="0.800" /></g>
          <g fill="#4a4470" opacity="0.2"><rect x="43" y="74" width="8" height="4.500" rx="0.800" /><rect x="44" y="50" width="6" height="4.500" rx="0.800" /><rect x="71" y="61" width="8" height="4.500" rx="0.800" /></g>
          <g stroke="#5f5a80" stroke-width="1" stroke-linecap="round" opacity="0.55"><path d="M40 78.500 H51 M71 78.500 H82 M41 69.500 H49 M66 69.500 H82 M42 56 H50 M70 56.500 H80 M54 47.500 H66" /></g>
          <path d="M37 82 L40.500 44 H53 L50.500 82 Z" fill="#332c58" opacity="0.26" />
          <path d="M79.500 44 L83 82" stroke="#fff" stroke-width="1.500" opacity="0.8" />
          {/* le bandeau d'or */}
          <path d="M39.300 63 H80.700 L81 66 H39 Z" fill="url(#mi-gold)" /><path d="M39.300 63 H80.700" stroke="#fff6c2" stroke-width="0.900" />
          {/* la porte, cerclée d'or */}
          <path d="M50 82 V72 Q50 62.500 60 62.500 Q70 62.500 70 72 V82 Z" fill="url(#mi-gold)" />
          <path d="M52.200 82 V72.200 Q52.200 64.700 60 64.700 Q67.800 64.700 67.800 72.200 V82 Z" fill="url(#mi-wood)" />
          <path d="M52.200 73.500 H67.800 M60 64.700 V82" stroke="#4a2a12" stroke-width="1.200" /><circle cx="63.200" cy="76" r="1.300" fill="#ffd45c" />
          {/* la fenêtre allumée */}
          <path d="M55.300 59 V53.500 Q55.300 48 60 48 Q64.700 48 64.700 53.500 V59 Z" fill="#4a4470" />
          <path class="mi-flicker" d="M56.800 59 V53.700 Q56.800 49.600 60 49.600 Q63.200 49.600 63.200 53.700 V59 Z" fill="#ffd98a" /><path d="M60 49.600 V59" stroke="#4a4470" stroke-width="0.900" />
          {/* les bannières */}
          {[41.500, 68.500].map((x, i) => (
            <g class="mi-sway" style={{ transformOrigin: `${x + 5}px 45px`, animationDelay: `${-i * 1.3}s` }}>
              <path d={`M${x} 45 H${x + 10} V66 L${x + 5} 61.500 L${x} 66 Z`} fill="url(#mi-blue)" />
              <path d={`M${x} 45 H${x + 10} V47.800 H${x} Z`} fill="#ffd45c" /><path d={`M${x + 5} 51 l2.800 3.800 l-2.800 3.800 l-2.800 -3.800 Z`} fill="#ffd45c" />
            </g>
          ))}
          {/* l'encorbellement et ses petites arches */}
          <path d="M33 44.500 L35.500 37.500 H84.500 L87 44.500 Z" fill="#9f9abc" /><path d="M35.500 37.500 H84.500 L85.500 40 H34.500 Z" fill="#fff" opacity="0.45" />
          <g fill="#3a3358">{[38, 45.500, 53, 60.500, 68, 75.500].map((x) => <path d={`M${x} 44.500 v-2 q0 -2.200 2.300 -2.200 q2.300 0 2.300 2.200 v2 Z`} />)}</g>
          {/* les créneaux, coiffés d'or */}
          <path d="M31 38 V24 h10 v6 h7 v-6 h8.500 v6 h7 v-6 h8.500 v6 h7 v-6 h10 V38 Z" fill="url(#mi-stone)" />
          <path d="M31 38 V24 h10 v6 h4 V38 Z" fill="#332c58" opacity="0.26" />
          <g fill="url(#mi-gold)"><rect x="30.300" y="22.300" width="11.400" height="3.200" rx="1" /><rect x="47.300" y="22.300" width="9.900" height="3.200" rx="1" /><rect x="62.800" y="22.300" width="9.900" height="3.200" rx="1" /><rect x="78.300" y="22.300" width="11.400" height="3.200" rx="1" /></g>
          <path d="M35 33.500 h5 M50 34.500 h6 M66 33.500 h5 M80 34.500 h5" stroke="#5f5a80" stroke-width="1" stroke-linecap="round" opacity="0.55" />
          <path d="M89 24 V38" stroke="#fff" stroke-width="1.400" opacity="0.8" />
        </g>
        {[[40, 112, 0], [78, 110, 1.1]].map(([x, y, d]) => <path class="mi-pebble" style={{ animationDelay: `${-d!}s` }} d={`M${x} ${y} l3 2 l-1 3 l-3 -1 Z`} fill="#5a4a8c" />)}
      </g>
      {/* le cristal qui flotte au-dessus */}
      <g class="mi-bob">
        <g class="mi-body">
          <path d="M60 0 L68.500 12 L60 25 L51.500 12 Z" fill="url(#mi-crystal)" />
          <path d="M60 0 L68.500 12 H60 Z" fill="#e9fdff" /><path d="M60 12 H68.500 L60 25 Z" fill="#7fdcf5" /><path d="M60 0 L51.500 12 H60 Z" fill="#a6ecfb" /><path d="M51.500 12 H60 V25 Z" fill="#3fa0d8" />
          <path d="M62 4.500 L65.500 10" stroke="#fff" stroke-width="1.400" stroke-linecap="round" />
        </g>
      </g>
      {twinkle(42, 12, 5)}{twinkle(80, 17, 4, 'an-late')}{twinkle(73, 3, 3, 'an-later')}
    </>
  );
}

// ---------- la boussole des Missions ----------
function CompassIcon() {
  const C = { x: 60, y: 66 };
  return (
    <>
      <ellipse cx="60" cy="112" rx="34" ry="5" fill="#000" opacity="0.26" />
      <g transform="rotate(-10 60 66)">
        <g class="mi-body">
          {/* l'anneau et le col */}
          <circle cx="60" cy="14" r="7.500" fill="none" stroke="#c2760a" stroke-width="6" /><circle cx="60" cy="14" r="7.500" fill="none" stroke="#ffd45c" stroke-width="3.400" />
          <rect x="54" y="20" width="12" height="9" rx="2.500" fill="url(#mi-gold)" /><path d="M54 24 H66" stroke="#a8650a" stroke-width="1.2" />
          {/* le boîtier */}
          <circle cx={C.x} cy={C.y} r="43" fill="url(#mi-gold)" />
          {Array.from({ length: 24 }, (_, i) => { const a = (i / 24) * Math.PI * 2; return <path d={`M${f(C.x + Math.cos(a) * 38.500)} ${f(C.y + Math.sin(a) * 38.500)} L${f(C.x + Math.cos(a) * 41.500)} ${f(C.y + Math.sin(a) * 41.500)}`} stroke="#a8650a" stroke-width="1.6" stroke-linecap="round" opacity="0.6" />; })}
          <circle cx={C.x} cy={C.y} r="36.500" fill="#a8650a" /><circle cx={C.x} cy={C.y} r="35" fill="#ffe28a" />
          {/* le cadran */}
          <circle cx={C.x} cy={C.y} r="33" fill="url(#mi-dial)" />
          <path d="M60 33 A33 33 0 0 0 27 66 A34 34 0 0 1 60 36 Z" fill="#8a6a3a" opacity="0.18" />
          {/* la rose des vents */}
          <g fill="#d9bd8c">{[45, 135, 225, 315].map((a) => <path transform={`rotate(${a} 60 66)`} d="M60 49 L63 66 L60 83 L57 66 Z" />)}</g>
          <g>{[0, 90, 180, 270].map((a) => <g transform={`rotate(${a} 60 66)`}><path d="M60 40 L64 66 H60 Z" fill="#b8925a" /><path d="M60 40 L56 66 H60 Z" fill="#8f6c3c" /></g>)}</g>
          {Array.from({ length: 24 }, (_, i) => <path transform={`rotate(${i * 15} 60 66)`} d={i % 6 === 0 ? 'M60 34.500 V39.500' : 'M60 34.500 V37'} stroke="#6b4a22" stroke-width={i % 6 === 0 ? 2 : 1.1} stroke-linecap="round" />)}
          <path d="M60 33.500 L62.800 38.500 H57.200 Z" fill="#d1493f" />
        </g>
        {/* l'aiguille, qui cherche le nord */}
        <g class="mi-needle" style={{ transformOrigin: '60px 66px' }}>
          <path d="M61.500 44 L67 68 L61.500 94 L56 68 Z" fill="#3a2a1a" opacity="0.22" />
          <g class="mi-body">
            <path d="M60 41 L65.500 66 H60 Z" fill="#f4705e" /><path d="M60 41 L54.500 66 H60 Z" fill="#b8352f" />
            <path d="M60 91 L65.500 66 H60 Z" fill="#f6f9fc" /><path d="M60 91 L54.500 66 H60 Z" fill="#a4b3c8" />
          </g>
        </g>
        <circle cx={C.x} cy={C.y} r="4.600" fill="#a8650a" /><circle cx={C.x} cy={C.y} r="3.400" fill="url(#mi-gold)" /><circle cx="61" cy="65" r="1.200" fill="#fff" />
        {/* le verre */}
        <path d="M64 37.500 A29 29 0 0 1 88.500 60" fill="none" stroke="#fff" stroke-width="4.500" stroke-linecap="round" opacity="0.55" />
        <path d="M90 66 A30 30 0 0 1 86.500 80" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity="0.35" />
      </g>
      {twinkle(96, 36, 5.500)}{twinkle(22, 92, 4, 'an-late')}
    </>
  );
}

// ---------- la porte des Donjons ----------
function GateIcon() {
  const joints = [-158, -134, -110, -70, -46, -22];
  return (
    <>
      <ellipse cx="60" cy="112" rx="50" ry="5.500" fill="#000" opacity="0.28" />
      <circle class="an-glow" cx="29" cy="50" r="17" fill="url(#mi-fire)" /><circle class="an-glow an-late" cx="91" cy="50" r="17" fill="url(#mi-fire)" />
      <g class="mi-body">
        {/* le seuil */}
        <path d="M8 113 L16 103 H104 L112 113 Z" fill="url(#mi-stone)" /><path d="M16 103 H104 L107 107 H13 Z" fill="#fff" opacity="0.5" />
        {/* l'arche de pierre */}
        <path d="M20 104 V56 Q20 17 60 17 Q100 17 100 56 V104 Z" fill="url(#mi-stone)" />
        <path d="M20 104 V56 Q20 28 42 19.500 L46 40 Q38 46 38 58 V104 Z" fill="#3a3358" opacity="0.24" />
        <path d="M100 104 V56 Q100 30 80 20.500" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.7" />
        {/* le fond : la nuit du donjon, et le feu qui rougeoie */}
        <path d="M38 104 V58 Q38 38 60 38 Q82 38 82 58 V104 Z" fill="url(#mi-cave)" />
        <g clip-path="url(#mi-gate)">
          <ellipse class="an-glow" cx="60" cy="106" rx="30" ry="22" fill="url(#mi-fire)" />
          {/* la herse, à demi levée */}
          <g fill="#2f2c3c">
            {[44.500, 52, 59.500, 67, 74.500].map((x) => <path d={`M${x - 1.600} 36 H${x + 1.600} V86 L${x} 91 L${x - 1.600} 86 Z`} />)}
            <rect x="38" y="50" width="44" height="3.200" /><rect x="38" y="64" width="44" height="3.200" /><rect x="38" y="78" width="44" height="3.200" />
          </g>
          <g stroke="#7a7690" stroke-width="0.900" opacity="0.8">{[44.500, 52, 59.500, 67, 74.500].map((x) => <path d={`M${x + 0.900} 38 V85`} />)}</g>
        </g>
        <path d="M38 104 V58 Q38 38 60 38 Q82 38 82 58 V104" fill="none" stroke="#5a5672" stroke-width="2" />
        <g fill="#fff" opacity="0.45"><rect x="22" y="71.500" width="6.500" height="11.500" /><rect x="92" y="85.500" width="7" height="9.500" /><rect x="84" y="71.500" width="6.500" height="11.500" /></g>
        <g fill="#3a3358" opacity="0.16"><rect x="29.500" y="71.500" width="7.500" height="11.500" /><rect x="22" y="85.500" width="9.500" height="9.500" /><rect x="84" y="97" width="9.500" height="7" /></g>
        {/* les claveaux et les assises */}
        <g stroke="#5f5a78" stroke-width="1.200" stroke-linecap="round" opacity="0.75">
          {joints.map((a) => { const r = (a * Math.PI) / 180; return <path d={`M${f(60 + Math.cos(r) * 22.500)} ${f(58 + Math.sin(r) * 20.500)} L${f(60 + Math.cos(r) * 39)} ${f(57 + Math.sin(r) * 39)}`} />; })}
          <path d="M21 70 H37 M21 84 H37 M21 96 H37 M83 70 H99 M83 84 H99 M83 96 H99 M29 70 V84 M32 84 V96 M26 96 V104 M91 70 V84 M88 84 V96 M94 96 V104" />
        </g>
        <path d="M22 70.800 H36 M84 70.800 H98 M22 84.800 H36 M84 84.800 H98" stroke="#fff" stroke-width="0.800" opacity="0.5" />
        {/* la clef de voûte et sa gemme */}
        <path d="M52.500 17.500 H67.500 L65 39 H55 Z" fill="#f6f3fb" /><path d="M52.500 17.500 H60 V39 H55 Z" fill="#3a3358" opacity="0.14" />
        <path d="M60 22.500 L64.500 29 L60 35.500 L55.500 29 Z" fill="#b81f2e" /><path class="mi-flicker" d="M60 22.500 L64.500 29 H60 Z" fill="#ff8a7a" /><path d="M60 29 H64.500 L60 35.500 Z" fill="#e23a44" />
        {/* les torchères */}
        {[29, 91].map((x) => <g><path d={`M${x - 5.500} 54 H${x + 5.500} L${x + 3.500} 61 H${x - 3.500} Z`} fill="#3a3648" /><path d={`M${x - 5.500} 54 H${x + 5.500} L${x + 5} 56 H${x - 5} Z`} fill="#8a86a0" /><rect x={x - 1.500} y="61" width="3" height="9" fill="#5a3418" /></g>)}
      </g>
      <Flame x={29} y={54.500} /><Flame x={91} y={54.500} delay={0.4} />
      {[[50, 100, 0], [66, 102, 1.4], [58, 98, 2.6]].map(([x, y, d]) => <circle class="ts-ember" style={{ animationDelay: `${-d!}s` }} cx={x} cy={y} r="1.500" fill="#ffd27a" />)}
    </>
  );
}

// ---------- le crâne du Boss du jour ----------
function SkullIcon() {
  const horn = (
    <>
      <path d="M45 39 C31 34 15 39 12.500 23 C11.500 15 13.500 9 17 3 C3 13 -2 30 6.500 44 C14 56.500 29 59 41 56 Z" fill="url(#mi-horn)" />
      <path d="M17 3 C3 13 -2 30 6.500 44 C14 56.500 29 59 41 56 L40 52 C29 54 17 51 11 41 C4.500 30 7 15 17 3 Z" fill="#2c201e" opacity="0.4" />
      <path d="M45 39 C31 34 15 39 12.500 23 C11.500 15 13.500 9 17 3 C15.500 10 15 16 16.500 22 C19 33 32 31 45 35.500 Z" fill="#fff" opacity="0.26" />
      <path d="M9 34 q5 -3 8.500 0 M15 45 q5 -4 9 -1 M25 51.500 q4 -5 8.500 -3" fill="none" stroke="#2c201e" stroke-width="1.300" stroke-linecap="round" opacity="0.6" />
    </>
  );
  return (
    <>
      <ellipse cx="60" cy="112" rx="32" ry="5" fill="#000" opacity="0.3" />
      <g class="mi-bob mi-slow">
        <g class="mi-body">
          {horn}<g transform="translate(120 0) scale(-1 1)">{horn}</g>
          {/* le crâne : voûte large, pommettes saillantes, mâchoire étroite */}
          <path d="M60 22 C82 22 95 36 94 55 C93.700 62 91 68 87 72 L90 78 L82.500 83 L81 93 H39 L37.500 83 L30 78 L33 72 C29 68 26.300 62 26 55 C25 36 38 22 60 22 Z" fill="url(#mi-bone)" />
          <path d="M60 22 C38 22 25 36 26 55 C26.300 62 29 68 33 72 L30 78 L37.500 83 L39 93 H50 L48 77 C41 70 38 62 38 53 C38 40 46 29 60 22 Z" fill="#5a3f4a" opacity="0.22" />
          <path d="M87 72 C91 68 93.700 62 94 55 C94.500 45 91 36 84 30" fill="none" stroke="#fff" stroke-width="1.500" opacity="0.75" />
          <path d="M46 30 C52 27 60 26 68 28" fill="none" stroke="#fff" stroke-width="2.400" stroke-linecap="round" opacity="0.55" />
          {/* les arcades et les orbites, en colère */}
          <path d="M31 47 L57 57 M89 47 L63 57" stroke="#fff" stroke-width="2.400" stroke-linecap="round" opacity="0.6" />
          <path d="M33 50 L56.500 59 L54.500 72.500 C47 76.500 38.500 74 35 65 Z" fill="#1f0e17" /><path d="M87 50 L63.500 59 L65.500 72.500 C73 76.500 81.500 74 85 65 Z" fill="#1f0e17" />
          {/* le nez, les pommettes, une fêlure */}
          <path d="M60 71 L54 85 Q60 81.500 66 85 Z" fill="#1f0e17" />
          <path d="M33 72 L30 78 L37.500 83 L44 80 L42 73 Z M87 72 L90 78 L82.500 83 L76 80 L78 73 Z" fill="#5a3f4a" opacity="0.2" />
          <path d="M64 23.500 L59.500 32 L65 38 L61 45.500" fill="none" stroke="#8a7658" stroke-width="1.400" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M76 26 l-3 5 l4 3" fill="none" stroke="#8a7658" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" opacity="0.7" />
          {/* les dents : quatre incisives entre deux crocs */}
          <rect x="39" y="89.500" width="42" height="4.500" fill="#4a3438" opacity="0.55" />
          <path d="M40.500 92 h7.500 l-3.800 15 Z M72 92 h7.500 l-3.700 15 Z" fill="#fffaec" /><path d="M40.500 92 h3.700 v15 Z M72 92 h3.700 v15 Z" fill="#bfa988" opacity="0.6" />
          {[49, 54.700, 60.400, 66.100].map((x) => <g><rect x={x} y="92" width="4.900" height="9" rx="1.800" fill="#fffaec" /><rect x={x} y="92" width="1.700" height="9" rx="0.800" fill="#bfa988" opacity="0.6" /></g>)}
        </g>
        {/* les yeux : des braises, et la flamme qui s'en échappe */}
        <circle class="an-glow" cx="45.500" cy="66" r="10" fill="url(#mi-eye)" /><circle class="an-glow" cx="74.500" cy="66" r="10" fill="url(#mi-eye)" />
        <g opacity="0.92"><Flame x={42} y={62} s={0.62} /><Flame x={78} y={62} s={0.62} delay={0.3} /></g>
        <ellipse class="mi-flicker" cx="46" cy="66.500" rx="3.600" ry="2.700" fill="#fff3b0" /><ellipse class="mi-flicker" cx="74" cy="66.500" rx="3.600" ry="2.700" fill="#fff3b0" />
      </g>
      {[[30, 104, 0, '#ffb09a'], [90, 102, 1.2, '#ffd27a'], [50, 110, 2.3, '#ffd27a'], [72, 108, 3.1, '#ffb09a']].map(([x, y, d, c]) => <circle class="ts-ember" style={{ animationDelay: `${-(d as number)}s` }} cx={x} cy={y} r="1.700" fill={c as string} />)}
    </>
  );
}

// ---------- le bouclier et les épées de l'Arène ----------
/** Une épée dessinée pointe en haut, autour du point où les deux lames se croisent. */
function Sword({ angle, flip }: { angle: number; flip?: boolean }) {
  return (
    <g class="mi-clash" style={{ transformOrigin: '60px 52px', animationDirection: flip ? 'reverse' : 'normal' }}>
      <g transform={`translate(60 52) rotate(${angle})`}>
        <g class="mi-body">
          {/* la lame : deux pans et une gorge */}
          <path d="M-6.500 -38 L0 -51 L6.500 -38 V24 H-6.500 Z" fill="#c9d4e2" />
          <path d={flip ? 'M0 -51 L6.500 -38 V24 H0 Z' : 'M-6.500 -38 L0 -51 V24 H-6.500 Z'} fill="#ffffff" />
          <path d={flip ? 'M-6.500 -38 L0 -51 V24 H-6.500 Z' : 'M0 -51 L6.500 -38 V24 H0 Z'} fill="#8c9bb5" />
          <path d="M-1.300 -34 H1.300 V20 H-1.300 Z" fill="#5f6c86" opacity="0.55" />
          {/* la garde : deux quillons relevés, une gemme */}
          <path d="M-17 20.500 H17 Q20.500 20.500 20.500 24 Q20.500 27.500 17 27.500 H-17 Q-20.500 27.500 -20.500 24 Q-20.500 20.500 -17 20.500 Z" fill="url(#mi-gold)" />
          <path d="M-17 25 H17 Q19.500 25 20.300 23.500 Q20.800 27.500 17 27.500 H-17 Q-20.800 27.500 -20.300 23.500 Q-19.500 25 -17 25 Z" fill="#c2760a" opacity="0.55" />
          <path d="M-16 22 H16" stroke="#fff6c2" stroke-width="1.100" stroke-linecap="round" />
          <path d="M0 20 l3.800 4 l-3.800 4 l-3.800 -4 Z" fill="#b81f2e" /><path d="M0 20 l3.800 4 H0 Z" fill="#ff8a7a" />
          {/* la fusée gainée de cuir, le pommeau */}
          <rect x="-4" y="27.500" width="8" height="16" rx="1.600" fill="url(#mi-wood)" /><path d="M-4 31 L4 33.500 M-4 35.500 L4 38 M-4 40 L4 42.500" stroke="#4a2a12" stroke-width="1.200" />
          <circle cx="0" cy="47.500" r="5.600" fill="url(#mi-gold)" /><circle cx="1.400" cy="46.200" r="1.600" fill="#fff" opacity="0.85" />
        </g>
        <path class="mi-glint" d={spark(0, 10, 5.500)} fill="#fff" />
      </g>
    </g>
  );
}

function SwordsIcon() {
  return (
    <>
      <ellipse cx="60" cy="113" rx="38" ry="5" fill="#000" opacity="0.26" />
      <g class="mi-body">
        <circle cx="60" cy="62" r="39" fill="url(#mi-gold)" /><circle cx="60" cy="62" r="33.500" fill="#a8650a" /><circle cx="60" cy="62" r="32" fill="url(#mi-shield)" />
        <path d="M60 30 V94 M28 62 H92" stroke="#1f4288" stroke-width="1.600" opacity="0.5" />
        <circle cx="60" cy="62" r="20" fill="none" stroke="#9cc0f5" stroke-width="1.200" opacity="0.6" />
        {[45, 135, 225, 315].map((a) => { const r = (a * Math.PI) / 180; return <g><circle cx={f(60 + Math.cos(r) * 36.200)} cy={f(62 + Math.sin(r) * 36.200)} r="2.300" fill="#a8650a" /><circle cx={f(60 + Math.cos(r) * 36.200 + 0.400)} cy={f(62 + Math.sin(r) * 36.200 - 0.400)} r="1.500" fill="#fff6c2" /></g>; })}
        <path d="M67 32.500 A30 30 0 0 1 89.500 54" fill="none" stroke="#fff" stroke-width="4.500" stroke-linecap="round" opacity="0.4" />
      </g>
      <Sword angle={-38} /><Sword angle={38} flip />
      {/* l'éclat du choc, là où les lames se croisent */}
      <g class="mi-spark" style={{ transformOrigin: '60px 52px' }}><path d={spark(60, 52, 13)} fill="#fff" /><path d={spark(60, 52, 7)} fill="#ffe27a" /></g>
    </>
  );
}

// ---------- le Colisée ----------
function ColosseumIcon() {
  const E = { x: 60, rx: 47, ry: 16.500 };
  const rows: [number, number][] = [[47, 8], [61, 10.500], [77, 12]]; // base de l'arcade (au centre), hauteur
  const flags: [number, number][] = [[28, 0], [60, 0.6], [92, 1.2]];
  const backY = (x: number) => 38 - E.ry * Math.sqrt(Math.max(0, 1 - ((x - E.x) / E.rx) ** 2));
  return (
    <>
      <ellipse cx="60" cy="106" rx="52" ry="7" fill="#000" opacity="0.26" />
      {/* les oriflammes de la galerie du fond */}
      {flags.map(([x, d]) => (
        <g><path d={`M${x} ${f(backY(x) + 2)} V${f(backY(x) - 15)}`} stroke="#5a3806" stroke-width="1.600" stroke-linecap="round" /><path class="bd-flag" style={{ transformOrigin: `${x}px ${f(backY(x) - 11)}px`, animationDelay: `${-d}s` }} d={`M${x} ${f(backY(x) - 15)} q8 -1 14 3.500 q-6 4 -14 4.500 Z`} fill="#e0463c" /></g>
      ))}
      <g class="mi-body">
        {/* l'intérieur : la galerie du fond, les gradins, la piste */}
        <ellipse cx={E.x} cy="38" rx={E.rx} ry={E.ry} fill="#7a5226" />
        <path d={`M${E.x - E.rx} 38 A${E.rx} ${E.ry} 0 0 1 ${E.x + E.rx} 38 L${E.x + 41} 41 A41 13.500 0 0 0 ${E.x - 41} 41 Z`} fill="#c9a060" />
        <ellipse cx={E.x} cy="41" rx="41" ry="13.500" fill="#9a7038" /><ellipse cx={E.x} cy="42.500" rx="35" ry="11" fill="#b88a4c" /><ellipse cx={E.x} cy="44" rx="29.500" ry="9" fill="#d2a866" />
        <ellipse cx={E.x} cy="45.500" rx="24" ry="7" fill="#f3dfa6" /><ellipse cx="66" cy="44.500" rx="13" ry="3.600" fill="#fff6d2" opacity="0.7" />
        {/* la façade : trois étages d'arcades */}
        <path d={`M${E.x - E.rx} 38 A${E.rx} ${E.ry} 0 0 0 ${E.x + E.rx} 38 V84 A${E.rx} ${E.ry} 0 0 1 ${E.x - E.rx} 84 Z`} fill="url(#mi-sand)" />
        <path d={`M${E.x - E.rx} 38 A${E.rx} ${E.ry} 0 0 0 ${E.x + E.rx} 38`} fill="none" stroke="#fff6d2" stroke-width="2.400" />
        {[52, 67].map((y) => <g><path d={`M${E.x - E.rx} ${y} A${E.rx} ${E.ry} 0 0 0 ${E.x + E.rx} ${y}`} fill="none" stroke="#8a5e28" stroke-width="1.500" opacity="0.6" /><path d={`M${E.x - E.rx} ${y + 1.600} A${E.rx} ${E.ry} 0 0 0 ${E.x + E.rx} ${y + 1.600}`} fill="none" stroke="#fff6d2" stroke-width="1" opacity="0.55" /></g>)}
        {rows.map(([base, h]) => Array.from({ length: 9 }, (_, i) => {
          const t = (Math.PI * (i + 1)) / 10, x = E.x - E.rx * Math.cos(t), yb = base + E.ry * Math.sin(t), w = Math.max(2.400, 7.400 * Math.sin(t)), top = yb - h + w / 2;
          return (
            <g>
              <path d={`M${f(x - w / 2)} ${f(yb)} V${f(top)} A${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(x + w / 2)} ${f(top)} V${f(yb)} Z`} fill="#4a2c0c" />
              <path d={`M${f(x - w / 2)} ${f(yb)} V${f(top)} A${f(w / 2)} ${f(w / 2)} 0 0 1 ${f(x)} ${f(top - w / 2)} A${f(w * 0.36)} ${f(w / 2)} 0 0 0 ${f(x - w * 0.14)} ${f(top)} V${f(yb)} Z`} fill="#8a5e28" opacity="0.75" />
            </g>
          );
        }))}
        {/* l'ombre du côté gauche, le liseré de lumière à droite */}
        <path d={`M${E.x - E.rx} 38 A${E.rx} ${E.ry} 0 0 0 ${E.x - 20} 53 V99 A${E.rx} ${E.ry} 0 0 1 ${E.x - E.rx} 84 Z`} fill="#4a2c0c" opacity="0.18" />
        <path d={`M${E.x + E.rx} 38 V84`} stroke="#fff6d2" stroke-width="1.400" opacity="0.8" />
      </g>
      {[[52, 45, 0], [68, 46, 1.6], [60, 43, 3]].map(([x, y, d]) => <circle class="ts-dust" style={{ animationDelay: `${-d!}s` }} cx={x} cy={y} r="1.500" fill="#fff" />)}
      {twinkle(100, 34, 5)}{twinkle(20, 60, 3.500, 'an-late')}
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
