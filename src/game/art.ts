// Les couleurs des éléments, raretés et objets, et les images des personnages dans les menus : leur visage
// (public/art/hd/v/<id>.webp) et leur respiration en pied (public/art/hd/pied/<id>.webp), tirés des planches HD par
// refonte-graphique/pixel/hd/anim/vignettes.py. Au combat, les planches HD elles-mêmes (hd-fight.ts).
import type { Element, Rarity } from '../core/types';
import { DEFAULT_LOOK, heroArt, monsterArtId, type Look } from './look';

export const ELEMENT_COLOR: Record<Element, string> = {
  fire: '#ff6b3d', water: '#3da5ff', wind: '#5bd17a', earth: '#c08a4a',
};
export const RARITY_COLOR: Record<Rarity, string> = {
  common: '#9aa0b5', rare: '#3d8bff', epic: '#a35cff', legendary: '#ffc94a',
};
export const ITEM_COLORS = ['#9aa0b5', '#4cc46b', '#3d8bff', '#a35cff', '#ffc94a', '#ff4d5e'];

/** Le visage d'un personnage HD (héros, monstre de clan, grand boss) : carré, en pixel art agrandi sans flou. */
export function faceUrl(id: string): string {
  return `art/hd/v/${id}.webp`;
}
/** La respiration d'un personnage HD : une bande d'images de même taille (mesures dans hd-figures.ts). */
export function figureUrl(id: string): string {
  return `art/hd/pied/${id}.webp`;
}

/** Image d'un héros pour les menus (balise <img>) : son visage. */
export function heroImage(defId: string): string {
  return faceUrl(heroArt(defId));
}

/** Image d'un monstre pour les menus ; `look` choisit le clan (celui du combat à venir). */
export function monsterImage(monsterId: string, element: Element = 'fire', look: Look = DEFAULT_LOOK): string {
  return faceUrl(monsterArtId(monsterId, element, look));
}
