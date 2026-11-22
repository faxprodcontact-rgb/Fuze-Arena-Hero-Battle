// Les pièces de l'interface dessinées par le code, dans le trait des décors (bandeau de titre, portail) : contour brun
// sombre, or en dégradé (clair en haut, foncé en bas), bois sculpté, émail, gemmes ; un reflet en haut de chaque volume.
// Les dégradés sont rangés une seule fois dans `ChromeDefs` (posé par l'application, jamais caché par display: none :
// un dégradé caché ne peint plus rien) ; chaque pièce s'en sert par son nom (`url(#cx-…)`).
import type { ComponentChildren } from 'preact';
import { useLayoutEffect, useRef, useState } from 'preact/hooks';
import { spark } from './portal';

/** La taille réelle d'un élément (pour dessiner à sa mesure exacte, sans rien étirer). */
export function useSize<T extends Element>() {
  const ref = useRef<T>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const measure = () => { const r = el.getBoundingClientRect(); setSize({ w: Math.round(r.width), h: Math.round(r.height) }); };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, size] as const;
}

/** Les trois bois des barres : celle du haut, celle des onglets (plus sombre), le bas de l'accueil (plus chaud). */
const BAR_WOOD = {
  top: ['#8c5d33', '#6b4423', '#4a2d15'],
  tabs: ['#6e4625', '#4e3018', '#33200e'],
  dock: ['#9c6b3c', '#7a4f2a', '#583619'],
} as const;

/**
 * Le fond d'une barre (en haut, en bas, sous le combat de l'accueil) : une planche de bois sculpté, un reflet doux, et
 * sur le bord qui touche l'écran un rail d'or entre deux filets sombres, avec ses clous et une gemme au milieu. Dessiné à
 * la taille exacte de la barre (rien n'est étiré). Les onglets ont leurs séparations creusées dans le bois.
 */
export function BarArt({ kind, cols = 0 }: { kind: 'top' | 'tabs' | 'dock'; cols?: number }) {
  const [ref, { w, h }] = useSize<HTMLSpanElement>();
  const [c0, c1, c2] = BAR_WOOD[kind];
  const railTop = kind === 'top' ? h - 7 : 0; // le rail : en bas pour la barre du haut, en haut pour les autres
  const body = kind === 'top' ? [0, h - 7] : [7, h];
  const id = `cx-bar-${kind}`;
  return (
    <span class={`bar-art bar-art-${kind}`} ref={ref} aria-hidden="true">
      {w > 0 && (
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
          <defs><linearGradient id={id} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color={c0} /><stop offset="0.55" stop-color={c1} /><stop offset="1" stop-color={c2} /></linearGradient></defs>
          <rect x="0" y={body[0]} width={w} height={body[1]! - body[0]!} fill={`url(#${id})`} />
          <rect x="0" y={body[0]} width={w} height={(body[1]! - body[0]!) * 0.42} fill="#fff" opacity="0.08" />
          {/* les séparations des onglets, creusées dans le bois */}
          {cols > 1 && Array.from({ length: cols - 1 }, (_, i) => {
            const x = Math.round((w * (i + 1)) / cols);
            return <g><path d={`M${x - 0.75} 16 V${h - 12}`} stroke="#1c1008" stroke-width="1.5" opacity="0.55" /><path d={`M${x + 0.9} 16 V${h - 12}`} stroke="#fff" stroke-width="1" opacity="0.1" /></g>;
          })}
          {/* le rail d'or */}
          <rect x="0" y={railTop} width={w} height="7" fill={INK} />
          <rect x="0" y={railTop + 1.5} width={w} height="4" fill="url(#cx-gold)" />
          <path d={`M0 ${railTop + 2} H${w}`} stroke="#fffbe0" stroke-width="0.9" opacity="0.8" />
          {[14, w - 14].map((x) => <g><circle cx={x} cy={railTop + 3.5} r="4.2" fill={INK} /><circle cx={x} cy={railTop + 3.5} r="3" fill="url(#cx-gold-ring)" /><circle cx={x - 0.8} cy={railTop + 2.7} r="1" fill="#fff" /></g>)}
          {kind !== 'tabs' && (
            <g>
              <path d={`M${w / 2 - 16} ${railTop + 3.5} L${w / 2} ${railTop - 4} L${w / 2 + 16} ${railTop + 3.5} L${w / 2} ${railTop + 11} Z`} fill={INK} />
              <path d={`M${w / 2 - 12.5} ${railTop + 3.5} L${w / 2} ${railTop - 1.5} L${w / 2 + 12.5} ${railTop + 3.5} L${w / 2} ${railTop + 8.5} Z`} fill="url(#cx-gold-ring)" />
              <Gem x={w / 2} y={railTop + 3.5} r={3.6} tone="red" />
            </g>
          )}
        </svg>
      )}
    </span>
  );
}

