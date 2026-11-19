// Équipement : 4 emplacements par héros, 6 raretés. Le bonus grandit avec le chapitre où l'objet a été trouvé.
import type { StatMods } from '../battle/types';
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
  /** Panoplie (à partir des objets Bleus) : 4 objets de la même panoplie donnent un bonus. */
  set?: GearSet;
}

// ---------- Ce que donne chaque emplacement ----------

/** Statistique principale de chaque emplacement (en %, sur la statistique du héros). */
export const SLOT_STAT: Record<GearSlot, 'atk' | 'hp' | 'def' | 'speed'> = { weapon: 'atk', armor: 'hp', helmet: 'def', boots: 'speed' };
/** La vitesse compte beaucoup : les bottes en donnent moins. */
const MAIN_SCALE: Record<GearSlot, number> = { weapon: 1, armor: 1, helmet: 1, boots: 0.4 };

/** Statistique principale de l'objet posé dans un emplacement renforcé (en %). */
export function itemMain(item: Pick<Item, 'rarity' | 'tier' | 'slot'>, slotLevel = 0): number {
  return Math.round(equippedBonus(item, slotLevel) * MAIN_SCALE[item.slot]);
}

/** Statistiques secondaires, à partir des objets Bleus (rareté 2), plus fortes avec la rareté. */
export function itemSubs(item: Pick<Item, 'rarity' | 'slot'>): StatMods {
  const r = item.rarity - 1;
  if (r < 1) return {};
  switch (item.slot) {
    case 'weapon': return { crit: 0.01 * r, ...(item.rarity >= 4 ? { critDmg: 0.05 * (item.rarity - 3) } : {}) };
    case 'armor': return { def: 0.03 * r };
    case 'helmet': return { tenacity: 0.02 * r };
    case 'boots': return { dodge: 0.015 * r };
  }
}

// ---------- Panoplies ----------

export const GEAR_SETS = ['fury', 'rampart', 'storm', 'vampire', 'guard'] as const;
export type GearSet = (typeof GEAR_SETS)[number];
export const SET_PIECES = 4;
/** Bonus d'une panoplie complète (4 objets). */
export const SET_BONUS: Record<GearSet, StatMods> = {
  fury: { critDmg: 0.25 },
  rampart: { hp: 0.12 },
  storm: { speed: 0.1 },
  vampire: { lifesteal: 0.1 },
  guard: { tenacity: 0.15 },
};

/** Tout ce que l'équipement d'un héros lui apporte (objets + renforcement des emplacements + panoplie). */
export function gearStats(worn: { item: Item; level: number }[]): StatMods {
  const total: Required<StatMods> = { hp: 0, atk: 0, def: 0, speed: 0, crit: 0, critDmg: 0, dodge: 0, tenacity: 0, lifesteal: 0 };
  const add = (m: StatMods) => {
    for (const [k, v] of Object.entries(m)) total[k as keyof StatMods] += v ?? 0;
  };
  const sets = new Map<GearSet, number>();
  for (const { item, level } of worn) {
    add({ [SLOT_STAT[item.slot]]: itemMain(item, level) / 100 });
    add(itemSubs(item));
    if (item.set) sets.set(item.set, (sets.get(item.set) ?? 0) + 1);
  }
  for (const [set, n] of sets) if (n >= SET_PIECES) add(SET_BONUS[set]);
  return total;
}

/** La panoplie complète portée, s'il y en a une. */
export function activeSet(worn: readonly Item[]): GearSet | undefined {
  const sets = new Map<GearSet, number>();
  for (const it of worn) if (it.set) sets.set(it.set, (sets.get(it.set) ?? 0) + 1);
  return [...sets].find(([, n]) => n >= SET_PIECES)?.[0];
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

/** Bonus en % d'un objet posé dans un emplacement renforcé (sert aussi à la puissance affichée). */
export function equippedBonus(item: Pick<Item, 'rarity' | 'tier'>, slotLevel: number): number {
  return Math.round(itemBonus(item) * (1 + SLOT_LEVEL_GAIN * slotLevel));
}
