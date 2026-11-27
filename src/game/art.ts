// Les couleurs des éléments, raretés et objets, et la tête des héros dans les menus (art/vecto/v/<id>.webp, faite
// par refonte-graphique/ui-moderne/heros/tetes.py). Le héros en entier : vecto.ts ; au combat : hd-fight.ts.
import type { Element, Rarity } from '../core/types';
import { artUrl } from './art-url';

export const ELEMENT_COLOR: Record<Element, string> = {
  fire: '#ff6b3d', water: '#3da5ff', wind: '#5bd17a', earth: '#c08a4a',
};
export const RARITY_COLOR: Record<Rarity, string> = {
  common: '#9aa0b5', rare: '#3d8bff', epic: '#a35cff', legendary: '#ffc94a',
};
export const ITEM_COLORS = ['#9aa0b5', '#4cc46b', '#3d8bff', '#a35cff', '#ffc94a', '#ff4d5e'];

/**
 * La tête d'un héros pour sa CARTE DE COMBAT (les cartes du bas, demande du 27/11) : sa tête vectorielle, lisse, centrée
 * sur le visage, à la même échelle pour tous (art/vecto/v/<id du jeu>.webp, faite par
 * refonte-graphique/ui-moderne/heros/tetes.py). Les cases des menus gardent le héros en entier.
 */
export function headUrl(defId: string): string {
  return artUrl(`art/vecto/v/${defId}.webp`);
}

/** Image d'un héros pour les menus (balise <img>) : sa tête vectorielle (la même que sa carte de combat). */
export function heroImage(defId: string): string {
  return headUrl(defId);
}