/** Le socle de l'onglet ouvert : une arche cerclée d'or, émaillée de bleu, qui dépasse au-dessus de la barre ; une lueur. */
export function TabSocket() {
  return (
    <svg class="tab-socket" viewBox="0 0 72 70" aria-hidden="true">
      <ellipse class="an-glow" cx="36" cy="30" rx="36" ry="26" fill="url(#cx-glow)" />
      <path d="M5 70 V32 Q5 6 36 4 Q67 6 67 32 V70 Z" fill={INK} />
      <path d="M8 70 V32 Q8 9 36 7 Q64 9 64 32 V70 Z" fill="url(#cx-gold-ring)" />
      <path d="M11 22 Q16 10 36 9" fill="none" stroke="#fffbe0" stroke-width="1.6" stroke-linecap="round" opacity="0.85" />
      <path d="M12 70 V33 Q12 13 36 11.5 Q60 13 60 33 V70 Z" fill={INK} />
      <path d="M13.5 70 V33 Q13.5 14.5 36 13 Q58.5 14.5 58.5 33 V70 Z" fill="url(#cx-enamel)" />
      <path d="M16 34 Q18 17 36 16 Q54 17 56 34 Q48 26 36 26 Q24 26 16 34 Z" fill="#fff" opacity="0.16" />
      <Gem x={36} y={7.5} r={3.4} tone="red" />
    </svg>
  );
}

/**
 * La plaque du chapitre, en haut de l'accueil : bois sculpté dans un cadre d'or, rubans cramoisis repliés derrière, le titre
 * en lettres d'or, et la progression du chapitre dans une rainure d'or. Un reflet passe sur la plaque.
 */
