// Calculs dérivés de l'état du joueur (rien n'est modifié ici).
import { heroPowerWithGear, heroToUnit } from '../../core/battle/units';
import type { Slot, UnitInit } from '../../core/battle/types';
import { incomePerHour, OFFLINE_CAP_HOURS, levelCost } from '../../core/data/economy';
import { heroDef } from '../../core/data/heroes';
import { equippedBonus, type GearSlot, type Item } from '../../core/data/items';
import { ESSENCE_RATIO, IDLE_ITEM_HOURS, UNLOCKS, type Feature } from '../../core/data/modes';
import { levelCap } from '../../core/data/stats';
import { slotsAt } from '../../core/stages';
import type { Hero } from '../../core/types';
import { now } from './store';
import type { PlayerState } from './types';

export function heroByUid(s: PlayerState, uid: number): Hero | undefined {
  return s.heroes.find((h) => h.uid === uid);
}

export function heroItems(s: PlayerState, uid: number): Partial<Record<GearSlot, Item>> {
  const out: Partial<Record<GearSlot, Item>> = {};
  for (const it of s.items) if (it.heroUid === uid) out[it.slot] = it;
  return out;
}

export function slotLevel(s: PlayerState, uid: number, slot: GearSlot): number {
  return s.slotLevels[uid]?.[slot] ?? 0;
}

/** Bonus total de l'équipement d'un héros, en % (objets × renforcement de leurs emplacements). */
export function gearPct(s: PlayerState, uid: number): number {
  return s.items.filter((it) => it.heroUid === uid).reduce((sum, it) => sum + equippedBonus(it, slotLevel(s, uid, it.slot)), 0);
}

export function heroPower(s: PlayerState, hero: Hero): number {
  return heroPowerWithGear(hero, gearPct(s, hero.uid));
}

export function teamHeroes(s: PlayerState): { hero: Hero; slot: Slot }[] {
  return s.formation
    .map(([uid, slot]) => ({ hero: heroByUid(s, uid)!, slot }))
    .filter((x) => x.hero);
}

export function teamPower(s: PlayerState): number {
  return teamHeroes(s).reduce((sum, { hero }) => sum + heroPower(s, hero), 0);
}

export function teamUnits(s: PlayerState): UnitInit[] {
  return teamHeroes(s).map(({ hero, slot }) => heroToUnit(hero, slot, gearPct(s, hero.uid)));
}

export function slotCount(s: PlayerState): number {
  return slotsAt(s.campaign.cleared);
}

export function isUnlocked(s: PlayerState, feature: Feature): boolean {
  return s.campaign.cleared >= UNLOCKS[feature];
}

/** Butin hors ligne accumulé depuis la dernière récolte. */
export function idlePreview(s: PlayerState) {
  const hours = Math.min(OFFLINE_CAP_HOURS, Math.max(0, (now() - s.campaign.idleFrom) / 3.6e6));
  const perHour = incomePerHour(s.campaign.cleared);
  return {
    hours,
    full: hours >= OFFLINE_CAP_HOURS,
    gold: Math.floor(hours * perHour),
    essence: Math.floor(hours * perHour * ESSENCE_RATIO),
    items: Math.floor((s.campaign.itemHours + hours) / IDLE_ITEM_HOURS),
    perHour,
  };
}

export function levelUpCost(hero: Hero): { gold: number; essence: number } | null {
  if (hero.level >= levelCap(hero.stars)) return null;
  const gold = levelCost(hero.level);
  return { gold, essence: Math.round(gold * ESSENCE_RATIO) };
}

export function canLevelUp(s: PlayerState, hero: Hero): boolean {
  const cost = levelUpCost(hero);
  return !!cost && s.wallet.gold >= cost.gold && s.wallet.essence >= cost.essence;
}

export function sortedHeroes(s: PlayerState): Hero[] {
  return [...s.heroes].sort((a, b) => heroPower(s, b) - heroPower(s, a));
}

export function heroName(hero: Hero): string {
  return heroDef(hero.defId).name;
}
