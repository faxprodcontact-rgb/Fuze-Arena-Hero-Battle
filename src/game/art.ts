// Dessins des personnages. Les dessins redessinés par Hailuo (public/art/, voir art-meta.ts) sont utilisés quand ils
// existent ; sinon, les anciens dessins provisoires faits par le code ci-dessous (tête de faction + accessoire de rôle).
// Tous regardent vers la droite ; les monstres sont retournés au combat.
import { heroDef } from '../core/data/heroes';
import type { Element, Faction, HeroDef, Rarity } from '../core/types';
import { ART_META } from './art-meta';
import { PIXEL } from './pixel-meta';
import { DEFAULT_LOOK, monsterArtId, type Look } from './look';

export const FACTION_COLOR: Record<Faction, string> = {
  knights: '#c9a227', assassins: '#3a3f58', mages: '#7b4bd6', demons: '#b3262e', angels: '#e9e4f5', myths: '#2a9d8f',
};
export const ELEMENT_COLOR: Record<Element, string> = {
  fire: '#ff6b3d', water: '#3da5ff', wind: '#5bd17a', earth: '#c08a4a',
};
export const RARITY_COLOR: Record<Rarity, string> = {
  common: '#9aa0b5', rare: '#3d8bff', epic: '#a35cff', legendary: '#ffc94a',
};
export const ITEM_COLORS = ['#9aa0b5', '#4cc46b', '#3d8bff', '#a35cff', '#ffc94a', '#ff4d5e'];

const S = 128;
const SKINS = ['#f2c9a0', '#e0ac7e', '#b97a56', '#f6d7c3'];
const HAIRS = ['#3b2a20', '#e8c15a', '#c0392b', '#1d1d2b', '#d9d9e3', '#6b3fa0'];

type Ctx = CanvasRenderingContext2D;

function fill(c: Ctx, color: string, alpha = 1) {
  c.globalAlpha = alpha;
  c.fillStyle = color;
}
function circle(c: Ctx, x: number, y: number, r: number) {
  c.beginPath();
  c.arc(x, y, r, 0, Math.PI * 2);
  c.fill();
}
function ellipse(c: Ctx, x: number, y: number, rx: number, ry: number) {
  c.beginPath();
  c.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
  c.fill();
}
function rrect(c: Ctx, x: number, y: number, w: number, h: number, r: number) {
  c.beginPath();
  c.roundRect(x, y, w, h, r);
  c.fill();
}
function tri(c: Ctx, ax: number, ay: number, bx: number, by: number, cx: number, cy: number) {
  c.beginPath();
  c.moveTo(ax, ay);
  c.lineTo(bx, by);
  c.lineTo(cx, cy);
  c.closePath();
  c.fill();
}
function halfDome(c: Ctx, x: number, y: number, r: number) {
  c.beginPath();
  c.arc(x, y, r, Math.PI, 0);
  c.fill();
}
function eyes(c: Ctx, color = '#1b1b2f', y = 44) {
  fill(c, color);
  circle(c, 69, y, 3.2);
  circle(c, 80, y, 3.2);
}