export function ChapterPlaque({ title, progress }: { title: string; progress: number }) {
  const p = Math.max(0, Math.min(1, progress));
  const size = title.length > 13 ? 17 : 20;
  return (
    <svg class="chapter-plaque" viewBox="0 0 236 66" aria-hidden="true">
      <defs><clipPath id="cp-clip"><rect x="27" y="10.5" width="182" height="41" rx="6" /></clipPath></defs>
      {[0, 1].map((i) => (
        <g transform={i ? 'translate(236 0) scale(-1 1)' : undefined}>
          <path d="M32 50 L22 57 V50 Z" fill="#5e1418" />
          <path d="M1 20 H34 V51 H1 L10 35.5 Z" fill={INK} />
          <path d="M3.8 21.5 H32.5 V49.5 H3.8 L11.8 35.5 Z" fill="#9c2a2e" /><path d="M3.8 21.5 H32.5 V35.5 H11.8 Z" fill="#e2574c" />
          <path d="M3.8 21.5 H32.5 V24 H5.5 Z M5.5 47 H32.5 V49.5 H3.8 Z" fill="#ffd45c" />
        </g>
      ))}
      <rect x="20" y="3.5" width="196" height="55" rx="11" fill={INK} />
      <rect x="21.8" y="5.3" width="192.4" height="51.4" rx="9.5" fill="url(#cx-gold)" />
      <path d="M24 12 Q24 7 30 6.8 H206 Q212 7 212 12" fill="none" stroke="#fffbe0" stroke-width="1" opacity="0.9" />
      <rect x="25.5" y="9" width="185" height="44" rx="7" fill={INK} />
      <rect x="27" y="10.5" width="182" height="41" rx="6" fill="url(#cx-wood)" />
      <g clip-path="url(#cp-clip)">
        <rect x="27" y="10.5" width="182" height="15" fill="#fff" opacity="0.13" />
        <path class="tb-sheen" d="M0 4 H16 L4 58 H-12 Z" fill="#fff" opacity="0.28" />
      </g>
      <text x="118" y="33.5" text-anchor="middle" font-family="'Lilita One', 'Trebuchet MS', sans-serif" font-size={size} fill="#1f1006" opacity="0.45" stroke="#1f1006" stroke-width="3.4" stroke-linejoin="round">{title}</text>
      <text x="118" y="32" text-anchor="middle" font-family="'Lilita One', 'Trebuchet MS', sans-serif" font-size={size} fill="url(#cx-text-gold)" stroke={INK} stroke-width="3.4" stroke-linejoin="round" paint-order="stroke">{title}</text>
      {/* la progression : une rainure sombre cerclée d'or, l'or qui la remplit */}
      <rect x="61" y="39" width="114" height="8.5" rx="4.25" fill={INK} />
      <rect x="62.5" y="40.5" width="111" height="5.5" rx="2.75" fill="#1c1008" />
      {p > 0 && <rect x="62.5" y="40.5" width={Math.max(5.5, 111 * p)} height="5.5" rx="2.75" fill="url(#cx-gold)" />}
      {p > 0 && <rect x="64" y="41.2" width={Math.max(2, 111 * p - 3)} height="1.4" rx="0.7" fill="#fff" opacity="0.6" />}
      {/* le fleuron du haut, une gemme à chaque bout, la goutte d'or du bas */}
      <path d="M118 -3.5 L122.5 3 L132 3.5 L124 7.5 L118 12.5 L112 7.5 L104 3.5 L113.5 3 Z" fill={INK} />
      <path d="M118 -1 L121.5 4.3 L128 4.8 L122.8 7.3 L118 10.8 L113.2 7.3 L108 4.8 L114.5 4.3 Z" fill="url(#cx-gold)" />
      <circle cx="118" cy="5.3" r="2.3" fill="#b81f2e" /><circle cx="118.6" cy="4.7" r="0.9" fill="#ff9a8a" />
      <Gem x={20} y={31} r={6.2} /><Gem x={216} y={31} r={6.2} />
      <path d="M118 55 L122 59 L118 63.5 L114 59 Z" fill={INK} /><path d="M118 56.6 L120.5 59 L118 61.8 L115.5 59 Z" fill="url(#cx-gold)" />
      <Twinkle x={20} y={24} r={4} /><Twinkle x={216} y={24} r={4} late />
    </svg>
  );
}

/**
 * Le fond du grand bouton Combattre : cadre d'or et ses deux gemmes, émail vert bombé, double filet d'or, un reflet qui
 * passe de temps en temps. Dessiné à la taille exacte du bouton.
 */
export function FightButtonArt({ off = false }: { off?: boolean }) {
  const [ref, { w, h }] = useSize<HTMLSpanElement>();
  return (
    <span class="fight-art" ref={ref} aria-hidden="true">
      {w > 0 && (
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
          <defs>
            <linearGradient id="fb-enamel" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color={off ? '#b8b0a0' : '#8eeb9c'} /><stop offset="0.5" stop-color={off ? '#8a8272' : '#3fb35c'} /><stop offset="1" stop-color={off ? '#5e5648' : '#1f6e36'} />
            </linearGradient>
            <clipPath id="fb-clip"><rect x="9" y="9" width={w - 18} height={h - 18} rx="10" /></clipPath>
          </defs>
          <rect x="1" y="3" width={w - 2} height={h - 3} rx="17" fill="#000" opacity="0.3" />
          <rect x="1" y="1" width={w - 2} height={h - 3} rx="17" fill={INK} />
          <rect x="3.2" y="3.2" width={w - 6.4} height={h - 7.4} rx="15" fill="url(#cx-gold)" />
          <path d={`M10 6.5 H${w - 10}`} stroke="#fffbe0" stroke-width="1.2" stroke-linecap="round" opacity="0.9" />
          <rect x="7.5" y="7.5" width={w - 15} height={h - 15} rx="11.5" fill={INK} />
          <rect x="9" y="9" width={w - 18} height={h - 18} rx="10" fill="url(#fb-enamel)" />
          <g clip-path="url(#fb-clip)">
            <ellipse cx={w / 2} cy={h * 0.18} rx={w * 0.46} ry={h * 0.32} fill="#fff" opacity="0.2" />
            <rect x="9" y={h - 22} width={w - 18} height="13" fill="#000" opacity="0.14" />
            {!off && <path class="fb-sheen" d={`M-40 0 H-18 L-48 ${h} H-70 Z`} fill="#fff" opacity="0.35" />}
          </g>
          <rect x="13" y="13" width={w - 26} height={h - 26} rx="7" fill="none" stroke="#ffe9a0" stroke-width="1.2" opacity="0.55" />
          {[[6, h / 2 - 1.5], [w - 6, h / 2 - 1.5]].map(([x, y]) => <g><circle cx={x} cy={y} r="7.5" fill={INK} /><circle cx={x} cy={y} r="6" fill="url(#cx-gold-ring)" /><Gem x={x!} y={y!} r={3.6} tone="red" /></g>)}
        </svg>
      )}
    </span>
  );
}

