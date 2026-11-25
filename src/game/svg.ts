// Un dessin fait par le code (en JSX) changé en fichier SVG autonome : Phaser s'en sert comme d'une image
// (pièces du panneau de combat, hud-art.tsx).
import { render, type VNode } from 'preact';

const NS = 'http://www.w3.org/2000/svg';

/** Un dessin (en JSX) changé en fichier SVG autonome, de la taille donnée. */
export function svgString(node: VNode, w: number, h: number): string {
  const host = document.createElementNS(NS, 'svg') as SVGSVGElement;
  render(node, host);
  host.setAttribute('xmlns', NS);
  host.setAttribute('width', String(w));
  host.setAttribute('height', String(h));
  host.setAttribute('viewBox', `0 0 ${w} ${h}`);
  const s = new XMLSerializer().serializeToString(host);
  render(null, host);
  return s;
}
