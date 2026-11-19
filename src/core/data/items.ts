// Équipement : 4 emplacements par héros, 6 raretés. Le bonus grandit avec le chapitre où l'objet a été trouvé.
import type { Rng } from '../rng';

export const GEAR_SLOTS = ['weapon', 'armor', 'helmet', 'boots'] as const;
export type GearSlot = (typeof GEAR_SLOTS)[number];

/** 0 Gris, 1 Vert, 2 Bleu, 3 Violet, 4 Or, 5 Rouge. */
export const ITEM_RARITIES = 6;
export const ITEM_BASE_BONUS = [3, 6, 10, 15, 22, 30];
export const ITEM_DROP_WEIGHTS = [40, 30, 18, 8, 3, 1];

export interface Item {
  uid: number;
  slot: GearSlot;
  rarity: number;
  /** Chapitre où l'objet a été trouvé (0 = premier chapitre). */
  tier: number;
  /** Héros qui le porte, s'il est équipé. */
  heroUid?: number;
}

/** Bonus de force de l'objet, en %. */
export function itemBonus(item: Pick<Item, 'rarity' | 'tier'>): number {
  return Math.round((ITEM_BASE_BONUS[item.rarity] ?? 0) * (1 + 0.06 * item.tier));
}

/** Tire la rareté d'un objet ; `luck` décale le tirage vers le haut (donjons, coffres). */
export function rollItemRarity(rng: Rng, luck = 0): number {
  const weights = ITEM_DROP_WEIGHTS.map((w, r) => w * (1 + luck * r));
  let roll = rng() * weights.reduce((a, b) => a + b, 0);
  for (let r = 0; r < weights.length; r++) {
    roll -= weights[r]!;
    if (roll < 0) return r;
  }
  return 0;
}