/** Le blason du niveau du joueur, sous son portrait : un petit écu bleu cerclé d'or. */
export function LevelShield({ level }: { level: number }) {
  return (
    <span class="lv-shield">
      <svg viewBox="0 0 30 30" aria-hidden="true">
        <path d="M2 3 H28 V14 Q28 25 15 29 Q2 25 2 14 Z" fill={INK} />
        <path d="M4 5 H26 V14 Q26 23.5 15 27 Q4 23.5 4 14 Z" fill="url(#cx-gold-ring)" />
        <path d="M6.5 7.5 H23.5 V14 Q23.5 21.5 15 24.5 Q6.5 21.5 6.5 14 Z" fill="url(#cx-enamel)" />
        <path d="M7 8 H23 V12 Q15 10 7 13 Z" fill="#fff" opacity="0.2" />
      </svg>
      <span>{level}</span>
    </span>
  );
}

/** Le contour de toutes les pièces. */
export const INK = '#2f1b0c';

/** Les dégradés communs. `objectBoundingBox` : chacun s'étire sur la forme qui s'en sert. */
export function ChromeDefs() {
  return (
    <svg class="chrome-defs" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="cx-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3b0" /><stop offset="0.45" stop-color="#ffc531" /><stop offset="1" stop-color="#b8720a" /></linearGradient>
        <linearGradient id="cx-gold-ring" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#fff6c4" /><stop offset="0.35" stop-color="#ffcf45" /><stop offset="0.7" stop-color="#e09a18" /><stop offset="1" stop-color="#9a5a06" /></linearGradient>
        <linearGradient id="cx-gold-soft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe9a0" /><stop offset="1" stop-color="#d08a14" /></linearGradient>
        <linearGradient id="cx-wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a97848" /><stop offset="0.5" stop-color="#7c5230" /><stop offset="1" stop-color="#55361a" /></linearGradient>
        <linearGradient id="cx-wood-dark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6e4a2a" /><stop offset="0.55" stop-color="#4e321b" /><stop offset="1" stop-color="#36210f" /></linearGradient>
        <linearGradient id="cx-slot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c1008" /><stop offset="1" stop-color="#3a2414" /></linearGradient>
        <radialGradient id="cx-enamel" cx="0.45" cy="0.3" r="0.75"><stop offset="0" stop-color="#5f7fe0" /><stop offset="0.55" stop-color="#2f3f98" /><stop offset="1" stop-color="#1a2160" /></radialGradient>
        <radialGradient id="cx-enamel-green" cx="0.45" cy="0.25" r="0.8"><stop offset="0" stop-color="#8ef0a0" /><stop offset="0.5" stop-color="#3fb85c" /><stop offset="1" stop-color="#1c6e33" /></radialGradient>
        <linearGradient id="cx-text-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0.15" stop-color="#fffbe0" /><stop offset="0.55" stop-color="#ffd24a" /><stop offset="1" stop-color="#e08a12" /></linearGradient>
        <linearGradient id="cx-gem-blue" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#bfe0ff" /><stop offset="0.45" stop-color="#4f8ae0" /><stop offset="1" stop-color="#1f3f8f" /></linearGradient>
        <linearGradient id="cx-gem-red" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffc0b8" /><stop offset="0.45" stop-color="#e0403a" /><stop offset="1" stop-color="#7a1418" /></linearGradient>
        <radialGradient id="cx-glow"><stop offset="0" stop-color="#fff6c2" stop-opacity="0.9" /><stop offset="0.5" stop-color="#ffd45c" stop-opacity="0.35" /><stop offset="1" stop-color="#ffd45c" stop-opacity="0" /></radialGradient>
      </defs>
    </svg>
  );
}