function drawHeroOn(c: Ctx, d: HeroDef, index: number) {
  const el = ELEMENT_COLOR[d.element];
  const skin = d.faction === 'demons' ? '#e8a28c' : SKINS[index % SKINS.length]!;
  const hair = d.faction === 'angels' ? '#ffe08a' : HAIRS[(index * 7) % HAIRS.length]!;

  if (d.rarity === 'legendary') {
    const g = c.createRadialGradient(64, 64, 10, 64, 64, 64);
    g.addColorStop(0, 'rgba(255,201,74,0.55)');
    g.addColorStop(1, 'rgba(255,201,74,0)');
    c.fillStyle = g;
    circle(c, 64, 64, 64);
  }
  if (d.faction === 'angels') {
    fill(c, '#ffffff', 0.9);
    ellipse(c, 34, 74, 17, 25);
    ellipse(c, 28, 64, 13, 17);
  }
  if (d.faction === 'demons') {
    fill(c, '#7a1219');
    tri(c, 30, 104, 18, 84, 40, 96);
  }
  // Corps et ceinture couleur de l'élément.
  fill(c, FACTION_COLOR[d.faction]);
  rrect(c, 42, 62, 44, 50, 14);
  fill(c, el);
  c.fillRect(42, 88, 44, 7);
  // Tête.
  fill(c, skin);
  circle(c, 66, 44, 22);

  switch (d.faction) {
    case 'knights':
      fill(c, '#9aa3b5');
      halfDome(c, 66, 44, 24);
      c.fillRect(42, 40, 48, 6);
      fill(c, el);
      tri(c, 60, 18, 66, 4, 72, 18);
      eyes(c);
      break;
    case 'assassins':
      fill(c, '#23263a');
      halfDome(c, 66, 44, 26);
      c.fillRect(40, 40, 10, 26);
      fill(c, skin);
      ellipse(c, 74, 46, 13, 11);
      eyes(c, '#c81d3a');
      fill(c, el);
      c.fillRect(48, 56, 40, 8);
      tri(c, 48, 56, 30, 70, 48, 64);
      break;
    case 'mages':
      fill(c, hair);
      halfDome(c, 66, 46, 23);
      eyes(c);
      fill(c, '#4b2a8f');
      tri(c, 38, 32, 94, 32, 74, -2);
      c.fillRect(36, 28, 60, 8);
      fill(c, el);
      circle(c, 80, 14, 4);
      break;
    case 'demons':
      fill(c, '#2b1a1a');
      halfDome(c, 66, 40, 22);
      tri(c, 48, 30, 42, 6, 58, 26);
      tri(c, 80, 26, 92, 4, 88, 30);
      eyes(c, '#ffd34a');
      break;
    case 'angels':
      fill(c, hair);
      halfDome(c, 66, 40, 23);
      eyes(c, '#2f5fd0');
      c.globalAlpha = 1;
      c.strokeStyle = '#ffd34a';
      c.lineWidth = 4;
      c.beginPath();
      c.ellipse(66, 14, 17, 5, 0, 0, Math.PI * 2);
      c.stroke();
      break;
    case 'myths':
      fill(c, hair);
      halfDome(c, 66, 42, 22);
      eyes(c);
      fill(c, '#e0e0e0', d.role === 'protector' ? 1 : 0);
      ellipse(c, 70, 60, 15, 9);
      fill(c, '#3fa34d');
      for (let i = 0; i < 6; i++) ellipse(c, 46 + i * 8, 24 - Math.sin((i / 5) * Math.PI) * 6, 4.5, 3);
      break;
  }

  // Accessoire du rôle.
  switch (d.role) {
    case 'protector':
      fill(c, '#5d4a1a');
      rrect(c, 84, 64, 28, 40, 9);
      fill(c, el);
      rrect(c, 89, 70, 18, 28, 6);
      fill(c, '#fff3c4');
      c.fillRect(96, 74, 4, 20);
      break;
    case 'warrior':
    case 'marksman':
    case 'assassin':
      if (d.ranged && d.faction !== 'mages') {
        c.globalAlpha = 1;
        c.strokeStyle = '#9b6b3a';
        c.lineWidth = 4;
        c.beginPath();
        c.arc(90, 80, 24, -1.2, 1.2);
        c.stroke();
        fill(c, el);
        tri(c, 92, 78, 116, 80, 92, 82);
      } else if (d.ranged) {
        fill(c, '#6b4a2a');
        c.fillRect(98, 40, 5, 72);
        fill(c, el);
        circle(c, 100, 36, 9);
      } else {
        fill(c, '#d7dce6');
        tri(c, 92, 84, 122, 50, 98, 90);
        fill(c, el);
        c.fillRect(88, 84, 14, 6);
      }
      break;
    case 'healer':
      fill(c, '#e8d7a8');
      c.fillRect(98, 36, 5, 76);
      fill(c, '#5dff9a', 0.9);
      circle(c, 100, 32, 10);
      fill(c, '#ffffff', 0.8);
      c.fillRect(98, 26, 4, 12);
      c.fillRect(94, 30, 12, 4);
      break;
    case 'support':
      fill(c, el, 0.35);
      circle(c, 104, 56, 16);
      fill(c, el);
      circle(c, 104, 56, 9);
      fill(c, '#ffffff', 0.8);
      circle(c, 101, 53, 3);
      break;
  }
  c.globalAlpha = 1;
}

