// Les décors des combats, la partie sans Phaser : les types (repères, éléments animés, particules, décor), la largeur des
// décors, et le passage d'un dessin JSX à un fichier SVG autonome. Les menus s'en servent aussi (compose.ts), sans
// charger Phaser.
import { render, type VNode } from 'preact';

export const NS = 'http://www.w3.org/2000/svg';
/** Largeur des décors : celle des combats. */
export const BW = 720;

/** Les repères d'un décor, en pixels de la scène. */
export interface Ctx {
  /** L'horizon : là où le sol de l'arène commence (le paysage se tient au-dessus). */
  hz: number;
  /** Le bas du décor (le haut du panneau des héros). */
  bottom: number;
  /** Le centre des pieds des combattants (milieu des deux équipes). */
  cx: number;
  cy: number;
  /** La plateforme de combat, d'un bord à l'autre : son bord du fond (p0) et son bord de devant (p1). Tous les pieds sont dessus. */
  p0: number;
  p1: number;
}

export type Anim =
  | { k: 'still' }
  /** dérive horizontale, en px/s ; repart de `from` une fois arrivé à `to` */
  | { k: 'drift'; speed: number; from: number; to: number }
  | { k: 'bob'; amp: number; period: number }
  | { k: 'sway'; deg: number; period: number }
  | { k: 'flicker'; min: number; period: number }
  | { k: 'pulse'; min: number; period: number }
  | { k: 'spin'; period: number }
  /** l'image défile vers le bas (cascade, chute de lave), en px/s */
  | { k: 'flow'; speed: number }
  /** apparaît par instants (éclair) : `every` = secondes entre deux éclats en moyenne */
  | { k: 'flash'; every: number };

/** Un élément animé (une texture, posée en un ou plusieurs endroits). */
export interface Sprite {
  id: string;
  /** Taille du dessin (son repère va de 0 à w, de 0 à h). */
  w: number;
  h: number;
  draw: () => VNode;
  /** Où le poser (x, y en px de la scène) : un exemplaire par position. */
  at: [number, number][];
  /** Point d'ancrage dans le dessin (0..1) : pied d'un fanion, axe des ailes d'un moulin… */
  origin?: [number, number];
  /** < 5 : derrière les combattants (le voile des compétences l'assombrit) ; > 1290 : devant eux. */
  depth: number;
  anim: Anim;
  /** Échelle de chaque exemplaire (sinon 1). */
  scale?: number[];
  alpha?: number;
  add?: boolean;
  /** Pour `flow` : hauteur visible de la bande qui défile (la texture se répète dedans). */
  flowH?: number;
}

/** Des particules (poussières de lumière, braises, neige, bulles, feuilles…). */
export interface Particles {
  id: string;
  size: number;
  draw: () => VNode;
  /** Zone d'apparition : x0, y0, x1, y1. */
  area: [number, number, number, number];
  depth: number;
  /** vitesse (px/s) en x et en y, chacune entre deux bornes */
  vx: [number, number];
  vy: [number, number];
  /** durée de vie (ms) */
  life: [number, number];
  /** combien à la fois (environ) */
  count: number;
  scale: [number, number];
  alpha: [number, number];
  add?: boolean;
  /** rotation (degrés par seconde), pour les feuilles */
  spin?: number;
}

/** Un décor de combat. */
export interface Scene {
  /** Couleur de secours (pendant le chargement, ou si les dessins ne passent pas). */
  base: number;
  sky: (c: Ctx) => VNode;
  land: (c: Ctx) => VNode;
  front?: (c: Ctx) => VNode;
  sprites?: (c: Ctx) => Sprite[];
  particles?: (c: Ctx) => Particles[];
}

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

