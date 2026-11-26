// Les pièces communes de l'interface, style moderne (26/11/2026, voir refonte-graphique/pixel/ui/STYLE.md) : barres,
// pilule du chapitre, bouton Combattre, pilule du niveau, médaillons, chevrons. Tout est dessiné par le CSS (style.css,
// « 4. Composants communs ») : formes lisses, dégradés doux, ombres douces. Plus aucun dessin en pixels ici.
import type { ComponentChildren } from 'preact';
import { useLayoutEffect, useRef, useState } from 'preact/hooks';
import type { Tone } from './px';

/** La taille réelle d'un élément (pour dessiner à sa mesure exacte). */
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

/**
 * Le fond d'une barre (en haut, en bas, sous le combat de l'accueil) : un bandeau raisin arrondi du côté du jeu.
 * **Toujours le dernier enfant de sa barre** (le tutoriel compte les onglets).
 */
export function BarArt({ kind }: { kind: 'top' | 'tabs' | 'dock'; cols?: number }) {
  return <span class={`bar-art bar-art-${kind}`} aria-hidden="true" />;
}

/** Le chapitre, en haut de l'accueil : une pilule de verre sombre, le titre, la progression ; le picto de la carte à droite. */
export function ChapterPlaque({ title, progress, icon }: { title: string; progress: number; icon?: ComponentChildren }) {
  const p = Math.max(0, Math.min(1, progress));
  return (
    <span class="chapter-plaque pxf" aria-hidden="true">
      <span class="chapter-text">
        <span class="chapter-title">{title}</span>
        <span class="chapter-bar pxf"><span style={{ width: `${p * 100}%` }} /></span>
      </span>
      {icon && <span class="chapter-map">{icon}</span>}
    </span>
  );
}

/** Le fond du grand bouton Combattre : le bouton vert arrondi (gris quand il n'y a plus rien à combattre). */
export function FightButtonArt({ off = false }: { off?: boolean }) {
  return <span class={`fight-art${off ? ' off' : ''}`} aria-hidden="true" />;
}

/** Le niveau du joueur, sous son portrait : une petite pilule d'or. */
export function LevelShield({ level }: { level: number }) {
  return <span class="lv-shield"><span>{level}</span></span>;
}

/** Le contour des personnages HD (pour les rares dessins qui le reprennent). */
export const INK = '#221022';

/**
 * Des dégradés SVG communs (anciens dessins SVG qui s'en servent encore) : posé une fois par l'application, jamais caché
 * par display: none.
 */
export function ChromeDefs() {
  return (
    <svg class="chrome-defs" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="cx-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff1a8" /><stop offset="0.45" stop-color="#ffc22e" /><stop offset="1" stop-color="#e58a00" /></linearGradient>
        <linearGradient id="cx-gold-ring" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#fff1a8" /><stop offset="0.5" stop-color="#ffb21f" /><stop offset="1" stop-color="#9a4f00" /></linearGradient>
        <linearGradient id="cx-gold-soft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd65c" /><stop offset="1" stop-color="#e58a00" /></linearGradient>
        <linearGradient id="cx-navy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2d86" /><stop offset="1" stop-color="#1e1648" /></linearGradient>
        <radialGradient id="cx-glow"><stop offset="0" stop-color="#fff6c2" stop-opacity="0.9" /><stop offset="0.5" stop-color="#ffc22e" stop-opacity="0.35" /><stop offset="1" stop-color="#ffc22e" stop-opacity="0" /></radialGradient>
      </defs>
    </svg>
  );
}

/**
 * Un médaillon (bouton des bords de l'accueil, portrait du joueur, portails) : une tuile lisse en dégradé de la teinte
 * (`tone`, raisin par défaut), le picto (`children`) posé dessus. `size` en pixels CSS ; la forme (rond, coins arrondis)
 * est réglée par le CSS de l'endroit.
 */
export function Medallion({ size, children, class: cls = '', tone = 'navy' }: { size: number; children?: ComponentChildren; class?: string; tone?: Tone }) {
  return (
    <span class={`medal medal-${tone} ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <span class="medal-in">{children}</span>
    </span>
  );
}

/** Le chevron d'une languette (vers le bas = déplier, vers le haut = replier) : un trait blanc arrondi. */
export function Chevron({ up }: { up: boolean }) {
  return <i class={`chevron${up ? ' up' : ''}`} aria-hidden="true" />;
}