/** Une petite gemme taillée (losange), sertie d'or. */
export function Gem({ x, y, r, tone = 'blue' }: { x: number; y: number; r: number; tone?: 'blue' | 'red' }) {
  return (
    <g>
      <path d={`M${x} ${y - r * 1.25} L${x + r} ${y} L${x} ${y + r * 1.25} L${x - r} ${y} Z`} fill={INK} />
      <path d={`M${x} ${y - r} L${x + r * 0.78} ${y} L${x} ${y + r} L${x - r * 0.78} ${y} Z`} fill={`url(#cx-gem-${tone})`} />
      <path d={`M${x} ${y - r} L${x + r * 0.78} ${y} H${x} Z`} fill="#fff" opacity="0.45" />
    </g>
  );
}

/**
 * Un médaillon (bouton rond des bords de l'accueil) : anneau d'or biseauté et ses quatre clous, disque d'émail bleu nuit
 * avec son reflet ; le picto (`children`) est posé dessus. `size` en pixels.
 */
export function Medallion({ size, children, class: cls = '' }: { size: number; children?: ComponentChildren; class?: string }) {
  return (
    <span class={`medal ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <svg viewBox="0 0 100 100" width={size} height={size} aria-hidden="true">
        <ellipse cx="50" cy="95" rx="34" ry="5" fill="#000" opacity="0.3" />
        <circle cx="50" cy="50" r="48" fill={INK} />
        <circle cx="50" cy="50" r="45" fill="url(#cx-gold-ring)" />
        <path d="M14 38 A38 38 0 0 1 62 13" fill="none" stroke="#fffbe0" stroke-width="2.6" stroke-linecap="round" opacity="0.85" />
        <path d="M86 62 A38 38 0 0 1 38 87" fill="none" stroke="#7a4406" stroke-width="2.6" stroke-linecap="round" opacity="0.55" />
        {[45, 135, 225, 315].map((a) => {
          const r = (a * Math.PI) / 180, x = 50 + Math.cos(r) * 41.5, y = 50 + Math.sin(r) * 41.5;
          return <g><circle cx={x} cy={y} r="3.1" fill={INK} /><circle cx={x} cy={y} r="2.2" fill="#ffe9a0" /><circle cx={x - 0.6} cy={y - 0.6} r="0.9" fill="#fff" /></g>;
        })}
        <circle cx="50" cy="50" r="37.5" fill={INK} />
        <circle cx="50" cy="50" r="35.5" fill="url(#cx-enamel)" />
        <path d="M22 40 Q26 20 50 17 Q74 20 78 40 Q66 30 50 30 Q34 30 22 40 Z" fill="#fff" opacity="0.18" />
        <circle cx="50" cy="50" r="35.5" fill="none" stroke="#9fb4ff" stroke-width="1" opacity="0.5" />
      </svg>
      <span class="medal-in">{children}</span>
    </span>
  );
}

/** Le chevron d'or d'une languette (vers le bas = déplier, vers le haut = replier). */
export function Chevron({ up }: { up: boolean }) {
  const d = up ? 'M36 58 L50 44 L64 58' : 'M36 44 L50 58 L64 44';
  return (
    <svg viewBox="0 0 100 100" class="chevron" aria-hidden="true">
      <path d={d} fill="none" stroke={INK} stroke-width="15" stroke-linecap="round" stroke-linejoin="round" />
      <path d={d} fill="none" stroke="url(#cx-gold-soft)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  );
}

/** Une petite étincelle qui scintille (à poser dans un dessin). */
export function Twinkle({ x, y, r, late = false }: { x: number; y: number; r: number; late?: boolean }) {
  return <path class={`an-twinkle${late ? ' an-late' : ''}`} style={{ transformOrigin: `${x}px ${y}px` }} d={spark(x, y, r)} fill="#fff" />;
}
