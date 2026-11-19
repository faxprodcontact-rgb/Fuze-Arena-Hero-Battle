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

// ---------- Forge, recyclage, renforcement ----------

/** Forge : 3 objets de même emplacement et même rareté donnent 1 objet de la rareté au-dessus. */
export const FORGE_COUNT = 3;

/** Poussière de forge rendue en recyclant un objet, selon sa rareté (un peu plus pour les chapitres avancés). */
const RECYCLE_DUST = [1, 3, 8, 20, 50, 120];
export function recycleDust(item: Pick<Item, 'rarity' | 'tier'>): number {
  return Math.round((RECYCLE_DUST[item.rarity] ?? 0) * (1 + 0.1 * item.tier));
}

/**
 * Renforcement des EMPLACEMENTS d'un héros (pas des objets) : +1 à +10.
 * Chaque cran ajoute 10 % au bonus de l'objet posé dans cet emplacement, quel qu'il soit :
 * changer d'objet ne fait rien perdre.
 */
export const SLOT_MAX_LEVEL = 10;
export const SLOT_LEVEL_GAIN = 0.1;

/** Coût pour passer l'emplacement du niveau `level` au niveau `level + 1`. Valeurs provisoires (réglage final avant la bêta). */
export function slotUpgradeCost(level: number): { gold: number; dust: number } {
  return { gold: Math.round(1500 * 1.75 ** level), dust: 5 * (level + 1) ** 2 };
}

/** Bonus en % d'un objet posé dans un emplacement renforcé. */
export function equippedBonus(item: Pick<Item, 'rarity' | 'tier'>, slotLevel: number): number {
  return Math.round(itemBonus(item) * (1 + SLOT_LEVEL_GAIN * slotLevel));
}
