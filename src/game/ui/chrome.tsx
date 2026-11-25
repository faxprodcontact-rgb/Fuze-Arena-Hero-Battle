// Les pièces de l'interface, nouvelle DA (26/11/2026) : pixel art HD épuré (voir refonte-graphique/pixel/ui/STYLE.md).
// Les dessins viennent de px.ts (pixel par pixel, une seule palette) ; ici, les composants qui les posent : barres,
// plaque du chapitre, bouton Combattre, plaque du niveau, médaillons, chevrons. Plus aucun ornement : ni losange, ni
// gemme, ni clou, ni ruban, ni reflet qui passe.
import type { ComponentChildren } from 'preact';
import { useLayoutEffect, useRef, useState } from 'preact/hooks';
import { chevronUrl, INK as PX_INK, medalUrl, type Tone } from './px';

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

/**
 * Le fond d'une barre (en haut, en bas, sous le combat de l'accueil) : émail bleu nuit, filet d'or et contour du côté du
 * jeu (dessin `bar-top` / `bar-bottom` de px.ts). **Toujours le dernier enfant de sa barre** (le tutoriel compte les onglets).
 */
export function BarArt({ kind }: { kind: 'top' | 'tabs' | 'dock'; cols?: number }) {
  return <span class={`bar-art bar-art-${kind}`} aria-hidden="true" />;
}

/** La plaque du chapitre, en haut de l'accueil : émail bleu nuit cerclé d'or, le titre, la progression du chapitre. */
export function ChapterPlaque({ title, progress }: { title: string; progress: number }) {
  const p = Math.max(0, Math.min(1, progress));
  return (
    <span class="chapter-plaque pxf" aria-hidden="true">
      <span class="chapter-title">{title}</span>
      <span class="chapter-bar pxf"><span style={{ width: `${p * 100}%` }} /></span>
    </span>
  );
}

/** Le fond du grand bouton Combattre : le bouton vert dessiné (gris quand il n'y a plus rien à combattre). */
export function FightButtonArt({ off = false }: { off?: boolean }) {
  return <span class={`fight-art${off ? ' off' : ''}`} aria-hidden="true" />;
}

/** Le niveau du joueur, sous son portrait : une petite plaque bleu nuit cerclée d'or. */
export function LevelShield({ level }: { level: number }) {
  return <span class="lv-shield"><span>{level}</span></span>;
}

/** Le contour de toutes les pièces (le même que les héros HD). */
export const INK = PX_INK;

/**
 * Anciennement : les dégradés SVG communs. Les pièces sont maintenant des dessins en pixels (px.ts) ; le composant reste
 * (posé une fois par l'application) pour les dessins SVG qui n'ont pas encore changé de style.
 */
export function ChromeDefs() {
  return (
    <svg class="chrome-defs" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="cx-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff4b0" /><stop offset="0.45" stop-color="#ffd650" /><stop offset="1" stop-color="#c76a1a" /></linearGradient>
        <linearGradient id="cx-gold-ring" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="#fff4b0" /><stop offset="0.5" stop-color="#f0a830" /><stop offset="1" stop-color="#8a3f16" /></linearGradient>
        <linearGradient id="cx-gold-soft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd650" /><stop offset="1" stop-color="#c76a1a" /></linearGradient>
        <linearGradient id="cx-navy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34489c" /><stop offset="1" stop-color="#1c2457" /></linearGradient>
        <radialGradient id="cx-glow"><stop offset="0" stop-color="#fff6c2" stop-opacity="0.9" /><stop offset="0.5" stop-color="#ffd650" stop-opacity="0.35" /><stop offset="1" stop-color="#ffd650" stop-opacity="0" /></radialGradient>
      </defs>
    </svg>
  );
}

/**
 * Un médaillon (bouton rond des bords de l'accueil, portrait du joueur) : anneau d'or et disque d'émail en pixels, éclairé
 * en haut à droite ; le picto (`children`) est posé dessus. `size` en pixels CSS (de préférence pair : 2 px = 1 pixel du
 * dessin). `tone` : la couleur de l'émail.
 */
export function Medallion({ size, children, class: cls = '', tone = 'navy' }: { size: number; children?: ComponentChildren; class?: string; tone?: Tone }) {
  return (
    <span class={`medal ${cls}`} style={{ width: `${size}px`, height: `${size}px` }}>
      <img class="medal-art" src={medalUrl(size, tone)} alt="" aria-hidden="true" />
      <span class="medal-in">{children}</span>
    </span>
  );
}

/** Le chevron d'or d'une languette (vers le bas = déplier, vers le haut = replier). */
export function Chevron({ up }: { up: boolean }) {
  return <img class="chevron" src={chevronUrl(up)} alt="" aria-hidden="true" />;
}