const MONSTERS: Record<string, (c: Ctx, el: string) => void> = {
  goblin: (c, el) => {
    fill(c, '#6b4a2a'); rrect(c, 46, 70, 38, 40, 12);
    fill(c, '#5bb34a'); circle(c, 64, 52, 22);
    tri(c, 44, 46, 22, 36, 46, 58); tri(c, 84, 46, 104, 36, 82, 58);
    eyes(c, '#ffe14a', 50);
    fill(c, el); rrect(c, 88, 58, 12, 44, 5);
  },
  wolf: (c, el) => {
    fill(c, '#5a5f73'); ellipse(c, 60, 84, 34, 22);
    fill(c, '#6c7189'); ellipse(c, 90, 62, 20, 17);
    tri(c, 80, 48, 84, 30, 92, 46); tri(c, 94, 46, 100, 30, 104, 48);
    fill(c, '#3a3d4d'); tri(c, 104, 64, 118, 68, 104, 72);
    eyes(c, el, 60);
    fill(c, '#4a4e60'); c.fillRect(38, 96, 8, 18); c.fillRect(72, 96, 8, 18);
    tri(c, 28, 80, 8, 70, 28, 90);
  },
  golem: (c, el) => {
    fill(c, '#7d8191'); rrect(c, 28, 40, 72, 72, 18);
    fill(c, '#6a6e7c'); rrect(c, 42, 14, 46, 36, 10);
    fill(c, el); c.fillRect(66, 26, 7, 7); c.fillRect(79, 26, 7, 7);
    fill(c, '#5c606d'); circle(c, 46, 66, 6); circle(c, 80, 92, 7);
  },
  archer: (c, el) => {
    fill(c, '#2c2c3a'); rrect(c, 46, 66, 36, 44, 10);
    fill(c, '#eeeadf'); circle(c, 64, 44, 20);
    fill(c, '#1b1b2f'); circle(c, 70, 42, 5); circle(c, 81, 42, 5);
    c.globalAlpha = 1; c.strokeStyle = el; c.lineWidth = 4;
    c.beginPath(); c.arc(86, 80, 26, -1.2, 1.2); c.stroke();
  },
  shaman: (c, el) => {
    fill(c, '#4f7a3a'); rrect(c, 44, 64, 40, 46, 12);
    fill(c, '#5bb34a'); circle(c, 64, 46, 20);
    fill(c, '#f3efe3'); rrect(c, 58, 32, 30, 26, 8);
    fill(c, '#1b1b2f'); circle(c, 68, 44, 3.5); circle(c, 79, 44, 3.5);
    fill(c, '#6b4a2a'); c.fillRect(94, 30, 5, 80);
    fill(c, el); tri(c, 96, 30, 110, 16, 104, 34);
  },
  wraith: (c, el) => {
    fill(c, '#3a3150', 0.9);
    c.beginPath(); c.moveTo(40, 112); c.quadraticCurveTo(30, 40, 64, 30); c.quadraticCurveTo(98, 40, 90, 112);
    c.lineTo(80, 100); c.lineTo(70, 112); c.lineTo(60, 100); c.lineTo(50, 112); c.closePath(); c.fill();
    fill(c, el); circle(c, 70, 52, 5); circle(c, 82, 52, 5);
  },
  ogre: (c, el) => {
    fill(c, '#6a4a8f'); rrect(c, 24, 52, 80, 64, 22);
    fill(c, '#8a6ab3'); circle(c, 64, 40, 28);
    eyes(c, '#ffe14a', 38);
    fill(c, '#ffffff'); tri(c, 66, 56, 70, 48, 74, 56); tri(c, 80, 56, 84, 48, 88, 56);
    fill(c, el); rrect(c, 98, 30, 18, 70, 8);
  },
  lich: (c, el) => {
    fill(c, '#2a1f3d'); tri(c, 30, 116, 98, 116, 64, 40);
    fill(c, '#eeeadf'); circle(c, 64, 40, 20);
    fill(c, '#7cf7c1'); circle(c, 70, 40, 4.5); circle(c, 81, 40, 4.5);
    fill(c, '#ffd34a'); tri(c, 46, 22, 52, 6, 58, 22); tri(c, 58, 22, 64, 2, 70, 22); tri(c, 70, 22, 76, 6, 82, 22);
    fill(c, el, 0.85); circle(c, 102, 70, 11);
  },
  dragon: (c, el) => {
    fill(c, el, 0.8); tri(c, 30, 40, 70, 60, 20, 90);
    fill(c, '#7a2a2a'); ellipse(c, 60, 82, 36, 24);
    fill(c, '#9a3a3a'); rrect(c, 78, 38, 18, 40, 8); ellipse(c, 98, 36, 20, 14);
    fill(c, '#ffe14a'); circle(c, 104, 32, 4);
    fill(c, '#ffffff'); tri(c, 108, 44, 112, 38, 116, 44);
    fill(c, '#5a1a1a'); tri(c, 24, 84, 4, 96, 26, 94);
  },
};

