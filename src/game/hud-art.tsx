// Les pièces du panneau des héros en combat (battle-scene.ts), dessinées par le code dans le même trait que les menus
// (chrome.tsx) : contour brun sombre, or en dégradé, émail bleu nuit. Chaque dessin a ses propres dégradés (il devient
// une image à part pour Phaser) ; les adresses des images sont gardées d'un combat à l'autre.
import type Phaser from 'phaser';
import type { VNode } from 'preact';
import { svgString } from './bg/core';

const INK = '#2f1b0c';

const GOLD = () => <linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>;
const GOLD_RING = () => <linearGradient id="gr" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#fff6c4" /><stop offset="0.35" stop-color="#ffcf45" /><stop offset="0.7" stop-color="#e09a18" /><stop offset="1" stop-color="#9a5a06" /></linearGradient>;

function gem(x: number, y: number, r: number, light: string, mid: string, dark: string) {
  return (
    <g>
      <path d={`M${x} ${y - r * 1.25} L${x + r} ${y} L${x} ${y + r * 1.25} L${x - r} ${y} Z`} fill={INK} />
      <path d={`M${x} ${y - r} L${x + r * 0.78} ${y} L${x} ${y + r} L${x - r * 0.78} ${y} Z`} fill={mid} />
      <path d={`M${x} ${y - r} L${x + r * 0.78} ${y} H${x} Z`} fill={light} />
      <path d={`M${x} ${y} H${x + r * 0.78} L${x} ${y + r} Z`} fill={dark} opacity="0.6" />
    </g>
  );
}

/** Le panneau (720 × 398) : émail bleu nuit ; le plateau creusé où se tiennent les portraits, cerclé d'or. */
function Panel() {
  const w = 720, h = 398;
  return (
    <>
      <defs>
        <linearGradient id="w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c3878" /><stop offset="0.5" stop-color="#1d2658" /><stop offset="1" stop-color="#0f1533" /></linearGradient>
        <linearGradient id="t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070a1e" /><stop offset="1" stop-color="#1a2250" /></linearGradient>
        <GOLD />
      </defs>
      <rect width={w} height={h} fill="url(#w)" />
      <rect y="8" width={w} height="110" fill="#fff" opacity="0.06" />
      <rect x="10" y="30" width="700" height="218" rx="27" fill={INK} />
      <rect x="13.5" y="33.5" width="693" height="211" rx="24" fill="url(#g)" />
      <path d="M40 36 H680" stroke="#fffbe0" stroke-width="1.6" stroke-linecap="round" opacity="0.8" />
      <rect x="19" y="39" width="682" height="200" rx="19" fill={INK} />
      <rect x="21" y="41" width="678" height="196" rx="17" fill="url(#t)" />
      <rect x="21" y="41" width="678" height="54" rx="17" fill="#fff" opacity="0.05" />
      {gem(13.5, 139, 7, '#ffc0b8', '#e0403a', '#7a1418')}{gem(706.5, 139, 7, '#ffc0b8', '#e0403a', '#7a1418')}
    </>
  );
}

/** Le rail d'or (720 × 18) posé à cheval sur le bas du terrain et le haut du panneau, une gemme au milieu. */
function Rail() {
  const w = 720;
  return (
    <>
      <defs><GOLD /><GOLD_RING /></defs>
      <rect y="4" width={w} height="9" fill={INK} />
      <rect y="5.8" width={w} height="5.4" fill="url(#g)" />
      <path d={`M0 6.6 H${w}`} stroke="#fffbe0" stroke-width="1.1" opacity="0.85" />
      {[16, w - 16].map((x) => <g><circle cx={x} cy="8.5" r="5.5" fill={INK} /><circle cx={x} cy="8.5" r="4" fill="url(#gr)" /></g>)}
      <path d={`M${w / 2 - 22} 8.5 L${w / 2} -1 L${w / 2 + 22} 8.5 L${w / 2} 18 Z`} fill={INK} />
      <path d={`M${w / 2 - 17.5} 8.5 L${w / 2} 1.8 L${w / 2 + 17.5} 8.5 L${w / 2} 15.2 Z`} fill="url(#gr)" />
      {gem(w / 2, 8.5, 5, '#ffc0b8', '#e0403a', '#7a1418')}
    </>
  );
}

/**
 * L'anneau d'un portrait (140 × 140) : cercle d'or biseauté, une rainure sombre où court l'énergie, le bord intérieur ;
 * le centre est vide (le portrait est dessous). Quatre clous d'or.
 */
function Ring() {
  return (
    <>
      <defs>
        <GOLD_RING />
        <mask id="m"><rect width="140" height="140" fill="#fff" /><circle cx="70" cy="70" r="48.5" fill="#000" /></mask>
      </defs>
      <g mask="url(#m)">
        <circle cx="70" cy="70" r="68" fill={INK} />
        <circle cx="70" cy="70" r="65" fill="url(#gr)" />
        <path d="M18 52 A54 54 0 0 1 88 19" fill="none" stroke="#fffbe0" stroke-width="2.4" stroke-linecap="round" opacity="0.85" />
        <path d="M122 88 A54 54 0 0 1 52 121" fill="none" stroke="#7a4406" stroke-width="2.4" stroke-linecap="round" opacity="0.5" />
        <circle cx="70" cy="70" r="60.5" fill={INK} />
        <circle cx="70" cy="70" r="59" fill="#070a1e" />
        <circle cx="70" cy="70" r="51.5" fill={INK} />
        <circle cx="70" cy="70" r="50" fill="#e8b84a" />
      </g>
    </>
  );
}

