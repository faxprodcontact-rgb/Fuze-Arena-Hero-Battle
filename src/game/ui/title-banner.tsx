// Le bandeau de titre d'une partie du jeu (« Aventure », « Héros »…), nouvelle DA (26/11/2026) : une plaque en pixels
// (px.ts « plaque-<teinte> » : contour, filet d'or, émail de la teinte), le picto de la partie à gauche, le titre en
// lettres cernées. Plus de ruban, de fleuron, de gemmes ni de reflet. Un titre long prend une taille plus petite (jamais coupé).
import type { ComponentChildren } from 'preact';
import { nearestTone, type Tone } from './px';

/**
 * `tone` = la teinte de l'émail (bleu nuit par défaut). `ribbon` (ancien réglage : trois couleurs de ruban) est encore
 * accepté : la teinte la plus proche de sa couleur du milieu est prise. Sans picto (`children`), le titre est centré.
 */
export function TitleBanner({ title, children, ribbon, tone }: { title: string; children?: ComponentChildren; ribbon?: [string, string, string]; tone?: Tone }) {
  const tn: Tone = tone ?? (ribbon ? nearestTone(ribbon[1]) : 'navy');
  const room = children ? 140 : 176;
  const size = Math.max(13, Math.min(22, room / (title.length * 0.55)));
  return (
    <div class={`title-banner pxf tb-${tn}`} style={{ '--pxf': `var(--px-plaque-${tn})` } as never}>
      {children}
      <span class="tb-title" style={{ fontSize: `${size}px` }}>{title}</span>
    </div>
  );
}