const cache = new Map<string, HTMLCanvasElement>();

function canvas(): [HTMLCanvasElement, Ctx] {
  const cv = document.createElement('canvas');
  cv.width = S;
  cv.height = S;
  return [cv, cv.getContext('2d')!];
}

/** Dessin d'un héros (canevas réutilisé par les menus et le combat). */
export function heroCanvas(defId: string): HTMLCanvasElement {
  const key = `h:${defId}`;
  let cv = cache.get(key);
  if (!cv) {
    let c: Ctx;
    [cv, c] = canvas();
    const d = heroDef(defId);
    drawHeroOn(c, d, Number(defId.split('-')[1] ?? 0));
    cache.set(key, cv);
  }
  return cv;
}

export function monsterCanvas(monsterId: string, element: Element = 'earth'): HTMLCanvasElement {
  const key = `m:${monsterId}:${element}`;
  let cv = cache.get(key);
  if (!cv) {
    let c: Ctx;
    [cv, c] = canvas();
    (MONSTERS[monsterId] ?? MONSTERS.goblin!)(c, ELEMENT_COLOR[element]);
    c.globalAlpha = 1;
    cache.set(key, cv);
  }
  return cv;
}

const urls = new Map<string, string>();

/** Les dessins redessinés par Hailuo existent-ils pour ce personnage (héros `knights-1`, monstre `glaces-6`…) ? */
export function hasArt(id: string): boolean {
  return id in ART_META.chars;
}
/** Image entière d'un personnage, pour les combats (pieds au point (106, 228) du repère du dessin). */
export function artUrl(id: string): string {
  return `art/p/${id}.webp`;
}
/** Vignette carrée d'un personnage, pour les menus. */
export function cardUrl(id: string): string {
  return isPixel(id) ? `art/px/c-${id}.webp` : `art/c/${id}.webp`;
}
/** Personnage redessiné en pixel art (planche animée art/px/<id>.webp, voir pixel-meta.ts). */
export function isPixel(id: string): boolean {
  return id in PIXEL.chars;
}
export function pixelUrl(id: string): string {
  return `art/px/${id}.webp`;
}

/** Image pour les menus (balise <img>). */
export function heroImage(defId: string): string {
  if (hasArt(defId)) return cardUrl(defId);
  let url = urls.get(defId);
  if (!url) {
    url = heroCanvas(defId).toDataURL();
    urls.set(defId, url);
  }
  return url;
}

/** Image d'un monstre pour les menus ; `look` choisit la famille (celle du combat à venir). */
export function monsterImage(monsterId: string, element: Element = 'earth', look: Look = DEFAULT_LOOK): string {
  const art = monsterArtId(monsterId, element, look);
  if (hasArt(art)) return cardUrl(art);
  const key = `${monsterId}:${element}`;
  let url = urls.get(key);
  if (!url) {
    url = monsterCanvas(monsterId, element).toDataURL();
    urls.set(key, url);
  }
  return url;
}