/** Le fond d'un portrait (100 × 100) : un disque d'émail de la couleur de l'élément du héros, plus clair en haut. */
function Disc({ c }: { c: [string, string, string] }) {
  return (
    <>
      <defs><radialGradient id="d" cx="0.5" cy="0.3" r="0.75"><stop offset="0" stop-color={c[0]} /><stop offset="0.55" stop-color={c[1]} /><stop offset="1" stop-color={c[2]} /></radialGradient></defs>
      <circle cx="50" cy="50" r="50" fill="url(#d)" />
      <ellipse cx="50" cy="26" rx="34" ry="16" fill="#fff" opacity="0.16" />
    </>
  );
}

/** La rainure de la barre de vie (120 × 22) : contour sombre, filet d'or, fond noir ; la vie la remplit (dessinée à part). */
function HpGroove() {
  return (
    <>
      <defs><GOLD /></defs>
      <rect x="0.5" y="0.5" width="119" height="21" rx="9" fill={INK} />
      <rect x="2.5" y="2.5" width="115" height="17" rx="7.5" fill="url(#g)" />
      <rect x="4.5" y="4.5" width="111" height="13" rx="6" fill="#070a1e" />
    </>
  );
}

/** Un bouton (w × h) : cadre d'or et ses deux gemmes, émail bombé de la couleur donnée, double filet, reflet. */
function Button({ w, h, c }: { w: number; h: number; c: [string, string, string] }) {
  const r = Math.min(20, h / 2.6);
  return (
    <>
      <defs>
        <GOLD /><GOLD_RING />
        <linearGradient id="e" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color={c[0]} /><stop offset="0.5" stop-color={c[1]} /><stop offset="1" stop-color={c[2]} /></linearGradient>
        <clipPath id="k"><rect x="8.5" y="8.5" width={w - 17} height={h - 20} rx={r - 6} /></clipPath>
      </defs>
      <rect x="1" y="4" width={w - 2} height={h - 4} rx={r + 2} fill="#000" opacity="0.3" />
      <rect x="1" y="1" width={w - 2} height={h - 5} rx={r + 2} fill={INK} />
      <rect x="3.5" y="3.5" width={w - 7} height={h - 10} rx={r} fill="url(#g)" />
      <path d={`M${r} 6.5 H${w - r}`} stroke="#fffbe0" stroke-width="1.3" stroke-linecap="round" opacity="0.9" />
      <rect x="7" y="7" width={w - 14} height={h - 17} rx={r - 4} fill={INK} />
      <rect x="8.5" y="8.5" width={w - 17} height={h - 20} rx={r - 6} fill="url(#e)" />
      <g clip-path="url(#k)">
        <ellipse cx={w / 2} cy={h * 0.16} rx={w * 0.46} ry={h * 0.3} fill="#fff" opacity="0.22" />
        <rect x="8.5" y={h - 26} width={w - 17} height="14" fill="#000" opacity="0.14" />
      </g>
      <rect x="12.5" y="12.5" width={w - 25} height={h - 28} rx={Math.max(3, r - 9)} fill="none" stroke="#ffe9a0" stroke-width="1.2" opacity="0.5" />
      {[6, w - 6].map((x) => <g><circle cx={x} cy={(h - 5) / 2} r="7" fill={INK} /><circle cx={x} cy={(h - 5) / 2} r="5.5" fill="url(#gr)" />{gem(x, (h - 5) / 2, 3.3, '#ffc0b8', '#e0403a', '#7a1418')}</g>)}
    </>
  );
}

/** Les couleurs des boutons : émail (clair, moyen, foncé) et la couleur du contour des lettres. */
export const HUD_BUTTONS = {
  green: { c: ['#9cf0a8', '#3fb35c', '#1f6e36'] as [string, string, string], ink: '#11461f' },
  blue: { c: ['#9fc8ff', '#3f86e0', '#23509e'] as [string, string, string], ink: '#16306a' },
  navy: { c: ['#8a9cf0', '#3a4994', '#1d2758'] as [string, string, string], ink: '#0a0e26' },
};

/** Les disques des portraits, par élément. */
const DISCS: Record<string, [string, string, string]> = {
  fire: ['#ffb07a', '#d8502e', '#7a1e12'], wind: ['#b8f5a0', '#4fae5a', '#1c5a2a'], water: ['#a8dcff', '#3f86e0', '#1a3a8a'],
  earth: ['#f5d08a', '#b8822e', '#5e3a12'], none: ['#a8b8ff', '#4a5fc0', '#1f2a6e'],
};

const urls = new Map<string, string>();
function queue(sc: Phaser.Scene, key: string, w: number, h: number, draw: () => VNode) {
  if (sc.textures.exists(key)) return;
  let url = urls.get(key);
  if (!url) {
    url = URL.createObjectURL(new Blob([svgString(draw(), w, h)], { type: 'image/svg+xml' }));
    urls.set(key, url);
  }
  sc.load.svg(key, url, { width: w, height: h });
}

/** Met en file toutes les pièces du panneau (à appeler dans `preload`). Les boutons : une taille par usage. */
export function loadHudArt(sc: Phaser.Scene) {
  queue(sc, 'hud-panel', 720, 398, () => <Panel />);
  queue(sc, 'hud-rail', 720, 18, () => <Rail />);
  queue(sc, 'hud-ring', 140, 140, () => <Ring />);
  queue(sc, 'hud-hp', 120, 22, () => <HpGroove />);
  for (const [el, c] of Object.entries(DISCS)) queue(sc, `hud-disc-${el}`, 100, 100, () => <Disc c={c} />);
  for (const [k, b] of Object.entries(HUD_BUTTONS)) {
    queue(sc, `hud-btn-${k}-290`, 290, 84, () => <Button w={290} h={84} c={b.c} />);
    queue(sc, `hud-btn-${k}-160`, 160, 62, () => <Button w={160} h={62} c={b.c} />);
  }
}
